from pyfbsdk import *
import csv

scene = FBSystem().Scene
app = FBApplication()

solvers = FBCharacterSolver.GetRegisteredSolverNames()

components = scene.Components
    
characters = scene.Characters

def addJointToCharacter ( characterObject, slot, jointName ):
    myJoint = FBFindModelByLabelName(jointName)
    
    property = characterObject.PropertyList.Find(slot + "Link")
    property.append (myJoint)
    
def bladeSolve():
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
    
def char_settings(char):
    #Reach
    head = char.PropertyList.Find('Head Reach R',True)
    head.Data = 100
    l_hand = char.PropertyList.Find('Left Hand Reach R',True)
    l_hand.Data = 100
    r_hand = char.PropertyList.Find('Right Hand Reach R',True)
    r_hand.Data = 100
    
    l_hand = char.PropertyList.Find('Left Hand Reach T',True)
    l_hand.Data = 10
    l_hand = char.PropertyList.Find('Left Elbow Reach',True)
    l_hand.Data = 10
    
    r_hand = char.PropertyList.Find('Right Hand Reach T',True)
    r_hand.Data = 10
    r_hand = char.PropertyList.Find('Right Elbow Reach',True)
    r_hand.Data = 10
    
    chest = char.PropertyList.Find('Chest Reach T',True)
    chest.Data = 70
    u_chest = char.PropertyList.Find('Upper Chest Reach R',True)
    u_chest.Data = 30
    lo_chest = char.PropertyList.Find('Lower Chest Reach R', True) 
    lo_chest.Data = 50
    
    #Pull
    l_foot_pull = char.PropertyList.Find('Left Foot Pull', True)
    l_foot_pull.Data = 100
    r_foot_pull = char.PropertyList.Find('Right Foot Pull', True)
    r_foot_pull.Data = 100
    hips = char.PropertyList.Find('Hips Pull', True)
    hips.Data = 15
    
    for solve in range(len(solvers)):
        if solvers[solve] == "HIK 2016 Solver":
            char.SetExternalSolverWithIndex(solve)
    for comp in components:
        if "HIK 2016 Solver" in comp.Name:
        
            comp.PropertyList.Find("Reach Left Shoulder",True).Data = 10
            comp.PropertyList.Find("Reach Right Shoulder",True).Data = 10
            
            comp.PropertyList.Find("Collar Stiffness X",True).Data = 20
            comp.PropertyList.Find("Collar Stiffness Y",True).Data = 30
            comp.PropertyList.Find("Collar Stiffness Z",True).Data = 10
    #Solving
    realistic_shoulder = char.PropertyList.Find('Realistic Shoulder Solving',True)
    realistic_shoulder.Data = 40
    
    #Retargeting
    match_source = char.PropertyList.Find('Match Source',True)
    match_source.Data = True
    
    #Offsets
    hips_lvl = char.PropertyList.Find('Hips Level',True)
    hips_lvl.Data = 0.0
    feet_space = char.PropertyList.Find('Feet Spacing', True)
    feet_space.Data = 0.0
    ankle_height = char.PropertyList.Find('Ankle Height Compensation', True)
    ankle_height.Data = 0.0
    mass_center = char.PropertyList.Find('Mass Center Compensation', True)
    mass_center.Data = 30.0
    
    #Stiffness
    neck_stiff = char.PropertyList.Find('Neck Stiffness', True)
    neck_stiff.Data = 15
    chest_stiff = char.PropertyList.Find("Chest Stiffness", True)
    chest_stiff.Data = 35.00
    spine_stiff = char.PropertyList.Find("Spine Stiffness", True)
    spine_stiff.Data = 35.00
    hips_stiff = char.PropertyList.Find("Hips Stiffness", True)
    hips_stiff.Data = 35.00
    l_leg_stiff = char.PropertyList.Find("Left Leg Stiffness", True)
    l_leg_stiff.Data = 100.00
    r_leg_stiff = char.PropertyList.Find("Right Leg Stiffness", True)
    r_leg_stiff.Data = 100.00
    
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
    
def input_actor():
     
    for char in characters:
        
        if char.Name == "Knight":
            app.CurrentCharacter = char
            
    curr_char = app.CurrentCharacter
    curr_char.ActiveInput = True
    characterInput = [char for char in characters if char.Name != curr_char.Name]
    curr_char.InputCharacter = characterInput[0]
    curr_char.InputType = FBCharacterInputType.kFBCharacterInputCharacter
    char_settings(curr_char)  
     
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
    FBPlayerControl().SetTransportFps(FBTimeMode.kFBTimeMode60Frames)
    
def unselect_mainrig(pModel, pList):
    if pModel:
        #add to list
        pList.append(pModel)
        pModel.Selected = False
        # Look at all the children to rename them, if needed.
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
            
def save_file():
    csv_file = "C:/Users/AVA_ME_TL/Documents/Gelo/Test/others/shots.csv"
    filePath = "C:/Users/AVA_ME_TL/Documents/Gelo/Test/"
    savingPath = "C:/Users/AVA_ME_TL/Documents/Gelo/Test/delivery/"
    with open(csv_file, 'r') as _filehandler:
        readCSV = csv.reader(_filehandler, delimiter=',')
        for row in readCSV:
            app.FileNew()
            print row[0]
            success_open = app.FileOpen(str(filePath+row[0]+".fbx"))
            if success_open:
                bladeSolve()
                FBSystem().Scene.Evaluate()
                characterize()
                FBSystem().CurrentTake.LocalTimeSpan = FBTimeSpan(
                    FBTime(0, 0, 0, int(row[1]), 0),
                    FBTime(0, 0, 0, int(row[2]), 0)
                )
                merge_char("C:/Users/AVA_ME_TL/Documents/Gelo/Test/others/Target.fbx")
                plotTo("skel","60")   
                root_motion() 
                plotTo("skel","60")
                clean_up()
                app.FileSave(str(savingPath+row[3]+".fbx"))
                
    _filehandler.close() 
            
save_file()  
