import bpy
import bmesh
from mathutils import Vector, Quaternion
import mathutils
import os
from fbx_importer.ui.properties import CapsuleScaleProperties, CapsuleLengthProperties, CapsuleToolsProperties, UVExportProperties
from bpy.props import StringProperty, EnumProperty, FloatProperty, BoolProperty, IntVectorProperty

# --- New vertex lists (capsule bottom and top only, no middle) ---
capsule_bottom = [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
capsule_top = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
# capsule_center removed completely


class collision_convtype(bpy.types.Operator):
    bl_idname = "mesh.collision_conv"
    bl_label = "Set Collision"

    def execute(self, context):
        obj = context.active_object
        props = context.scene.uv_export_props
        collision_type = props.collision_type
        
        if obj and obj.type == 'MESH':
            new_name = None

            if obj.name.startswith("collision_"):
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
                
            if new_name is None:
                new_name = collision_type + "_" + obj.name + "_" + props.bone_name

                base_name = new_name
                suffix = 1
                formatted_suffix = f"{suffix:03}"
                existing_objects = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(base_name)]
                while any(o.name.endswith(formatted_suffix) for o in existing_objects):
                    suffix += 1
                    formatted_suffix = f"{suffix:03}"
                new_name = base_name + formatted_suffix

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
        min=0.01,
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

    prefs = bpy.context.preferences.edit
    old_undo = prefs.use_global_undo
    prefs.use_global_undo = False

    current_mode = obj.mode
    try:
        if current_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

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
        prefs.use_global_undo = old_undo

    return {'FINISHED'}


class placer(bpy.types.Operator):
    bl_idname = "place.place"
    bl_label = "place.Collidable"

    def execute(self, context):
        arm = context.active_object
        if not arm or arm.type != 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}

        if arm.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        selected_bones = context.selected_pose_bones
        if not selected_bones:
            self.report({'ERROR'}, "Please select 1 or 2 bones in Pose Mode.")
            return {'CANCELLED'}

        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Sphere case
        if len(selected_bones) == 1:
            bone_1 = selected_bones[0]
            print("Trying to place sphere...")

            fbx_path = os.path.join(script_dir, "sphere.fbx")
            if not os.path.exists(fbx_path):
                self.report({'ERROR'}, f"'sphere.fbx' not found in: {script_dir}")
                return {'CANCELLED'}

            bpy.ops.import_scene.fbx(filepath=fbx_path)
            original_mesh_obj = bpy.data.objects.get("Collidable_sphere")
            if not original_mesh_obj:
                self.report({'ERROR'}, "Imported mesh 'Collidable_sphere' not found")
                return {'CANCELLED'}

            number = 1
            while bpy.data.objects.get(f"collision_sphere_{bone_1.name}{number:03}"):
                number += 1

            original_mesh_obj.name = f"collision_sphere_{bone_1.name}{number:03}"
            original_mesh_obj.animation_data_clear()
            if original_mesh_obj.name not in context.collection.objects:
                context.collection.objects.link(original_mesh_obj)

            midpoint = arm.matrix_world @ bone_1.head
            original_mesh_obj.location = midpoint

            bpy.context.view_layer.objects.active = original_mesh_obj
            bpy.ops.object.mode_set(mode='EDIT')

            bm = bmesh.from_edit_mesh(original_mesh_obj.data)
            bm.verts.ensure_lookup_table()
            bmesh.update_edit_mesh(original_mesh_obj.data)

            bpy.ops.object.mode_set(mode='OBJECT')

            self.report({'INFO'}, f"Collidable '{original_mesh_obj.name}' created and placed successfully")
            return {'FINISHED'}

        # Capsule case
        elif len(selected_bones) == 2:
            bone_1, bone_2 = selected_bones
            print("Trying to place capsule...")

            fbx_path = os.path.join(script_dir, "collidable.fbx")
            if not os.path.exists(fbx_path):
                self.report({'ERROR'}, f"'collidable.fbx' not found in: {script_dir}")
                return {'CANCELLED'}

            bpy.ops.import_scene.fbx(filepath=fbx_path)
            original_mesh_obj = bpy.data.objects.get("collision_Bone001")
            if not original_mesh_obj:
                self.report({'ERROR'}, "Imported mesh 'collision_Bone001' not found")
                return {'CANCELLED'}

            number = 1
            while bpy.data.objects.get(f"collision_capsule_{bone_1.name}{number:03}"):
                number += 1

            original_mesh_obj.name = f"collision_capsule_{bone_1.name}{number:03}"
            original_mesh_obj.animation_data_clear()
            if original_mesh_obj.name not in context.collection.objects:
                context.collection.objects.link(original_mesh_obj)

            b1_head = arm.matrix_world @ bone_1.head
            b2_head = arm.matrix_world @ bone_2.head
            bone_distance = (b2_head - b1_head).length * 0.5
            direction = b2_head - b1_head

            if direction.length == 0:
                self.report({'ERROR'}, "Bones overlap. Cannot place capsule.")
                bpy.data.objects.remove(original_mesh_obj)
                return {'CANCELLED'}

            midpoint = (b1_head + b2_head) * 0.5
            direction.normalize()
            original_mesh_obj.location = midpoint

            capsule_forward = mathutils.Vector((0, 0, 1))
            axis = capsule_forward.cross(direction)

            if axis.length == 0:
                angle = 0 if capsule_forward.dot(direction) > 0 else math.pi
                quat = mathutils.Quaternion((1, 0, 0), angle)
            else:
                quat = mathutils.Quaternion(axis.normalized(), capsule_forward.angle(direction))

            original_mesh_obj.rotation_mode = 'QUATERNION'
            original_mesh_obj.rotation_quaternion = quat

            bpy.context.view_layer.objects.active = original_mesh_obj
            bpy.ops.object.mode_set(mode='EDIT')

            bm = bmesh.from_edit_mesh(original_mesh_obj.data)
            bm.verts.ensure_lookup_table()

            # Uses the new top/bottom lists for scaling
            top_zs = [(original_mesh_obj.matrix_world @ bm.verts[i].co).z for i in capsule_top if i < len(bm.verts)]
            bottom_zs = [(original_mesh_obj.matrix_world @ bm.verts[i].co).z for i in capsule_bottom if i < len(bm.verts)]

            if not top_zs or not bottom_zs:
                bpy.ops.object.mode_set(mode='OBJECT')
                self.report({'ERROR'}, "Invalid vertex groups.")
                return {'CANCELLED'}

            min_z = min(bottom_zs)
            max_z = max(top_zs)
            current_length = max_z - min_z

            if current_length <= 0:
                bpy.ops.object.mode_set(mode='OBJECT')
                self.report({'ERROR'}, "Current length is invalid.")
                return {'CANCELLED'}

            scale = (bone_distance - current_length) / 2
            for v in bm.verts:
                if v.index in capsule_bottom:
                    v.co.z += scale
                elif v.index in capsule_top:
                    v.co.z -= scale

            bmesh.update_edit_mesh(original_mesh_obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')

            self.report({'INFO'}, f"Collidable '{original_mesh_obj.name}' created and placed successfully")
            print(f"Capsule '{original_mesh_obj.name}' placed, rotated and resized to length {bone_distance:.3f}")
            return {'FINISHED'}

        else:
            self.report({'ERROR'}, "Please select 1 or 2 bones")
            return {'CANCELLED'}


class ResizeCapsuleOperator(bpy.types.Operator):
    bl_idname = "mesh.resize_capsule"
    bl_label = "Resize Capsule"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH' or not obj.name.startswith("collision_"):
            self.report({'ERROR'}, "Please select a capsule object")
            return {'CANCELLED'}

        props = obj.capsule_scale_props

        bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()

        def scale_group(vertex_ids, current_scale, prev_scale):
            if prev_scale == 0:
                prev_scale = 1.0
            scale_ratio = current_scale / prev_scale
            group_verts = [bm.verts[i] for i in vertex_ids if i < len(bm.verts)]
            if not group_verts:
                return
            center = sum((v.co for v in group_verts), Vector()) / len(group_verts)
            for v in group_verts:
                offset = v.co - center
                v.co = center + offset * scale_ratio

        # Only bottom and top are scaled (center removed)
        scale_group(capsule_bottom, props.scale_bottom, props.prev_scale_bottom)
        scale_group(capsule_top, props.scale_top, props.prev_scale_top)
        
        props.prev_scale_bottom = props.scale_bottom
        props.prev_scale_top = props.scale_top
        
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

        self.report({'INFO'}, f"Capsule '{obj.name}' resized successfully")
        return {'FINISHED'}


class CollidableCreateOperator(bpy.types.Operator):
    bl_idname = "import_scene.collidable_create"
    bl_label = "Create Collidable"
    bl_description = "Import 'collidable.fbx' from the same folder as this addon script"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
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
        if not os.path.exists(filepath):
            return []
            
        vertex_ids = []
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
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
        bpy.ops.object.select_all(action='DESELECT')
        
        try:
            bpy.ops.import_scene.fbx(filepath=fbx_path)
        except Exception as e:
            print(f"FBX import failed: {e}")
            return None
            
        if not bpy.context.selected_objects:
            print("No objects were imported")
            return None
            
        capsule_obj = bpy.context.selected_objects[0]
        
        bone1_head = bone1.head
        bone2_head = bone2.head
        direction = bone2_head - bone1_head
        distance = direction.length
        direction.normalize()
        midpoint = (bone1_head + bone2_head) / 2
        
        capsule_obj.location = midpoint
        capsule_forward = Vector((0, 0, 1))
        angle = capsule_forward.angle(direction)
        rotation_axis = capsule_forward.cross(direction).normalized()
        rotation_quaternion = mathutils.Quaternion(rotation_axis, angle)
        
        capsule_obj.rotation_mode = 'QUATERNION'
        capsule_obj.rotation_quaternion = rotation_quaternion
        
        print(f"Capsule placed and rotated between bones")
        return capsule_obj