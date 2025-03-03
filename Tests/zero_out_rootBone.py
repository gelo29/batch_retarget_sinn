from pyfbsdk import *
from pyfbsdk_additions import *
from PySide2 import QtWidgets
import shiboken2
import os
import copy

app = FBApplication() 


class NativeWidgetHolder(FBWidgetHolder):

    def WidgetCreate(self, pWidgetParent):

        self.mNativeQtWidget = QtWidgets.QWidget(shiboken2.wrapInstance(pWidgetParent, QtWidgets.QWidget))
        main_layout = QtWidgets.QVBoxLayout(self.mNativeQtWidget)
        source_file_grp = QtWidgets.QGroupBox("Source Files")
        source_file_hLayout = QtWidgets.QHBoxLayout(source_file_grp)
        source_file_hLayout.addSpacing(10)
        source_file_btn_dir = QtWidgets.QPushButton("...",objectName="source_file")
        source_file_btn_dir.clicked.connect(lambda: self.get_directory(source_file_btn_dir))
        self.source_file_lineEdit_dir = QtWidgets.QLineEdit()
        
        source_file_hLayout.addWidget(source_file_btn_dir)
        source_file_hLayout.addWidget(self.source_file_lineEdit_dir)
        
        outPut_file_grp = QtWidgets.QGroupBox("OutPut Files")
        outPut_file_hBoxLayout = QtWidgets.QHBoxLayout(outPut_file_grp)
        outPut_file_hBoxLayout.addSpacing(10)
        outPut_file_btn_dir = QtWidgets.QPushButton("...",objectName="outPut_file")
        outPut_file_btn_dir.clicked.connect(lambda: self.get_directory(outPut_file_btn_dir))
        self.outPut_file_lineEdit_dir = QtWidgets.QLineEdit()
        
        outPut_file_hBoxLayout.addWidget(outPut_file_btn_dir)
        outPut_file_hBoxLayout.addWidget(self.outPut_file_lineEdit_dir)
        
        execute_btn = QtWidgets.QPushButton("Execute")
        execute_btn.clicked.connect(self.execute_files)
        main_layout.addWidget(source_file_grp)
        main_layout.addWidget(outPut_file_grp)
        main_layout.addWidget(execute_btn)
        
        return shiboken2.getCppPointer(self.mNativeQtWidget)[0]
        
    def execute_files(self):
        succesfull_msgBox = QtWidgets.QMessageBox()
        succesfull_msgBox.setIcon(QtWidgets.QMessageBox.Information)
        critical_msgBox = QtWidgets.QMessageBox()
        critical_msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        warning_msgBox = QtWidgets.QMessageBox()
        warning_msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        get_fbx_file_path = self.source_file_lineEdit_dir.text()
        get_outPut_file_path = self.outPut_file_lineEdit_dir.text()
        fbx_files = [f for f in os.listdir(get_fbx_file_path) if f.lower().endswith(".fbx")]
        
        if len(fbx_files) != 0:
            for file in fbx_files:
                try:
                    app.FileNew()
                    
                    complete_file_path_text = os.path.join(get_fbx_file_path,file.replace(".FBX",".fbx"))
                    app.FileOpen(complete_file_path_text)
                    self.root = FBFindModelByLabelName("root")
                    self.pelvis = FBFindModelByLabelName("pelvis")
                    
                    self.root_copy = copy.copy(self.root)
                    self.pelvis_copy = copy.copy(self.pelvis)
                    
                    self.parent_duplicate()
                    self.parent_const()
                    self.zeroOut_rootBone()
                    self.moveKey_pelvis()
                    self.clean_up()
                    
                    outPut_path = os.path.join(get_outPut_file_path,file.replace(".FBX",".fbx"))
                    app.FileSave(outPut_path)
                except:
                    critical_msgBox.setWindowTitle("Details")
                    
                    critical_msgBox.setText("Something went wrong with the opening or saving of file!")
                    critical_msgBox.exec_()
                    QCoreApplication.instance().quit()
                    
            succesfull_msgBox.setWindowTitle("Details")
            succesfull_msgBox.setText("Process Done!")
            succesfull_msgBox.exec_()
        else:
            warning_msgBox.setWindowTitle("Details")
            warning_msgBox.setText("There are no files in this directory!")
            warning_msgBox.exec_()
            return
                
    #parent the duplicated pelvis and root
    def parent_duplicate(self):
        
        self.pelvis_copy.Parent = self.root_copy
        playerControl = FBPlayerControl()
        playerControl.StepForward()
        playerControl.StepBackward()
    
    #parent constraint the duplicated pelvis to original pelvis
    def parent_const(self):
        consManager = FBConstraintManager()
        parentCons = consManager.TypeCreateConstraint(3)
        parentCons.Active = False
        parentCons.ReferenceAdd(0,self.pelvis)
        parentCons.ReferenceAdd(1,self.pelvis_copy)
        parentCons.Snap()
    #Zero out rotation of root bone
    def zeroOut_rootBone(self):
        root_rot = FBVector3d(-90,0,0)
        self.root.SetVector(root_rot,FBModelTransformationType.kModelRotation,True)
        
        root_trans = FBVector3d()
        self.root.GetVector(root_trans,FBModelTransformationType.kModelTranslation)
        
        root_scale = FBVector3d(1,1,1)
        
        self.root.Selected = True
        
        FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, self.root, root_trans, root_rot, root_scale, FBSystem().LocalTime)     
        FBSystem().Scene.Evaluate()
    #movekeys on pelvis
    def moveKey_pelvis(self):
        pelvis_rot = FBVector3d()
        self.pelvis.GetVector(pelvis_rot,FBModelTransformationType.kModelRotation)
        pelvis_trans = FBVector3d()
        self.pelvis.GetVector(pelvis_trans,FBModelTransformationType.kModelTranslation)
        pelvis_scale = FBVector3d(1,1,1)
        self.pelvis.Selected = True
        FBKeyControl().MoveKeys(FBSystem().CurrentTake.LocalTimeSpan, self.pelvis, pelvis_trans, pelvis_rot, pelvis_scale, FBSystem().LocalTime)     
        FBSystem().Scene.Evaluate()
        
    def clean_up(self):
        self.root_copy.FBDelete()
        self.pelvis_copy.FBDelete()
        constraints = FBSystem().Scene.Constraints
        for cons in constraints:
            cons.FBDelete()
            
    def get_directory(self,btn):
        
        fileDialog_obj = QtWidgets.QFileDialog.getExistingDirectory(self.mNativeQtWidget, self.mNativeQtWidget.tr("Choose directory"), self.mNativeQtWidget.tr("c:\\"), options=QtWidgets.QFileDialog.ShowDirsOnly)
        if fileDialog_obj:
            if btn.objectName() == "outPut_file":
                self.outPut_file_lineEdit_dir.setText(fileDialog_obj)
            elif btn.objectName() == "source_file":
                self.source_file_lineEdit_dir.setText(fileDialog_obj)
            
class NativeQtWidgetTool(FBTool):
    def BuildLayout(self):
        x = FBAddRegionParam(0,FBAttachType.kFBAttachLeft,"")
        y = FBAddRegionParam(0,FBAttachType.kFBAttachTop,"")
        w = FBAddRegionParam(0,FBAttachType.kFBAttachRight,"")
        h = FBAddRegionParam(0,FBAttachType.kFBAttachBottom,"")
        self.AddRegion("main","main", x, y, w, h)
        self.SetControl("main", self.mNativeWidgetHolder)
                
    def __init__(self, name):
        FBTool.__init__(self, name)
        self.mNativeWidgetHolder = NativeWidgetHolder();
        self.BuildLayout()
        self.StartSizeX = 600
        self.StartSizeY = 280        
        
gToolName = "Zero Root Bone"

gDEVELOPMENT = True

if gDEVELOPMENT:
    FBDestroyToolByName(gToolName)

if gToolName in FBToolList:
    tool = FBToolList[gToolName]
    ShowTool(tool)
else:
    tool=NativeQtWidgetTool(gToolName)
    FBAddTool(tool)
    if gDEVELOPMENT:
        ShowTool(tool)
    
  