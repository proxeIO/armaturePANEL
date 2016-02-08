# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {'name': 'Armature Data Panel',
           'author': 'proxe',
           'version': (0, 0, 8),
           'blender': (2, 66, 0),
           'location': '3D View > Properties Panel',
           'warning': 'Work in Progress',
           #'wiki_url': '',
           #'tracker_url': '',
           'description': "Quickly access many of the most commonly used armatu"
                          "re options within the 3D View",
           'category': 'Rigging'}

import bpy

# ##### BEGIN INFO BLOCK #####
#
#    Author: Trentin Frederick (a.k.a, proxe)
#    Contact: trentin.frederick@gmail.com, proxe.err0r@gmail.com
#    Version: 0.0.8
#
# ##### END INFO BLOCK #####

# ##### BEGIN VERSION BLOCK #####
#
#   0.0
#   - 0.0.8 - Included properties in the operator that allows for more specific
#             control over the shape to bone process, included these properties
#             in the armature data panel, as toggle options that can be
#             displayed when needed, refined the way the armature data panel
#             displays the options related to custom bone shapes when there was
#             not currently one assigned to the active pose bone.
#   - 0.0.7 - Rewrote code to be PEP8 compliant and optimized it, Included this
#             info in this script, followed similar code format used in the
#             past in respect to previous add-ons I have created.
#   - 0.0.6 - Added a prop that allows for a user to turn on the auto-naming
#             feature when snapping shapes to bones, rather then always being
#             applied.
#   - 0.0.5 - Slightly adjusted the position and size of some of the buttons
#             within the panel.
#   - 0.0.4 - Refined code slightly.
#   - 0.0.3 - Added simple auto-naming functionality for the custom bone shape
#             as a temporary measure, takes the name of the armature adds on the
#             name of the bone and prefixes the name with the WGT- prefix, the
#             is done to the object data name minus the prefix, these names are
#             applied when the custom bone shape is snapped to the bone, via
#             Shape to Bone operator.
#   - 0.0.2 - Created armature panel props and integrated them with the panel
#             this allows for the visibility of several armature options within
#             the panel to be hidden, primarily for use of animation where many
#             of these options would no longer be needed.
#   - 0.0.1 - Created custom bone shape operator, this takes a bones custom
#             shape and aligns it to the bone, it also puts the custom shapes
#             draw type to wire and toggles on the show wire option specific to
#             the bone shape.
#   - 0.0.0 - Created armature data panel, refined button layout and placement
#             to offer the most options possible in the minimal space while
#             still maintaining a somewhat vague separation between related
#             options.
#
#   To do:
#   0.0
#   - 0.0.9 - Rewrite so that the custom shape object does not have to be on a
#             visible layer in order for it to be snapped to the bone.
#
#   0.1
#   - 0.1.0 - Create the object to bone operator, this should allow a object
#             currently selected within the 3D View to be snapped to a given
#             bone, try to add a offset value so that objects can be placed
#             along the length of the bone.
#   - 0.1.1 - Create a more refined draw wire operator, that will toggle the
#             draw type of any custom shape to wire/texture if there is
#             currently an assigned custom bone shape.
#   - 0.1.2 - Add a batch option for the Object to Bone operator, when using
#             it to snap bone custom shapes, will allow all custom shapes to be
#             snapped to selected pose bones.
#   - 0.1.3 - Add a global toggle option for Object to Bone, this will snap
#             all assigned custom shapes to all the bones within the current
#             armature.
#   - 0.1.4 - Create Bone List Panel, allow all bones within current selection
#             to be displayed within the panel, rename add-on and update
#             description to account for this feature.
#   - 0.1.5 - Add ability to display constraints for the selected bones within
#             the Bone List Panel.
#   - 0.1.6 - Add property group for Bone List Panel, allowing display of
#             constraints to be toggled off.
#   - 0.1.7 - Add Quick access bone options to be displayed below each bone in
#             bone list, add option to toggle their display via PropertyGroup.
#   - 0.1.8 - Add Constraint quick access options for the bone constraints
#             that are displayed within the bone list, add option to toggle
#             their display via PropertyGroup.
#   - 0.1.9 - Cleanup and optimize code
#
#   0.2
#   - 0.2.0 - Add Constraint Quick Naming Operator, will name based off
#             Constraint type, little auto-car as an option in the bone list
#             panel.
#
# ##### END VERSION BLOCK #####

  # PEP8 Compliant

###############
## OPERATORS ##
###############
  # Imports
from bpy.types import Operator
from mathutils import Matrix


  # Custom Shape to Bone (OT)
class POSE_OT_custom_shape_to_bone(Operator):
    """
    Align currently assigned custom bone shape on a visible scene layer to
    active pose bone.
    """
    bl_idname = 'pose.custom_shape_to_bone'
    bl_label = 'Align to Bone'
    bl_description = ("Align currently assigned custom bone shape on a visible "
                      "scene layer to this bone.")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """ Must have an active bone selected and be in pose mode. """
        return context.active_bone
        return context.mode in 'POSE'

    def execute(self, context):
        """ Execute the operator. """
        useGlobalUndo = context.user_preferences.edit.use_global_undo
       
        try:
            context.user_preferences.edit.use_global_undo = False
            customShapeToBone = bpy.context.window_manager.customShapeToBoneUI

            activeArmature = bpy.context.active_object
            activeBone = bpy.context.active_bone
            activePoseBone = activeArmature.pose.bones[activeBone.name]

            customShape = activePoseBone.custom_shape

            activeArmatureMatrix = activeArmature.matrix_world
            customShapeTransform = activePoseBone.custom_shape_transform

            if customShapeTransform:
                customShapeTransformMatrix = customShapeTransform.matrix
                targetMatrix = (activeArmatureMatrix *
                                customShapeTransformMatrix)
            else:
                activeBoneMatrix = activeBone.matrix_local
                targetMatrix = (activeArmatureMatrix * activeBoneMatrix)

            customShape.location = targetMatrix.to_translation()
            customShape.rotation_mode = 'XYZ'
            customShape.rotation_euler = targetMatrix.to_euler()

            targetScale = targetMatrix.to_scale()
            scaleAverage = ((targetScale[0] + targetScale[1] +
                             targetScale[2]) / 3)
            customShape.scale = ((activeBone.length * scaleAverage),
                                 (activeBone.length * scaleAverage),
                                 (activeBone.length * scaleAverage))
            if customShapeToBone.showWire:
                activeBone.show_wire = True
            else:
                pass

            if customShapeToBone.wireDrawType:
                customShape.draw_type = 'WIRE'
            else:
                pass

            if customShapeToBone.nameCustomShape:
                customShapeName = activeBone.name
                
                if customShapeToBone.addArmatureName:
                   customShapeName = (activeArmature.name +
                                      customShapeToBone.separateName +
                                      customShapeName)
                else:
                    pass
                
                customShape.name = (customShapeToBone.prefixShapeName +
                                    customShapeName)        
                
                if customShapeToBone.prefixShapeDataName:
                    customShape.data.name = (customShapeToBone.prefixShapeName +
                                             customShapeName)
                else:
                    customShape.data.name = customShapeName
            else:
                pass
        except (AttributeError, KeyError, TypeError):
            self.report({'WARNING'}, "Must assign a custom bone shape!")
        finally:
            context.user_preferences.edit.use_global_undo = useGlobalUndo
        
        return {'FINISHED'}

###############
## INTERFACE ##
###############
  # Imports
from bpy.types import PropertyGroup, Panel
from bpy.props import *


  # Armature Data PropertyGroup
class armatureData(PropertyGroup):
    """
    UI property group for the add-on "Armature Data Panel & Custom Bone Shapes"
    (space_view3d_armatureData.py)
    
    Options to adjust how the panel is displayed.
    
    bpy > types > WindowManager > armatureDataUI
    bpy > context > window_manager > armatureDataUI
    """
    displayMode = BoolProperty(name='Display Mode', description="Use this to hi"
                               "de many of the options below that are generally"
                               " needed while rigging. (Useful for animating.)",
                               default=False)
    deformOptions = BoolProperty(name='Deform Options', description="Display th"
                                 "e deform options for this bone.",
                                 default=False)
    shapeToBoneOptions = BoolProperty(name='Shape to Bone Options', description=
                                      "Display additional options for the custo"
                                      "m shape to bone operator.",
                                      default=False)
                                
class customShapeToBone(PropertyGroup):
    """
    UI property group for the add-on "Armature Data Panel & Custom Bone Shapes"
    (space_view3d_armatureData.py)
    
    Parameters for the custom shape to bone operator that effect how it will
    behave.
    
    bpy > types > WindowManager > customShapeToBone
    bpy > context > window_manager > customShapeToBone
    """

    showWire = BoolProperty(name='Draw Wire', description="Turn on the bones dr"
                            "aw wire option when the shape is aligned to the bo"
                            "ne (Bone is always drawn as a wire-frame regardles"
                            "s of the view-port draw mode.)", default=False)
    wireDrawType = BoolProperty(name='Wire Draw Type', description="Change the "
                                "custom shape object draw type to wire, when th"
                                "e shape is aligned to the bone.",
                                default=False)
    nameCustomShape = BoolProperty(name='Auto-Name', description="Automatically"
                                   " name and prefix the custom shape based on "
                                   "the bone it is assigned to.", default=False)
    prefixShapeName = StringProperty(name='Prefix', description="Use this prefi"
                                     "x when naming a custom bone shape. (Erase"
                                     " if you do not wish to prefix the name.)",
                                     default='WGT-')
    prefixShapeDataName = BoolProperty(name='Prefix Shape Data Name',
                                       description="Prefix the custom shape's o"
                                       "bject data name in addition to prefixin"
                                       "g the custom shapes name.",
                                       default=False)
    addArmatureName = BoolProperty(name='Include Armature Name', description="I"
                                  "nclude the armature name when renaming the c"
                                  "ustom shape.", default=False)
    separateName = StringProperty(name='Separator', description="Separate the n"
                                  "ame of the armature and the name of the bone"
                                  " with this character.", default='_')
    
    

  # Armature Data (PT)
class VIEW3D_PT_armature_data(Panel):  # TODO: Account for linked armatures.
    """ Armatur Data Panel. """
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Armature Data'

    @classmethod
    def poll(cls, context):
        """ Must be in either pose mode or armature edit mode. """
        return context.mode in {"POSE", "EDIT_ARMATURE"}

    def draw_header(self, context):
        """ Armature data panel header. """
        layout = self.layout
        armatureDataUIProps = context.window_manager.armatureDataUI

        layout.prop(armatureDataUIProps, "displayMode", text="")

    def draw(self, context):
        """ Armature data panel body. """
        layout = self.layout
        column = layout.column(align=True)
        
        armatureData = context.window_manager.armatureDataUI
        customShapeToBone = context.window_manager.customShapeToBoneUI

        activeArmature = context.active_object
        activeBone = context.active_bone
        activePoseBone = activeArmature.pose.bones[activeBone.name]

  # Armature Options
        if context.mode in 'POSE':
            row = column.row()
            row.prop(activeArmature.data, 'pose_position', expand=True)
            column = layout.column(align=True)
        else:
            pass

        column.prop(activeArmature.data, 'layers', text="")

        row = column.row()
        row.separator()

        row = column.row()
        row.label(icon='BLANK1')
        row.prop(activeArmature.data, 'draw_type', text="")

        row = column.row()
        row.prop(activeArmature.data, 'show_names', text="Names", toggle=True)
        row.prop(activeArmature.data, 'show_group_colors', text="Colors",
                 toggle=True)

        row = column.row()
        row.prop(activeArmature.data, 'show_axes', text="Axes", toggle=True)
        row.prop(activeArmature, 'show_x_ray', text="X-Ray", toggle=True)

        if context.mode in 'POSE':
            row = column.row()
            row.scale_y = 1.25
            row.prop(activeArmature.data, 'show_bone_custom_shapes',
                     text="Shapes", toggle=True)

            row = column.row()
            row.scale_y = 1.25
            row.prop(activeArmature.data, 'use_deform_delay',
                     text="Delay Refresh", toggle=True)
        else:
            pass

  # Bone Options
        if not armatureData.displayMode:
            column = layout.column(align=True)
            column.prop(activeBone, 'layers', text="")

            row = column.row()
            row.separator()

            row = column.row()
            row.label(icon='BLANK1')
            row.prop_search(activeBone, 'parent', activeArmature.data,
                            'edit_bones', text="")

            if context.mode in 'EDIT_ARMATURE':
                row = column.row()
                row.prop(activeBone, 'use_connect', toggle=True)

                row = column.row()
                row.prop(activeBone, 'use_local_location', text="Loc",
                         toggle=True)
                row.prop(activeBone, 'use_inherit_rotation', text="Rot",
                         toggle=True)
                row.prop(activeBone, 'use_inherit_scale', text="Scale",
                         toggle=True)
            else:
                pass

            if context.mode in 'POSE':
                row = column.row()
                row.prop_search(activePoseBone, 'bone_group',
                                activeArmature.pose, 'bone_groups', text="")
            else:
                pass

            column = layout.column(align=True)
            
            row = column.row()
            row.scale_y = 1.25
            if armatureData.deformOptions:
                ico = 'RADIOBUT_ON'
            else:
                ico = 'RADIOBUT_OFF'
            row.prop(armatureData, 'deformOptions', text="", icon=ico)
            row.prop(activeBone, 'use_deform', text="Deform:", toggle=True)
            if armatureData.deformOptions:
                box = layout.column(align=True).box().column(align=True)
                box.enabled = activeBone.use_deform
                
#                box = box.column(align=True)
#                box.label(text="Envelope:")
                
                box = box.column(align=True)
                box.prop(activeBone, 'envelope_distance', text="Distance")
                
                box = box.column(align=True)
                box.prop(activeBone, 'envelope_weight', text="Weight")
                
                box = box.column(align=True)
                box.prop(activeBone, 'use_envelope_multiply', text="Multiply",
                         toggle=True)
                         
#                box = box.column(align=True)
#                box.label(text="Radius:")
                
                box.separator()
                
                box = box.column(align=True)
                box.prop(activeBone, 'head_radius', text="Head")
                
                box = box.column(align=True)
                box.prop(activeBone, 'tail_radius', text="tail")
                
#                box = box.column(align=True)
#                box.label(text="Curved Bones:")
                
                box.separator()
                
                box = box.column(align=True)
                box.prop(activeBone, 'bbone_segments', text="Segments")
                
                box = box.column(align=True)
                box.prop(activeBone, 'bbone_in', text="Ease In")
                
                box = box.column(align=True)
                box.prop(activeBone, 'bbone_out', text="Ease Out")
            
            else:
                pass

# Custom Bone Shape
            if context.mode in 'POSE':
                column = layout.column(align=True)

                row = column.row()
                row.label(text="", icon='BLANK1')
                row.prop(activePoseBone, 'custom_shape', text="")

                row = column.row()
                row.prop_search(activePoseBone, 'custom_shape_transform',
                                activeArmature.pose, 'bones', text="")

                if activePoseBone.custom_shape:
                    row = column.row()
                    row.prop(activeBone, 'show_wire', toggle=True)
                    row.prop(activeBone, 'hide', toggle=True)
    
                    column = layout.column(align=True)
                    
                    row = column.row()
                    row.scale_y = 1.25
                    if armatureData.shapeToBoneOptions:
                        ico = 'RADIOBUT_ON'
                    else:
                        ico = 'RADIOBUT_OFF'
                    row.prop(armatureData, 'shapeToBoneOptions', text="",
                             icon=ico)
                    row.operator('pose.custom_shape_to_bone',
                                 text="Align to Bone")
                    if armatureData.shapeToBoneOptions:
                        column.prop(customShapeToBone, 'showWire', toggle=True)
                        column.prop(customShapeToBone, 'wireDrawType',
                                    toggle=True)
                        column.prop(customShapeToBone, 'nameCustomShape',
                                    toggle=True)
                        if customShapeToBone.nameCustomShape:
                            column.prop(customShapeToBone, 'prefixShapeName',
                                        text="")
                            column.prop(customShapeToBone,
                                        'prefixShapeDataName',
                                        toggle=True)
                            column.prop(customShapeToBone, 'addArmatureName',
                                        toggle=True)
                            if customShapeToBone.addArmatureName:
                                column.prop(customShapeToBone, 'separateName',
                                            text="")
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass



##############
## REGISTER ##
##############


  # Register
def register():
    """ Register """
    registerModule = bpy.utils.register_module
    windowManager = bpy.types.WindowManager
    pointerProperty = bpy.props.PointerProperty

    registerModule(__name__)
    windowManager.armatureDataUI = pointerProperty(type=armatureData)
    windowManager.customShapeToBoneUI = pointerProperty(type=customShapeToBone)
    
    armatureDataProps = bpy.context.window_manager.armatureDataUI
    customShapeToBoneProps = bpy.context.window_manager.customShapeToBoneUI
    armatureDataProps.name = "Armature Data Panel Properties"
    customShapeToBoneProps.name = 'Custom Shape to Bone Properties'


  # Unregister
def unregister():
    """ Unregister """
    unregisterModule = bpy.utils.unregister_module
    windowManager = bpy.types.WindowManager

    unregisterModule(__name__)
    try:
        del windowManager.armatureDataUI
        del windowManager.customShapeToBoneUI
    except:
        pass

if __name__ in '__main__':
    register()
