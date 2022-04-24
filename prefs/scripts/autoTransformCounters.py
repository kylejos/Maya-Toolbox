# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

import maya.cmds as cmds

''' Counters roation, but not translation. See CounterTransform for additional arguments. '''
def counterRotate(*args, **kwargs):
    kwargs["rotation"] = True
    kwargs["translation"] = False
    return counterTransform(*args, **kwargs)

''' Counters translation, but not rotation. See CounterTransform for additional arguments. '''
def counterTranslate(*args, **kwargs):
    kwargs["rotation"] = False
    kwargs["translation"] = True
    return counterTransform(*args, **kwargs)

'''
Creates a rig that "Counters" specific transformation attributes.

Arguments:
    rotation=[bool] - Whether or not to counter rotation transformations (default True)
    translation=[bool] - Whether or not to counter translation transformations (default True)
    addOffsets=[bool] - Whether to add offset attributes to control node. (default False)
    maintainOffsets=[bool] - Whether to maintain current offsets between object and parent.
        Setting the value to True forces maintainOffsets to be True. Default is to match addOffsets' value.
    addBlends=[bool] - Whether or not to add blend nodes. Doing so allows scaling or altering the degree of countering. (default True)
    hideUtilityNodes=[bool] - Whether or not to hide utility nodes from the attribute editor.
        Done by setting .isHistoricallyInteresting to false. (defualt True)
'''
def counterTransform(*args, **kwargs):
    objs = cmds.ls(sl=1) if not args else args
    rotation = kwargs.pop("rotation", True)
    translation = kwargs.pop("translation", True)
    addBlends = kwargs.pop("addBlends", True)
    hideUtilityNodes = kwargs.pop("hideUtilityNodes", True)
    if "addOffsets" in kwargs and "maintainOffsets" not in kwargs:
        addOffsets = kwargs.pop("addOffsets")
        maintainOffsets = addOffsets
    else:
        maintainOffsets = kwargs.pop("maintainOffsets", True)
        addOffsets = kwargs.pop("addOffsets", False) or maintainOffsets

    if kwargs:
        raise TypeError("Invalid flag %s" % kwargs.keys()[0])

    if not (rotation or translation):
        raise ValueError("Need to specify at least one of rotation or translation")

    new_objs = [] # New paths of input objects
    for obj in objs:
        prnt = cmds.listRelatives(obj, p=1, f=1)

        ctrl_nd = None
        if addBlends or addOffsets:
            # Dummy node to hold control channels
            ctrl_nd = cmds.createNode("network", n="counterTransform1")
            cmds.addAttr(ctrl_nd, ln="historyConnection", at="message", k=0, h=1)
            cmds.connectAttr(obj + ".msg", ctrl_nd + ".historyConnection")

            if translation:
                if addBlends:
                    cmds.addAttr(ctrl_nd, ln="translateCounterBlend", sn="tb", at="double", min=0, max=1, dv=1, k=1, h=0)
                if addOffsets:
                    cmds.addAttr(ctrl_nd, ln="translateOffset", sn="to", at="double3", k=1, h=0)
                    cmds.addAttr(ctrl_nd, ln="translateOffsetX", sn="tox", p="translateOffset", at="double", k=1, h=0)
                    cmds.addAttr(ctrl_nd, ln="translateOffsetY", sn="toy", p="translateOffset", at="double", k=1, h=0)
                    cmds.addAttr(ctrl_nd, ln="translateOffsetZ", sn="toz", p="translateOffset", at="double", k=1, h=0)
                    if maintainOffsets:
                        vs = cmds.getAttr(obj + ".translate")[0]
                        if rotation:
                            vs = [sum(v) for v in zip(vs, cmds.getAttr(obj + ".rotatePivot")[0],
                                                      cmds.getAttr(obj + ".rotatePivotTranslate")[0])]
                        cmds.setAttr(ctrl_nd + ".to", *vs)
            if rotation:
                if addBlends:
                    cmds.addAttr(ctrl_nd, ln="rotateCounterBlend", sn="rb", at="double", min=0, max=1, dv=1, k=1, h=0)
                if addOffsets:
                    cmds.addAttr(ctrl_nd, ln="rotateOffset", sn="ro", at="double3", k=1, h=0)
                    cmds.addAttr(ctrl_nd, ln="rotateOffsetX", sn="rox", p="rotateOffset", at="doubleAngle", k=1, h=0)
                    cmds.addAttr(ctrl_nd, ln="rotateOffsetY", sn="roy", p="rotateOffset", at="doubleAngle", k=1, h=0)
                    cmds.addAttr(ctrl_nd, ln="rotateOffsetZ", sn="roz", p="rotateOffset", at="doubleAngle", k=1, h=0)
                    if maintainOffsets:
                        cmds.setAttr(ctrl_nd + ".ro", *(cmds.getAttr(obj + ".rotate")[0]))

        # Group to maintain offsets
        offset_grp = None
        if addOffsets and rotation:
            if prnt:
                offset_grp = cmds.group(em=1, p=prnt[0])
            else:
                offset_grp = cmds.group(em=1, w=1)

            if translation:
                cmds.connectAttr(ctrl_nd + ".to", offset_grp + ".translate")
            if rotation:
                cmds.connectAttr(ctrl_nd + ".ro", offset_grp + ".rotate")

        # Group to do the countering
        pvt_grp = None
        if offset_grp:
            pvt_grp = cmds.group(em=1, p=offset_grp)
        elif prnt:
            pvt_grp = cmds.group(em=1, p=prnt[0])
        else:
            pvt_grp = cmds.group(em=1, w=1)

        cmds.setAttr(pvt_grp + ".scale", l=1, k=0, cb=0)
        cmds.setAttr(pvt_grp + ".scaleX", l=1, k=0, cb=0)
        cmds.setAttr(pvt_grp + ".scaleY", l=1, k=0, cb=0)
        cmds.setAttr(pvt_grp + ".scaleZ", l=1, k=0, cb=0)

        utilityNodes = []

        if rotation:
            # Addition node to account for pivot values
            plusNode = cmds.shadingNode("plusMinusAverage", asUtility=1)
            utilityNodes.append(plusNode)
            cmds.setAttr(plusNode + ".operation", 1) # Make sure set to sum
            cmds.connectAttr(obj + ".translate", plusNode + ".i3[0]")
            cmds.connectAttr(obj + ".rotatePivot", plusNode + ".i3[1]")
            cmds.connectAttr(obj + ".rotatePivotTranslate", plusNode + ".i3[2]")
            cmds.connectAttr(plusNode + ".o3", pvt_grp + ".rotatePivot")
            cmds.connectAttr(plusNode + ".o3", pvt_grp + ".scalePivot")
            if addOffsets and not translation:
                cmds.connectAttr(plusNode + ".o3", offset_grp + ".translate")

        # Subtraction node to invert translation values
        subNode = cmds.shadingNode("plusMinusAverage", asUtility=1)
        utilityNodes.append(subNode)
        cmds.setAttr(subNode + ".operation", 2) # Set to subtract
        if rotation:
            cmds.connectAttr(obj + ".transMinusRotatePivot", subNode + ".i3[0]")
        else:
            cmds.setAttr(subNode + ".i3[0]", 0, 0, 0)
        cmds.connectAttr(obj + ".translate", subNode + ".i3[1]")

        outputAttr = subNode + ".o3"
        if translation:
            if addBlends:
                blendNode = cmds.shadingNode("multiplyDivide", asUtility=1)
                utilityNodes.append(blendNode)
                cmds.setAttr(blendNode + ".operation", 1) # Make sure set to multiply
                cmds.connectAttr(outputAttr, blendNode + ".input1")
                cmds.connectAttr(ctrl_nd + ".tb", blendNode + ".input2X")
                cmds.connectAttr(ctrl_nd + ".tb", blendNode + ".input2Y")
                cmds.connectAttr(ctrl_nd + ".tb", blendNode + ".input2Z")
                outputAttr = blendNode + ".output"

            if addOffsets and not rotation:
                offsetNode = cmds.shadingNode("plusMinusAverage", asUtility=1)
                utilityNodes.append(offsetNode)
                cmds.setAttr(offsetNode + ".operation", 1) # Make sure set to sum
                cmds.connectAttr(outputAttr, offsetNode + ".i3[0]")
                cmds.connectAttr(ctrl_nd + ".to", offsetNode + ".i3[1]")
                outputAttr = offsetNode + ".o3"

        cmds.connectAttr(outputAttr, pvt_grp + ".translate")

        if rotation:
            # Choice node to select reverse rotate order
            choiceNode = cmds.shadingNode("choice", asUtility=1)
            utilityNodes.append(choiceNode)
            for (a,b) in ((5, 0), (3, 1), (4, 2)): # Mapping for ro reversal
                cmds.setAttr(choiceNode + ".i[%d]" % a, b)
                cmds.setAttr(choiceNode + ".i[%d]" % b, a)
            cmds.connectAttr(obj + ".rotateOrder", choiceNode + ".s")
            cmds.connectAttr(choiceNode + ".o", pvt_grp + ".rotateOrder")

            # Multiplication node to invert rotation values
            multNode = cmds.shadingNode("multiplyDivide", asUtility=1)
            utilityNodes.append(multNode)
            cmds.setAttr(multNode + ".operation", 1) # Make sure set to multiply
            cmds.connectAttr(obj + ".rotate", multNode + ".input1")
            cmds.setAttr(multNode + ".input2", -1.0, -1.0, -1.0)

            outputAttr = multNode + ".output"
            if addBlends:
                blendNode = cmds.shadingNode("multiplyDivide", asUtility=1)
                utilityNodes.append(blendNode)
                cmds.setAttr(blendNode + ".operation", 1) # Make sure set to multiply
                cmds.connectAttr(outputAttr, blendNode + ".input1")
                cmds.connectAttr(ctrl_nd + ".rb", blendNode + ".input2X")
                cmds.connectAttr(ctrl_nd + ".rb", blendNode + ".input2Y")
                cmds.connectAttr(ctrl_nd + ".rb", blendNode + ".input2Z")
                outputAttr = blendNode + ".output"

            cmds.connectAttr(outputAttr, pvt_grp + ".rotate")

        if hideUtilityNodes:
            # Hide utility nodes
            for node in utilityNodes:
                cmds.setAttr(node + ".isHistoricallyInteresting", 0)

        for attr in (["tx","ty","tz"] if translation else []) + (["rx","ry","rz"] if rotation else []):
            if cmds.getAttr(obj + "." + attr, se=1):
                cmds.setAttr(obj + "." + attr, 0)
        obj = cmds.parent(obj, pvt_grp, r=1)[0]
        pvt_grp = cmds.rename(pvt_grp, "grp_counter_" + obj.split("|")[-1])
        if offset_grp:
            offset_grp = cmds.rename(offset_grp, "grp_counter_offset_" + obj.split("|")[-1])

        new_objs.append(obj)

    cmds.select(new_objs)
    return new_objs
