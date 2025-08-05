bl_info = {
    "name": "UV Index Exporter",
    "author": "Tlarok",
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > UV Tools",
    "description": "Exports UV indices per vertex and allows vertex selection from saved files",
    "category": "UV",
}

import bpy
import bmesh
import os
import subprocess
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty
from mathutils import Vector, Quaternion
import mathutils
from bpy.app.handlers import persistent
from io_scene_fbx import import_fbx
from math import fabs, isclose
import struct

EXPORT_FOLDER_NAME = "export_data"

capsule_bottom = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
capsule_top = [144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271]
capsule_center = [128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143]


def float_to_hex64(value: float) -> str:
    """Convert a float to its IEEE 754 double-precision hex representation."""
    packed = struct.pack('>d', value)  # Big-endian double
    return packed.hex()

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

def get_export_folder():
    folder = os.path.join(bpy.path.abspath("//"), EXPORT_FOLDER_NAME)
    os.makedirs(folder, exist_ok=True)
    return folder

def list_saved_files(self, context):
    
    props = context.scene.uv_export_props
    obj = context.active_object
    if not obj:
        return [("NONE", "None", "", 0)]
    
    if props.exportpath != "":
        blend_path = props.exportpath
    else:
        blend_path = bpy.data.filepath
        if not blend_path:
            return [("NONE", "None", "", 0)]

    folder = os.path.join(os.path.dirname(blend_path), "export_data", "selectionsets")
    if not os.path.exists(folder):
        return [("NONE", "None", "", 0)]

    files = []
    prefix = obj.name + "_"
    for fname in os.listdir(folder):
        if fname.endswith(".txt") and fname.startswith(prefix):
            short_name = fname[len(prefix):-4]  # strip prefix and ".txt"
            files.append((fname, short_name, ""))

    if not files:
        files = [("NONE", "None", "")]

    return files

class ExportVertexGroupWeightsOperator(bpy.types.Operator):
    bl_idname = "mesh.export_vertex_group_weights"
    bl_label = "Export Vertex Group Weights (UV Order)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.uv_export_props
        obj = context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object.")
            return {'CANCELLED'}

        vg_name = props.vertex_group_name
        if vg_name not in obj.vertex_groups:
            self.report({'ERROR'}, f"Vertex group '{vg_name}' not found.")
            return {'CANCELLED'}

        vgroup = obj.vertex_groups[vg_name]

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "Mesh has no active UV map.")
            bm.free()
            return {'CANCELLED'}

        loop_weights = []  # List of (uv_index, hex_weight)

        uv_index = 0
        for face in bm.faces:
            if len(face.verts) != 3:
                self.report({'ERROR'}, "Non-triangular face detected. Please triangulate the mesh.")
                bm.free()
                return {'CANCELLED'}

            for loop in face.loops:
                vert = loop.vert
                try:
                    weight = vgroup.weight(vert.index)
                except RuntimeError:
                    weight = 0.0
                hex_value = weight
                loop_weights.append((uv_index, hex_value))
                uv_index += 1

        bm.free()

        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/floatchannels")
        os.makedirs(export_dir, exist_ok=True)

        filename = f"{obj.name}_{vg_name}.txt"
        filepath = os.path.join(export_dir, filename)
        
        props = context.scene.uv_export_props
        export_mode = props.export_type
        
        clamp_min = context.scene.uv_export_props.clamp_min
        clamp_max = context.scene.uv_export_props.clamp_max
        
        export_mode_int = {
            'FLOAT': 0,
            'DISTANCE': 1,
            'ANGLE': 2
        }[export_mode]
                
        try:
            with open(filepath, 'w') as f:
                f.write(f"{export_mode_int}\n")
                for uv_idx, hex_weight in loop_weights:
                    w = (hex_weight * (clamp_max - clamp_min)) + clamp_min
                    f.write(f"{round(w, 5)}\n")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to write file: {str(e)}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported {len(loop_weights)} UV weights to {filepath}")
        return {'FINISHED'}

class UVTestPanel(bpy.types.Panel):
    bl_label = "Test Panel"
    bl_idname = "VIEW3D_PT_test_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'UV Tools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.uv_export_props

        layout.prop(props, "vertex_group_name")

class UVExportProperties(bpy.types.PropertyGroup):

    def vertex_group_items(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return [(vg.name, vg.name, "") for vg in obj.vertex_groups]
        return [("NONE", "None", "")]

    vertex_group_name: bpy.props.EnumProperty(
        name="Vertex Group",
        description="Select a vertex group",
        items=vertex_group_items
    )

    def update_selected_file(self, context):
        obj = context.active_object
        if not obj or not self.selected_file or self.selected_file == "NONE":
            return

        prefix = obj.name + "_"
        filename = self.selected_file

        if filename.startswith(prefix):
            filename = filename[len(prefix):]

        if filename.lower().endswith(".txt"):
            filename = filename[:-4]

        self.filename = filename
    
    def update_clamp_min(self, context):
        if self.clamp_min > self.clamp_max:
            self.clamp_min = self.clamp_max

    def update_clamp_max(self, context):
        if self.clamp_max < self.clamp_min:
            self.clamp_max = self.clamp_min
    
    clamp_min: bpy.props.FloatProperty(
        name="Min Export Value",
        description="Minimum value to normalize to during export",
        default=0.0000,
        min=0.0,
        max=100.0,
        precision=6,
        update=update_clamp_min
    )

    clamp_max: bpy.props.FloatProperty(
        name="Max Export Value",
        description="Maximum value to normalize to during export",
        default=1.0,
        min=0.0,
        max=100.0,
        precision=6,
        update=update_clamp_max
    )

    filename: bpy.props.StringProperty(
        name="File Name",
        description="Filename to save UV indices to",
        default="uv_indices.txt"
    )
    
    exportpath: bpy.props.StringProperty(
        name="(optional)Export Path",
        description="Path to save export data to",
        default="",
        subtype='DIR_PATH'
    )
    
    export_type: bpy.props.EnumProperty(
        name="Export Type",
        description="Choose the type of export",
        items=[
            ('FLOAT', "Float", "Export as float", 0),
            ('DISTANCE', "Distance", "Export as distance", 1),
            ('ANGLE', "Angle", "Export as angle", 2),
        ],
        default='FLOAT'
    )
    
    selected_file: bpy.props.EnumProperty(
        name="Saved Files",
        description="Choose a previously saved file",
        items=list_saved_files,
        update=update_selected_file
    )

    fbx_importer_path: bpy.props.StringProperty(
        name="FBX Importer Path",
        description="Path to external FBXImporter executable",
        subtype='FILE_PATH'
    )

    fbx_export_name: bpy.props.StringProperty(
        name="FBX Export Name",
        description="Name of the FBX file to export",
        default="cloth.fbx"
    )

    bottom_file: bpy.props.StringProperty(
        name="Bottom Vertex File",
        description="Path to the text file containing bottom vertex IDs",
        subtype='FILE_PATH'
    )
    top_file: bpy.props.StringProperty(
        name="Top Vertex File",
        description="Path to the text file containing top vertex IDs",
        subtype='FILE_PATH'
    )
    middle_file: bpy.props.StringProperty(
        name="Middle Vertex File",
        description="Path to the text file containing middle vertex IDs",
        subtype='FILE_PATH'
    )

    scale_bottom: bpy.props.FloatProperty(
        name="Bottom Scale",
        description="Scale factor for the bottom part",
        default=1.0,
        min=0.0
    )
    scale_top: bpy.props.FloatProperty(
        name="Top Scale",
        description="Scale factor for the top part",
        default=1.0,
        min=0.0
    )
    scale_center: bpy.props.FloatProperty(
        name="Center Scale",
        description="Scale factor for the middle part",
        default=1.0,
        min=0.0
    )

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

class UVIndexExtractorOperator(bpy.types.Operator):
    bl_idname = "mesh.extract_uv_indices"
    bl_label = "Save UV Indices"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.uv_export_props
        filename = props.filename.strip()
        if not filename:
            self.report({'ERROR'}, "Filename cannot be empty")
            return {'CANCELLED'}
        if not filename.endswith(".txt"):
            filename += ".txt"

        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Please select a mesh object")
            return {'CANCELLED'}

        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/selectionsets")
        os.makedirs(export_dir, exist_ok=True)

        filename = obj.name + "_" + filename
        output_path = os.path.join(export_dir, filename)
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.faces.ensure_lookup_table()

        uv_layer = bm.loops.layers.uv.active
        if not uv_layer:
            self.report({'ERROR'}, "Mesh has no UV layer")
            return {'CANCELLED'}

        uv_index_counter = 0
        loop_to_uv_index = {}
        
        for face in bm.faces:
            if len(face.verts) != 3:
                self.report({'ERROR'}, "Mesh contains non-triangular face(s). Operation cancelled.")
                return {'CANCELLED'}
            for loop in face.loops:
                loop_to_uv_index[loop] = uv_index_counter
                uv_index_counter += 1

        vertex_uv_map = {}
        for vert in bm.verts:
            if not vert.select:
                continue

            uv_entries = []
            for loop in vert.link_loops:
                if loop.face not in bm.faces or len(loop.face.verts) != 3:
                    continue
                if loop not in loop_to_uv_index:
                    continue

                uv_idx = loop_to_uv_index[loop]
                uv_entries.append((uv_idx, loop.face.index))

            if uv_entries:
                vertex_uv_map[vert.index] = uv_entries

        with open(output_path, 'w') as f:
            for vtx_idx, uv_refs in vertex_uv_map.items():
                f.write(f"{vtx_idx}: ")
                for uv_idx, face_idx in uv_refs:
                    f.write(f"{uv_idx} ")
                f.write("\n")

        bm.free()
        self.report({'INFO'}, f"UV indices saved to: {output_path}")
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

class ExportFBXAndRunImporterOperator(bpy.types.Operator):
    bl_idname = "mesh.export_and_run_fbximporter"
    bl_label = "Export FBX and Run Importer"

    def execute(self, context):
        obj = context.active_object
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fbx_importer = os.path.join(script_dir, f"FBXImporter.exe")

        if not os.path.isfile(fbx_importer):
            self.report({'ERROR'}, "FBXImporter path is invalid")
            return {'CANCELLED'}
        props = context.scene.uv_export_props
        if props.exportpath != "":
            blend_dir = props.exportpath
        else:
            blend_dir = bpy.path.abspath("//")
        fbx_path = os.path.join(blend_dir, f"cloth.fbx")

        # Export selected object to FBX
        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            global_scale=0.01,
            add_leaf_bones=False,
        )

        try:
            subprocess.run([fbx_importer, fbx_path], check=True)
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"FBXImporter failed: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported and ran FBXImporter on: {fbx_path}")
        return {'FINISHED'}

class CapsuleUtils:
    @staticmethod
    def load_vertex_ids_from_file(filepath):
        """Helper function to load vertex IDs from a file (one ID per line)"""
        if not os.path.exists(filepath):
            return []
            
        vertex_ids = []
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:  # Only process non-empty lines
                        try:
                            vertex_id = int(line)
                            vertex_ids.append(vertex_id)
                        except ValueError:
                            print(f"Skipping invalid line in {filepath}: {line}")
                            continue
        except Exception as e:
            print(f"Failed to read vertex IDs from {filepath}: {e}")
        return vertex_ids

    @staticmethod
    def import_and_place_fbx(fbx_path, bone1, bone2):
        """Import FBX and place/rotate it between two bones"""
        # Deselect all first
        bpy.ops.object.select_all(action='DESELECT')
        
        # Import FBX
        try:
            bpy.ops.import_scene.fbx(filepath=fbx_path)
        except Exception as e:
            print(f"FBX import failed: {e}")
            return None
            
        # The newly imported object should be selected
        if not bpy.context.selected_objects:
            print("No objects were imported")
            return None
            
        capsule_obj = bpy.context.selected_objects[0]
        
        # Calculate placement and rotation
        bone1_head = bone1.head
        bone2_head = bone2.head
        direction = bone2_head - bone1_head
        distance = direction.length
        direction.normalize()
        midpoint = (bone1_head + bone2_head) / 2
        
        # Position and rotate capsule
        capsule_obj.location = midpoint
        capsule_forward = Vector((0, 0, 1))
        angle = capsule_forward.angle(direction)
        rotation_axis = capsule_forward.cross(direction).normalized()
        rotation_quaternion = mathutils.Quaternion(rotation_axis, angle)
        
        capsule_obj.rotation_mode = 'QUATERNION'
        capsule_obj.rotation_quaternion = rotation_quaternion
        
        print(f"Capsule placed and rotated between bones")
        return capsule_obj

class CapsuleScaleProperties(bpy.types.PropertyGroup):
    prev_scale_bottom: bpy.props.FloatProperty(default=1.0)
    prev_scale_top: bpy.props.FloatProperty(default=1.0)
    prev_scale_center: bpy.props.FloatProperty(default=1.0)
    scale_bottom: bpy.props.FloatProperty(default=1.0, min=0.01)
    scale_top: bpy.props.FloatProperty(default=1.0, min=0.01)
    scale_center: bpy.props.FloatProperty(default=1.0, min=0.01)


class CapsuleToolsProperties(bpy.types.PropertyGroup):
    bottom_file: bpy.props.StringProperty(
        name="Bottom Vertex File",
        description="Path to the text file containing bottom vertex IDs",
        subtype='FILE_PATH'
    )
    top_file: bpy.props.StringProperty(
        name="Top Vertex File",
        description="Path to the text file containing top vertex IDs",
        subtype='FILE_PATH'
    )
    middle_file: bpy.props.StringProperty(
        name="Middle Vertex File",
        description="Path to the text file containing middle vertex IDs",
        subtype='FILE_PATH'
    )
    scale_bottom: bpy.props.FloatProperty(
        name="Bottom Scale",
        description="Scale factor for the bottom part",
        default=1.0,
        min=0.01
    )
    scale_top: bpy.props.FloatProperty(
        name="Top Scale",
        description="Scale factor for the top part",
        default=1.0,
        min=0.01
    )
    scale_center: bpy.props.FloatProperty(
        name="Center Scale",
        description="Scale factor for the middle part",
        default=1.0,
        min=0.01
    )



class SelectVertexByIDOperator(bpy.types.Operator):
    bl_idname = "mesh.select_vertex_by_id"
    bl_label = "Select Vertex by ID"
    bl_description = "Select a vertex in Edit Mode by its index"
    bl_options = {'REGISTER', 'UNDO'}

    vertex_id: bpy.props.IntProperty(name="Vertex ID", default=0)

    def execute(self, context):
        obj = context.active_object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object must be a mesh")
            return {'CANCELLED'}

        if obj.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        try:
            obj.data.vertices[self.vertex_id].select = True
        except IndexError:
            self.report({'ERROR'}, f"Vertex ID {self.vertex_id} out of range")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        return {'FINISHED'}

#fbx import
class CollidableCreateOperator(bpy.types.Operator):
    bl_idname = "import_scene.collidable_create"
    bl_label = "Create Collidable"
    bl_description = "Import 'collidable.fbx' from the same folder as this addon script"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the folder where this script file resides
        script_dir = os.path.dirname(os.path.abspath(__file__))

        fbx_path = os.path.join(script_dir, "collidable.fbx")
        if not os.path.exists(fbx_path):
            self.report({'ERROR'}, f"'collidable.fbx' not found in: {script_dir}")
            return {'CANCELLED'}

        bpy.ops.import_scene.fbx(filepath=fbx_path)
        
        fbx_path = os.path.join(script_dir, "sphere.fbx")
        if not os.path.exists(fbx_path):
            self.report({'ERROR'}, f"'sphere.fbx' not found in: {script_dir}")
            return {'CANCELLED'}

        bpy.ops.import_scene.fbx(filepath=fbx_path)
        
        self.report({'INFO'}, f"Imported: {fbx_path}")
        return {'FINISHED'}

#resize classes

class ResizeCapsuleOperator(bpy.types.Operator):
    bl_idname = "mesh.resize_capsule"
    bl_label = "Resize Capsule"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH' or not obj.name.startswith("collision_"):
            self.report({'ERROR'}, "Please select a capsule object")
            return {'CANCELLED'}

        # Get per-object properties
        props = obj.capsule_scale_props

        bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        def scale_group(vertex_ids, current_scale, prev_scale):
            if prev_scale == 0:
                prev_scale = 1.0  # Prevent division by zero

            scale_ratio = current_scale / prev_scale
            group_verts = [bm.verts[i] for i in vertex_ids if i < len(bm.verts)]
            if not group_verts:
                return

            center = sum((v.co for v in group_verts), Vector()) / len(group_verts)

            for v in group_verts:
                offset = v.co - center
                v.co = center + offset * scale_ratio

        # Use hardcoded vertex IDs
        scale_group(capsule_bottom, props.scale_bottom, props.prev_scale_bottom)
        scale_group(capsule_top, props.scale_top, props.prev_scale_top)
        scale_group(capsule_center, props.scale_center, props.prev_scale_center)
        
        # Update previous scales for next operation
        props.prev_scale_bottom = props.scale_bottom
        props.prev_scale_top = props.scale_top
        props.prev_scale_center = props.scale_center
        
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

        self.report({'INFO'}, f"Capsule '{obj.name}' resized successfully")
        return {'FINISHED'}

def place_capsule_logic():
    print("Trying to place capsule...")

    # Get the imported object
    mesh_obj = bpy.data.objects.get("collision_Bone001")
    if not mesh_obj:
        print("Capsule not found after import.")
        return False

    arm = bpy.context.object
    if not arm or arm.type != 'ARMATURE':
        print("Active object is not an armature.")
        return False

    selected_bones = bpy.context.selected_pose_bones
    if not selected_bones or len(selected_bones) != 2:
        print("Please select exactly 2 bones in Pose Mode.")
        return False

    bone_1, bone_2 = selected_bones
    b1_head = arm.matrix_world @ bone_1.head
    b2_head = arm.matrix_world @ bone_2.head
    direction = b2_head - b1_head

    if direction.length == 0:
        print("Bones overlap. Cannot place capsule.")
        return False

    midpoint = (b1_head + b2_head) * 0.5
    direction.normalize()

    mesh_obj.location = midpoint
    capsule_forward = mathutils.Vector((0, 0, 1))
    axis = capsule_forward.cross(direction)

    if axis.length == 0:
        angle = 0 if capsule_forward.dot(direction) > 0 else math.pi
        quat = mathutils.Quaternion((1, 0, 0), angle)
    else:
        quat = mathutils.Quaternion(axis.normalized(), capsule_forward.angle(direction))

    mesh_obj.rotation_mode = 'QUATERNION'
    mesh_obj.rotation_quaternion = quat

    print("Capsule placed and rotated.")
    return True

def set_capsule_length(obj, bottom_ids, top_ids, target_length=1.0):
    if not obj or obj.type != 'MESH':
        return {'CANCELLED'}

    current_mode = obj.mode
    if current_mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    try:
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        top_zs = [bm.verts[i].co.z for i in top_ids if i < len(bm.verts)]
        bottom_zs = [bm.verts[i].co.z for i in bottom_ids if i < len(bm.verts)]

        if not top_zs or not bottom_zs:
            print("Invalid vertex groups.")
            return {'CANCELLED'}

        min_z = min(bottom_zs)
        max_z = max(top_zs)
        current_length = max_z - min_z

        if current_length <= 0:
            print("Current length is invalid.")
            return {'CANCELLED'}

        scale = (target_length - current_length) / 2

        for v in bm.verts:
            if v.index in bottom_ids:
                v.co.z -= scale
            elif v.index in top_ids:
                v.co.z += scale

        bmesh.update_edit_mesh(obj.data)
        print(f"Set capsule length to {target_length:.3f}")

    finally:
        bpy.ops.object.mode_set(mode=current_mode)

    return {'FINISHED'}

class placer(bpy.types.Operator):
    bl_idname = "place.place"
    bl_label = "place.Collidable"
    
    def execute(self, context):
        print("Trying to place capsule...")

        arm = context.active_object
        if not arm or arm.type != 'ARMATURE':
            print("Active object is not an armature.")
            return {'CANCELLED'}
        
        current_mode = arm.mode
        if current_mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        selected_bones = bpy.context.selected_pose_bones
        if len(selected_bones) == 1:
            bone_1 = selected_bones[0]
            
            original_mesh_obj = bpy.data.objects.get("Collidable_sphere")
            
            if not original_mesh_obj:
                print("Original mesh 'Collidable_sphere' not found")
                return {'CANCELLED'}
            mesh_obj = original_mesh_obj.copy()
            mesh_obj.data = original_mesh_obj.data.copy()
            number = 1
            while True:
                existing_obj = bpy.data.objects.get(f"collision_sphere_{bone_1.name}{number:03}")
                if not existing_obj:
                    break
                number += 1
            mesh_obj.name = f"collision_sphere_{bone_1.name}{number:03}"
            mesh_obj.animation_data_clear()
            context.collection.objects.link(mesh_obj)

            midpoint = arm.matrix_world @ bone_1.head
            
            mesh_obj.location = midpoint
            
            bpy.context.view_layer.objects.active = mesh_obj
            bpy.ops.object.mode_set(mode='EDIT')

            bm = bmesh.from_edit_mesh(mesh_obj.data)
            bm.verts.ensure_lookup_table() 
            
            bmesh.update_edit_mesh(mesh_obj.data)

            bpy.ops.object.mode_set(mode='OBJECT')

            self.report({'INFO'}, f"Collidable '{mesh_obj.name}' created and placed successfully")

            return {'FINISHED'}
            
        if not selected_bones or len(selected_bones) != 2:
            print("Please select exactly 2 bones in Pose Mode.")
            return {'CANCELLED'}
        
        original_mesh_obj = bpy.data.objects.get("collision_Bone001")
        if not original_mesh_obj:
            print("Original mesh 'collision_Bone001' not found")
            return {'CANCELLED'}
        
        bone_1, bone_2 = selected_bones
        
        mesh_obj = original_mesh_obj.copy()
        mesh_obj.data = original_mesh_obj.data.copy()
        number = 1
        while True:
            existing_obj = bpy.data.objects.get(f"collision_capsule_{bone_1.name}{number:03}")
            if not existing_obj:
                break
            number += 1
        mesh_obj.name = f"collision_capsule_{bone_1.name}{number:03}"
        mesh_obj.animation_data_clear()
        context.collection.objects.link(mesh_obj)

        b1_head = arm.matrix_world @ bone_1.head
        b2_head = arm.matrix_world @ bone_2.head
        bone_distance = (b2_head - b1_head).length * 0.5
        direction = b2_head - b1_head

        if direction.length == 0:
            print("Bones overlap. Cannot place capsule.")
            bpy.data.objects.remove(mesh_obj)
            return {'CANCELLED'}

        midpoint = (b1_head + b2_head) * 0.5
        direction.normalize()

        mesh_obj.location = midpoint
        capsule_forward = mathutils.Vector((0, 0, 1))
        axis = capsule_forward.cross(direction)

        if axis.length == 0:
            angle = 0 if capsule_forward.dot(direction) > 0 else math.pi
            quat = mathutils.Quaternion((1, 0, 0), angle)
        else:
            quat = mathutils.Quaternion(axis.normalized(), capsule_forward.angle(direction))
        
        mesh_obj.rotation_mode = 'QUATERNION'
        mesh_obj.rotation_quaternion = quat
        
        bpy.context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(mesh_obj.data)
        bm.verts.ensure_lookup_table() 
        
        top_zs = [(mesh_obj.matrix_world @ bm.verts[i].co).z for i in capsule_top if i < len(bm.verts)]
        bottom_zs = [(mesh_obj.matrix_world @ bm.verts[i].co).z for i in capsule_bottom if i < len(bm.verts)]

        if not top_zs or not bottom_zs:
            print("Invalid vertex groups.")
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'CANCELLED'}

        min_z = min(bottom_zs)
        max_z = max(top_zs)
        current_length = max_z - min_z

        if current_length <= 0:
            print("Current length is invalid.")
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'CANCELLED'}

        scale = (bone_distance - current_length) / 2

        for v in bm.verts:
            if v.index in capsule_bottom:
                v.co.z += scale
            elif v.index in capsule_top:
                v.co.z -= scale

        bmesh.update_edit_mesh(mesh_obj.data)

        bpy.ops.object.mode_set(mode='OBJECT')

        print(f"Capsule '{mesh_obj.name}' placed, rotated and resized to length {bone_distance:.3f}")
        self.report({'INFO'}, f"Collidable '{mesh_obj.name}' created and placed successfully")

        return {'FINISHED'}


class ImportCollidableFBXOperator(bpy.types.Operator):
    bl_idname = "import_scene.collidable_create"
    bl_label = "Create Collidable"
    bl_description = "Import 'collidable.fbx' and place it between two bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        blend_dir = os.path.dirname(bpy.data.filepath)
        if not blend_dir:
            self.report({'ERROR'}, "Please save the .blend file first.")
            return {'CANCELLED'}

        fbx_path = os.path.join(blend_dir, "collidable.fbx")
        if not os.path.isfile(fbx_path):
            self.report({'ERROR'}, f"'collidable.fbx' not found in: {blend_dir}")
            return {'CANCELLED'}

        # Import FBX
        bpy.ops.import_scene.fbx(filepath=fbx_path)
        
        if context.object and context.object.type == 'ARMATURE' and context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        
        self.report({'INFO'}, "FBX import triggered, waiting for capsule...")
        return {'FINISHED'}

class CapsuleLengthProperties(bpy.types.PropertyGroup):
    original_length: bpy.props.FloatProperty(
        name="Original Length",
        default=1
    )
    
    bottom_ids_str: bpy.props.StringProperty(
        name="Bottom IDs",
        default=",".join(str(i) for i in capsule_top)
    )
    
    top_ids_str: bpy.props.StringProperty(
        name="Top IDs",
        default=",".join(str(i) for i in capsule_bottom)
    )

    @property
    def bottom_ids(self):
        return [int(i) for i in self.bottom_ids_str.split(",") if i.strip()]
    
    @property
    def top_ids(self):
        return [int(i) for i in self.top_ids_str.split(",") if i.strip()]
    
    def toggle_length(self, obj, target_length=2.0):
        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}

        current_mode = obj.mode
        if current_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        try:
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()

            # Get z-values for top/bottom vertices
            top_zs = [bm.verts[i].co.z for i in self.top_ids if i < len(bm.verts)]
            bottom_zs = [bm.verts[i].co.z for i in self.bottom_ids if i < len(bm.verts)]

            if not top_zs or not bottom_zs:
                print("Invalid vertex groups.")
                return {'CANCELLED'}

            min_z = min(bottom_zs)
            max_z = max(top_zs)
            current_length = max_z - min_z

            # Determine if we should stretch or shrink
            if isclose(current_length, target_length, rel_tol=1e-3):
                new_length = self.original_length
            else:
                new_length = target_length

            scale = (new_length - current_length) / 2

            for v in bm.verts:
                if v.index in self.bottom_ids:
                    v.co.z -= scale
                elif v.index in self.top_ids:
                    v.co.z += scale

            bmesh.update_edit_mesh(obj.data)

        finally:
            bpy.ops.object.mode_set(mode=current_mode)

        return {'FINISHED'}
    
    def set_length(self, obj, target_length=1.0):
        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}

        current_mode = obj.mode
        if current_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        try:
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()

            top_zs = [bm.verts[i].co.z for i in self.top_ids if i < len(bm.verts)]
            bottom_zs = [bm.verts[i].co.z for i in self.bottom_ids if i < len(bm.verts)]

            if not top_zs or not bottom_zs:
                print("Invalid vertex groups.")
                return {'CANCELLED'}

            min_z = min(bottom_zs)
            max_z = max(top_zs)
            current_length = max_z - min_z

            if current_length <= 0:
                print("Current length is invalid.")
                return {'CANCELLED'}

            scale = (target_length - current_length) / 2

            for v in bm.verts:
                if v.index in self.bottom_ids:
                    v.co.z -= scale
                elif v.index in self.top_ids:
                    v.co.z += scale

            bmesh.update_edit_mesh(obj.data)
            print(f"Set capsule length to {target_length:.3f}")

        finally:
            bpy.ops.object.mode_set(mode=current_mode)

        return {'FINISHED'}
    
class OBJECT_OT_toggle_capsule_length(bpy.types.Operator):
    bl_idname = "object.toggle_capsule_length"
    bl_label = "Toggle Capsule Length"
    bl_options = {'REGISTER', 'UNDO'}
    
    target_length: bpy.props.FloatProperty(
        name="Target Length",
        default=0.3522,
        min=0.01
    )
    
    def execute(self, context):
        if not hasattr(context.scene, 'capsule_length_props'):
            self.report({'ERROR'}, "Capsule properties not initialized")
            return {'CANCELLED'}
            
        props = context.scene.capsule_length_props
        if not context.active_object:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
            
        return props.toggle_length(context.active_object, self.target_length)

class SimpleFileBrowserOperator(bpy.types.Operator):
    bl_idname = "wm.select_export_folder"
    bl_label = "Select Export Folder"

    # This will execute when the user selects a folder
    def execute(self, context):
        # Get the file path selected by the user
        props = context.scene.uv_export_props
        context.scene.exportpath = props.filepath
        return {'FINISHED'}

    # This defines the file browser settings
    def invoke(self, context, event):
        # Open the folder selection dialog
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


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
        
        
            # Resizing controls
            box = layout.box()
            box.label(text="Resize Settings:")
        
        
            if obj.name.startswith("collision_capsule"):
                props = obj.capsule_scale_props
                row = box.row()
                row.prop(props, "scale_bottom", text="Bottom")
                row.prop(props, "scale_center", text="Middle")
                row.prop(props, "scale_top", text="Top")

                layout.operator("mesh.resize_capsule", icon='MOD_ARRAY')
        
        layout.separator()
        layout.label(text="Collidable:")
        layout.operator("import_scene.collidable_create", icon='IMPORT')
        
        if obj and obj.type == 'ARMATURE':
            layout.operator("place.place", icon='IMPORT')
        
        if obj and obj.type == 'MESH':
            if obj.name.startswith("collision_capsule"):
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
        layout.prop(props, "exportpath")
        layout.operator("mesh.export_and_run_fbximporter", icon='EXPORT')
        

classes = [
    UVExportProperties,
    UVIndexExtractorOperator,
    UVRenameFileOperator,
    UVOpenFolderOperator,
    UVSelectVerticesFromFileOperator,
    UVIndexExtractorPanel,
    SelectVertexByIDOperator,
    ExportFBXAndRunImporterOperator,
    ResizeCapsuleOperator,
    ImportCollidableFBXOperator,
    CollidableCreateOperator,
    placer,
    CapsuleLengthProperties, 
    OBJECT_OT_toggle_capsule_length,
    UVDeleteFileOperator,
    ExportVertexGroupWeightsOperator,
    CapsuleScaleProperties,
    SimpleFileBrowserOperator
]

def register():
    # Register all classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            print(f"Class {cls.__name__} already registered")
    
    # Initialize properties
    bpy.types.Scene.uv_export_props = bpy.props.PointerProperty(type=UVExportProperties)
    bpy.types.Object.capsule_scale_props = bpy.props.PointerProperty(type=CapsuleScaleProperties)

def unregister():
    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove properties
    del bpy.types.Scene.uv_export_props
    del bpy.types.Object.capsule_scale_props

if __name__ == "__main__":
    register()