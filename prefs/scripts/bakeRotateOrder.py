# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.
'''
Tool to change the rotation order value without changing either the current
world rotation OR the world rotation of any rotation keys. Note that this
requires a certain degree of baking (using 'smart' bake), so that single
channel keys will necessarily become 3 channel keys (ie rx, ry, rz). In
addition, tangent behaviour may be difficult to gaurantee.
'''

import maya.cmds as cmds
from queryMousePosition import queryMousePosition

rotateOrderList = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']

''' UI tool to select new rotation order and run the script '''
def bakeRotateOrderTool():
    mpos = queryMousePosition()
    window = cmds.window(te=mpos[0]-18, le=mpos[1]-118, tb=False, title="Bake Rotate Order", w=150)
    #cmds.rowLayout(numberOfColumns=2)

    def closeAction(*args):
        cmds.deleteUI(window, window=1)
    def bakeAction(ro):
        if ro in rotateOrderList:
            roi = rotateOrderList.index(ro)
            cmds.deleteUI(window, window=1)
            bakeRotateOrder(roi)

    cmds.columnLayout(cat=("both",0), adj=1)
    menu = cmds.optionMenu(label="Rotate Order", cc=bakeAction)

    cmds.menuItem(label="---")
    for ro in rotateOrderList:
        cmds.menuItem(label=ro)

    cmds.button(label="Cancel", c=closeAction)

    cmds.showWindow( window )

''' Actual script to change the rotation order '''
def bakeRotateOrder(new_rotate_order, *args):
    objs = cmds.ls(sl=1) if not args else args

    cur_time = cmds.currentTime(q=1)
    time_range = (cmds.playbackOptions(q=1, min=1), cmds.playbackOptions(q=1, max=1))

    for obj in objs:
        if cmds.getAttr(obj + ".rotateOrder", se=1):
            prnt = cmds.listRelatives(obj, p=1, f=1)
            skip_rot = [r for r in "xyz" if not cmds.getAttr(obj + ".r" + r, se=1)]
            target_rot = ["r" + r for r in "xyz" if r not in skip_rot]

            loc = cmds.spaceLocator()[0]
            if prnt:
                loc = cmds.parent(loc, prnt, r=1)[0]

            cmds.setAttr(loc + ".rotateOrder", new_rotate_order)
            orient_constraint1 = cmds.orientConstraint(obj, loc)
            cmds.bakeResults(loc, at=["rx", "ry", "rz"], t=time_range, sm=1, smart=1, dic=1)

            cmds.cutKey(obj, at=target_rot, cl=1)
            cmds.setAttr(obj + ".rotateOrder", new_rotate_order)
            orient_constraint2 = cmds.orientConstraint(loc, obj, sk = skip_rot)

            cmds.bakeResults(obj, at=target_rot, t=time_range, sm=1, smart=1, dic=1)
            cmds.delete(loc)
        else:
            print "Error: Rotate order attribute on object", obj, "is not setable"

    cmds.currentTime(cur_time)
    cmds.select(objs)
