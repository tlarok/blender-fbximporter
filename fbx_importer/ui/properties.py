import bpy
import os
import bmesh
from math import fabs, isclose
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty

capsule_bottom = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
capsule_top = [144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271]
capsule_center = [128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143]

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

class CapsuleScaleProperties(bpy.types.PropertyGroup):
    prev_scale_bottom: bpy.props.FloatProperty(default=1.0)
    prev_scale_top: bpy.props.FloatProperty(default=1.0)
    prev_scale_center: bpy.props.FloatProperty(default=1.0)
    scale_bottom: bpy.props.FloatProperty(default=1.0, min=0.01)
    scale_top: bpy.props.FloatProperty(default=1.0, min=0.01)
    scale_center: bpy.props.FloatProperty(default=1.0, min=0.01)

def list_saved_files(self, context):
    props = context.scene.uv_export_props
    obj = context.active_object
    
    if not obj:
        return [("NONE", "None", "", 0)]
    
    try:
        # Get the correct base directory
        if props.exportpath and props.exportpath != "//":
            base_dir = bpy.path.abspath(props.exportpath)
        else:
            base_dir = os.path.dirname(bpy.path.abspath(bpy.data.filepath))
        
        folder = os.path.join(base_dir, "export_data", "selectionsets")
        folder = bpy.path.abspath(folder)
        
        # Debug prints
        print(f"Checking folder: {folder}")
        print(f"Object name: {obj.name}")
        
        # Create directory if doesn't exist
        os.makedirs(folder, exist_ok=True)
        
        files = []
        prefix = obj.name + "_"
        
        if os.path.exists(folder):
            for fname in sorted(os.listdir(folder)):
                if fname.endswith(".txt") and fname.startswith(prefix):
                    short_name = fname[len(prefix):-4]  # Remove prefix and .txt
                    full_path = os.path.join(folder, fname)
                    files.append((fname, short_name, full_path))
                    
            if not files:
                print(f"No matching files found with prefix {prefix}")
                return [("NONE", "No saved files found", "", 0)]
                
            return files
            
    except Exception as e:
        print(f"Error listing saved files: {e}")
    
    return [("NONE", "Error loading files", "", 0)]


class UVExportProperties(bpy.types.PropertyGroup):

    def vertex_group_items(self, context):
        obj = context.active_object
        if obj and obj.type == 'MESH':
            return [(vg.name, vg.name, "") for vg in obj.vertex_groups]
        return [("NONE", "None", "")]
    
    def bone_items(self, context):
        # Find the first armature in the scene
        armature = None
        for potential_armature in bpy.data.objects:
            if potential_armature.type == 'ARMATURE':
                armature = potential_armature
                break  # Exit after finding the first armature
        
        if armature:
            # Return bones from the first armature
            return [(bone.name, bone.name, "") for bone in armature.data.bones]
        
        return [("NONE", "None", "")]

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
    
    
    vertex_group_name: bpy.props.EnumProperty(
        name="Vertex Group",
        description="Select a vertex group",
        items=vertex_group_items
    )
    
    bone_name: bpy.props.EnumProperty(
        name="(unrigged)Rig collidable to",
        description="Select a bone",
        items=bone_items
    )
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
    
    filterpath: bpy.props.StringProperty(
        name="standalone filter manager path",
        description="Path to save export data to",
        default="",
        subtype='FILE_PATH'
    )
    
    collision_type: bpy.props.EnumProperty(
        name="Collision Type",
        description="Choose the type of collidable",
        items=[
            ("collision_sphere", "Sphere", "A spherical collision"),
            ("collision_plane", "Plane", "A flat plane collision"),
            ("collision_capsule", "Capsule", "A capsule-shaped collision"),
            ("collision_convexgeom", "Convex Geometry", "A convex-shaped geometry"),
            ("collision_convexheight", "Convex Heightfield", "A convex heightfield collision")
        ],
        default='collision_convexgeom'
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