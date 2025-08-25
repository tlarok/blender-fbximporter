import bpy
import os
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty
import subprocess

def load_vertex_ids(filepath):
    """Reads vertex IDs from a text file and returns them as a list of integers."""
    if not os.path.isfile(filepath):
        return []

    vertex_ids = []
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if ":" in line:
                    try:
                        index = int(line.split(":")[0])
                        vertex_ids.append(index)
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Error loading vertex IDs from file {filepath}: {e}")
    return vertex_ids


class UVSelectVerticesFromFileOperator(bpy.types.Operator):
    bl_idname = "mesh.select_vertices_from_file"
    bl_label = "Select Vertices From File"

    def execute(self, context):
        props = context.scene.uv_export_props
        obj = bpy.context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        # Ensure correct filename
        filename = props.selected_file
        if not filename.startswith(obj.name + "_"):
            filename = f"{obj.name}_{filename}"

        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
        if not blend_path:
            self.report({'ERROR'}, "Please save your .blend file first.")
            return {'CANCELLED'}

        folder = os.path.join(os.path.dirname(blend_path), "export_data", "selectionsets")
        filepath = os.path.join(folder, filename)

        if not os.path.isfile(filepath):
            self.report({'ERROR'}, f"File not found: {filepath}")
            return {'CANCELLED'}

        # Go to edit mode and deselect all
        if bpy.context.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        selected_indices = []

        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if ":" in line:
                        try:
                            index = int(line.split(":")[0])
                            selected_indices.append(index)
                        except ValueError:
                            continue
        except Exception as e:
            self.report({'ERROR'}, f"Failed to read file: {e}")
            return {'CANCELLED'}

        for idx in selected_indices:
            if 0 <= idx < len(mesh.vertices):
                mesh.vertices[idx].select = True

        bpy.ops.object.mode_set(mode='EDIT')
        self.report({'INFO'}, f"Selected {len(selected_indices)} vertices from {filename}")
        return {'FINISHED'}

class UVDeleteFileOperator(bpy.types.Operator):
    bl_idname = "mesh.delete_uv_file"
    bl_label = "Delete UV File"

    def execute(self, context):
        import os

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
        file_path = os.path.join(folder, selected_file)

        if not os.path.exists(file_path):
            self.report({'ERROR'}, "Selected file not found")
            return {'CANCELLED'}

        try:
            os.remove(file_path)
            self.report({'INFO'}, f"Deleted file: {selected_file}")

            # Clear selection safely
            if "selected_file" in props:
                del props["selected_file"]

            # Optional: force UI to redraw
            for area in context.screen.areas:
                if area.type == 'PROPERTIES':
                    area.tag_redraw()

            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to delete file: {e}")
            return {'CANCELLED'}

class UVOpenFolderOperator(bpy.types.Operator):
    bl_idname = "mesh.open_uv_folder"
    bl_label = "Open Output Folder"

    def execute(self, context):
        props = context.scene.uv_export_props
        if props.exportpath != "":
            folder = props.exportpath
        else:
            folder = get_export_folder()
        if os.name == 'nt':
            subprocess.Popen(f'explorer "{folder}"')
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', folder])
        else:
            self.report({'WARNING'}, "Unsupported OS for opening folder")
        return {'FINISHED'}

class UVRenameFileOperator(bpy.types.Operator):
    bl_idname = "mesh.rename_uv_file"
    bl_label = "Rename UV File"
    new_name: StringProperty(name="New Name", default="renamed_uv_indices")

    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}
            
        props = context.scene.uv_export_props
        old_file = props.selected_file
        new_file = self.new_name.strip()
        if not new_file.endswith(".txt"):
            new_file += ".txt"
            
        new_file = obj.name + "_" + new_file
        
        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        folder = os.path.join(os.path.dirname(blend_path), "export_data", "selectionsets")
        os.makedirs(folder, exist_ok=True)
        old_path = os.path.join(folder, old_file)
        new_path = os.path.join(folder, new_file)

        if not os.path.exists(old_path):
            self.report({'ERROR'}, "Original file not found")
            return {'CANCELLED'}
        if os.path.exists(new_path):
            self.report({'ERROR'}, "A file with the new name already exists")
            return {'CANCELLED'}

        os.rename(old_path, new_path)
        self.report({'INFO'}, f"Renamed to: {new_file}")
        return {'FINISHED'}

    def invoke(self, context, event):
        props = context.scene.uv_export_props
        
        obj = context.active_object
        if obj and props.selected_file and props.selected_file != "NONE":
            prefix = obj.name + "_"
            base_name = props.selected_file
            if base_name.startswith(prefix):
                base_name = base_name[len(prefix):]
            if base_name.endswith(".txt"):
                base_name = base_name[:-4]
            self.new_name = base_name  # Pre-fill dialog
        return context.window_manager.invoke_props_dialog(self)