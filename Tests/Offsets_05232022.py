from pyfbsdk import *
import csv
import re
from os.path import exists
import os
import configparser

config = configparser.RawConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(current_dir, 'settings.ini'))

config_dict = dict(config.items('default'))

scene = FBSystem().Scene
app = FBApplication()

solvers = FBCharacterSolver.GetRegisteredSolverNames()

components = scene.Components
    
characters = scene.Characters

pattern = re.compile("(?:ALICE|JUNIOR)_[0-9]+_Hips")


def rotate_hips(rootOffset,rotOffset1, rotOffset2):
    for c in components:
        if(bool(re.match(pattern, c.Name)) == False and c.Name != 'pelvis'):
            c.Selected = False
        elif(bool(re.match(pattern, c.Name))):
            c.Selected = True
            trans = FBVector3d()
            c.GetVector(trans,FBModelTransformationType.kModelTranslation, True)
            rot = FBVector3d(0,(float(rootOffset)),0)
            scale = FBVector3d(1,1,1)
            
            c.SetVector(rot,FBModelTransformationType.kModelRotation,True)
            FBSystem().Scene.Evaluate()
            FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, c, trans, rot, scale, FBSystem().LocalTime)
            c.Selected = False
        elif(c.Name == 'pelvis'):
            root = FBFindModelByLabelName("root")
            root_rot = FBVector3d()
            root.GetVector(root_rot,FBModelTransformationType.kModelRotation,True)
            print root_rot
            root_rot_offset = FBVector3d(0,0,-90 + (root_rot[2]+float(rootOffset) * -1)) #-90 + (root_rot[0]+float(x) * -1)
            
            root.SetVector(root_rot_offset,FBModelTransformationType.kModelRotation,True)
            
            root_trans = FBVector3d()
            root.GetVector(root_trans,FBModelTransformationType.kModelTranslation, True)
            root_scale = FBVector3d(1,1,1)
            
            
            pelvis_trans = FBVector3d()
            c.GetVector(pelvis_trans,FBModelTransformationType.kModelTranslation, True)
            print pelvis_trans
            pelvis_trans_offset = FBVector3d(pelvis_trans[0]+rotOffset1, pelvis_trans[1], pelvis_trans[2]+rotOffset2)
            c.SetVector(pelvis_trans_offset,FBModelTransformationType.kModelTranslation, True)
            
            pelvis_rot = FBVector3d()
            pelvis_rot_val = c.GetVector(pelvis_rot,FBModelTransformationType.kModelRotation, True)
            
            pelvis_rot_offset = FBVector3d(-90 + (float(pelvis_rot[0]+float(rootOffset)) * -1), 0, 90)
           
            c.SetVector(pelvis_rot_offset,FBModelTransformationType.kModelRotation, True)
            
            pelvis_scale = FBVector3d(1,1,1)
            
            
            c.Selected = True
            root.Selected = True

            FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, root, root_trans, root_rot_offset, root_scale, FBSystem().LocalTime)
            FBSystem().Scene.Evaluate()
            FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, c, pelvis_trans_offset, pelvis_rot_offset, pelvis_scale, FBSystem().LocalTime)


            
def run_program():
    root_dir = config_dict["root_dir"]
    csv_file_path = os.path.join(root_dir, config_dict["csv_file_name"])

    with open(csv_file_path, 'r') as _filehandler:
        readCSV = csv.reader(_filehandler, delimiter=',')
        for row in readCSV:
            app.FileNew()
            fbx_file = os.path.join(root_dir, config_dict["read_dir"], row[0].strip() + ".fbx")
            success_open = app.FileOpen(fbx_file)
            if success_open:
                
                rotate_hips(row[1].strip(),row[2].strip(),row[3].strip())
                
                saved_file_path = os.path.join(root_dir, config_dict["save_dir"], row[0].strip() + ".fbx")
                app.FileSave(saved_file_path)
            else:
                print('Fbx file path is invalid for '+ fbx_file)
                
    _filehandler.close()
            
run_program()
