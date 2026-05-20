import bpy
import bmesh
import os
from .json_export import append_to_json

def extract_uv_indices(obj, filename, exportpath=None):
    """
    Extracts UV indices from the given mesh object and saves them to a JSON file.
    Uses vertex attribute (with 0/1 values) instead of vertex selection state.
    
    Parameters:
        obj (bpy.types.Object): The mesh object to extract UV indices from.
        filename (str): The name of the vertex attribute to use (0/1 values).
        exportpath (str, optional): Optional base path for export. If None, uses .blend file path.
    
    Returns:
        str: The path to the JSON file where data was saved.
    
    Raises:
        ValueError: If the mesh is invalid or input parameters are incorrect.
    """

    filename = filename.strip()
    if not filename:
        raise ValueError("Filename/attribute name cannot be empty")
    if not filename.endswith(".json"):
        filename += ".json"

    if not obj or obj.type != 'MESH':
        raise ValueError("Please provide a valid mesh object")

    # Get the vertex attribute
    attribute_name = filename.rsplit(".", 1)[0].strip()
    if attribute_name not in obj.data.attributes:
        raise ValueError(f"Vertex attribute '{attribute_name}' not found")
    
    attr = obj.data.attributes[attribute_name]
    if attr.data_type not in ['INT', 'FLOAT', 'INT8', 'INT32']:
        raise ValueError(f"Attribute '{attribute_name}' must be an integer or float type (0/1 values)")

    # Ensure object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Determine export directory
    if exportpath:
        export_dir = os.path.join(exportpath, "selectionsets")
    else:
        blend_path = bpy.data.filepath
        if not blend_path:
            raise ValueError("Please save your .blend file first.")
        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/selectionsets")

    os.makedirs(export_dir, exist_ok=True)

    # Create bmesh
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        bm.free()
        raise ValueError("Mesh has no UV layer")

    # Map loops to UV indices
    uv_index_counter = 0
    loop_to_uv_index = {}
    for face in bm.faces:
        if len(face.verts) != 3:
            bm.free()
            raise ValueError("Mesh contains non-triangular face(s). Operation cancelled.")
        for loop in face.loops:
            loop_to_uv_index[loop] = uv_index_counter
            uv_index_counter += 1

    # Collect vertices with attribute value == 1
    selected_vertex_indices = []
    for i, data in enumerate(attr.data):
        if attr.data_type == 'FLOAT':
            if abs(data.value - 1.0) < 0.001:
                selected_vertex_indices.append(i)
        else:
            if data.value == 1:
                selected_vertex_indices.append(i)

    if not selected_vertex_indices:
        print(f"Warning: No vertices found with value 1 in attribute '{attribute_name}'")

    # Collect all UV indices from selected vertices (use a set to avoid duplicates)
    uv_indices = set()
    for vert_idx in selected_vertex_indices:
        if vert_idx >= len(bm.verts):
            continue
        vert = bm.verts[vert_idx]
        for loop in vert.link_loops:
            face = loop.face
            if face is None or len(face.verts) != 3:
                continue
            if loop not in loop_to_uv_index:
                continue
            uv_indices.add(loop_to_uv_index[loop])

    group_name = attribute_name
    if not group_name:
        bm.free()
        raise ValueError("Attribute name cannot be empty")

    # Convert to JSON-serializable format (list of ints)
    mesh_data = {group_name: sorted(uv_indices)}  # sorted for consistent output

    # Clean object name
    obj_name = obj.name.split("|")[0].strip()

    # Write JSON
    json_path = os.path.join(export_dir, "uv_indices.json")
    append_to_json(json_path, obj_name, mesh_data)

    bm.free()
    
    print(f"Exported {len(uv_indices)} UV indices from {len(selected_vertex_indices)} vertices with attribute '{attribute_name}' == 1")
    return json_path




def extract_face_indices(obj, filename, exportpath=None):
    """
    Extracts face indices from the given mesh object where all vertices of the face
    have the specified vertex attribute set to 1. Saves the result to a JSON file.

    Parameters:
        obj (bpy.types.Object): The mesh object to process.
        filename (str): The name of the vertex attribute to use (0/1 values).
        exportpath (str, optional): Optional base path for export. If None, uses .blend file path.

    Returns:
        str: The path to the JSON file where data was saved.

    Raises:
        ValueError: If the mesh is invalid, attribute not found, or non‑triangular faces exist.
    """
    filename = filename.strip()
    if not filename:
        raise ValueError("Filename/attribute name cannot be empty")

    if not obj or obj.type != 'MESH':
        raise ValueError("Please provide a valid mesh object")

    # Get the vertex attribute
    attribute_name = filename  # Use the given name directly (no .json extension)
    if attribute_name not in obj.data.attributes:
        raise ValueError(f"Vertex attribute '{attribute_name}' not found")

    attr = obj.data.attributes[attribute_name]
    if attr.data_type not in ['INT', 'FLOAT', 'INT8', 'INT32']:
        raise ValueError(f"Attribute '{attribute_name}' must be an integer or float type (0/1 values)")

    # Ensure object mode
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Determine export directory
    if exportpath:
        export_dir = os.path.join(exportpath, "selectionsets")
    else:
        blend_path = bpy.data.filepath
        if not blend_path:
            raise ValueError("Please save your .blend file first.")
        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/selectionsets")

    os.makedirs(export_dir, exist_ok=True)

    # Create bmesh
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # Ensure lookup tables
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Check for triangular faces (required for vertex selection logic)
    for face in bm.faces:
        if len(face.verts) != 3:
            bm.free()
            raise ValueError("Mesh contains non‑triangular face(s). Operation cancelled.")

    # Build a list of selected vertex indices (attribute == 1)
    selected_vertex_indices = set()
    for i, data in enumerate(attr.data):
        if attr.data_type == 'FLOAT':
            if abs(data.value - 1.0) < 0.001:
                selected_vertex_indices.add(i)
        else:  # Integer type
            if data.value == 1:
                selected_vertex_indices.add(i)

    # Collect faces where all three vertices are selected
    face_indices = []
    for face in bm.faces:
        # Get the three vertex indices
        verts = [v.index for v in face.verts]
        if all(v_idx in selected_vertex_indices for v_idx in verts):
            face_indices.append(face.index)

    if not face_indices:
        print(f"Warning: No faces found where all vertices have attribute '{attribute_name}' == 1")

    group_name = attribute_name
    mesh_data = {group_name: face_indices}

    # Clean object name
    obj_name = obj.name.split("|")[0].strip()

    # Write JSON (hardcoded filename "uv_faces.json" as requested)
    json_path = os.path.join(export_dir, "uv_faces.json")
    append_to_json(json_path, obj_name, mesh_data)

    bm.free()
    print(f"Exported {len(face_indices)} faces with attribute '{attribute_name}' == 1 on all vertices")
    return json_path




def export_vertex_group_weights(obj, vg_name, exportpath, export_type, clamp_min, clamp_max):
    """
    Export vertex group weights in UV loop order.

    Returns:
        str: path to weight_groups.json

    Raises:
        ValueError: on invalid state or input
    """

    if not obj or obj.type != 'MESH':
        raise ValueError("Please select a mesh object.")

    if vg_name not in obj.vertex_groups:
        raise ValueError(f"Vertex group '{vg_name}' not found.")

    vgroup = obj.vertex_groups[vg_name]

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        bm.free()
        raise ValueError("Mesh has no active UV map.")

    loop_weights = []  # (uv_index, weight)
    uv_index = 0

    for face in bm.faces:
        if len(face.verts) != 3:
            bm.free()
            raise ValueError("Non-triangular face detected. Please triangulate the mesh.")

        for loop in face.loops:
            vert = loop.vert
            try:
                weight = vgroup.weight(vert.index)
            except RuntimeError:
                weight = 0.0

            loop_weights.append((uv_index, weight))
            uv_index += 1

    bm.free()

    # Determine export directory
    if exportpath:
        export_dir = os.path.join(exportpath, "floatchannels")
    else:
        blend_path = bpy.data.filepath
        if not blend_path:
            raise ValueError("Please save your .blend file first.")
        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/floatchannels")

    os.makedirs(export_dir, exist_ok=True)

    export_mode_int = {
        'FLOATS': 0,
        'DISTANCE': 1,
        'ANGLE': 2
    }.get(export_type)

    if export_mode_int is None:
        raise ValueError(f"Invalid export type: '{export_type}'")

    # Compute weights
    weights = [(w * (clamp_max - clamp_min)) + clamp_min for _, w in loop_weights]

    data = {
        vg_name: {
            "export_mode": export_mode_int,
            "weights": weights
        }
    }

    obj_name = obj.name.split("|")[0].strip()

    json_path = os.path.join(export_dir, "weight_groups.json")
    append_to_json(json_path, obj_name, data)

    return json_path















def export_vertex_color_attribute(obj, attr_name, exportpath, export_type, clamp_min, clamp_max):
    """
    Export vertex color attribute as float channel in UV order.
    Assumes attribute is authored per-vertex (original behavior).
    
    Returns:
        str: path to weight_groups.json

    Raises:
        ValueError
    """

    if not obj or obj.type != 'MESH':
        raise ValueError("Please select a mesh object.")

    mesh = obj.data
    color_attrs = mesh.color_attributes

    if not attr_name or color_attrs.get(attr_name) is None:
        raise ValueError(f"Vertex color '{attr_name}' not found.")

    color_layer = color_attrs.get(attr_name)

    # Original logic: build per-vertex float list
    loop_colors = [c.color[:] for c in color_layer.data]

    floats_src = []
    for c in loop_colors:
        if c[0] > (c[1] + c[2]) / 2:
            floats_src.append(-c[0])
        else:
            floats_src.append((c[0] + c[1] + c[2]) / 3)

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        bm.free()
        raise ValueError("Mesh has no active UV map.")

    loop_floats = []  # (uv_index, float)
    uv_index = 0

    for face in bm.faces:
        if len(face.verts) != 3:
            bm.free()
            raise ValueError("Non-triangular face detected. Please triangulate the mesh.")

        for loop in face.loops:
            vert = loop.vert
            loop_floats.append((uv_index, floats_src[vert.index]))
            uv_index += 1

    bm.free()

    # Determine export directory
    if exportpath:
        export_dir = os.path.join(exportpath, "floatchannels")
    else:
        blend_path = bpy.data.filepath
        if not blend_path:
            raise ValueError("Please save your .blend file first.")
        export_dir = os.path.join(os.path.dirname(blend_path), "export_data/floatchannels")

    os.makedirs(export_dir, exist_ok=True)

    export_mode_int = {
        'FLOATS': 0,
        'DISTANCE': 1,
        'ANGLE': 2
    }.get(export_type)

    if export_mode_int is None:
        raise ValueError(f"Invalid export type: {export_type}")

    # Clamp remap
    floats = [(v * (clamp_max - clamp_min)) + clamp_min for _, v in loop_floats]

    data = {
        attr_name: {
            "export_mode": export_mode_int,
            "weights": floats
        }
    }

    obj_name = obj.name.split("|")[0].strip()
    json_path = os.path.join(export_dir, "weight_groups.json")
    append_to_json(json_path, obj_name, data)

    return json_path