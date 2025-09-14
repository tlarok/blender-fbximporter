import bpy
import os
import json
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty
import subprocess
import json
import os
from ..ui.properties import list_saved_files


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

        mesh_entry = content[mesh_name]
        if group_name not in mesh_entry:
            print(f"Group '{group_name}' not found under mesh '{mesh_name}' in {filepath}")
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
        import os
        import json

        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        props = context.scene.uv_export_props
        selected_file = props.selected_file

        if not selected_file or selected_file == "NONE":
            self.report({'ERROR'}, "No file selected to delete")
            return {'CANCELLED'}
        
        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        folder = os.path.join(os.path.dirname(blend_path), "export_data", "selectionsets")
        json_path = os.path.join(folder, "uv_indices.json")

        if not os.path.exists(json_path):
            self.report({'ERROR'}, f"No uv_indices.json file found at {json_path}")
            return {'CANCELLED'}

        # Load JSON
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load JSON: {e}")
            return {'CANCELLED'}

        # Remove the selected group
        mesh_name = obj.name
        if mesh_name in data and selected_file in data[mesh_name]:
            del data[mesh_name][selected_file]

            # If no groups left for this mesh, optionally remove the mesh entry
            if not data[mesh_name]:
                del data[mesh_name]

            # Save back JSON
            try:
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                self.report({'ERROR'}, f"Failed to save JSON: {e}")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, f"Group '{selected_file}' not found in JSON")
            return {'CANCELLED'}

        # Update EnumProperty safely
        items = [item[0] for item in list_saved_files(None, context)]
        if items:
            props.selected_file = items[0]
        else:
            props.selected_file = "NONE"

        # Optional: force UI redraw
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()

        self.report({'INFO'}, f"Deleted group: {selected_file}")
        return {'FINISHED'}



class UVSelectVerticesFromFileOperator(bpy.types.Operator):
    bl_idname = "mesh.select_vertices_from_file"
    bl_label = "Select Vertices From JSON"

    def execute(self, context):
        props = context.scene.uv_export_props
        obj = bpy.context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Group name comes from props.selected_file
        group_name = props.selected_file.strip()
        if not group_name:
            self.report({'ERROR'}, "No group selected in props.selected_file")
            return {'CANCELLED'}

        # Always use uv_indices.json
        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
        if not blend_path:
            self.report({'ERROR'}, "Please save your .blend file first.")
            return {'CANCELLED'}

        folder = os.path.join(os.path.dirname(blend_path), "export_data", "selectionsets")
        filepath = os.path.join(folder, "uv_indices.json")

        if not os.path.isfile(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        # Load vertex IDs from JSON
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = json.load(f)

            if obj.name not in content:
                self.report({'ERROR'}, f"Mesh '{obj.name}' not found in {filepath}")
                return {'CANCELLED'}

            mesh_entry = content[obj.name]

            if group_name not in mesh_entry:
                self.report({'ERROR'}, f"Group '{group_name}' not found in mesh '{obj.name}'")
                return {'CANCELLED'}

            group_entry = mesh_entry[group_name]

            # Vertex IDs are the keys in the group
            selected_indices = [int(v_id) for v_id in group_entry.keys()]

        except Exception as e:
            self.report({'ERROR'}, f"Failed to read JSON: {e}")
            return {'CANCELLED'}

        # Switch to edit mode and select vertices
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        for idx in selected_indices:
            if 0 <= idx < len(mesh.vertices):
                mesh.vertices[idx].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        self.report({'INFO'}, f"Selected {len(selected_indices)} vertices from group '{group_name}'")
        return {'FINISHED'}


class UVOpenFolderOperator(bpy.types.Operator):
    bl_idname = "mesh.open_uv_folder"
    bl_label = "Open Output Folder"

    def execute(self, context):
        props = context.scene.uv_export_props
        if props.exportpath != "":
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
    bl_label = "Rename UV Group"
    new_name: bpy.props.StringProperty(name="New Name", default="renamed_group")

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        props = context.scene.uv_export_props
        old_group = props.selected_file
        new_group = self.new_name.strip()

        if not old_group or old_group == "NONE":
            self.report({'ERROR'}, "No group selected to rename")
            return {'CANCELLED'}
        if old_group == new_group:
            self.report({'ERROR'}, "New name is the same as the current name")
            return {'CANCELLED'}

        # Determine JSON path
        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        folder = os.path.join(os.path.dirname(blend_path), "export_data", "selectionsets")
        os.makedirs(folder, exist_ok=True)
        json_path = os.path.join(folder, "uv_indices.json")

        if not os.path.exists(json_path):
            self.report({'ERROR'}, "uv_indices.json not found")
            return {'CANCELLED'}

        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if obj.name not in data or old_group not in data[obj.name]:
            self.report({'ERROR'}, f"Group '{old_group}' not found for mesh '{obj.name}'")
            return {'CANCELLED'}

        # Check for name conflicts
        if new_group in data[obj.name]:
            self.report({'ERROR'}, f"A group with name '{new_group}' already exists")
            return {'CANCELLED'}

        # Rename key
        data[obj.name][new_group] = data[obj.name].pop(old_group)

        # Save JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # Update selection
        props.selected_file = new_group
        self.report({'INFO'}, f"Renamed group '{old_group}' to '{new_group}'")
        return {'FINISHED'}

    def invoke(self, context, event):
        props = context.scene.uv_export_props
        old_group = props.selected_file
        if old_group and old_group != "NONE":
            self.new_name = old_group
        return context.window_manager.invoke_props_dialog(self)
