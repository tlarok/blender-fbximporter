import bpy
import bmesh
import os
from .json_todo_export import register_export_item

EXPORT_TYPE_MAP = {
    'FLOATS': 0,
    'DISTANCE': 1,
    'ANGLE': 2,
}

class ExportVertexGroupWeightsOperator(bpy.types.Operator):
    bl_idname = "mesh.export_vertex_group_weights"
    bl_label = "Export Vertex Group Weights (UV Order)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.uv_export_props
        obj = context.active_object
        export_type_value = EXPORT_TYPE_MAP.get(props.export_type, 0)

        try:
            json_path = register_export_item(
                exportpath=props.exportpath,
                mesh_name=obj.name,
                data_type="weight_groups",
                group_name=props.vertex_group_name,
                clamp_min=props.clamp_min,
                clamp_max=props.clamp_max,
                float_type=export_type_value,
            )
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported vertex group weights to: {json_path}")
        return {'FINISHED'}