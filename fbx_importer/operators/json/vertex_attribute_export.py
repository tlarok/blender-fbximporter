import bpy
import bmesh
import os
from .json_todo_export import register_export_item

EXPORT_TYPE_MAP = {
    'FLOATS': 0,
    'DISTANCE': 1,
    'ANGLE': 2,
}

class ExportVertexColorAttributeOperator(bpy.types.Operator):
    bl_idname = "mesh.export_vertex_color_atribute"
    bl_label = "Export Vertex attribute"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.uv_export_props
        obj = context.active_object
        export_type_value = EXPORT_TYPE_MAP.get(props.export_type, 0)
        
        try:
            json_path = register_export_item(
                exportpath=props.exportpath,
                mesh_name=obj.name,
                data_type="vertex_colors",
                group_name=props.vertex_color_name,
                clamp_min=props.clamp_min,
                clamp_max=props.clamp_max,
                float_type=export_type_value,
            )
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported {props.vertex_color_name} to: {json_path}")
        return {'FINISHED'}