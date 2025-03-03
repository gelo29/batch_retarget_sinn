from pyfbsdk import *
import re

scene = FBSystem().Scene
components = scene.Components

pattern = re.compile("(?:ALICE|JUNIOR)_[0-9]+_Hips")

time = FBTime()
#FBVector3d(0,0,0)
def run_program(rootOffset):
    skeletons = [skel for skel in scene.ModelSkeletons]
    for c in components:
        if(bool(re.match(pattern, c.Name))):
            c.Selected = True
            trans = FBVector3d()
            rot = FBVector3d()
            scale = FBVector3d(1,1,1)
            
            c.SetVector(rot,FBModelTransformationType.kModelRotation,True)
            FBSystem().Scene.Evaluate()
            trans_vec = c.GetVector(trans,FBModelTransformationType.kModelTranslation,True)
            rot_vec = c.GetVector(rot,FBModelTransformationType.kModelRotation,True)
            scale_vec = c.GetVector(scale,FBModelTransformationType.kModelScaling,True)
            
            FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, c, trans, rot, scale, FBSystem().LocalTime)
            c.Selected = False
            #c.Translation.SetAnimated(True)
            #node = c.Translation.GetAnimationNode()
            #fcurve = node.Nodes[0].FCurve
            #FBKeyControl().MoveKeys = True
            #for key in fcurve.Keys:
                #print(key.Value)
                
        elif(c.Name == 'pelvis'):
            c.Selected = True
            print('%d -- %d' % (
                FBSystem().CurrentTake.LocalTimeSpan.GetStart().GetFrame(),
                FBSystem().CurrentTake.LocalTimeSpan.GetStop().GetFrame()
            ))
            trans = FBVector3d()
            rot = FBVector3d(rootOffset,0,90)
            scale = FBVector3d(1,1,1)
            
            c.SetVector(rot,FBModelTransformationType.kModelRotation,True)
            FBSystem().Scene.Evaluate()
            trans_vec = c.GetVector(trans,FBModelTransformationType.kModelTranslation,True)
            rot_vec = c.GetVector(rot,FBModelTransformationType.kModelRotation,True)
            scale_vec = c.GetVector(scale,FBModelTransformationType.kModelScaling,True)
            
            FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, c, trans, rot, scale, FBSystem().LocalTime)
            c.Selected = False
            #c.Translation.SetAnimated(True)
            #node = c.Translation.GetAnimationNode()
            #fcurve = node.Nodes[0].FCurve
            #for key in fcurve.Keys:
                #print(key.Value)

##        else:
##            c.Selected = False 

run_program(-90)