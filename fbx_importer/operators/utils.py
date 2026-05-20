import bpy
import os
import json
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty
import subprocess
import os
from ..ui.properties import list_saved_files
from .json.json_todo_export import rename_export_item, remove_export_item


def load_vertex_ids(filepath, mesh_name, group_name):
    """
    Reads vertex IDs from a JSON file for a given mesh and group.
    
    Returns a list of integers (vertex IDs).
    """
    if not os.path.isfile(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        
        if mesh_name not in content:
            print(f"Mesh '{mesh_name}' not found in {filepath}")
            return []
        
        
        obj_name = mesh_name.split("|")[0].strip()
        mesh_entry = content[obj_name]
        if group_name not in mesh_entry:
            print(f"Group '{group_name}' not found under mesh '{obj_name}' in {filepath}")
            return []

        group_entry = mesh_entry[group_name]

        # The keys are vertex IDs (as strings), values are uv index lists
        vertex_ids = [int(v_id) for v_id in group_entry.keys()]
        return vertex_ids

    except Exception as e:
        print(f"Error loading vertex IDs from {filepath}: {e}")
        return []


class UVDeleteFileOperator(bpy.types.Operator):
    bl_idname = "mesh.delete_uv_file"
    bl_label = "Delete UV File"
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        props = context.scene.uv_export_props
        selected_file = props.selected_file

        if not selected_file or selected_file == "NONE":
            self.report({'ERROR'}, "No file selected to delete")
            return {'CANCELLED'}
        
        mesh_name = obj.name  # Full object name
        data_type = "uv_indices"
        exportpath = props.exportpath
        
        # 1. Check if attribute exists and remove it
        if selected_file in obj.data.attributes:
            mesh = obj.data
            attributes = mesh.attributes
            attributes.remove(attributes[selected_file])
        
        # 2. Remove from JSON
        try:
            success = remove_export_item(
                exportpath=exportpath,
                mesh_name=mesh_name,
                data_type=data_type,
                group_name=selected_file
            )
            
            if not success:
                self.report({'ERROR'}, f"Group '{selected_file}' not found in JSON")
                return {'CANCELLED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove from JSON: {e}")
            return {'CANCELLED'}

        # 3. Update EnumProperty safely
        # Re-run list_saved_files to get updated list
        items = [item[0] for item in list_saved_files(None, context)]
        if items:
            props.selected_file = items[0]
        else:
            props.selected_file = "NONE"

        # 4. Force UI redraw
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()

        self.report({'INFO'}, f"Deleted attribute and group: {selected_file}")
        return {'FINISHED'}



class UVSelectVerticesFromFileOperator(bpy.types.Operator):
    bl_idname = "mesh.select_vertices_from_file"
    bl_label = "Select Vertices From Attribute"

    def execute(self, context):
        props = context.scene.uv_export_props
        obj = context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Attribute name comes from props.selected_file
        attribute_name = props.selected_file.strip()
        if not attribute_name:
            self.report({'ERROR'}, "No attribute selected")
            return {'CANCELLED'}

        # Get the attribute
        if attribute_name not in obj.data.attributes:
            self.report({'ERROR'}, f"Attribute '{attribute_name}' not found")
            return {'CANCELLED'}
        
        
        bpy.ops.object.mode_set(mode='OBJECT')
        attr = obj.data.attributes[attribute_name]

        # Get vertex indices where attribute value is 1
        selected_indices = []
        for i, data in enumerate(attr.data):
            if data.value == 1:
                selected_indices.append(i)

        if not selected_indices:
            self.report({'WARNING'}, f"No vertices found with value 1 in attribute '{attribute_name}'")
            # Still clear selection and return
            if context.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            if context.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}

        # Switch to edit mode and select vertices (using the proven pattern)
        if context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Deselect all first
        bpy.ops.mesh.select_all(action='DESELECT')
        
        # Switch to object mode for vertex selection
        bpy.ops.object.mode_set(mode='OBJECT')

        # Select the vertices
        mesh = obj.data
        for idx in selected_indices:
            if 0 <= idx < len(mesh.vertices):
                mesh.vertices[idx].select = True

        # Switch back to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        self.report({'INFO'}, f"Selected {len(selected_indices)} vertices from attribute '{attribute_name}'")
        return {'FINISHED'}



class UVOpenFolderOperator(bpy.types.Operator):
    bl_idname = "mesh.open_uv_folder"
    bl_label = "Open Output Folder"

    def execute(self, context):
        props = context.scene.uv_export_props
        if props.exportpath:
            folder = props.exportpath
        else:
            if bpy.data.filepath:
                blend_path = bpy.data.filepath
                folder = os.path.join(os.path.dirname(blend_path), "export_data")
            else:
                self.report({'ERROR'}, f"blend file does not have a path")
                return {'CANCELLED'}
        if os.name == 'nt':
            subprocess.Popen(f'explorer "{folder}"')
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', folder])
        else:
            self.report({'WARNING'}, "Unsupported OS for opening folder")
        return {'FINISHED'}




class UVRenameFileOperator(bpy.types.Operator):
    bl_idname = "mesh.rename_uv_file"
    bl_label = "Rename Export Item"
    
    new_name: StringProperty(name="New Name", default="")
    
    def execute(self, context):
        obj = context.active_object
        mesh_name = obj.name
        
        props = context.scene.uv_export_props
        old_name = props.selected_file
        
        if not old_name or old_name == "NONE":
            self.report({'ERROR'}, "Select item to rename")
            return {'CANCELLED'}
        
        new_name = self.new_name.strip()
        
        if not new_name:
            self.report({'ERROR'}, "Enter new name")
            return {'CANCELLED'}
        
        if old_name == new_name:
            self.report({'ERROR'}, "Names are same")
            return {'CANCELLED'}
        
        exportpath = props.exportpath
        data_type = "uv_indices"  # Since your class is for UV indices
        
        # 1. Rename attribute on mesh (if it exists)
        if old_name in obj.data.attributes:
            attr = obj.data.attributes[old_name]
            attr.name = new_name
        
        # 2. Rename in JSON
        try:
            json_path = rename_export_item(
                exportpath=exportpath,
                data_type=data_type,
                mesh_name=mesh_name,
                old_name=old_name,
                new_name=new_name
            )
            
            # 3. Update UI selection
            props.selected_file = new_name
            
            self.report({'INFO'}, f"Renamed '{old_name}' to '{new_name}'")
            return {'FINISHED'}
            
        except Exception as e:
            # If JSON rename fails, revert attribute name
            if new_name in obj.data.attributes:
                obj.data.attributes[new_name].name = old_name
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        props = context.scene.uv_export_props
        old_name = props.selected_file
        if old_name and old_name != "NONE":
            self.new_name = old_name
        return context.window_manager.invoke_props_dialog(self)