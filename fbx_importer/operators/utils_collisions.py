import bpy
import bmesh
from mathutils import Vector, Quaternion
import mathutils
import os
from fbx_importer.ui.properties import CapsuleScaleProperties, CapsuleLengthProperties, CapsuleToolsProperties, UVExportProperties
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty

capsule_bottom = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127]
capsule_top = [144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271]
capsule_center = [128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143]


class collision_convtype(bpy.types.Operator):
    bl_idname = "mesh.collision_conv"
    bl_label = "Set Collision"

    def execute(self, context):
        # Get the active object and the collision type property
        obj = context.active_object
        props = context.scene.uv_export_props
        collision_type = props.collision_type  # The selected collision type
        
        if obj and obj.type == 'MESH':
            # Ensure that new_name is always defined
            new_name = None  # Default value in case no condition matches

            # Check if the object name starts with a known collision prefix
            if obj.name.startswith("collision_"):
                
                # Define the collision type to replace in the name
                if obj.name.startswith("collision_capsule_"):
                    new_name = collision_type  + "_" +  obj.name[len("collision_capsule_"):]
                elif obj.name.startswith("collision_sphere_"):
                    new_name = collision_type  + "_" +  obj.name[len("collision_sphere_"):]
                elif obj.name.startswith("collision_plane_"):
                    new_name = collision_type  + "_" +  obj.name[len("collision_plane_"):]
                elif obj.name.startswith("collision_convexgeom_"):
                    new_name = collision_type  + "_" +  obj.name[len("collision_convexgeom_"):]
                elif obj.name.startswith("collision_convexheight_"):
                    new_name = collision_type  + "_" +  obj.name[len("collision_convexheight_"):]
                
            if new_name is None:  # In case no collision type was matched, create a new name
                new_name = collision_type + "_" + obj.name + "_" + props.bone_name

                # Ensure the name ends with a 3-digit ID
                base_name = new_name
                suffix = 1  # Start the suffix from 1
                formatted_suffix = f"{suffix:03}"  # Format the suffix as a 3-digit number (e.g., 001)

                # Check if a mesh with this name already exists
                existing_objects = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(base_name)]

                # If there are meshes with the same name, increment the suffix until a unique name is found
                while any(o.name.endswith(formatted_suffix) for o in existing_objects):
                    suffix += 1
                    formatted_suffix = f"{suffix:03}"

                # Append the suffix to the new name
                new_name = base_name + formatted_suffix

            # Rename the object with the new name
            obj.name = new_name
            print(f"Object renamed to: {obj.name}")
            
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