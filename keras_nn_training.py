import os
import threading

import time

import numpy as np
import random

from enum import IntEnum

import pickle

#from sklearn.preprocessing import MinMaxScaler, StandardScaler
import keras

from keras_nn_gen_01 import KerasNNGenerator


class NormalizationTypes(IntEnum):
    NORMALIZE_NOT = 0
    NORMALIZE_DEGREE_PHASE = 1
    NORMALIZE_MINMAX_PERSISTENT = 2
    NOMALIZE_STANDARDIZATION_PERSISTENT = 3
    NORMALIZE_MINMAX = 4
    NOMALIZE_STANDARDIZATION = 5
    NORMALIZE_MINMAX_5V = 6

class TrainMyNN(threading.Thread):
    def __init__(self,input_shape,nTargetsInData,nTgt,nnFolder,nnModelFile,dataFolder):
        threading.Thread.__init__(self)

        # load model from here & save weights to here
        self.nn_filename = nnModelFile
        self.data_folder = dataFolder
        self.nn_folder = nnFolder

        self.input_shape = input_shape
        self.nTgt = nTgt
        self.nTargetsInData = nTargetsInData
        self.n_dataset_train = 5
        self.training_time = 20.0
        self.training_intervall = 40.0
        self.lastTime = time.time()
        self.auto_trigger_training = False
        self.backup_start_weights = True
        self.backup_steps = True
        self.randomSetselection = True
        self.batch_size = 64
        self.validation_split = 0.3
        self.workers = 2
        self.train_only_with_n_datasets = True
        self.trigger_training = False
        self.exit_thread = False
        self.alwaysIncludeLatestsDataset = True

        self.model = None
        self.loss = 0
        self.loss_val = 0
        self.epoch_count = 0
        self.session_count = 0

        self.normalization_types = []
        self.normalization_data = []
        self.normalization_initialized = False
        self.trainData = []
        self.trainLabels = []

        self.checkInitialization()
        self.loadModel()

        self.start()



    def setTiming(self,ttime,tintervall,autoTrigger = True):
        self.training_time = ttime
        self.training_intervall = tintervall
        self.auto_trigger_training = autoTrigger
        self.lastTime = time.time()


    def checkInitialization(self):
        self.normalization_initialized = self.loadNormnalizationData()

    def loadModel(self):
        filePath = os.path.join(self.nn_folder, self.nn_filename)
        self.model = keras.models.load_model(filePath)
    
    def saveModel(self):
        filePath = os.path.join(self.nn_folder, self.nn_filename)
        keras.models.save_model(self.model,filePath)

    def defineDataNormalization(self,types):
        self.normalization_types = types

    def triggerTraining(self):
        self.trigger_training = True
        self.lastTime = time.time()

    def startAutoTriggeredTraining(self):
        self.auto_trigger_training = True

    def doOfflineTraining(self,relTest,epochs):
        # check datasets - reserve some for testing, train with the rest -> continuously with all data for given number of epochs;
        # requires normalizaton initialization

        # TODO: get data file number, remove & note relTest fraction - set self.n_dataset_train 
        n = self.getNDataSets()
        n1 = self.n_dataset_train
        self.n_dataset_train = int(n-n*relTest)
        self.prepareData()
        self.runTraining(epochs)
        self.n_dataset_train = n1
        self.saveModelWeights()


    def calculateSingleOutput(self,dataIn):
        data = self.normalizeDataset(self,dataIn)
        predictions = self.model.predict(data)
        return predictions

    def prepareData(self):
        setList = self.getDataSets() # TODO?: always include newest set?
        if( len(setList)<1 ):
            return False

        # load all sets
        data = self.loadDataSets(setList)

        # Normalize data
        data = self.normalizeDataset(data)

        # generate input formt ~ timesteps
        (self.trainData,self.trainLabels) = self.generateTrainingSets(data)

        return True


    def runTraining(self,epochs=3):
        # continue for number of epochs estimated to fill given time - whenm finished check if theres more time - recalculate time per epoch -> maybe train some more
        ep2 = self.epoch_count + epochs
        self.model.fit(self.trainData, self.trainLabels , initial_epoch = self.epoch_count , epochs = ep2, batch_size = self.batch_size, validation_split = self.validation_split, workers = self.workers) 
        self.epoch_count = ep2

    def getNDataSets(self):
        flist = os.listdir(self.data_folder) # from the folder get a list of filenames
        dat = [".train_dat" in f for f in flist]
        num = np.sum(dat)
        return num

    def getDataSets(self):
        flist = os.listdir(self.data_folder) # from the folder get a list of filenames
        dat = [".train_dat" in f for f in flist]
        num = np.sum(dat)
        if(self.train_only_with_n_datasets and num<self.n_dataset_train or num<1):
            return []
        ixi = np.nonzero(dat)
        ixi = ixi[0]

        if(self.randomSetselection):
            nFile = self.n_dataset_train
            if(self.alwaysIncludeLatestsDataset):
                ixi2 = random.sample(ixi[0:-1].tolist(), nFile-1)
                ixi2.append(ixi[-1])
            else:
                ixi2 = random.sample(ixi.tolist(), nFile)
        else:
            ixi2 = ixi[-nFile:]

        setList = [flist[ixi2[i]] for i in range(len(ixi2))]

        return setList


    def loadDataSets(self,fileList):
         # read in data - panda? -> normalize based on norm_types
        dat = []
        for f in fileList:
            filePath = os.path.join(self.data_folder, f)
            tDat = np.load(filePath)
            dat.append(tDat)

        return dat


    def normalizeDataset(self,dataIn):

        datNorm = []

        for data in dataIn:
            shp = np.shape(data) # full dataset according to types

            t_datNorm = np.zeros(shp)
            #if( self.input_shape[1] == shp[1] and shp[1] == len(self.normalization_types) ):
            for i,tp in enumerate(self.normalization_types):
                if(tp == NormalizationTypes.NORMALIZE_DEGREE_PHASE):
                    if(not self.normalization_initialized):
                        self.normalization_data.append([0,360])
                    t_datNorm[:,i] = self.normalizeMinMax(data[:,i],self.normalization_data[i])
                elif(tp==NormalizationTypes.NORMALIZE_MINMAX_PERSISTENT):
                    if(not self.normalization_initialized):
                        ttdat = dataIn[0][:,i]
                        for k in range(1,len(dataIn)):
                            ttdat = np.vstack((ttdat,dataIn[k][:,i]))
                        self.normalization_data.append( [np.min(ttdat),np.max(ttdat)] )
                    t_datNorm[:,i] = self.normalizeMinMax( data[:,i], self.normalization_data[i] )
                elif(tp==NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT):
                    if(not self.normalization_initialized):
                        ttdat = dataIn[0][:,i]
                        for k in range(1,len(dataIn)):
                            ttdat = np.vstack((ttdat,dataIn[k][:,i]))
                        self.normalization_data.append( [np.mean(ttdat),np.std(ttdat)] )
                    t_datNorm[:,i] = self.normalizeNormal( data[:,i], self.normalization_data[i] )
                elif(tp==NormalizationTypes.NORMALIZE_MINMAX):
                    if(not self.normalization_initialized):
                        self.normalization_data.append( [np.min(data[:,i]),np.max(data[:,i])] )
                    else:
                        self.normalization_data[i] = [np.min(data[:,i]),np.max(data[:,i])]
                    t_datNorm[:,i] = self.normalizeMinMax( data[:,i], self.normalization_data[i] )
                elif(tp==NormalizationTypes.NOMALIZE_STANDARDIZATION):
                    if(not self.normalization_initialized):
                        self.normalization_data.append( [np.mean(data[:,i]),np.std(data[:,i])] )
                    else:
                        self.normalization_data[i] = [np.mean(data[:,i]),np.std(data[:,i])]
                    t_datNorm[:,i] = self.normalizeNormal( data[:,i], self.normalization_data[i] )
                elif(tp==NormalizationTypes.NORMALIZE_MINMAX_5V):
                    if(not self.normalization_initialized):
                        self.normalization_data.append([0,5.0])
                    t_datNorm[:,i] = self.normalizeMinMax(data[:,i],self.normalization_data[i])
                else:# no norm
                    if(not self.normalization_initialized):
                        self.normalization_data.append([1])
                    t_datNorm[:,i] = data[:,i]
            datNorm.append(t_datNorm)
        if(not self.normalization_initialized):
            self.saveNormalizationData()
        self.normalization_initialized = True
        return datNorm

    def generateTrainingSets(self,data):
        trainLabels = []
        trainData = []

        self.nTgt
        self.nTargetsInData
        self.input_shape # of in data, not of in NN self.input_shape[1]-=self.nTargetsInData -> input shape NN
        nPerSet = self.input_shape[0]

        for dat in data:
            shp = np.shape(dat)
            for i in range(nPerSet,shp[0]):
                trainData.append(dat[i-nPerSet:i, self.nTargetsInData:])
                trainLabels.append(dat[i, 0:self.nTgt])

        return (np.array(trainData),np.array(trainLabels))


    def normalizeMinMax(self,dat,minmax):
        return (dat-minmax[0])/(minmax[1]-minmax[0])

    def normalizeNormal(self,dat,meanstd):
        return (dat-meanstd[0])/meanstd[1]

    # def inverseNormalizeDataset(self,data): # not needed since targets are normal vectors - need no normalization...
    #     1 # reverse
    

    def saveNormalizationData(self):
        fileName = self.getNormalizerFilename()
        filePath = os.path.join(self.nn_folder, fileName)
        normTypes = [en.value for en in self.normalization_types]
        with open(filePath, 'wb') as f: 
            mylist = [normTypes,self.normalization_data]
            pickle.dump(mylist, f)
    
    def loadNormnalizationData(self):
        fileName = self.getNormalizerFilename()
        filePath = os.path.join(self.nn_folder, fileName)
        if( os.path.isfile(filePath) ):
            with open(filePath, 'rb') as f: 
                mylist = pickle.load(f)
            normTypes = mylist[0]
            self.normalization_data = mylist[1]
            self.normalization_types = [ NormalizationTypes(nt) for nt in normTypes]
            return True
        return False

    def getWeightsFilename(self):
        if(self.session_count>0):
            return self.nn_filename + "_" + str(self.session_count).zfill(3) + ".weights"
        else:
            return self.nn_filename + "_.weights" # generate according to NN model filename

    def saveModelWeights(self):
        # in NN folder
        fn = self.getWeightsFilename()
        filePath = os.path.join(self.nn_folder, fn)
        self.model.save_weights( filePath )
        
    def loadNewestWeights(self):
        flist = os.listdir(self.nn_folder) # from the folder get a list of filenames
        dat = [".weights" in f for f in flist]
        ixi = np.nonzero(dat)
        fList2 = [flist[ixi[i]] for i in range(len(ixi))]
        fpList2 = [os.path.join(self.nn_folder, f) for f in fList2]
        ftm = [os.path.getmtime(fp) for fp in fpList2]
        ix = ftm.index(max(ftm))
        lastWeightsFn = fpList2[ix]

        self.model.load_weights(lastWeightsFn)

    def getTrainingStatus(self):
        return (self.loss,self.loss_val) 

    def getNormalizerFilename(self):
        return self.nn_filename + "_.normal"

    def printTrainingStatus(self):
        (loss,loss_val) = self.getTrainingStatus()
        print("After " + str(self.session_count) + "sessions, trained for " + str(self.epoch_count) + " epochs, los/ loss_vall are: " + str(loss) + "/" + str(loss_val) )


    def timedTrainingSession(self):

        if(not self.prepareData() ): # same labes/ data per session - only if enough.
            return

        if(self.backup_steps or (self.session_count<=0 and self.backup_start_weights) ):
            self.saveModelWeights()
        
        t1 =  time.time()
        nStart = 2
        self.runTraining(nStart)
        t2 = time.time()
        print("Trained " + str(nStart) + " epochs in " + str(t2-t1) + "seconds")
        nCum = nStart
        for i in range(2):
            dt = (t2-t1)/(nCum)
            tRest = self.training_time-(dt*nCum)
            nRest = int(tRest/dt)
            print(str(nRest)+" more...")
            nCum += nRest
            if(nRest>0):
                self.runTraining(nRest)
            t2 = time.time()
            print("Trained " + str(nCum) + " epochs in " + str(t2-t1) + "seconds")


    def run(self):
        while(not self.exit_thread):
            if(self.trigger_training or (self.auto_trigger_training and time.time()-self.lastTime>self.training_intervall) ):
                self.lastTime = time.time()
                self.timedTrainingSession()
                self.session_count += 1
            time.sleep(0.5)

    def killThread(self):
        self.exit_thread = True
        self.join()

        # traing function
        # offlibne traINING
        # content here
        # make suitable recording (develop in UI channel selection & recording...)
        # test
        # integrate in UI




if __name__ == '__main__':

    dataShape = [100,14]
    trainingNum = 3
    inputShape = dataShape
    nTargets = 2

    if 0:
        inputShape[1] = inputShape[1]-trainingNum
        kmg = KerasNNGenerator()
        kmg.createNeuralNet(inputShape, nTargets)
        nnmdl = kmg.saveNeuralNet()
        print(nnmdl)
    else:
        nnmdl = "20220924_2148594_64_0.2.nn_model"
    tnn = TrainMyNN(dataShape,trainingNum,nTargets,".\\NNModelData",nnmdl,".\\TrainingData")
    tnn.defineDataNormalization(
        [NormalizationTypes.NORMALIZE_NOT,NormalizationTypes.NORMALIZE_NOT,NormalizationTypes.NORMALIZE_NOT,
        NormalizationTypes.NORMALIZE_MINMAX_5V,NormalizationTypes.NORMALIZE_MINMAX_5V,NormalizationTypes.NORMALIZE_MINMAX_5V,
        NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT,NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT,NormalizationTypes.NORMALIZE_DEGREE_PHASE,NormalizationTypes.NORMALIZE_DEGREE_PHASE,
        NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT,NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT,NormalizationTypes.NORMALIZE_DEGREE_PHASE,NormalizationTypes.NORMALIZE_DEGREE_PHASE]
        )
    #tnn.setTiming(30,40,True)
    tnn.doOfflineTraining(0.25,25)
    #tnn.triggerTraining()

