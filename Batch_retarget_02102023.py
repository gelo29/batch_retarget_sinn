from pyfbsdk import *
import csv
from os.path import exists
import os
import ConfigParser
import re

config = ConfigParser.RawConfigParser()
current_dir = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(current_dir, 'settings.ini'))

config_dict = dict(config.items('default'))

scene = FBSystem().Scene
app = FBApplication()

solvers = FBCharacterSolver.GetRegisteredSolverNames()

components = scene.Components
    
characters = scene.Characters

pattern = re.compile("(?:ALICE|JUNIOR)_[0-9]+_Hips")

def addJointToCharacter(characterObject, slot, jointName ):
    myJoint = FBFindModelByLabelName(jointName)
    
    property = characterObject.PropertyList.Find(slot + "Link")
    property.append (myJoint)
    
def solve_skel():
    skeletons = [skel for skel in scene.ModelSkeletons]
    hips = scene.Components
    for hip in hips:
        if "_Hips" in hip.Name:
            skeletons.append(hip)
            
    for skel in skeletons:
        skel.Rotation = FBVector3d(0,0,0)
        
def characterize():
    skeletons = [skel for skel in scene.ModelSkeletons]
    hips = scene.Components
    for hip in hips:
        if "_Hips" in hip.Name:
            skeletons.append(hip)
            
    actor_name = skeletons[0].Name
    actor_name_idx = str(actor_name).find('_')
    actor = actor_name[:actor_name_idx]

    char = FBCharacter(actor)
    
    for skel in skeletons:
        part_name = str(skel.Name)
        part_name_idx = part_name.rfind('_')
        
        slot = str(skel.Name)[part_name_idx+1:]
       
        joint = skel.LongName
        
        addJointToCharacter(char,slot,joint)
                                
    char.SetCharacterizeOn(True)
    
def plotTo(plotToWhere, fps): 
    char = app.CurrentCharacter
    fpsDic = {"1000": FBTimeMode.kFBTimeMode1000Frames, "120": FBTimeMode.kFBTimeMode120Frames, "100": FBTimeMode.kFBTimeMode100Frames, "96": FBTimeMode.kFBTimeMode96Frames, "72": FBTimeMode.kFBTimeMode72Frames, "60": FBTimeMode.kFBTimeMode60Frames,
    "5994": FBTimeMode.kFBTimeMode5994Frames, "50": FBTimeMode.kFBTimeMode50Frames, "48": FBTimeMode.kFBTimeMode48Frames, "30": FBTimeMode.kFBTimeMode30Frames, "2997_d": FBTimeMode.kFBTimeMode2997Frames_Drop, "2997": FBTimeMode.kFBTimeMode2997Frames, "25": FBTimeMode.kFBTimeMode25Frames
    ,"24": FBTimeMode.kFBTimeMode24Frames, "23976": FBTimeMode.kFBTimeMode23976Frames, "c": FBTimeMode.kFBTimeModeCustom}
    plotDic = {"rig": FBCharacterPlotWhere.kFBCharacterPlotOnControlRig, "skel": FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton}
    
    myPlotOptions = FBPlotOptions()
    myPlotOptions.PlotPeriod = FBTime(0,0,0,1,fpsDic[fps])
    myPlotOptions.ConstantKeyReducerKeepOneKey = False
    myPlotOptions.UseConstantKeyReducer = False
    myPlotOptions.PlotTranslationOnRootOnly = True
    myPlotOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll

    char.PlotAnimation(plotDic[plotToWhere],myPlotOptions)
    
    for skel in scene.Components:
        if skel.ClassName() == "FBModelSkeleton":
            if "roll" in skel.Name:
                skel.Show = False
            else:
                skel.Show = True
                
def root_motion():
    playerControl = FBPlayerControl()

    mtrx = FBMatrix()
    rootTransPos = FBVector3d()
    pelvisTransPos = FBVector3d()
    
    root = FBFindModelByLabelName("root")
    pelvis = FBFindModelByLabelName("pelvis")
   
    root.Translation.SetAnimated(True)
    FBSystem().Scene.Evaluate()
    pelvis.GetVector(pelvisTransPos)
    root.GetVector(rootTransPos)
    
    rootTransPos[0] = pelvisTransPos[0]
    rootTransPos[2] = pelvisTransPos[2]
    
    root.SetVector(rootTransPos)
    
    root.Translation.GetAnimationNode().Nodes[0].FCurve = pelvis.Translation.GetAnimationNode().Nodes[0].FCurve
    root.Translation.GetAnimationNode().Nodes[1].FCurve = pelvis.Translation.GetAnimationNode().Nodes[1].FCurve
    pelvis.Translation.GetAnimationNode().Nodes[0].FCurve.EditClear()
    pelvis.Translation.GetAnimationNode().Nodes[1].FCurve.EditClear()
    
    #root center on 0Frame/startframe
    root.Translation.SetAnimated(True)
    node = root.Translation.GetAnimationNode()
    node.KeyAdd(playerControl.LoopStart,[0.0,0.0,0.0])
    
    
    trans = FBVector3d()
    rot = FBVector3d()
    root.GetVector(trans,FBModelTransformationType.kModelTranslation, True)
    root.GetVector(rot,FBModelTransformationType.kModelRotation, True)
    scale = FBVector3d(1,1,1)
    
    FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, root, trans, rot, scale, FBSystem().LocalTime)
        
def input_actor():
    for char in characters:
        if char.Name == "Knight":
            
            app.CurrentCharacter = char
        else:
            print('FAIL')
            
    curr_char = app.CurrentCharacter
    curr_char.ActiveInput = True
    characterInput = [char for char in characters if char.Name != curr_char.Name]
    curr_char.InputCharacter = characterInput[0]
    curr_char.InputType = FBCharacterInputType.kFBCharacterInputCharacter
      
     
def merge_char(path):
    lOptions = FBFbxOptions( True, path )
    for lTakeIndex in range( 0, lOptions.GetTakeCount() ):
        lOptions.SetTakeSelect( lTakeIndex, False )
    lOptions.BaseCameras = False
    lOptions.CameraSwitcherSettings = False  
    lOptions.CurrentCameraSettings = False
    lOptions.GlobalLightingSettings = False
    lOptions.TransportSettings = False
    app.FileMerge(path,False,lOptions)
    input_actor()
    
def unselect_mainrig(pModel, pList):
    if pModel:
        pList.append(pModel)
        pModel.Selected = False
        
        for lChild in pModel.Children:
            unselect_mainrig( lChild, pList)
        else:
            return pList 
            
def clean_up():
    comps = scene.Components
    for comp in comps:
        if comp.ClassName() == "FBModelNull":
            comp.Selected = True
        if comp.ClassName() == "FBModel":
            comp.Selected = True
        if comp.ClassName() == "FBModelRoot":
            comp.Selected = True
        if comp.ClassName() == "FBModelSkeleton":
            comp.Selected = True
    
    character_rig = FBFindModelByLabelName("CCN_Knight_01")        
    unselect_mainrig(character_rig,[])
    
    chars = scene.Characters
    modelList = FBModelList()
    FBGetSelectedModels(modelList)
    toDelete = []
    char_delete = []
    
    for model in modelList:
        toDelete.append(model)
        
    for char in chars:
        char_delete.append(char)
        
    for char in char_delete:
        char.FBDelete()
    
    for delete in toDelete:
        delete.FBDelete()
        
def remove_animation_data():
    for c in components:
        if(bool(re.match(pattern, c.Name)) == False and c.Name != 'pelvis'):
            c.Selected = False
        elif(bool(re.match(pattern, c.Name))):
            c.Selected = True
            node = c.Translation.GetAnimationNode()
            fcurve = node.Nodes[0].FCurve
            c.Translation.GetAnimationNode().Nodes[0].FCurve.EditClear()
            c.Translation.GetAnimationNode().Nodes[2].FCurve.EditClear()

def run_program(fps):
    fpsDic = {"1000": FBTimeMode.kFBTimeMode1000Frames, "120": FBTimeMode.kFBTimeMode120Frames, "100": FBTimeMode.kFBTimeMode100Frames, "96": FBTimeMode.kFBTimeMode96Frames, "72": FBTimeMode.kFBTimeMode72Frames, "60": FBTimeMode.kFBTimeMode60Frames,
    "5994": FBTimeMode.kFBTimeMode5994Frames, "50": FBTimeMode.kFBTimeMode50Frames, "48": FBTimeMode.kFBTimeMode48Frames, "30": FBTimeMode.kFBTimeMode30Frames, "2997_d": FBTimeMode.kFBTimeMode2997Frames_Drop, "2997": FBTimeMode.kFBTimeMode2997Frames, "25": FBTimeMode.kFBTimeMode25Frames
    ,"24": FBTimeMode.kFBTimeMode24Frames, "23976": FBTimeMode.kFBTimeMode23976Frames, "c": FBTimeMode.kFBTimeModeCustom}
    plotDic = {"rig": FBCharacterPlotWhere.kFBCharacterPlotOnControlRig, "skel": FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton}
    
    root_dir = config_dict["root_dir"]
    csv_file_path = os.path.join(root_dir, config_dict["csv_file_name"])
   
    rigged_character = os.path.join(root_dir, "Target.fbx")
    target_file_exists = exists(rigged_character)
    if not target_file_exists:
        print('Rigged character file path is invalid for ' + rigged_character)
        return
    with open(csv_file_path, 'r') as _filehandler:
        readCSV = csv.reader(_filehandler, delimiter=';')
        
        #row = list(readCSV)
        for row in readCSV:
            app.FileNew()
            fbx_file = os.path.join(root_dir, config_dict["read_dir"], row[0].strip() + ".fbx")
            
            success_open = app.FileOpen(fbx_file)
            if success_open:
                #remove_animation_data()
                solve_skel()
                FBSystem().Scene.Evaluate()
                characterize()
                merge_char(rigged_character) # Character rig
                plotTo("skel",fps)
                if('Idle' not in row[0].strip()):
                    print row[0].strip()
                    root_motion()
                    
                FBPlayerControl().SetTransportFps(fpsDic[fps])
                plotTo("skel",fps)
                clean_up()
                saved_file_path = os.path.join(root_dir, config_dict["save_dir"], row[3].strip() + ".fbx")
                app.FileSave(saved_file_path)
            else:
                print('Fbx file path is invalid for '+ fbx_file)
                
    _filehandler.close()
            
run_program("60")