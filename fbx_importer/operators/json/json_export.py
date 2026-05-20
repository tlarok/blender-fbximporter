import bpy
import bmesh
import os
import json


def append_to_json(json_path, mesh_name, new_data):
    """
    Merge new_data into existing JSON file without overwriting old groups.
    - mesh_name: the key for the mesh
    - new_data: dict like {"MyGroup": {"export_mode": 0, "weights": [ ... ]}}
    """
    
    content = {}
    
    if os.path.exists(json_path):
        try:
            # Check if file has content
            if os.path.getsize(json_path) > 0:
                with open(json_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
        except:
            # If anything goes wrong, start fresh
            content = {}
    
    # Ensure content is a dict
    if not isinstance(content, dict):
        content = {}
    
    # Initialize mesh entry if not exists
    if mesh_name not in content:
        content[mesh_name] = {}
    
    # Merge each group into the mesh
    for group_name, group_data in new_data.items():
        content[mesh_name][group_name] = group_data
    
    # Write back to file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4, ensure_ascii=False)