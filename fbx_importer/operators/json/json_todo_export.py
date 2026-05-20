import json
import os
import bpy

EXPORT_JSON_NAME = "to_export.json"

BASE_EXPORT_STRUCTURE = {
    "uv_indices": {},
    "weight_groups": {},
    "vertex_colors": {},
    "uv_faces": {}
}

def get_export_json_path(exportpath):
    """
    Resolves the directory from exportpath and returns full path to to_export.json.
    If exportpath is empty, defaults to the Blender file's path with 'export_data' directory.
    """
    if exportpath:
        export_dir = os.path.dirname(exportpath)
    else:
        # Default to Blender file path
        blend_path = bpy.data.filepath
        if not blend_path:
            raise ValueError("Please save your .blend file first.")
        export_dir = os.path.join(os.path.dirname(blend_path), "export_data")

    os.makedirs(export_dir, exist_ok=True)
    if not export_dir:
        raise ValueError("Invalid exportpath")

    return os.path.join(export_dir, EXPORT_JSON_NAME)


def register_export_item(exportpath, mesh_name, data_type, group_name, clamp_min=0, clamp_max=1, float_type=0):
    if not mesh_name or not data_type or not group_name:
        raise ValueError("mesh_name, data_type and group_name are required")

    json_path = get_export_json_path(exportpath)

    # Load or init JSON
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Ensure base structure
    for key, value in BASE_EXPORT_STRUCTURE.items():
        data.setdefault(key, value.copy())

    # Create or update the entry for the data_type (e.g., weight_groups, vertex_colors)
    if data_type not in data:
        data[data_type] = {}

    data[data_type].setdefault(mesh_name, {})

    # Add group name with clamp values only if the data_type is weight_groups or vertex_colors
    mesh_data = data[data_type][mesh_name]
    group_data = mesh_data.setdefault(group_name, {})

    if data_type in ["weight_groups", "vertex_colors"]:
        # Only add clamp values for weight_groups and vertex_colors
        group_data["clamp_min"] = clamp_min
        group_data["clamp_max"] = clamp_max
        group_data["type"] = float_type

    # Prevent duplicate group names
    if group_name not in mesh_data:
        mesh_data[group_name] = group_data

    # Write the updated data back to the JSON file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return json_path





def remove_export_item(exportpath, mesh_name, data_type, group_name):
    """
    Remove item from JSON (fixed for dict)
    """
    import os
    import json
    
    json_path = get_export_json_path(exportpath)

    if not os.path.exists(json_path):
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return False

    # Check if item exists in JSON
    if data_type not in data or mesh_name not in data[data_type]:
        return False

    # This is a dict, not a list
    groups = data[data_type][mesh_name]

    if group_name not in groups:
        return False
    
    # FIXED: Use dict deletion, not list .remove()
    del groups[group_name]

    if not groups:
        del data[data_type][mesh_name]

    if not data[data_type]:
        del data[data_type]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return True








def rename_export_item(exportpath, data_type, mesh_name, old_name, new_name):
    """
    Rename in JSON only - now with data_type parameter
    Uses get_export_json_path to find the JSON file
    """
    
    # Get the JSON path using your existing function
    json_path = get_export_json_path(exportpath)
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON not found: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check data_type exists
    if data_type not in data:
        raise KeyError(f"Data type '{data_type}' not found in JSON")
    
    # Check mesh exists in data_type
    if mesh_name not in data[data_type]:
        raise KeyError(f"Mesh '{mesh_name}' not found in '{data_type}'")
    
    # Check old_name exists
    if old_name not in data[data_type][mesh_name]:
        raise KeyError(f"'{old_name}' not found in mesh '{mesh_name}'")
    
    # Check new_name doesn't exist
    if new_name in data[data_type][mesh_name]:
        raise ValueError(f"'{new_name}' already exists in mesh '{mesh_name}'")
    
    # Rename in JSON
    data[data_type][mesh_name][new_name] = data[data_type][mesh_name].pop(old_name)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return json_path