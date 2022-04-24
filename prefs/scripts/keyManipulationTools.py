# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

import maya.cmds as cmds

'''
Smart setkey function. Creates keys for selected attribute *CURVES* in graph
editor, if any such curves selected. Otherwise, keys selected attribute in
world editor. If all else fails, keyall keyable attributes.
'''
def setKey()
    objs = cmds.ls(sl=1)
    attrs = None
    cvs = cmds.keyframe(q=1, sl=1, n=1)
    if not cvs:
        attrs = cmds.channelBox("mainChannelBox", q=1, sma=1)
        if not attrs:
            cvs = cmds.keyframe(q=1, n=1)
            if not cvs:
                cvs = cmds.keyframe(objs, q=1, n=1)

    if cvs:
        for cv in cvs:
            cmds.setKeyframe(cv, v=cmds.keyframe(cv, q=1, eval=1)[0])
    elif attrs:
        for obj in objs:
            for attr in attrs:
                if cmds.attributeQuery(attr, node=obj, ex=1) and cmds.getAttr(obj+"."+attr, se=1):
                    cmds.setKeyframe(obj+"."+attr)
    else:
        # Keyall fallthrough
        for obj in objs:
            for attr in cmds.listAttr(obj, k=1, se=1):
                cmds.setKeyframe(obj+"."+attr)
