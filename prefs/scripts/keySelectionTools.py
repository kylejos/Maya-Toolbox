# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

import maya.cmds as cmds

''' Select animation curves from EITHER selected keys in graph editor or selected channels in attribute editor '''
def getActiveAnimationCurves():
    cvs = cmds.keyframe(q=1, sl=1, n=1)
    if cvs:
        return cvs

    objs = cmds.ls(sl=1)
    attrs = cmds.channelBox("mainChannelBox", q=1, sma=1)
    if attrs:
        targets = [obj+"."+attr for obj in objs for attr in attrs if cmds.attributeQuery(attr, node=obj, ex=1)]
        if targets:
            cvs = cmds.keyframe(targets, q=1, n=1)
            if cvs:
                return cvs

    return cmds.keyframe(q=1, n=1)

''' Select keys for argument frame, or current frame in no argument provided. Set add=True to make an additive selection. '''
def selectKeys(add=False, frame=None):
    anim_curves = getActiveAnimationCurves()
    if frame == None:
        frame = cmds.currentTime(q=1)

    if not add:
        cmds.selectKey(cl=1)
    for cv in anim_curves:
        cmds.selectKey(cv, time=(frame,frame), add=1)

'''
Expand selection to include next key along any active curve.
    dir=1 (default) adds next key, dir=-1 adds previous key, and dir=0 adds both next and previous keys.
'''
def expandSelection(dir=1):
    anim_curves = cmds.keyframe(q=1, sl=1, n=1)
    if not anim_curves:
        selectKeys()
        return

    if dir >= 0:
        next_frame = None
        for cv in anim_curves:
            cur_index = max(cmds.keyframe(cv, q=1, sl=1, iv=1))
            if cur_index < cmds.keyframe(cv, q=1, kc=1)-1:
                next_key = cmds.keyframe(cv, q=1, index=(cur_index+1, cur_index+1))[0]
                if next_frame == None or next_key < next_frame:
                    next_frame = next_key
        if next_frame != None:
            selectKeys(add=True, frame=next_frame)
    if dir <= 0:
        prev_frame = None
        for cv in anim_curves:
            cur_index = min(cmds.keyframe(cv, q=1, sl=1, iv=1))
            if cur_index > 0:
                prev_key = cmds.keyframe(cv, q=1, index=(cur_index-1, cur_index-1))[0]
                if prev_frame == None or prev_key > prev_frame:
                    prev_frame = prev_key
        if prev_frame != None:
            selectKeys(add=True, frame=prev_frame)

''' Select all keys before (dir=-1) or after (dir=1) current selection. '''
def expandSelectAll(dir=1):
    anim_curves = getActiveAnimationCurves()

    for cv in anim_curves:
        keyframes = cmds.keyframe(cv, q=1, sl=1, iv=1)

        if keyframes:
            min_index = 0 if dir < 0 else min(cmds.keyframe(cv, q=1, sl=1, iv=1))
            max_index = cmds.keyframe(cv, q=1, kc=1)-1 if dir > 0 else max(cmds.keyframe(cv, q=1, sl=1, iv=1))

            cmds.selectKey(cv, add=True, index=(min_index, max_index))
        else:
            cur_time = cmds.currentTime(q=1)
            min_time = 0 if dir < 0 else cur_time
            max_time = max(cmds.keyframe(cv, q=1)) if dir > 0 else cur_time
            
            if min_time <= max_time:
                cmds.selectKey(cv, add=True, time=(min_time, max_time))

''' Unselect leftmost (if dir=1) or rightmost (if dir=-1) curently selected key. dir=0 removes in both directions '''
def contractSelection(dir=1):
    anim_curves = cmds.keyframe(q=1, sl=1, n=1)
    frames = cmds.keyframe(q=1, sl=1)
    if not anim_curves or not frames:
        return

    remove_keys = []
    if dir >= 0:
        min_frame = min(frames)
        remove_keys.append((min_frame,min_frame))
    if dir <= 0:
        max_frame = max(frames)
        remove_keys.append((max_frame,max_frame))
    for cv in anim_curves:
        cmds.selectKey(cv, time=remove_keys, rm=1)

def selectKnots():
    tangentPicker(it=False, ot=False)

''' Select both input and output tangents for all selected keys '''
def selectTangents():
    tangentPicker(it=True, ot=True)

''' Select input tangents for all selected keys '''
def selectInTangents():
    tangentPicker(it=True, ot=False)

''' Select output tangents for all selected keys '''
def selectOutTangents():
    tangentPicker(it=False, ot=True)

##
## INTERNAL
##

def tangentPicker(ot=False, it=False):
    anim_curves = cmds.keyframe(q=1, sl=1, n=1)
    anim_curves_indices = []

    for cv in anim_curves:
        anim_curves_indices.append([(x,x) for x in cmds.keyframe(cv, q=1, sl=1, iv=1)])

    cmds.selectKey(cl=1)
    for (cv, indices) in zip(anim_curves, anim_curves_indices):
        cmds.selectKey(cv, index=indices, add=1, it=it, ot=ot)