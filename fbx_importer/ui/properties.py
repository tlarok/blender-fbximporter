import bpy
import os
import bmesh
import json
from math import isclose
from bpy.props import (
    StringProperty, EnumProperty, FloatProperty, BoolProperty, CollectionProperty
)

# ========== CONFIGURATION MANAGEMENT ==========
class ConfigManager:
    CONFIG_FILE_NAME = "config.json"

    @classmethod
    def get_config_file(cls):
        addon_root = os.path.dirname(os.path.abspath(__file__))
        config_dir = os.path.join(addon_root, "config")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, cls.CONFIG_FILE_NAME)

    @classmethod
    def save_option(cls, name, value):
        config_file = cls.get_config_file()
        data = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print("Error reading config file, overwriting.")
        data[name] = value
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_option(cls, name, default=None):
        config_file = cls.get_config_file()
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get(name, default)
            except json.JSONDecodeError:
                print("Error reading config file.")
        return default


# ========== CAPSULE VERTEX LISTS (UPDATED) ==========
# Old lists replaced with the new model's vertex groups
CAPSULE_TOP =    [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65]
CAPSULE_BOTTOM = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
# CAPSULE_CENTER removed – no middle group in the new model


# ========== CAPSULE LENGTH PROPERTIES ==========
class CapsuleLengthProperties(bpy.types.PropertyGroup):
    original_length: FloatProperty(name="Original Length", default=1.0)

    # These now use the correct lists (previously they were swapped)
    bottom_ids_str: StringProperty(
        name="Bottom IDs",
        default=",".join(str(i) for i in CAPSULE_BOTTOM)   # was using CAPSULE_TOP
    )
    top_ids_str: StringProperty(
        name="Top IDs",
        default=",".join(str(i) for i in CAPSULE_TOP)      # was using CAPSULE_BOTTOM
    )

    @property
    def bottom_ids(self):
        return [int(i) for i in self.bottom_ids_str.split(",") if i.strip()]

    @property
    def top_ids(self):
        return [int(i) for i in self.top_ids_str.split(",") if i.strip()]

    # ----- Helper methods for capsule length operations -----
    def _get_edit_bmesh(self, obj):
        """Enter edit mode and return bmesh, ensure cleanup."""
        if not obj or obj.type != 'MESH':
            return None, None
        current_mode = obj.mode
        if current_mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        return bm, current_mode

    def _get_current_z_range(self, bm):
        """Return (min_z, max_z) from top and bottom vertex groups."""
        bottom_zs = [bm.verts[i].co.z for i in self.bottom_ids if i < len(bm.verts)]
        top_zs = [bm.verts[i].co.z for i in self.top_ids if i < len(bm.verts)]
        if not top_zs or not bottom_zs:
            return None, None
        return min(bottom_zs), max(top_zs)

    def _apply_scale_offset(self, bm, offset):
        """Apply vertical offset to bottom and top vertex groups."""
        for v in bm.verts:
            if v.index in self.bottom_ids:
                v.co.z -= offset
            elif v.index in self.top_ids:
                v.co.z += offset

    def _adjust_length(self, obj, target_length, store_original=False):
        """Core logic to adjust capsule length."""
        bm, prev_mode = self._get_edit_bmesh(obj)
        if bm is None:
            return {'CANCELLED'}

        try:
            min_z, max_z = self._get_current_z_range(bm)
            if min_z is None or max_z is None:
                print("Invalid vertex groups.")
                return {'CANCELLED'}

            current_length = max_z - min_z
            if store_original and isclose(current_length, target_length, rel_tol=1e-3):
                target_length = self.original_length

            offset = (target_length - current_length) / 2.0
            self._apply_scale_offset(bm, offset)
            bmesh.update_edit_mesh(obj.data)
        finally:
            bpy.ops.object.mode_set(mode=prev_mode)
        return {'FINISHED'}

    def toggle_length(self, obj, target_length=2.0):
        return self._adjust_length(obj, target_length, store_original=True)

    def set_length(self, obj, target_length=1.0):
        return self._adjust_length(obj, target_length, store_original=False)


# ========== CAPSULE TOOLS PROPERTIES ==========
class CapsuleToolsProperties(bpy.types.PropertyGroup):
    bottom_file: StringProperty(name="Bottom Vertex File", subtype='FILE_PATH')
    top_file: StringProperty(name="Top Vertex File", subtype='FILE_PATH')
    middle_file: StringProperty(name="Middle Vertex File", subtype='FILE_PATH')  # keep for UI, but no longer used
    scale_bottom: FloatProperty(name="Bottom Scale", default=1.0, min=0.01)
    scale_top: FloatProperty(name="Top Scale", default=1.0, min=0.01)
    scale_center: FloatProperty(name="Center Scale", default=1.0, min=0.01)   # unused now


class CapsuleScaleProperties(bpy.types.PropertyGroup):
    prev_scale_bottom: FloatProperty(default=1.0)
    prev_scale_top: FloatProperty(default=1.0)
    prev_scale_center: FloatProperty(default=1.0)   # may be removed if you clean up later
    scale_bottom: FloatProperty(default=1.0, min=0.01)
    scale_top: FloatProperty(default=1.0, min=0.01)
    scale_center: FloatProperty(default=1.0, min=0.01)   # ditto


# ========== UV EXPORT PROPERTIES (unchanged except for removal of center references if any) ==========
class UVExportProperties(bpy.types.PropertyGroup):
    # ----- Config helpers -----
    def _save_property(self, prop_name, value, context=None):
        ConfigManager.save_option(prop_name, value)
        print(f"{prop_name} updated: {value}")

    # ----- JSON helpers for clamp values -----
    def _get_export_json_path(self):
        if self.exportpath:
            json_dir = self.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                return None
            json_dir = os.path.join(os.path.dirname(blend_path), "export_data")
        return os.path.join(json_dir, "to_export.json")

    def _load_json_data(self):
        json_path = self._get_export_json_path()
        if not json_path or not os.path.exists(json_path):
            return None
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return None

    def _get_clamp_from_json_section(self, data, section_key, obj_name, attr_name):
        section = data.get(section_key)
        if not section or obj_name not in section:
            return None, None
        attr_data = section[obj_name].get(attr_name)
        if attr_data and "clamp_min" in attr_data and "clamp_max" in attr_data:
            return attr_data["clamp_min"], attr_data["clamp_max"]
        return None, None

    def load_clamp_values_for_mesh(self, obj):
        if not obj or obj.type != 'MESH':
            return False

        default_min, default_max = 0.0, 1.0
        data = self._load_json_data()
        if data is None:
            self["clamp_min"] = default_min
            self["clamp_max"] = default_max
            return False

        mesh_name = obj.name
        section_key = "weight_groups" if self.group_type == 'VERTEX_GROUP' else "vertex_colors"
        attr_name = self.vertex_group_name if self.group_type == 'VERTEX_GROUP' else self.vertex_color_name

        if attr_name and attr_name != "NONE":
            min_val, max_val = self._get_clamp_from_json_section(data, section_key, mesh_name, attr_name)
            if min_val is not None and max_val is not None:
                self["clamp_min"] = min_val
                self["clamp_max"] = max_val
                return True

        self["clamp_min"] = default_min
        self["clamp_max"] = default_max
        return False

    # ----- Update callbacks -----
    def update_filterpath(self, context):
        self._save_property("filterpath", self.filterpath)

    def update_filename(self, context):
        self._save_property("filename", self.filename)

    def update_collision_type(self, context):
        self._save_property("collision_type", self.collision_type)

    def update_export_type(self, context):
        self._save_property("export_type", self.export_type)

    def update_group_type(self, context):
        self._save_property("group_type", self.group_type)
        if context.active_object:
            self.load_clamp_values_for_mesh(context.active_object)

    def update_vertex_group_name(self, context):
        if context.active_object:
            self.load_clamp_values_for_mesh(context.active_object)

    def update_vertex_color_name(self, context):
        if context.active_object:
            self.load_clamp_values_for_mesh(context.active_object)

    def update_clamp_min(self, context):
        if self.clamp_min > self.clamp_max:
            self.clamp_min = self.clamp_max
        self._save_property("clamp_min", self.clamp_min)

    def update_clamp_max(self, context):
        if self.clamp_max < self.clamp_min:
            self.clamp_max = self.clamp_min
        self._save_property("clamp_max", self.clamp_max)

    def update_load_from_json(self, context):
        self._save_property("load_from_json", self.load_from_json)
        if self.load_from_json and context.active_object:
            self.load_clamp_values_from_json(context)

    def update_selected_file(self, context):
        if self.selected_file != "NONE":
            self.filename = self.selected_file
            self._save_property("selected_file", self.selected_file)
        if context.active_object:
            self.load_clamp_values_for_mesh(context.active_object)

    # ----- Property items callbacks (instance methods, not static) -----
    def vertex_group_items(self, context):
        obj = context.active_object
        items = [("NONE", "None", "")]
        if obj and obj.type == 'MESH':
            for vg in obj.vertex_groups:
                items.append((vg.name, vg.name, ""))
        return items

    def bone_items(self, context):
        for armature in bpy.data.objects:
            if armature.type == 'ARMATURE':
                return [(bone.name, bone.name, "") for bone in armature.data.bones]
        return [("NONE", "None", "")]

    # ----- Properties -----
    auto_normalize: BoolProperty(
        name="Auto Normalize",
        default=False
    )

    group_type: EnumProperty(
        name="Group Type",
        items=[
            ('VERTEX_GROUP', "Vertex Group", "Export vertex group weights"),
            ('VERTEX_COLOR', "Vertex Color", "Export vertex colors"),
        ],
        default=ConfigManager.load_option("group_type", 'VERTEX_GROUP'),
        update=update_group_type
    )

    vertex_color_name: StringProperty(
        name="Vertex Color",
        default="",
        update=update_vertex_color_name
    )

    vertex_group_name: EnumProperty(
        name="Vertex Group",
        items=vertex_group_items,
        update=update_vertex_group_name
    )

    bone_name: EnumProperty(
        name="Bone selector",
        items=bone_items,
    )

    clamp_min: FloatProperty(
        name="Min Export Value",
        default=ConfigManager.load_option("clamp_min", 0.0),
        min=0.0, max=100.0, precision=6,
        update=update_clamp_min
    )

    clamp_max: FloatProperty(
        name="Max Export Value",
        default=ConfigManager.load_option("clamp_max", 1.0),
        min=0.0, max=100.0, precision=6,
        update=update_clamp_max
    )

    filename: StringProperty(
        name="Vertex set Name(UV)",
        default=ConfigManager.load_option("filename", "uv_indices.txt"),
        update=update_filename
    )

    exportpath: StringProperty(
        name="(optional)Export Path",
        default="",
        subtype='DIR_PATH'
    )

    filterpath: StringProperty(
        name="Standalone Filter Manager Path",
        default=ConfigManager.load_option("filterpath", ""),
        subtype='FILE_PATH',
        update=update_filterpath
    )

    collision_type: EnumProperty(
        name="Collision Type",
        items=[
            ("collision_sphere", "Sphere", "A spherical collision"),
            ("collision_plane", "Plane", "A flat plane collision"),
            ("collision_capsule", "Capsule", "A capsule-shaped collision"),
            ("collision_convexgeom", "Convex Geometry", "A convex-shaped geometry"),
            ("collision_convexheight", "Convex Heightfield", "A convex heightfield collision")
        ],
        default=ConfigManager.load_option("collision_type", 'collision_convexgeom'),
        update=update_collision_type
    )

    export_type: EnumProperty(
        name="Export Type",
        items=[
            ('FLOATS', "Floats", "Export as floats", 0),
            ('DISTANCE', "Distance", "Export as distance", 1),
            ('ANGLE', "Angle", "Export as angle", 2),
        ],
        default=ConfigManager.load_option("export_type", 'FLOAT'),
        update=update_export_type
    )

    selected_file: EnumProperty(
        name="Saved Groups",
        items=lambda self, ctx: list_saved_files(self, ctx),
        update=update_selected_file
    )

    fbx_importer_path: StringProperty(
        name="FBX Importer Path",
        subtype='FILE_PATH'
    )

    fbx_export_name: StringProperty(
        name="FBX Export Name",
        default="cloth.fbx"
    )

    bottom_file: StringProperty(
        name="Bottom Vertex File",
        subtype='FILE_PATH'
    )
    top_file: StringProperty(
        name="Top Vertex File",
        subtype='FILE_PATH'
    )
    middle_file: StringProperty(
        name="Middle Vertex File",
        subtype='FILE_PATH'
    )

    scale_bottom: FloatProperty(
        name="Bottom Scale",
        default=1.0, min=0.0
    )
    scale_top: FloatProperty(
        name="Top Scale",
        default=1.0, min=0.0
    )
    scale_center: FloatProperty(
        name="Center Scale",
        default=1.0, min=0.0
    )

    load_from_json: BoolProperty(
        name="Load Values from JSON",
        default=ConfigManager.load_option("load_from_json", False),
        update=update_load_from_json
    )

    # ----- Compatibility collection -----
    vertex_color_point_list: CollectionProperty(type=bpy.types.PropertyGroup)


# ========== STANDALONE FUNCTIONS ==========
def list_saved_files(self, context):
    """Enum items for saved UV groups. Uses the exact same logic as before."""
    props = context.scene.uv_export_props
    obj = context.active_object

    if not obj or obj.type != 'MESH':
        return [("NONE", "None", "", 0)]

    try:
        if props.exportpath:
            json_path = os.path.join(os.path.dirname(props.exportpath), "to_export.json")
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                return [("NONE", "Please save your .blend file first.", "", 0)]
            json_path = os.path.join(os.path.dirname(blend_path), "export_data", "to_export.json")

        if not os.path.exists(json_path):
            return [("NONE", "No to_export.json found", "", 0)]

        with open(json_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        if not isinstance(content, dict):
            return [("NONE", "Invalid JSON structure", "", 0)]

        # Get both uv_indices and uv_faces
        uv_indices = content.get("uv_indices", {})
        uv_faces = content.get("uv_faces", {})
        
        mesh_name = obj.name
        
        # Combine both into a list of attribute names with their source type
        all_attributes = []
        
        # Process uv_indices
        if mesh_name in uv_indices and isinstance(uv_indices[mesh_name], dict):
            for attr_name in uv_indices[mesh_name].keys():
                all_attributes.append((attr_name, "uv_indices"))
        
        # Process uv_faces
        if mesh_name in uv_faces and isinstance(uv_faces[mesh_name], dict):
            for attr_name in uv_faces[mesh_name].keys():
                all_attributes.append((attr_name, "uv_faces"))
        
        if not all_attributes:
            return [("NONE", "No attributes in JSON", "", 0)]

        # Filter attributes that exist on mesh and are integer types
        available_attributes = []
        for attr_name, source_type in all_attributes:
            if attr_name in obj.data.attributes:
                attr = obj.data.attributes[attr_name]
                if attr.data_type in {'INT', 'INT8', 'INT32'}:
                    available_attributes.append(attr_name)

        if not available_attributes:
            return [("NONE", "No matching attributes found", "", 0)]

        return [
            (attr_name, attr_name, f"{attr_name}", idx)
            for idx, attr_name in enumerate(sorted(available_attributes))
        ]

    except Exception as e:
        print(f"Error in list_saved_files: {e}")
        return [("NONE", "Error loading", "", 0)]