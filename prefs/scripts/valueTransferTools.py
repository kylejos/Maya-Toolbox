# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

import maya.cmds as cmds

'''
Copies the selected attributes between selected objects. If more than two
objects are selected, script will pair objects from the first half of the
selection with the second half.
'''
def CopyValues():
    objs = cmds.ls(sl=1)
    attrs = cmds.channelBox("mainChannelBox", q=1, sma=1)

    if len(objs) % 2 == 0 and attrs:
        div = len(objs) / 2
        sources = objs[:div]
        targets = objs[div:]
        
        for (source, target) in zip(sources, targets):
            for attr in attrs:
                if not cmds.attributeQuery(attr, node=source, ex=1):
                    print "Warning: Could not copy attribute", attr, "from object", source, "because it does not exist"
                elif not cmds.attributeQuery(attr, node=target, ex=1):
                    print "Warning: Could not copy attribute", attr, "to object", target, "because it does not exist"
                elif cmds.keyframe(source+"."+attr, q=1, kc=1) > 0:
                    cmds.cutKey(target, at=attr, cl=1)
                    cmds.copyKey(source, at=attr)
                    cmds.pasteKey(target, at=attr)
                else:
                    cmds.setAttr(target+"."+attr, cmds.getAttr(source+"."+attr))
        print "Copied values between pair objects (first half selection to second half selection)"
    elif (len(objs) == 1 and len(attrs) == 2):
        source_attr = attrs[0]
        target_attr = attrs[1]
        obj = objs[0]
        
        if cmds.keyframe(obj+"."+source_attr, q=1, kc=1) > 0:
            cmds.cutKey(obj, at=target_attr, cl=1)
            cmds.copyKey(obj, at=source_attr)
            cmds.pasteKey(obj, at=target_attr)
        else:
            cmds.setAttr(obj+"."+target_attr, cmds.getAttr(obj+"."+source_attr))
        print "Copied valkues between pair attributes"
    else:
        print "Copy values must take an even number of objects or pair of attributes on a single object"

'''
Swaps the selected attributes between selected objects. If more than two
objects are selected, script will pair objects from the first half of the
selection with the second half.
'''
def SwapValues():
    objs = cmds.ls(sl=1)
    attrs = cmds.channelBox("mainChannelBox", q=1, sma=1)

    if (len(objs) % 2 == 0):
        div = len(objs) / 2
        sources = objs[:div]
        targets = objs[div:]
        
        for (source, target) in zip(sources, targets):
            for attr in attrs:
                if not cmds.attributeQuery(attr, n=source, ex=1):
                    print "Warning: Could not copy attribute", attr, "from object", source, "because it does not exist"
                elif not cmds.attributeQuery(attr, n=target, ex=1):
                    print "Warning: Could not copy attribute", attr, "to object", target, "because it does not exist"
                else:
                    swapVals_(source, attr, target, attr)
        
        print "Swapped values between pair objects (first half selection to second half selection)"
        
    elif (len(objs) == 1 and len(attrs) == 2):
        
        swapVals_(objs[0], attrs[0], objs[0], attrs[1])
        
        print "Swapped values between pair attributes"
    else:
        print "Swap values must take an even number of objects or pair of attributes on a single object"

##
## INTERNAL
##

def swapVals_(obj1, attr1, obj2, attr2):
    val1 = None
    val2 = None
    
    if cmds.keyframe(obj1+"."+attr1, q=1, kc=1) > 0:
        cmds.copyKey(obj1, at=attr1, cb="anim")
        cmds.cutKey(obj1, at=attr1, cl=1)
    else:
        val1 = cmds.getAttr(obj1+"."+attr1)
    
    if cmds.keyframe(obj2+"."+attr2, q=1, kc=1) > 0:
        cmds.copyKey(obj2, at=attr2, cb="api")
        cmds.cutKey(obj2, at=attr2, cl=1)
    else:
        val2 = cmds.getAttr(obj2+"."+attr2)
    
    if val1 == None:
        cmds.pasteKey(obj2, at=attr2, cb="anim")
    else:
        cmds.setAttr(obj2+"."+attr2, val1)
    
    if val2 == None:
        cmds.pasteKey(obj1, at=attr1, cb="api")
    else:
        cmds.setAttr(obj1+"."+attr1, val2)
