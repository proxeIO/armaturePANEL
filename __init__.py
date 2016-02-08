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

# ##### BEGIN INFO BLOCK #####
#
#    Author: Trentin Frederick (a.k.a, proxe)
#    Contact: trentin.shaun.frederick@gmail.com
#    Version: 0.0.8
#
# ##### END INFO BLOCK #####

# blender info
bl_info = {
  'name': 'Armature Data Panel',
  'author': 'proxe',
  'version': (0, 0, 8),
  'blender': (2, 66, 0),
  'location': '3D View > Properties Panel',
  'warning': 'Work in Progress',
  #'wiki_url': '',
  #'tracker_url': '',
  'description': 'Quickly access many of the most commonly used armature options within the 3D View',
  'category': 'Rigging'
}

# Imports
import bpy
from bpy.types import Operator
from mathutils import Matrix
from bpy.types import PropertyGroup, Panel
from bpy.props import *

# Custom Shape to Bone (OT)
class POSE_OT_custom_shape_to_bone(Operator):
  '''
    Align currently assigned custom bone shape on a visible scene layer to active pose bone.
  '''
  bl_idname = 'pose.custom_shape_to_bone'
  bl_label = 'Align to Bone'
  bl_description = 'Align currently assigned custom bone shape on a visible scene layer to this bone.'
  bl_options = {'REGISTER', 'UNDO'}

  @classmethod
  def poll(cls, context):
    '''
      Must have an active bone selected and be in pose mode.
    '''
    return context.active_bone
    return context.mode in 'POSE'

  def execute(self, context):
    '''
      Execute the operator.
    '''

    # use global undo
    useGlobalUndo = context.user_preferences.edit.use_global_undo

    # try
    try:

      # use global undo
      context.user_preferences.edit.use_global_undo = False

      # custom shape to bone
      customShapeToBone = bpy.context.window_manager.customShapeToBoneUI

      # active armature
      activeArmature = bpy.context.active_object

      # active bone
      activeBone = bpy.context.active_bone

      # active pose bone
      activePoseBone = activeArmature.pose.bones[activeBone.name]

      # custom shape
      customShape = activePoseBone.custom_shape

      # active armature matrix
      activeArmatureMatrix = activeArmature.matrix_world

      # custom shape transform
      customShapeTransform = activePoseBone.custom_shape_transform
      if customShapeTransform:

        # custom shape transform matrix
        customShapeTransformMatrix = customShapeTransform.matrix

        # target matrix
        targetMatrix = activeArmatureMatrix * customShapeTransformMatrix
      else:

        # active bone matrix
        activeBoneMatrix = activeBone.matrix_local

        # target matrix
        targetMatrix = activeArmatureMatrix * activeBoneMatrix

      # location
      customShape.location = targetMatrix.to_translation()

      # rotation mode
      customShape.rotation_mode = 'XYZ'

      # rotation euler
      customShape.rotation_euler = targetMatrix.to_euler()

      # target scale
      targetScale = targetMatrix.to_scale()

      # scale average
      scaleAverage = (targetScale[0] + targetScale[1] + targetScale[2]) / 3

      # scale
      customShape.scale = ((activeBone.length * scaleAverage), (activeBone.length * scaleAverage), (activeBone.length * scaleAverage))

      # show wire
      if customShapeToBone.showWire:
        activeBone.show_wire = True

      # wire draw type
      if customShapeToBone.wireDrawType:
        customShape.draw_type = 'WIRE'

      # name custom shape
      if customShapeToBone.nameCustomShape:
        customShapeName = activeBone.name

        # add armature name
        if customShapeToBone.addArmatureName:
         customShapeName = activeArmature.name + customShapeToBone.separateName + customShapeName

        # assign name
        customShape.name = customShapeToBone.prefixShapeName + customShapeName

        # prefix shape data name
        if customShapeToBone.prefixShapeDataName:
          customShape.data.name = customShapeToBone.prefixShapeName + customShapeName
        else:
          customShape.data.name = customShapeName

    # exception
    except (AttributeError, KeyError, TypeError):

      # report
      self.report({'WARNING'}, 'Must assign a custom bone shape!')
    finally:

      # use global undo
      context.user_preferences.edit.use_global_undo = useGlobalUndo

    return {'FINISHED'}

# Armature Data PropertyGroup
class armatureData(PropertyGroup):
  '''
    Armature Data Panel property group
  '''

  # display mode
  displayMode = BoolProperty(
    name = 'Display Mode',
    description = 'Use this to hide many of the options below that are generally needed while rigging. (Useful for animating.)',
    default=False
  )

  # deform options
  deformOptions = BoolProperty(
    name = 'Deform Options',
    description = 'Display the deform options for this bone.',
    default = False
  )

  # shape to bone options
  shapeToBoneOptions = BoolProperty(
    name = 'Shape to Bone Options',
    description = 'Display additional options for the custom shape to bone operator.',
    default = False
  )

# custom shape to bone
class customShapeToBone(PropertyGroup):
  '''
    Custom Shape to Bone property group.
  '''

  # show wire
  showWire = BoolProperty(
    name='Draw Wire',
    description='Turn on the bones draw wire option when the shape is aligned to the bone (Bone is always drawn as a wire-frame regardless of the view-port draw mode.)',
    default=False
  )

  # wire draw type
  wireDrawType = BoolProperty(
    name='Wire Draw Type',
    description='Change the custom shape object draw type to wire, when the shape is aligned to the bone.',
    default=False
  )

  # name custom shape
  nameCustomShape = BoolProperty(
    name='Auto-Name',
    description='Automatically name and prefix the custom shape based on the bone it is assigned to.',
    default=False
  )

  # prefix shape name
  prefixShapeName = StringProperty(
    name='Prefix',
    description='Use this prefix when naming a custom bone shape. (Erase if you do not wish to prefix the name.)',
    default='WGT-'
  )

  # prefix shape data name
  prefixShapeDataName = BoolProperty(
    name='Prefix Shape Data Name',
    description='Prefix the custom shape\'s object data name in addition to prefixing the custom shapes name.',
    default=False
  )

  # add armature name
  addArmatureName = BoolProperty(
    name='Include Armature Name',
    description='Include the armature name when renaming the custom shape.',
    default=False
  )

  # seperate name
  separateName = StringProperty(
    name='Separator',
    description='Separate the name of the armature and the name of the bone with this character.',
    default='_'
  )

# Armature Data (PT)
class VIEW3D_PT_armature_data(Panel):  # TODO: Account for linked armatures.
  '''
    Armatur Data Panel.
  '''
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_label = 'Armature Data'

  # class method
  @classmethod
  def poll(cls, context):
    '''
      Must be in either pose mode or armature edit mode.
    '''

    # context mode in pose or edit
    return context.mode in {'POSE', 'EDIT_ARMATURE'}

  # draw header
  def draw_header(self, context):
    '''
      Armature data panel header.
    '''

    # layout
    layout = self.layout

    # armature data ui props
    armatureDataUIProps = context.window_manager.armatureDataUI

    # display mode
    layout.prop(armatureDataUIProps, 'displayMode', text='')

  # draw
  def draw(self, context):
    '''
      Armature data panel body.
    '''

    # layout
    layout = self.layout

    # column
    column = layout.column(align=True)

    # armature data
    armatureData = context.window_manager.armatureDataUI

    # custom shape to bone
    customShapeToBone = context.window_manager.customShapeToBoneUI

    # active armature
    activeArmature = context.active_object

    # active bone
    activeBone = context.active_bone

    # active pose bone
    activePoseBone = activeArmature.pose.bones[activeBone.name]

    # pose mode
    if context.mode in 'POSE':

      # row
      row = column.row(align=True)

      # pose position
      row.prop(activeArmature.data, 'pose_position', expand=True)

      # column
      column = layout.column(align=True)

    # layers
    column.prop(activeArmature.data, 'layers', text='')

    # row
    row = column.row()

    # separator
    row.separator()

    # row
    row = column.row(align=True)

    # label
    row.label(icon='BLANK1')

    # draw type
    row.prop(activeArmature.data, 'draw_type', text='')

    # row
    row = column.row(align=True)

    # show names
    row.prop(activeArmature.data, 'show_names', text='Names', toggle=True)

    # show group colors
    row.prop(activeArmature.data, 'show_group_colors', text='Colors', toggle=True)

    # row
    row = column.row(align=True)

    # show axes
    row.prop(activeArmature.data, 'show_axes', text='Axes', toggle=True)

    # show x-ray
    row.prop(activeArmature, 'show_x_ray', text='X-Ray', toggle=True)

    # pose mode
    if context.mode in 'POSE':

      # row
      row = column.row(align=True)

      # scale
      row.scale_y = 1.25

      # show bone custom shapes
      row.prop(activeArmature.data, 'show_bone_custom_shapes', text='Shapes', toggle=True)

      # row
      row = column.row(align=True)

      # scale
      row.scale_y = 1.25

      # use deform layer
      row.prop(activeArmature.data, 'use_deform_delay', text='Delay Refresh', toggle=True)

    # not display mode
    if not armatureData.displayMode:

      # column
      column = layout.column(align=True)

      # layers
      column.prop(activeBone, 'layers', text='')

      # row
      row = column.row()

      # separator
      row.separator()

      # row
      row = column.row(align=True)

      # label
      row.label(icon='BLANK1')

      # parent
      row.prop_search(activeBone, 'parent', activeArmature.data, 'edit_bones', text='')

      # edit mode
      if context.mode in 'EDIT_ARMATURE':

        # row
        row = column.row(align=True)

        # use connect
        row.prop(activeBone, 'use_connect', toggle=True)

        # row
        row = column.row(align=True)

        # use local location
        row.prop(activeBone, 'use_local_location', text='Loc', toggle=True)

        # use inherit rotation
        row.prop(activeBone, 'use_inherit_rotation', text='Rot', toggle=True)

        # use inherit scale
        row.prop(activeBone, 'use_inherit_scale', text='Scale', toggle=True)

      # pose mode
      if context.mode in 'POSE':

        # row
        row = column.row(align=True)

        # bone group search
        row.prop_search(activePoseBone, 'bone_group', activeArmature.pose, 'bone_groups', text='')

      # column
      column = layout.column(align=True)

      # row
      row = column.row(align=True)

      # scale
      row.scale_y = 1.25

      # deform option
      if armatureData.deformOptions:

        # icon
        icon = 'RADIOBUT_ON'
      else:

        # icon
        icon = 'RADIOBUT_OFF'

      # deform options
      row.prop(armatureData, 'deformOptions', text='', icon=icon)

      # use deform
      row.prop(activeBone, 'use_deform', text='Deform:', toggle=True)

      # deform options
      if armatureData.deformOptions:

        # box
        box = layout.column(align=True).box().column(align=True)

        # active
        box.active = activeBone.use_deform

        # box
        box = box.column(align=True)

        # envelope distance
        box.prop(activeBone, 'envelope_distance', text='Distance')

        # box
        box = box.column(align=True)

        # envelope weight
        box.prop(activeBone, 'envelope_weight', text='Weight')

        # box
        box = box.column(align=True)

        # box
        box.prop(activeBone, 'use_envelope_multiply', text='Multiply', toggle=True)

        # separator
        box.separator()

        # box
        box = box.column(align=True)

        # head radius
        box.prop(activeBone, 'head_radius', text='Head')

        # box
        box = box.column(align=True)

        # tail radius
        box.prop(activeBone, 'tail_radius', text='tail')

        # separator
        box.separator()

        # box
        box = box.column(align=True)

        # bbone segments
        box.prop(activeBone, 'bbone_segments', text='Segments')

        # box
        box = box.column(align=True)

        # bbone in
        box.prop(activeBone, 'bbone_in', text='Ease In')

        # box
        box = box.column(align=True)

        # bbone out
        box.prop(activeBone, 'bbone_out', text='Ease Out')

      # pose mode
      if context.mode in 'POSE':

        # column
        column = layout.column(align=True)

        # row
        row = column.row(align=True)

        # label
        row.label(text='', icon='BLANK1')

        # custom shape
        row.prop(activePoseBone, 'custom_shape', text='')

        # row
        row = column.row(align=True)

        # custom shape transform
        row.prop_search(activePoseBone, 'custom_shape_transform', activeArmature.pose, 'bones', text='')

        # custom shape
        if activePoseBone.custom_shape:

          # row
          row = column.row(align=True)

          # show wire
          row.prop(activeBone, 'show_wire', toggle=True)

          # hide
          row.prop(activeBone, 'hide', toggle=True)

          # column
          column = layout.column(align=True)

          # row
          row = column.row(align=True)

          # scale
          row.scale_y = 1.25

          # shape to bone options
          if armatureData.shapeToBoneOptions:

            # icon
            icon = 'RADIOBUT_ON'
          else:

            # icon
            icon = 'RADIOBUT_OFF'

          # shape to bone options
          row.prop(armatureData, 'shapeToBoneOptions', text='', icon=icon)

          # custom shape to bone
          row.operator('pose.custom_shape_to_bone', text='Align to Bone')

          # shape to bone options
          if armatureData.shapeToBoneOptions:

            # show wire
            column.prop(customShapeToBone, 'showWire', toggle=True)

            # wire draw type
            column.prop(customShapeToBone, 'wireDrawType', toggle=True)

            # name custom shape
            column.prop(customShapeToBone, 'nameCustomShape', toggle=True)

            # name custom shape
            if customShapeToBone.nameCustomShape:

              # prefi shape name
              column.prop(customShapeToBone, 'prefixShapeName', text='')

              # prefix shape data name
              column.prop(customShapeToBone, 'prefixShapeDataName', toggle=True)

              # add armature name
              column.prop(customShapeToBone, 'addArmatureName', toggle=True)

              # add armature name
              if customShapeToBone.addArmatureName:

                # separate name
                column.prop(customShapeToBone, 'separateName', text='')

# Register
def register():
  '''
    Register
  '''

  # register module
  registerModule = bpy.utils.register_module

  # window manager
  windowManager = bpy.types.WindowManager

  # pointer property
  pointerProperty = bpy.props.PointerProperty

  # register
  registerModule(__name__)

  # armature data ui pointer property
  windowManager.armatureDataUI = pointerProperty(type=armatureData)

  # custom shape to bone ui pointer property
  windowManager.customShapeToBoneUI = pointerProperty(type=customShapeToBone)

  # Unregister
def unregister():
  '''
    Unregister
  '''

  # unregister module
  unregisterModule = bpy.utils.unregister_module

  # window manager
  windowManager = bpy.types.WindowManager

  # unregister
  unregisterModule(__name__)

  # try
  try:

    # delete armature data ui
    del windowManager.armatureDataUI

    # delete custom shape to bone ui
    del windowManager.customShapeToBoneUI

  # except
  except:
    pass

if __name__ in '__main__':
  register()
