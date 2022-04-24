# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

import maya.cmds as cmds

''' Variety of functions designed to be bound to hotkeys for quick and easy environment control. '''

'''
Change axis orientation of transformation tools. This allows easy switching
between transforming along object, parent, or world transforms. Context aware
between rotation, translation, and scaling tools.
dir=1 to iterate forward, dir=-1 to iterate backwards.
'''
def iterAxisOrientation(dir):
    ctx = cmds.currentCtx()
    object_mode = not cmds.ls(hl=True)

    if ctx == 'moveSuperContext':
        tool = 'Move'
        mode = cmds.manipMoveContext(tool, q=1, m=1)
        ordering = [2,1,0]
        if not object_mode:
            ordering = [2,0,10]
        cmds.manipMoveContext(tool, e=1, m=iter_ordering(ordering, mode, dir))

    if ctx == 'RotateSuperContext':
        tool = 'Rotate'
        mode = cmds.manipRotateContext(tool, q=1, m=1)
        ordering = [1,0,2]
        if not object_mode:
            ordering = [1,0,10]

        cmds.manipRotateContext(tool, e=1, m=iter_ordering(ordering, mode, dir))

    if ctx == 'scaleSuperContext':
        tool = 'Scale'
        mode = cmds.manipScaleContext(tool, q=1, m=1)
        ordering = [2,1,0]
        if not object_mode:
            ordering = [2,0,10]
        cmds.manipScaleContext(tool, e=1, m=iter_ordering(ordering, mode, dir))

'''
Iterate between object view modes. Allows multiple view modes to be accessible
under a single hotkey.
dir=1 to iterate forward, dir=-1 to iterate backwards.
'''
def iterViewDisplayMode(dir):
    cur_panel = cmds.getPanel(wf=1)
    if (cmds.getPanel(to=cur_panel) == "modelPanel"):
        ordering = [("smoothShaded", "default", False),
                    ("smoothShaded", "default", True),
                    ("smoothShaded", "all", True),
                    ("smoothShaded", "none", False),
                    ("wireframe", "default", False)]

        cur_ordering = (cmds.modelEditor(cur_panel, q=1, da=1),
                        cmds.modelEditor(cur_panel, q=1, dl=1),
                        cmds.modelEditor(cur_panel, q=1, dtx=1))

        new_ordering = iter_ordering(ordering, cur_ordering, dir)
        cmds.modelEditor(cur_panel, e=1, da=new_ordering[0], dl=new_ordering[1], dtx=new_ordering[2])

''' Toggles between smoothing levels '''
def iterDisplaySmoothness(dir=None): #Currently this is a toggle
    #ordering = [(0,0,4,1,1),(1,1,8,2,2),(3,3,16,4,3)]
    ordering = [(0,0,4,1,1),(3,3,16,4,3)]

    cur_divisions = cmds.displaySmoothness(q=1, polygonObject=1)

    if cur_divisions:
        cur_divisions = min(cur_divisions)
        #new_settings = ordering[cur_divisions%3]
        new_settings = ordering[1 if cur_divisions==3 else 0]

        cmds.displaySmoothness(divisionsU=new_settings[0],
                               divisionsV=new_settings[1],
                               pointsWire=new_settings[2],
                               pointsShaded=new_settings[3],
                               polygonObject=new_settings[4])

''' Iterates between graph editor view modes (absolute, stacked, normalized) '''
def iterGraphEditorView(dir):
    ordering = [(False, False),
                (True, True),
                (True, False)]

    cur_mode = (cmds.animCurveEditor("graphEditor1GraphEd", q=1, dn=1),
                cmds.animCurveEditor("graphEditor1GraphEd", q=1, sc=1))

    new_mode = iter_ordering(ordering, cur_mode, dir)
    cmds.animCurveEditor("graphEditor1GraphEd", e=1, dn=new_mode[0], sc=new_mode[1])

''' Toggle visibility of nurbs objects, motion trails, and locators '''
def toggleCurves():
    cur_panel = cmds.getPanel(wf=1)

    toggle = not cmds.modelEditor(cur_panel, q=1, nurbsCurves=1)
    cmds.modelEditor(cur_panel, e=1, nurbsCurves=toggle, nurbsSurfaces=toggle, motionTrails=toggle, locators=toggle)

##
## INTERNAL
##

def iter_ordering(ordering, m, dir):
    if m not in ordering:
        return ordering[0]
    n = len(ordering)
    return ordering[(ordering.index(m) + dir) % n]
