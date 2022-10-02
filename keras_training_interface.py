

from channel_sample_info import *
from keras_nn_training import TrainMyNN, NormalizationTypes


# TODO: ? additional functions?: Manual trigger training button/ with epoch num?
#       When continuing: load latest weights***
#       on/off/ update rate of UI direction feedback

# call setupDataSizes, setupModel, setupMeta, setupParameter -> running / or start after with runTraining

class KerasTrainingInterface():
    def __init__(self,targetMode,nTargetsinData,nData,nTimestep,sampleinfo,nnPath=".\\NNModelData",trainPath=".\\TrainingData"):
        self.sampleinfo = sampleinfo
        self.nnPath = nnPath
        self.trainPath = trainPath
        self.nn_training = None

        self.targetMode = targetMode
        self.nTargetsinData = nTargetsinData
        self.nTimestep = nTimestep
        self.nData = nData

        self.testingOnly = False
        self.vizOut = False



    def setupDataSizes(self,targetMode,nTargetsinData,nData,nTimestep):
        self.targetMode = targetMode
        self.nTargetsinData = nTargetsinData
        self.nTimestep = nTimestep
        self.nData = nData

    def setupMeta(self,backupWeights=True,backupSteps=True,continueTraining=True,visualizeOutout=False,onlyTesting=False):
        self.testingOnly = onlyTesting
        self.vizOut = visualizeOutout
        if(onlyTesting):
            self.nn_training.runTraining(False)
        # continueTraining=True -> loadNewestWeights()
        self.nn_training.setMetaData(backupWeights,backupSteps,continueTraining)
    
    def updateUIPrediction(self,trainingFileWriter,ui3D):
        # TODO: call getModelOutput -> set direction to ui3D; TODO: ui3D setter function
        (dat,count) = self.getModelOutput(trainingFileWriter)
        if(not dat is None):
            ui3D.setPredictedDirection(True,dat,count)
        #print("Prediction update: " + str(dat))

    def getModelOutput(self,trainingFileWriter): # result as feedback to the 3D UI
        (dat,count) = self.nn_training.predictOutput(trainingFileWriter.getLastDataSet()) # TODO: in file writer update lastSet when writing - but if enough data is there use from data buffer.
        return (dat,count)

    def runTraining(self,doRun=True):
        self.nn_training.runTraining(doRun)

    def setupModel(self,pathname):
        self.setupExistingModel(pathname)

    def setupParameter(self,trainingTime,trasiningInterval,minTrainSetNum,useRandomTrainSets=True,doAutoTriggeredTraining=True):
        self.nn_training.specifyTrainingSetNumber(minTrainSetNum)
        self.nn_training.specifyRandomSetSel(useRandomTrainSets)
        self.nn_training.setTiming(trainingTime,trasiningInterval,doAutoTriggeredTraining)

    def haltTraining(self):
        self.nn_training.switchAutoTrain(False)

    def setupExistingModel(self,pathname):
        self.nn_training  = TrainMyNN([self.nTimestep,self.nData],self.nTargetsinData,self.targetsFromMode(self.targetMode),".\\NNModelData",pathname,".\\TrainingData")
        self.setNormalizationModes()


    def setNormalizationModes(self):
        # determine according to sampleinfo
        idLst = self.sampleinfo.getTrainIdList()
        normType = []

        for ids in idLst:
            if(ids[3]):
                normType.append( self.getNormFromType(ids[1],ids[2]) )
        
        if(not self.nn_training is None):
            self.nn_training.defineDataNormalization(normType)

        return normType


    def targetsFromMode(self,targetMode):
        return 2


    def getNormFromType(self,tp,cpl):
        # as in ChannelSampleInfo.type2num
        if(tp==1): # FFT
            if(cpl==0):
                return NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT
            elif(cpl==1):
                return NormalizationTypes.NORMALIZE_DEGREE_PHASE
        elif(tp==2): # correlation
            return NormalizationTypes.NORMALIZE_NOT
        elif(tp==3): # Mean
            return NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT
        elif(tp==4): # Max
            return NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT
        elif(tp==5): # min
            return NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT
        elif(tp==6): # divide
            return NormalizationTypes.NORMALIZE_NOT
        elif(tp==7): # serial
            return NormalizationTypes.NORMALIZE_NOT
        elif(tp==8): # Accell etc.
            return NormalizationTypes.NORMALIZE_MINMAX_5V
        elif(tp==9): # Training target
            return NormalizationTypes.NORMALIZE_NOT


    def killThread(self):
        if(not self.nn_training is None):
            self.nn_training.killThread()
            self.nn_training.join()


