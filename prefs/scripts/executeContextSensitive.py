# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

import maya.cmds as cmds

'''
Helper function. Takes functions as arguments, executes modelPanel if the model
panel (3d world view) is visible, graphEditor if the graph (animation curve)
editor is visible, and default otherwise.
If arguments are ommited their case will be skipped.
'''
def executeContextSensitive(default=None, modelPanel=None, graphEditor=None):
    cur_panel = cmds.getPanel(wf=1)
    if modelPanel and cmds.getPanel(to=cur_panel) == "modelPanel":
        modelPanel()
    elif graphEditor and cur_panel.rstrip("0123456789") == "graphEditor":
        graphEditor()
    elif default:
        default()
