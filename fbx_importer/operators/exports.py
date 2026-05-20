import bpy
import bmesh
import os
import subprocess
import threading
import re
import json
import shutil
from .json.json_to_exports import extract_uv_indices, export_vertex_group_weights, export_vertex_color_attribute, extract_face_indices










def export_object_data(obj, export_path, filename="to_export.json"):
    """
    Export ALL data entries for a single object based on JSON structure
    FIXED VERSION for your actual JSON structure
    """
    
    config_path = os.path.join(export_path, filename)
    
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        return
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    mesh_name = obj.name
    mesh_found = False
    
    # Map export_type integer to string
    def get_export_type_string(type_int):
        type_map = {
            0: 'FLOATS',
            1: 'DISTANCE',
            2: 'ANGLE'
        }
        return type_map.get(type_int, 'FLOATS')
    
    # 1. UV INDICES - FIXED for your structure
    if "uv_indices" in config:
        uv_data = config["uv_indices"]
        # In your JSON, uv_data IS the mesh dictionary
        if mesh_name in uv_data:
            mesh_found = True
            # uv_data[mesh_name] is dict with ANY number of entries
            # Example: {"fixed": {}, "sim": {}} or {"only_one": {}}
            for property_name, property_data in uv_data[mesh_name].items():
                try:
                    extract_uv_indices(
                        obj=obj,
                        filename=property_name,  # "fixed", "sim", or any other name
                        exportpath=export_path
                    )
                    print(f"✓ UV: {mesh_name} | {property_name}")
                except Exception as e:
                    print(f"✗ UV Export failed: {e}")
    
    # 1. UV Faces - FIXED for your structure
    if "uv_faces" in config:
        uv_data = config["uv_faces"]
        # In your JSON, uv_data IS the mesh dictionary
        if mesh_name in uv_data:
            mesh_found = True
            # uv_data[mesh_name] is dict with ANY number of entries
            # Example: {"fixed": {}, "sim": {}} or {"only_one": {}}
            for property_name, property_data in uv_data[mesh_name].items():
                try:
                    extract_face_indices(
                        obj=obj,
                        filename=property_name,  # "fixed", "sim", or any other name
                        exportpath=export_path
                    )
                    print(f"✓ UV: {mesh_name} | {property_name}")
                except Exception as e:
                    print(f"✗ UV Export failed: {e}")
    
    # 2. WEIGHT GROUPS - FIXED
    if "weight_groups" in config:
        weight_data = config["weight_groups"]
        if mesh_name in weight_data:
            mesh_found = True
            # weight_data[mesh_name] is dict with ANY number of entries
            # Example: {"Group": params} or {"Arm_Weight": params, "Leg_Weight": params}
            for vg_name, params in weight_data[mesh_name].items():
                try:
                    export_vertex_group_weights(
                        obj=obj,
                        vg_name=vg_name,  # Any vertex group name
                        exportpath=export_path,
                        export_type=get_export_type_string(params.get("type", 0)),
                        clamp_min=params.get("clamp_min", 0.0),
                        clamp_max=params.get("clamp_max", 1.0)
                    )
                    print(f"✓ Weights: {mesh_name} | {vg_name}")
                except Exception as e:
                    print(f"✗ Weight Export failed: {e}")
    
    # 3. VERTEX COLORS - FIXED
    if "vertex_colors" in config:
        color_data = config["vertex_colors"]
        if mesh_name in color_data:
            mesh_found = True
            # color_data[mesh_name] is dict with ANY number of entries
            # Example: {"Color": params} or {"Color1": params, "Color2": params}
            for color_name, params in color_data[mesh_name].items():
                try:
                    export_vertex_color_attribute(
                        obj=obj,
                        attr_name=color_name,  # Any vertex color name
                        exportpath=export_path,
                        export_type=get_export_type_string(params.get("type", 0)),
                        clamp_min=params.get("clamp_min", 0.0),
                        clamp_max=params.get("clamp_max", 1.0)
                    )
                    print(f"✓ Vertex Colors: {mesh_name} | {color_name}")
                except Exception as e:
                    print(f"✗ Vertex Color Export failed: {e}")
    
    if not mesh_found:
        print(f"Mesh '{mesh_name}' not found in export config")
        print(f"config file located in {config_path}")


def clear_mesh_data_files(export_path):
    """
    Clear the specified mesh data files before export
    """
    
    files_to_clear = [
        os.path.join(export_path, "floatchannels", "weight_groups.json"),
        os.path.join(export_path, "selectionsets", "uv_indices.json")
    ]
    
    for file_path in files_to_clear:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleared: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Could not clear {file_path}: {e}")
        else:
            print(f"File not found: {os.path.basename(file_path)}")














def normalize_all_weights(scene=None):
    if scene is None:
        scene = bpy.context.scene

    view_layer = bpy.context.view_layer
    prev_active = view_layer.objects.active
    prev_mode = bpy.context.mode
    # Must be in OBJECT or WEIGHT_PAINT mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        if not obj.vertex_groups:
            continue

        # Make object active & selected
        view_layer.objects.active = obj
        obj.select_set(True)

        # Normalize all vertex group weights
        bpy.ops.object.vertex_group_normalize_all(
            lock_active=False
        )

        obj.select_set(False)

    # Restore previous state
    if prev_active:
        view_layer.objects.active = prev_active
        prev_active.select_set(True)

    bpy.ops.object.mode_set(mode='OBJECT')









class ExportFBXAndRunImporterOperator(bpy.types.Operator):
    bl_idname = "mesh.export_and_run_fbximporter"
    bl_label = "Export FBX and Run Importer"
    bl_description = "Export FBX, convert to HKT, and open in Filter Manager"

    def execute(self, context):
        # Helper to include armatures needed by the given objects
        def include_armature_dependencies(objs):
            result = set(objs)
            for obj in objs:
                # Armature modifiers
                for mod in obj.modifiers:
                    if mod.type == 'ARMATURE' and mod.object:
                        result.add(mod.object)
                # Bone parent (object parent is an armature)
                if obj.parent and obj.parent.type == 'ARMATURE':
                    result.add(obj.parent)
            return result

        script_dir = os.path.dirname(os.path.abspath(__file__))
        addon_root = os.path.dirname(script_dir)
        fbx_importer = os.path.join(script_dir, "FBXImporter.exe")

        if not os.path.isfile(fbx_importer):
            self.report({'ERROR'}, "FBXImporter path is invalid")
            return {'CANCELLED'}

        props = context.scene.uv_export_props

        if props.auto_normalize:
            normalize_all_weights()

        # Use the export path if provided, else fallback to the blend directory
        if props.exportpath != "":
            export_dir = os.path.join(os.path.dirname(props.exportpath))
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}
            export_dir = os.path.join(os.path.dirname(blend_path), "export_data")

        os.makedirs(export_dir, exist_ok=True)

        # --- Clear mesh data files ---
        clear_mesh_data_files(export_dir)

        json_config_path = os.path.join(export_dir, "to_export.json")
        if os.path.exists(json_config_path):
            # (This part exports mesh data – you may also want to filter
            #  it using the same white/black list logic if needed.
            #  For now, it remains untouched.)
            mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
            if mesh_objects:
                print(f"\n=== Exporting Mesh Data from {json_config_path} ===")
                for obj in mesh_objects:
                    export_object_data(obj, export_dir, "to_export.json")
                print("=== Mesh Data Export Complete ===\n")
            else:
                print("No mesh objects found in scene")
        else:
            print(f"Mesh export config not found: {json_config_path}")
            print("Skipping mesh data export")
        # --- end mesh data export ---

        # --- Handle export.json ---
        default_export_config = os.path.join(addon_root, "export.json")
        local_export_config = os.path.join(export_dir, "export.json")

        if not os.path.exists(local_export_config) and os.path.exists(default_export_config):
            shutil.copy2(default_export_config, local_export_config)
            self.report({'INFO'}, f"Copied default export.json to {local_export_config}")

        # --- Define paths ---
        fbx_path = os.path.join(export_dir, "cloth.fbx")
        hkt_path = os.path.join(export_dir, "cloth.hkt")

        # --- Minimal default FBX export settings ---
        default_fbx_export = {
            "filepath": fbx_path,
            "global_scale": 0.01,
            "add_leaf_bones": False,
            "apply_unit_scale": True,
            "use_active_collection": False,
        }

        export_settings = default_fbx_export.copy()

        addon_export_config = os.path.join(addon_root, "ui", "config", "export.json")
        local_export_config = os.path.join(export_dir, "export.json")

        # Ensure export.json exists in export_data
        if not os.path.exists(local_export_config):
            if os.path.exists(addon_export_config):
                try:
                    shutil.copy2(addon_export_config, local_export_config)
                    self.report({'INFO'}, f"Copied addon export.json to {local_export_config}")
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to copy addon export.json: {e}")
            else:
                try:
                    with open(local_export_config, "w", encoding="utf-8") as f:
                        json.dump({"fbx_export": default_fbx_export}, f, indent=4)
                    self.report({'INFO'}, f"Created default export.json at {local_export_config}")
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to create export.json: {e}")

        # Load export.json (merge with defaults)
        if os.path.exists(local_export_config):
            try:
                with open(local_export_config, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f).get("fbx_export", {})
                    export_settings.update(loaded_settings)
            except Exception as e:
                self.report({'WARNING'}, f"Could not load export.json, using defaults: {e}")

        # =================================================================
        # White/Black list collection filtering (new logic)
        # =================================================================
        scene = context.scene
        all_objects = set(scene.objects)

        white_coll = bpy.data.collections.get("white_list")
        black_coll = bpy.data.collections.get("black_list")

        # --- Filtering part (only the changed lines) ---
        if white_coll is not None:
            # Use all_objects to include objects from sub‑collections
            export_objects = include_armature_dependencies(set(white_coll.all_objects))
        elif black_coll is not None:
            # Same for the blacklist – exclude everything from the whole black_list hierarchy
            black_set = set(black_coll.all_objects)
            export_objects = include_armature_dependencies(all_objects - black_set)
        else:
            export_objects = all_objects

        # Save current selection to restore later
        previous_selection = context.selected_objects

        # Deselect all, then select the objects to export
        bpy.ops.object.select_all(action='DESELECT')
        for obj in export_objects:
            obj.select_set(True)

        # Tell the FBX exporter to use only the selected objects
        export_settings['use_selection'] = True
        # =================================================================

        # Debug log
        print("==== Final FBX Export Settings ====")
        for key, value in export_settings.items():
            print(f"{key}: {value}")
        print("===================================")

        # Run the FBX export
        bpy.ops.export_scene.fbx(**export_settings)

        # Restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in previous_selection:
            if obj.name in scene.objects:   # still exists
                obj.select_set(True)

        # Check if filter path is provided
        if props.filterpath == "":
            self.report({'ERROR'}, "Filter path is missing")
            return {'CANCELLED'}

        filter_manager = props.filterpath

        if not os.path.isfile(filter_manager) or not filter_manager.lower().endswith(('.exe', '.bat', '.cmd')):
            self.report({'ERROR'}, f"Filter manager executable not found at {filter_manager}")
            return {'CANCELLED'}

        bat_file_path = os.path.join(export_dir, "run_filter_manager.bat")
        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(f"@echo off\n")
            bat_file.write(f"rem Running filter manager\n")
            bat_file.write(f"\"{filter_manager}\" --asset=\"{fbx_path}\" -i \"{hkt_path}\"\n")

        try:
            subprocess.run([fbx_importer, "-t", fbx_path], check=True)
            subprocess.Popen(f'"{bat_file_path}"', shell=True)
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"FBXImporter failed: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Exported and ran FBXImporter on: {fbx_path}")
        return {'FINISHED'}