# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.
'''
Includes various functions that snaps one (or more) objects to last selected
object's transformation. They generally function identically to creating the
corresponding constraint, then immediately deleting it, which may sometimes be
more powerful or desirable then Maya's alignment tools. Will automatically
exclude non-settable channels.
'''

import maya.cmds as cmds

''' Snap translation + rotation using a parent constraint '''
def snapParentConstraint(*args):
    objs = cmds.ls(sl=1) if not args else args

    if (len(objs) >= 2):
        source = objs[:-1]
        target = objs[-1]

        skip_trans = [t for t in "xyz" if not cmds.getAttr(target + ".t" + t, se=1)]
        skip_rot = [r for r in "xyz" if not cmds.getAttr(target + ".r" + r, se=1)]

        constraint = cmds.parentConstraint(source, target, st = skip_trans, sr = skip_rot)
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz"]:
            if cmds.keyframe(target+"."+attr, q=1, kc=1) > 0:
                cmds.setKeyframe(target+"."+attr)
        cmds.delete(constraint)

        cmds.select(target)
        return [target]
    else:
        print "Need at least two objects to apply constraint"
        return []

''' Snap rotation using a orientation constraint '''
def snapOrientConstraint(*args):
    objs = cmds.ls(sl=1) if not args else args

    if (len(objs) >= 2):
        source = objs[:-1]
        target = objs[-1]

        skip_rot = [r for r in "xyz" if not cmds.getAttr(target + ".r" + r, se=1)]

        constraint = cmds.orientConstraint(source, target, sk = skip_rot)
        for attr in ["rx", "ry", "rz"]:
            if cmds.keyframe(target+"."+attr, q=1, kc=1) > 0:
                cmds.setKeyframe(target+"."+attr)
        cmds.delete(constraint)

        cmds.select(target)
        return [target]
    else:
        print "Need at least two objects to apply constraint"
        return []

''' Snap translation using a point constraint '''
def snapPointConstraint(*args):
    objs = cmds.ls(sl=1) if not args else args

    if (len(objs) >= 2):
        source = objs[:-1]
        target = objs[-1]

        skip_trans = [t for t in "xyz" if not cmds.getAttr(target + ".t" + t, se=1)]

        constraint = cmds.pointConstraint(source, target, sk = skip_trans)
        for attr in ["tx", "ty", "tz"]:
            if cmds.keyframe(target+"."+attr, q=1, kc=1) > 0:
                cmds.setKeyframe(target+"."+attr)
        cmds.delete(constraint)

        cmds.select(target)
        return [target]
    else:
        print "Need at least two objects to apply constraint"
        return []

'''
Snaps orientation using an Aim constraint. Default is to aim positively along
the snapping object's x-axis, but "aim" argument can be provided (as a vector)
to set a different axis / direction.
'''
def snapAimConstraint(*args, **kwargs):
    objs = cmds.ls(sl=1) if not args else args
    aim_vector = (1,0,0) if "aim" not in kwargs else kwargs["aim"]

    if (len(objs) >= 2):
        source = objs[:-1]
        target = objs[-1]

        skip_rot = [r for r in "xyz" if not cmds.getAttr(target + ".r" + r, se=1)]

        constraint = cmds.aimConstraint(source, target, sk = skip_rot, aim = aim_vector, u=aim_vector)
        for attr in ["rx", "ry", "rz"]:
            if cmds.keyframe(target+"."+attr, q=1, kc=1) > 0:
                cmds.setKeyframe(target+"."+attr)
        cmds.delete(constraint)

        cmds.select(target)
        return [target]
    else:
        print "Need at least two objects to apply constraint"
        return []

''' Snap scale using a scale constraint '''
def snapScaleConstraint(*args):
    objs = cmds.ls(sl=1) if not args else args

    if (len(objs) >= 2):
        source = objs[:-1]
        target = objs[-1]

        skip_scale = [s for s in "xyz" if not cmds.getAttr(target + ".s" + s, se=1)]

        constraint = cmds.scaleConstraint(source, target, sk = skip_scale)
        for attr in ["sx", "sy", "sz"]:
            if cmds.keyframe(target+"."+attr, q=1, kc=1) > 0:
                cmds.setKeyframe(target+"."+attr)
        cmds.delete(constraint)

        cmds.select(target)
        return [target]
    else:
        print "Need at least two objects to apply constraint"
        return []
