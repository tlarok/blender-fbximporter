import bpy
import bmesh
import os
from .json_todo_export import register_export_item

class UVIndexExtractorOperator(bpy.types.Operator):
    bl_idname = "mesh.extract_uv_indices"
    bl_label = "Save UV Indices"
    bl_options = {'REGISTER', 'UNDO'}

    def create_or_update_boolean_attribute(self, obj, filename, selection_states):
        """Create integer attribute on POINT domain from given selection states."""
        original_mode = obj.mode
        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        if filename in mesh.attributes:
            mesh.attributes.remove(mesh.attributes[filename])

        attr = mesh.attributes.new(name=filename, type='INT', domain='POINT')
        for i, selected in enumerate(selection_states):
            if i < len(attr.data):
                attr.data[i].value = 1 if selected else 0

        if original_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode=original_mode)
        return attr

    def execute(self, context):
        props = context.scene.uv_export_props
        filename = props.filename
        export_path = props.exportpath
        obj = context.active_object

        if obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh")
            return {'CANCELLED'}

        # Detect selection mode
        mesh_select_mode = context.tool_settings.mesh_select_mode
        if mesh_select_mode[0]:      # vertex mode
            data_type = "uv_indices"
            # We'll fill vertex selection directly
            use_face_mode = False
        elif mesh_select_mode[2]:    # face mode
            data_type = "uv_faces"
            use_face_mode = True
        else:
            self.report({'ERROR'}, "Please switch to Vertex or Face selection mode")
            return {'CANCELLED'}

        # Store original mode
        original_mode = obj.mode

        # Ensure EDIT mode to read selections
        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        mesh = obj.data
        bm = bmesh.from_edit_mesh(mesh)

        # Collect vertex selection states
        if use_face_mode:
            # Face mode: mark vertices belonging to any selected face
            bm.faces.ensure_lookup_table()
            # Initialize all vertices as unselected
            bm.verts.ensure_lookup_table()
            for v in bm.verts:
                v.select = False
            # Select vertices of selected faces
            for face in bm.faces:
                if face.select:
                    for vert in face.verts:
                        vert.select = True
            # Store selection state for each vertex
            selection_states = [v.select for v in bm.verts]
        else:
            # Vertex mode: directly read vertex selection
            bm.verts.ensure_lookup_table()
            selection_states = [v.select for v in bm.verts]

        bmesh.update_edit_mesh(mesh)

        # Create the attribute (always POINT domain)
        try:
            self.create_or_update_boolean_attribute(obj, filename, selection_states)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create attribute: {str(e)}")
            if original_mode != obj.mode:
                bpy.ops.object.mode_set(mode=original_mode)
            return {'CANCELLED'}

        # Restore original mode
        if original_mode != obj.mode:
            bpy.ops.object.mode_set(mode=original_mode)

        # Register export item with the determined data_type
        try:
            json_path = register_export_item(
                exportpath=export_path,
                mesh_name=obj.name,
                data_type=data_type,
                group_name=filename,
            )
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, f"UV indices saved to: {json_path}")
        return {'FINISHED'}