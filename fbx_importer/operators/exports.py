import bpy
import bmesh
import os
import subprocess
import threading

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


class ExportFBXAndRunImporterOperator(bpy.types.Operator):
    bl_idname = "mesh.export_and_run_fbximporter"
    bl_label = "Export FBX and Run Importer"

    def execute(self, context):
        # Get the active object (we're still checking but no longer exporting just it)
        obj = context.active_object
        
        # Check if there is an active object
        if not obj:
            self.report({'ERROR'}, "No active object selected")
            return {'CANCELLED'}
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        fbx_importer = os.path.join(script_dir, "FBXImporter.exe")

        # Check if FBXImporter exists
        if not os.path.isfile(fbx_importer):
            self.report({'ERROR'}, "FBXImporter path is invalid")
            return {'CANCELLED'}

        props = context.scene.uv_export_props

        # Use the export path if provided, else fallback to the blend directory
        if props.exportpath != "":
            blend_path = props.exportpath
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}

        # Create the export_data directory next to the .blend file
        export_dir = os.path.join(os.path.dirname(blend_path), "export_data") 
        os.makedirs(export_dir, exist_ok=True)

        # Define paths for FBX and HKT
        fbx_path = os.path.join(export_dir, "cloth.fbx")
        
        armature = next((obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE'), None)

        if armature:
            valid_bone_names = {bone.name for bone in armature.data.bones}

            for obj in bpy.context.scene.objects:
                if obj.type == 'MESH' and obj.vertex_groups:
                    # Filter vertex groups to only include ones that match bones in the Armature
                    group_map = {g.index: g.name for g in obj.vertex_groups if g.name in valid_bone_names}
                    
                    # Build a dictionary of weights per vertex (only valid groups)
                    vertex_weights = {v.index: {} for v in obj.data.vertices}
                    for v in obj.data.vertices:
                        for g in v.groups:
                            if g.group in group_map:
                                vertex_weights[v.index][g.group] = g.weight

                    # Normalize weights for each vertex using only valid groups
                    for v_index, weights in vertex_weights.items():
                        total_weight = sum(weights.values())
                        if total_weight > 0.0:
                            for group_index, weight in weights.items():
                                normalized_weight = weight / total_weight
                                obj.vertex_groups[group_index].add([v_index], normalized_weight, 'REPLACE')


        
        # Export the entire scene to FBX (no selection limitation)
        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            global_scale=0.01,
            add_leaf_bones=False,
            apply_unit_scale=True,
            use_active_collection=False,  # Export the whole scene, not just the active collection
        )

        # Check if filter path is provided
        if props.filterpath == "":
            self.report({'ERROR'}, "Filter path is missing")
            return {'CANCELLED'}
        
        filter_manager = props.filterpath

        # Check if the filter manager is a valid executable
        if not os.path.isfile(filter_manager) or not filter_manager.lower().endswith(('.exe', '.bat', '.cmd')):
            self.report({'ERROR'}, f"Filter manager executable not found at {filter_manager}")
            return {'CANCELLED'}
        
        hkt_path = os.path.join(export_dir, "cloth.hkt")

        # Create a temporary .bat file to run the filter manager
        bat_file_path = os.path.join(export_dir, "run_filter_manager.bat")
        
        # Create the .bat file with the required content
        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(f"@echo off\n")
            bat_file.write(f"rem Running filter manager\n")
            bat_file.write(f"\"{filter_manager}\" --asset=\"{fbx_path}\" -i \"{hkt_path}\"\n")
            bat_file.write(f"pause\n")  # Keep the window open after execution
        
        # Run the .bat file asynchronously
        def run_filter_manager_threadsafe():
            try:
                subprocess.run([bat_file_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
                message = "Filter Manager completed successfully."
                severity = 'INFO'
            except subprocess.CalledProcessError as e:
                message = f"Filter Manager failed: {e}"
                severity = 'ERROR'
            except subprocess.TimeoutExpired as e:
                message = f"Filter Manager process timed out: {e}"
                severity = 'ERROR'

            # Function to safely report back to the main thread
            def report_result():
                self.report({severity}, message)

            # Register a timer to run the report in the main thread after a short delay
            bpy.app.timers.register(report_result, first_interval=0.1)

        # Run the FBX importer in the main thread
        try:
            subprocess.run([fbx_importer, fbx_path], check=True)
            # Start the filter manager in a background thread
            threading.Thread(target=run_filter_manager_threadsafe).start()
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"FBXImporter failed: {e}")
            return {'CANCELLED'}

        # Inform the user that the export was successful
        self.report({'INFO'}, f"Exported and ran FBXImporter on: {fbx_path}")
        return {'FINISHED'}