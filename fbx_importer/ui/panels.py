import bpy

class UVIndexExtractorPanel(bpy.types.Panel):
    bl_label = "UV Index Exporter"
    bl_idname = "VIEW3D_PT_uv_index_exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UV Tools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.uv_export_props
        obj = context.active_object
        scene = context.scene
        
        if obj and obj.type == 'MESH':
            if not obj.name.startswith("collision_"):
                layout.prop(props, "filename")
                layout.operator("mesh.extract_uv_indices", icon='EXPORT')
                
                layout.separator()
                layout.label(text="Manage Saved Files:")
                layout.prop(props, "selected_file")
                layout.operator("mesh.select_vertices_from_file", icon='RESTRICT_SELECT_OFF')
                layout.operator("mesh.rename_uv_file", icon='FILE_REFRESH')
                layout.operator("mesh.delete_uv_file", icon='FILE_REFRESH')
                layout.operator("mesh.open_uv_folder", icon='FILE_FOLDER')
        
        
        
        
            if obj.name.startswith("collision_capsule_"):
                # Resizing controls
                box = layout.box()
                box.label(text="Resize Settings:")
                
                props_capsule = obj.capsule_scale_props
                row = box.row()
                row.prop(props_capsule, "scale_top", text="Bottom")
                row.prop(props_capsule, "scale_center", text="Middle")
                row.prop(props_capsule, "scale_bottom", text="Top")

                layout.operator("mesh.resize_capsule", icon='MOD_ARRAY')
        
        layout.separator()
        layout.label(text="Collidable:")
        layout.operator("import_scene.collidable_create", icon='IMPORT')
        
        if obj and obj.type == 'ARMATURE':
            layout.operator("place.place", icon='IMPORT')
        
        if obj and obj.type == 'MESH':
            layout.prop(props, "bone_name")
            layout.prop(props, "collision_type")
            layout.operator("mesh.collision_conv")
            if obj.name.startswith("collision_capsule_"):
                row = layout.row()
                row.operator("object.toggle_capsule_length")
            elif not obj.name.startswith("collision_"):
                box = layout.box()
                box.label(text="Export Normalize:")

                row = box.row()
                row.prop(props, "clamp_min")
                row.prop(props, "clamp_max")
                layout.prop(props, "export_type", text="Weight Type")
                layout.prop(props, "vertex_group_name")
                layout.operator("mesh.export_vertex_group_weights", icon='EXPORT')
        
        layout.separator()
        layout.prop(props, "filterpath")
        layout.prop(props, "exportpath")
        layout.operator("mesh.export_and_run_fbximporter", icon='EXPORT')