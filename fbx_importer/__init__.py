# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Havok physics exporter",
    "author": "Tlarok and OpheliaComplex",
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar > Havok export",
    "description": "Starfield Havok physics export tools",
    "warning": "",
    "category": "Import-Export | Object",
}

import bpy
from fbx_importer.ui.panels import UVIndexExtractorPanel
from fbx_importer.ui.properties import UVExportProperties, list_saved_files, CapsuleScaleProperties, CapsuleToolsProperties, CapsuleLengthProperties
from fbx_importer.operators.exports import ExportVertexGroupWeightsOperator, UVIndexExtractorOperator, ExportFBXAndRunImporterOperator
from fbx_importer.operators.utils import UVSelectVerticesFromFileOperator, UVDeleteFileOperator, UVRenameFileOperator, UVOpenFolderOperator
from fbx_importer.operators.utils_collisions import CollidableCreateOperator, ResizeCapsuleOperator, placer, OBJECT_OT_toggle_capsule_length, collision_convtype


classes = [
    UVExportProperties,
    UVIndexExtractorOperator,
    UVRenameFileOperator,
    UVOpenFolderOperator,
    UVSelectVerticesFromFileOperator,
    UVIndexExtractorPanel,
    ExportFBXAndRunImporterOperator,
    ResizeCapsuleOperator,
    CollidableCreateOperator,
    placer,
    CapsuleLengthProperties, 
    OBJECT_OT_toggle_capsule_length,
    UVDeleteFileOperator,
    ExportVertexGroupWeightsOperator,
    CapsuleScaleProperties,
    collision_convtype
]

def register():
    # Register all classes
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except ValueError:
            print(f"Class {cls.__name__} already registered")
    
    # Initialize properties
    bpy.types.Scene.uv_export_props = bpy.props.PointerProperty(type=UVExportProperties)
    bpy.types.Object.capsule_scale_props = bpy.props.PointerProperty(type=CapsuleScaleProperties)
    bpy.types.Scene.capsule_length_props = bpy.props.PointerProperty(type=CapsuleLengthProperties)

def unregister():
    # Unregister all classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Remove properties
    del bpy.types.Scene.uv_export_props
    del bpy.types.Object.capsule_scale_props
    del bpy.types.Scene.capsule_length_props

if __name__ == "__main__":
    register()