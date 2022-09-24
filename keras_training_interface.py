

from channel_sample_info import *
from keras_nn_training import TrainMyNN, NormalizationTypes


# TODO: ? additional functions?: Manual trigger training button/ with epoch num?
#       When continuing: load latest weights***
#       on/off/ update rate of UI direction feedback

class KerasTrainingInterface():
    def __init__(self,targetMode,nTargetsinData,nData,nTimestep,sampleinfo,nnPath=".\\NNModelData",trainPath=".\\TrainingData"):
        self.sampleinfo = sampleinfo
        self.nnPath = nnPath
        self.trainPath = trainPath
        self.nn_training = None

    def setupMeta(self,backupWeights=True,backupSteps=True,continueTraining=True,VisualizeOutout=False,OnlyTesting=False):
        1
    
    def updateUIPrediction(self,trainingFileWriter,ui3D):
        1

    def getModelOutput(self,trainingFileWriter): # result as feedback to the 3D UI
        1

    def setupModel(self,pathname,modelOrSkript,inputSize):
        1

    def setupParameter(self,trainingTime,trasiningInterval,minTrainSetNum,useRandomTrainSets=True,doAutoTriggeredTraining=True):
        1

    def setupExistingModel(self):
        1

    def setupModelGenerationSkript(self):
        1

    def setNormalizationModes(self):
        1 # determine according to sampleinfo

