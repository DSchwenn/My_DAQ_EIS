from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QWidget, QPushButton, qApp, QLabel, QHBoxLayout, QVBoxLayout, QSplitter
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

# https://stackoverflow.com/questions/48262716/integrating-a-pyqt3d-window-into-a-qmainwindow
# https://doc.qt.io/qtforpython/examples/example_3d__simple3d.html


        

class TrainingModesDirection(Enum):
    DIR_2D_CARDINAL = 0
    DIR_2D_ANY = 1
    DIR_3D_CARDINAL = 2
    DIR_3D_ANY = 3

class TrainingModesChangeType(Enum):
    DIR_CHANGE_CONTINUOUS = 0
    DIR_CHANGE_STEPWISE = 1


class View3D(QWidget):
    def __init__(self):
        super(View3D, self).__init__()
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
        self.training_target = [0,1]
        self.running = True

        self.startTrainingTimer()


    def setAllRotation(self,axis,ang):
        self.arrow.setRotation(axis,ang)
        self.target.setRotation(axis,ang)


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
            self.training_target = [np.cos(np.deg2rad(ang)),np.sin(np.deg2rad(ang))]
        else: # DIR_2D_ANY TODO: implement 3D/ continuous
            ang = float(np.random.randint(0,360))
            self.setAllRotation(QVector3D(0, 0, 1.0),ang)
            self.training_target = [np.cos(np.deg2rad(ang)),np.sin(np.deg2rad(ang))]

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
    


class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        #
        view3d = View3D()
        self.setCentralWidget(view3d)
        self.resize(800,640)
        self.show()


'''
# Approach 2 - A native Qt3DWindow
if __name__ == '__main__':
    #app = QGuiApplication(sys.argv)
    #view = Qt3DWindow()

    #scene = createScene()
    #initialiseCamera(view, scene)

    #view.setRootEntity(scene)

    #view.show()

    app = QApplication(sys.argv)
    view = View3D()
    view.show()

    sys.exit(app.exec_())
'''

# Approach 1 - Integrate Qt3DWindow into a QMainWindow
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())


