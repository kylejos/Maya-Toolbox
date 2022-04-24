# Copyright 2022 by Kyle Joswiak
#
# This is released under the "MIT License Agreement".
# See License file that should have been included in distribution.

'''
Custom skin copying script that skips vertices that aren't close to any others.
Useful for skins on partial meshes to or from a whole mesh (or even another partial mesh).
'''

import maya.cmds as cmds
import maya.mel as mel

def CopySkinWeightsLimitedByDistance(threshold = .01):
    objs = cmds.ls(sl=1)
    source = objs[0]

    source_vertices = [cmds.xform(source+".vtx[%d]"%i, q=1, t=1, ws=0) for i in xrange(cmds.polyEvaluate(source, vertex=1))]
    source_cluster = mel.eval('findRelatedSkinCluster '+source)
    source_influences = cmds.skinCluster(source_cluster, q=1, inf=1)

    threshold2 = threshold*threshold
    for target in objs[1:]:
        target_cluster = mel.eval('findRelatedSkinCluster '+target)
        target_influences = cmds.skinCluster(target_cluster, q=1, inf=1)
        new_influences = [influence for influence in source_influences if influence not in target_influences]
        if new_influences:
            cmds.skinCluster(target_cluster, e=1, addInfluence=new_influences, wt=0)
            print "Added %d new influences to target %s" % (len(new_influences), target)
        
        count = 0
        for vi in xrange(cmds.polyEvaluate(target, vertex=1)):
            v = cmds.xform(target+".vtx[%d]"%vi, q=1, t=1, ws=0)
            
            (min_dist2, min_i) = min((((v[0]-sv[0])**2 + (v[1]-sv[1])**2 + (v[2]-sv[2])**2, i) for (i, sv) in enumerate(source_vertices)))

            if min_dist2 < threshold2:
                source_influences = zip(cmds.skinPercent(source_cluster, source+".vtx[%d]"%min_i, q=1, t=None), cmds.skinPercent(source_cluster, source+".vtx[%d]"%min_i, q=1, v=1))
                cmds.skinPercent(target_cluster, target+".vtx[%d]"%vi, tv=source_influences, zeroRemainingInfluences=1)
                count += 1
            
        print "Copied %d vertices to %s" % (count, target)

    cmds.select(objs)
