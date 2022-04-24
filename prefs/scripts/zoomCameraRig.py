# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

import maya.cmds as cmds

from autoTransformCounters import counterTranslate

'''
Creates a sub camera for selected camera that counters default zooming and
instead does a film zoom. This allows easily and intuitively focusing on how
an area will look on screen, WITHOUT changing the perspective of the final
shot.
'''
def createZoomCamRig(target_cams = None, panscale = 1.0):
    cur_panel = cmds.getPanel(underPointer=1)
    if not cur_panel:
        cur_panel = cmds.getPanel(withFocus=1)

    if not target_cams:
        target_cams = cmds.ls(sl=1, typ="camera")
    if not target_cams:
        cur_cam = cmds.modelPanel(cur_panel, q=1, cam=1)
        if cur_cam:
            target_cams = [cur_cam]

    new_cams = []
    for cur_cam in target_cams:
        cam_name = cur_cam.split("|")[-1]

        zoom_cam = cmds.duplicate(cur_cam, n=cam_name+"_zoom")[0]
        zoom_cam = cmds.parent(zoom_cam, cur_cam)[0]
        zoom_cam_shape = cmds.listRelatives(zoom_cam, s=1)[0]
        zoom_cam = counterTranslate(zoom_cam, maintainOffsets=False, addOffsets=False, addBlends=False)[0]

        cmds.setAttr(zoom_cam+'.tx', lock=0)
        cmds.setAttr(zoom_cam+'.ty', lock=0)
        cmds.setAttr(zoom_cam+'.tz', lock=0)
        cmds.setAttr(zoom_cam+'.centerOfInterest', lock=0)
        cmds.setAttr(zoom_cam+'.rx', lock=1)
        cmds.setAttr(zoom_cam+'.ry', lock=1)
        cmds.setAttr(zoom_cam+'.rz', lock=1)
        cmds.setAttr(zoom_cam+".tz", -1.0)
        cmds.transformLimits(zoom_cam, tz=(-2.0, -1.0), etz=(0,1))
        
        coi_control = cmds.shadingNode("multDoubleLinear", asUtility=1)
        cmds.connectAttr(zoom_cam+".translateZ", coi_control+".input1")
        cmds.connectAttr(zoom_cam+".translateZ", coi_control+".input2")
        cmds.connectAttr(coi_control+".output", zoom_cam_shape+".centerOfInterest")

        mul_zoom = cmds.shadingNode("multiplyDivide", asUtility=1)
        cmds.connectAttr(zoom_cam+".translate", mul_zoom+".input1")
        cmds.setAttr(mul_zoom+".input2", panscale, panscale, -1.0)
        
        cmds.connectAttr(mul_zoom+".outputX", zoom_cam_shape+".filmTranslateH")
        cmds.connectAttr(mul_zoom+".outputY", zoom_cam_shape+".filmTranslateV")
        cmds.connectAttr(mul_zoom+".outputZ", zoom_cam_shape+".postScale")

        cur_cam = cmds.modelPanel(cur_panel, e=1, cam=zoom_cam)

        new_cams.append(zoom_cam)

    return new_cams
