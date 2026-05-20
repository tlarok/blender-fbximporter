import bpy
import bmesh
import os
import subprocess
import threading
import re
import json
import shutil


class OpenExistingScene(bpy.types.Operator):
    bl_idname = "mesh.open_existing_scene"
    bl_label = "Opens existing scene"

    def execute(self, context):

        props = context.scene.uv_export_props
        
        if props.exportpath != "":
            export_dir = os.path.join(os.path.dirname(props.exportpath)) 
        else:
            blend_path = bpy.data.filepath
            if not blend_path:
                self.report({'ERROR'}, "Please save your .blend file first.")
                return {'CANCELLED'}
            export_dir = os.path.join(os.path.dirname(blend_path), "export_data")
        
        
        # Check if the batch file exists
        bat_file_path = os.path.join(export_dir, "run_filter_manager.bat")
        
        # Run the batch file if it exists
        if os.path.isfile(bat_file_path):
            subprocess.Popen(f'"{bat_file_path}"', shell=True)
            self.report({'INFO'}, f"Opened batch file from: {export_dir}")
            return {'FINISHED'}
        else:
            self.report({'INFO'}, f"No batch file found at: {bat_file_path}")
            return {'FINISHED'}