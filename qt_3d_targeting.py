

from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QWidget, QPushButton, qApp, QLabel, QHBoxLayout, QVBoxLayout, QSplitter, QDialog
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QImage, QMatrix4x4, QQuaternion, QVector3D, QColor, QGuiApplication
from PyQt5.QtGui import QTransform as QTT
from PyQt5.QtCore import QSize, Qt
from PyQt5 import QtCore
import sys
from PyQt5.Qt3DCore import QEntity, QAspectEngine, QTransform
from PyQt5.Qt3DRender import QCamera, QCameraLens, QRenderAspect, QBlendEquation
from PyQt5.Qt3DInput import QInputAspect
from PyQt5.Qt3DExtras import QForwardRenderer, QPhongMaterial, QPhongAlphaMaterial, QCylinderMesh, QSphereMesh, QTorusMesh, QPlaneMesh, Qt3DWindow, QConeMesh,QOrbitCameraController

from PyQt5.Qt3DLogic import QFrameAction

import numpy as np
import time, threading

from enum import Enum


#from qt_for_python.uic.my_custom_dialog_3d import *



class TrainingModesDirection(Enum):
    DIR_2D_CARDINAL = 0
    DIR_2D_ANY = 1
    DIR_3D_CARDINAL = 2
    DIR_3D_ANY = 3

class TrainingModesChangeType(Enum):
    DIR_CHANGE_CONTINUOUS = 0
    DIR_CHANGE_STEPWISE = 1


class QT3DTargetDialog(QDialog):
    def __init__(self):
        super(QT3DTargetDialog,self).__init__()
        #self.ui = Ui_Dialog()
        #self.ui.setupUi(self)
        #self.ui.gridLayout.addWidget(self.btm_channel_cb)
        self.layout = QVBoxLayout()
        self.q3d = QT3DTarget()
        self.layout.addWidget(self.q3d)
        self.setLayout(self.layout)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.resize(1024,768)
        self.setModal(False)


    def setupTraining(self,change_time, mode,changeTimeMin,changeTimeMax):
        self.q3d.setupTraining(change_time, mode,changeTimeMin,changeTimeMax)


    def getTargetDir(self):
        return self.q3d.getTargetDir()


    def setTrainingMode(self,mode):
        return self.q3d.setTrainingMode(mode)



class QT3DTarget(QWidget):
    def __init__(self):
        #super(QT3DTarget, self).__init__()
        super(QT3DTarget,self).__init__()


        self.view = Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor( QColor("#000000") )
        self.container = self.createWindowContainer(self.view)


        vboxlayout = QHBoxLayout()
        vboxlayout.addWidget(self.container)
        self.setLayout(vboxlayout)

        self.arrow = None
        self.target = None

        self.scene = self.createScene()

        self.arrow.setAnimation(True)
        #self.arrow.setRotation(QVector3D(-1.0, 0.0, 0.0),90)

        self.target.setAnimation(False)
        #self.target.setRotation(QVector3D(0, 0, 1.0),90)



        # Camera.
        self.initialiseCamera(self.view, self.scene)

        fa = QFrameAction()
        self.scene.addComponent( fa )
        fa.triggered.connect( self.frame_cb )

        self.view.setRootEntity(self.scene)

        self.lastFrameTime = time.time()
        #self.resize(800,640)

        self.training_change_time_min = 3
        self.training_change_time_max = 10
        self.training_change_time = 5
        self.training_mode = TrainingModesDirection.DIR_2D_ANY
        self.training_target = [0,1,0]
        self.running = True

        self.startTrainingTimer()


    def setAllRotation(self,axis,ang):
        self.arrow.setRotation(axis,ang)
        self.target.setRotation(axis,ang)

    def setTrainingMode(self,mode):
        self.training_mode = mode
        self.trainingCallback()

    def setupTraining(self,change_time, mode,changeTimeMin,changeTimeMax):
        self.training_change_time_min = changeTimeMin
        self.training_change_time_max = changeTimeMax
        self.updateTrainingTime()

        self.training_change_time = change_time
        self.training_mode = mode


    def trainingCallback(self):
        if( self.training_mode == TrainingModesDirection.DIR_2D_CARDINAL ):
            dirRotX = np.random.randint(0,4)
            ang = 90.0*dirRotX
            self.setAllRotation(QVector3D(0, 0, 1.0),ang)
            self.training_target = [np.cos(np.deg2rad(ang)),np.sin(np.deg2rad(ang)),0]
        else: # DIR_2D_ANY TODO: implement 3D/ continuous
            ang = float(np.random.randint(0,360))
            self.setAllRotation(QVector3D(0, 0, 1.0),ang)
            self.training_target = [np.cos(np.deg2rad(ang)),np.sin(np.deg2rad(ang)),0]

        if(self.running):
            self.startTrainingTimer()


    def startTrainingTimer(self):
        threading.Timer(self.training_change_time,self.trainingCallback).start()
        self.updateTrainingTime()

    def updateTrainingTime(self):
        self.training_change_time = np.random.rand()*(self.training_change_time_max-self.training_change_time_min)+self.training_change_time_min


    def getTargetDir(self):
        return self.training_target


    @QtCore.pyqtSlot()
    def frame_cb(self):
        t = time.time()
        dt = t-self.lastFrameTime
        self.lastFrameTime = t

        self.arrow.updateAnimation(dt)
        self.target.updateAnimation(dt)

        #print("Frame: "+str(dt))

        # TODO:
        #   Camera view
        #       All directions must be visible
        #   animation -> 
        #      set target direction -> arrow wiggle int given direction
        #      set detected direction -> wiggle sphere into vector direction
        #   Training functions
        #       change direction in random intervalls to random directions
        #           Modes: 2D cardinal directions, 2D any direction, 3d cardinal directions, 3d any direction
        #               any direction: continuous direction change; stpwise direction change
        #       function: get current training direction vector
        #       function set current detected direction
        

    def initialiseCamera(self,view, scene):
        # Camera.
        camera = view.camera()
        camera.lens().setPerspectiveProjection(60.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.setPosition(QVector3D(0.0, 0.0, 30.0))
        camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))
        # camera.rotate(QQuaternion.fromAxisAndAngle(QVector3D(0.0, 1.0, 0.0), 10.0))
        # camera.rotate(QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), -10.0))
        # camera.translate( QVector3D(5.0, 5.0, 0.0) )
        

        # For camera controls.
        camController = QOrbitCameraController(scene)
        camController.setLinearSpeed(50.0)
        camController.setLookSpeed(180.0)
        camController.setCamera(camera)


    def createScene(self):
        # Root entity.
        rootEntity = QEntity()

        # Material.
        material = QPhongAlphaMaterial(rootEntity)
        material.setDiffuse(QColor("#DF0000"))
        material.setAmbient(QColor("#FFFFFF"))
        material.setAlpha(0.3)
        material.setBlendFunctionArg( QBlendEquation.BlendFunction.Add )

        material2 = QPhongMaterial(rootEntity)
        material2.setDiffuse(QColor("#AAAAAA"))
        material2.setAmbient(QColor("#FFFFFF"))
        material2.setSpecular(QColor("#000000"))

        self.target = TragetEntity(rootEntity,material2)

        self.arrow = ArrowEntity(rootEntity,material)
        self.arrow.setPosition(8)


        return rootEntity



class ArrowEntity():
    def __init__(self,root,material,arrowLength=5,arrowWidth=4,arrowWidthRatio=0.5,arrowHeightRatio=1):
        self.mat = material

        self.arrowLength=arrowLength
        self.arrowWidth=arrowWidth
        self.arrowWidthRatio=arrowWidthRatio
        self.arrowHeightRatio=arrowHeightRatio

        self.pos_centerDistance = 0
        self.rotAxis = QVector3D(0.0, 0.0, 0.0)
        self.rotAngle = 0.0

        self.coneEntity = None
        self.coneMesh = None
        self.coneTransform = None

        self.cylinderEntity = None
        self.cylinderMesh = None
        self.cylinderTransform = None

        self.ani_enabled = False
        self.ani_dist = 1
        self.ani_freq = 0.7
        self.t_ani = 0

        self.initArrow(root)


    def setAnimation(self,en,dist=1,freq=0.7):
        self.ani_enabled = en
        self.ani_dist = dist
        self.ani_freq = freq
        self.t_ani = 0
        self.updateTransform()


    def updateAnimation(self,dt):
        if(self.ani_enabled):
            self.t_ani += dt
            dPos = np.sin(2*np.pi*self.t_ani*self.ani_freq)*self.ani_dist+self.ani_dist/2
            self.updateTransform(dPos)


    def setPosition(self,pos):
        self.pos_centerDistance = pos
        if(not self.ani_enabled):
            self.updateTransform()

    def setRotation(self,rotAxisVector,rotAngle):
        self.rotAxis = rotAxisVector
        self.rotAngle = rotAngle
        self.updateTransform()

    def updateTransform(self,dPos=0):

        qcone_t = QTransform()
        qcyl_t = QTransform()


        hCone = self.arrowLength*self.arrowHeightRatio

        # qcyl_t.setTranslation(QVector3D(0.0, self.pos_centerDistance+dPos, 0.0))
        # qcone_t.setTranslation(QVector3D(0.0, self.arrowLength/2+hCone/2+self.pos_centerDistance+dPos, 0.0))

        # a = qcyl_t.matrix()
        # a.rotate(self.rotAngle,self.rotAxis)
        # self.cylinderTransform.setMatrix( a )
        # b = qcone_t.matrix()
        # b.rotate(self.rotAngle,self.rotAxis)
        # self.coneTransform.setMatrix(b)

        qcyl_t.setRotation(QQuaternion.fromAxisAndAngle(self.rotAxis, self.rotAngle))
        qcone_t.setRotation(QQuaternion.fromAxisAndAngle(self.rotAxis, self.rotAngle))

        a = qcyl_t.matrix()
        a.translate(QVector3D(0.0, self.pos_centerDistance+dPos, 0.0))
        self.cylinderTransform.setMatrix( a )
        b = qcone_t.matrix()
        b.translate(QVector3D(0.0, self.arrowLength/2+hCone/2+self.pos_centerDistance+dPos, 0.0))
        self.coneTransform.setMatrix(b)


    # def setTranslation(self,posVector):
    #     hCone = self.arrowLength*self.arrowHeightRatio

    #     self.cylinderTransform.setTranslation( posVector )
    #     self.coneTransform.setTranslation( QVector3D(0, self.arrowLength/2+hCone/2, 0)+posVector )


    def initArrow(self,root):
        self.coneEntity = QEntity(root)
        self.coneMesh = QConeMesh(self.coneEntity)
        self.coneMesh.setBottomRadius(self.arrowWidth)
        hCone = self.arrowLength*self.arrowHeightRatio
        self.coneMesh.setLength(hCone)
        #self.coneMesh.setRings(40)
        #self.coneMesh.setSlices(10)

        self.coneTransform = QTransform()

        self.coneEntity.addComponent(self.coneMesh)
        self.coneEntity.addComponent(self.coneTransform)
        self.coneEntity.addComponent(self.mat)

        #coneTransform.setScale3D(QVector3D(1, 1.0, 1))
        #coneTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), 0.0))
        #self.coneTransform.setTranslation(QVector3D(0,13, 0))


        self.cylinderEntity = QEntity(root)
        self.cylinderMesh = QCylinderMesh(self.cylinderEntity)
        self.cylinderMesh.setRadius(self.arrowWidth*self.arrowWidthRatio)
        self.cylinderMesh.setLength(self.arrowLength)

        self.cylinderTransform = QTransform()

        self.cylinderEntity.addComponent(self.cylinderMesh)
        self.cylinderEntity.addComponent(self.cylinderTransform)
        self.cylinderEntity.addComponent(self.mat)


        self.coneTransform.setTranslation( QVector3D(0, self.arrowLength/2+hCone/2, 0) )
        self.updateTransform()




class TragetEntity():
    def __init__(self,root,material,radius=3):

        self.mat = material

        self.radius = radius
        self.rotAxis = QVector3D(0.0, 0.0, 0.0)
        self.rotAngle = 0.0


        self.sphereEntity = None
        self.sphereMesh = None
        self.sphereTransform = None

        self.ani_enabled = False
        self.ani_dist = 1
        self.ani_freq = 2


        self.t_ani = 0

        self.upMoveRatio = 0.25

        self.initTarget(root)


    def setAnimation(self,en,dist=1,freq=2,upMoveRatio=0.25):
        self.ani_enabled = en
        self.ani_dist = dist
        self.ani_freq = freq
        self.upMoveRatio = upMoveRatio
        self.t_ani = 0
        self.updateTransform()


    def updateAnimation(self,dt):

        if(self.ani_enabled):
            T = 1/self.ani_freq
            self.t_ani+=dt
            while(self.t_ani>T):
                self.t_ani-=T

            relT = self.t_ani/T
            if( relT<=self.upMoveRatio ):
                dist = relT/self.upMoveRatio*self.ani_dist
            else:
                dist = self.ani_dist * (1-((relT-self.upMoveRatio)/(1-self.upMoveRatio)))

            #print(str(dist) + ": " + str(relT))

            self.updateTransform(dist)


    def setRotation(self,rotAxisVector,rotAngle):
        self.rotAxis = rotAxisVector
        self.rotAngle = rotAngle
        self.updateTransform()


    def updateTransform(self,dPos=0):

        qcone_t = QTransform()

        qcone_t.setRotation(QQuaternion.fromAxisAndAngle(self.rotAxis, self.rotAngle))

        a = qcone_t.matrix()
        a.translate(QVector3D(0.0, dPos, 0.0))
        self.sphereTransform.setMatrix( a )


    def initTarget(self, root):


        self.sphereEntity = QEntity(root)
        self.sphereMesh = QSphereMesh(self.sphereEntity)
        
        self.sphereMesh.setRadius(self.radius)

        self.sphereTransform = QTransform()

        self.sphereEntity.addComponent(self.sphereMesh)
        self.sphereEntity.addComponent(self.mat)
        self.sphereEntity.addComponent(self.sphereTransform)