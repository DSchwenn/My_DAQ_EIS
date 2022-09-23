import os
import threading

import time

import numpy as np
import random

from enum import Enum

import pickle

#from sklearn.preprocessing import MinMaxScaler, StandardScaler

import keras

class NormalizationTypes(Enum):
    NORMALIZE_NOT = 0
    NORMALIZE_DEGREE_PHASE = 1
    NORMALIZE_MINMAX_PERSISTENT = 2
    NOMALIZE_STANDARDIZATION_PERSISTENT = 3
    NORMALIZE_MINMAX = 4
    NOMALIZE_STANDARDIZATION = 5

class TrainMyNN(threading.Thread):
    def __init__(self,input_shape,nnFolder,nnModelFile,dataFolder):
        # load model from here & save weights to here
        self.nn_filename = nnModelFile
        self.data_folder = dataFolder
        self.nn_folder = nnFolder

        self.input_shape = input_shape
        self.n_dataset_train = 5
        self.training_time = 20.0
        self.auto_trigger_training = False
        self.backup_start_weights = True
        self.backup_steps = True
        self.randomSetselection = True
        self.batch_size = 64
        self.train_only_with_n_datasets = True
        self.trigger_training = False
        self.exit_thread = False

        self.model = None
        self.loss = 0
        self.loss_val = 0
        self.epoch_count = 0
        self.session_count = 0

        self.normalization_types = []
        self.normalization_data = []
        self.normalization_initialized = False

        self.checkInitialization()
        self.loadModel()

        self.start()


    def checkInitialization(self):
        self.normalization_initialized = self.loadNormnalizationData(self)

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

    def startAutoTriggeredTraining(self):
        self.auto_trigger_training = True

    def doOfflineTraining(self,relTest,epochs):
        # check datasets - reserve some for testing, train with the rest -> continuously with all data for given number of epochs;
        # requires normalizaton initialization
        self.runTraining(epochs)

    def calculateSingleOutput(self,dataIn):
        data = self.normalizeDataset(self,dataIn)
        predictions = self.model.predict(data)
        return predictions

    def runTraining(self,startNepoch=3):
        # check number of avbailable datasets
        setList = self.getDataSets()
        if( len(setList)<1 ):
            return

        # load all sets
        data = self.loadDataSets(setList)

        # Normalize data
        self.normalizeDataset(data)

        # backup weights if set - differentiate between first save (session count) and continuous training
        self.saveModelWeights()

        # check time between eochs... cotinue with last epoch if nbot zero
        self.model.fit(features_set, labels, epochs = 5, batch_size = 32, validation_split = 0.3, workers = 2)

        # continue for number of epochs estimated to fill given time - whenm finished check if theres more time - recalculate time per epoch -> maybe train some more
        self.model.fit(features_set, labels, initial_epoch = 5, epochs = 10, batch_size = 32, validation_split = 0.3, workers = 2) 


    def getDataSets(self):
        flist = os.listdir(self.data_folder) # from the folder get a list of filenames
        dat = [".train_dat" in f for f in flist]
        num = np.sum(dat)
        if(self.train_only_with_n_datasets and num<self.n_dataset_train or num<1):
            return []
        ixi = np.nonzero(dat)

        if(self.randomSetselection):
            ixi = random.sample(ixi, self.n_dataset_train)
        else:
            ixi = ixi[-self.n_dataset_train:]

        setList = [flist[ixi[i]] for i in range(len(ixi))]

        return setList



    def loadDataSets(self,fileList):
         # read in data - panda? -> normalize based on norm_types
        dat = np.array([])
        for f in fileList:
            filePath = os.path.join(self.data_folder, f)
            tDat = np.fromfile(filePath,dtype=float)
            if(np.size(dat)<1):
                dat = tDat
            else:
                dat = np.vstack(dat,tDat)

        return dat


    def normalizeDataset(self,data):
        shp = np.shape(data) # full dataset according to types

        datNorm = np.zeros(shp)
        if( self.input_shape[1] == shp[1] and shp[1] == len(self.type) ):
            for i,tp in enumerate(self.normalization_types):
                if(tp == NormalizationTypes.NORMALIZE_DEGREE_PHASE):
                    if(not self.normalization_initialized):
                        self.normalization_data.append([0,360])
                    datNorm[:,i] = self.normalizeMinMax(data[:,i],self.normalization_data[i])
                elif(tp==NormalizationTypes.NORMALIZE_MINMAX_PERSISTENT):
                    if(not self.normalization_initialized):
                        self.normalization_data.append( [np.min(data[:,i]),np.max(data[:,i])] )
                    datNorm[:,i] = self.normalizeMinMax( data[:,i], self.normalization_data[i] )
                elif(tp==NormalizationTypes.NOMALIZE_STANDARDIZATION_PERSISTENT):
                    if(not self.normalization_initialized):
                        self.normalization_data.append( [np.mean(data[:,i]),np.std(data[:,i])] )
                    datNorm[:,i] = self.normalizeNormal( data[:,i], self.normalization_data[i] )
                elif(tp==NormalizationTypes.NORMALIZE_MINMAX):
                    if(not self.normalization_initialized):
                        self.normalization_data.append( [np.min(data[:,i]),np.max(data[:,i])] )
                    else:
                        self.normalization_data[i] = [np.min(data[:,i]),np.max(data[:,i])]
                    datNorm[:,i] = self.normalizeMinMax( data[:,i], self.normalization_data[i] )
                elif(tp==NormalizationTypes.NOMALIZE_STANDARDIZATION):
                    if(not self.normalization_initialized):
                        self.normalization_data.append( [np.mean(data[:,i]),np.std(data[:,i])] )
                    else:
                        self.normalization_data[i] = [np.mean(data[:,i]),np.std(data[:,i])]
                    datNorm[:,i] = self.normalizeNormal( data[:,i], self.normalization_data[i] )
                else:# no norm
                    datNorm[:,i] = data[:,i]
        
        self.normalization_initialized = True

    def normalizeMinMax(self,dat,minmax):
        return (dat-minmax[0])/(minmax[1]-minmax[0])

    def normalizeNormal(self,dat,meanstd):
        return (dat-meanstd[0])/meanstd[1]

    # def inverseNormalizeDataset(self,data): # not needed since targets are normal vectors - need no normalization...
    #     1 # reverse
    

    def saveNormalizationData(self):
        fileName = self.getNormalizerFilename()
        filePath = os.path.join(self.nn_folder, fileName)
        with open(filePath, 'wb') as f: 
            mylist = [self.normalization_types,self.normalization_data]
            pickle.dump(mylist, f)
    
    def loadNormnalizationData(self):
        fileName = self.getNormalizerFilename()
        filePath = os.path.join(self.nn_folder, fileName)
        if( os.path.isfile(filePath) ):
            with open(fileName, 'rb') as f: 
                mylist = pickle.load(f)
            self.normalization_types  = mylist[0]
            self.normalization_data = mylist[1]
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



    def run(self):
        # traing function
        # offlibne traINING
        # content here
        # make suitable recording (develop in UI channel selection & recording...)
        # test
        # integrate in UI