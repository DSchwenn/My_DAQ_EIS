

import threading
from datetime import datetime
import time

import os.path
from os import path

import numpy as np

from channel_sample_info import *

# get allnon raw  channels from data distreibution ni_datahandler
# gets list of what to write from sampleInfo (must be update from UI: Sample info recipient update & additional sub-channel data info)
#       get from ni_datahandler all data for all channels of which data was selected
#       Subselections ( which part of multipart data incl complex) must also be available
#           per channel N times 2 ids...? via sample info? must stay the same once started
# may not change list while recording
# accumulates data until tiumelimit in numpy array in memory
# saves it so it can be read by the training software


class TrainingFileWriter(threading.Thread):
    def __init__(self,plotIndex,sampleInfo,pth=""):
        threading.Thread.__init__(self)

        self.plotIndex = plotIndex
        self.sampleInfo = sampleInfo
        self.is_recording = False

        self.datasetLength = 30.0
        self.samples_per_block = self.sampleInfo.getSampleRate()*self.datasetLength

        self.start_time = "" # for filenames
        self.set_counter = 0 # file number N
        self.set_sample_counter = 0 # for when to save
        self.subchannel_selection = [] # per channel N times 2 ids...? via sample info? must stay the same once started

        self.sampleBuffer = []
        self.blockData = np.array([])
        self.idLst = []
        self.idLst_reordered = []
        self.recieving = False
        self.end_thread = False
        self.path = pth
        self.start()

        self.nnInputSize = [0,0]
        self.lastSampleData = np.array([])
    
    def setNNInputSize(self,inSize):
        self.nnInputSize = inSize

    def backupLastSampleData(self):
        self.lastSampleData = self.blockData[-self.nnInputSize[0]:,:] 

    def getLastDataSet(self):
        if( self.set_sample_counter >= self.nnInputSize[0] ):
            return self.blockData[self.set_sample_counter-self.nnInputSize[0]:self.set_sample_counter,:]
        else:
            return self.lastSampleData


    def settings(self,recLength):
        self.datasetLength = recLength

    def setPath(self,pth):
        if(pth[-1]!='\\' and pth[-1]!='/'):
            pth += "\\"
        if(os.path.isdir(pth)):
            self.path = pth
    
    def getPath(self):
        return self.path

    def killThread(self): # startRecording after killing will lead to exception
        self.stopRecording()
        self.end_thread = True

    def getPlotIndex(self):
        return self.plotIndex
    
    def generateFilename(self):
        now = datetime.now() 
        if(len(self.start_time)<1):
            self.start_time = now.strftime("%Y%m%d_%H%M%S")
        fn = self.start_time + "_" + str(self.set_counter).zfill(4) + ".train_dat"
        fnp = os.path.join(self.path,fn)

        return fnp

    def startRecording(self):
        if(self.is_recording):
            return
        print("Start Training Rec " + str(self.plotIndex))

        self.samples_per_block = int(self.sampleInfo.getprocessSR()*self.datasetLength)
        self.idLst = self.sampleInfo.getTrainIdList()

        chnm = [l[0] for l in self.idLst]
        isphase = [l[2] for l in self.idLst]
        useIt = [l[3] for l in self.idLst]
        self.idLst_reordered = [np.array(chnm),np.array(isphase),np.array(useIt)]

        chnEn = [l[3] for l in self.idLst]
        nCh = int(np.sum(np.array(chnEn)))
        self.blockData = np.zeros([self.samples_per_block,nCh])
        self.usedChannels = self.sampleInfo.getRecipiensUsedChannels(self.plotIndex)

        self.start_time = "" # for filenames
        self.set_counter = 0 # file number N
        self.set_sample_counter = 0 # for when to save

        self.generateFilename() # to save data string

        self.is_recording = True


    def stopRecording(self):
        if(not self.is_recording ):
            return
        print("Stopping Training Rec " + str(self.plotIndex))
        # stop when device is stopped (-> new file when restarted)
        self.is_recording = False


    def updateData(self,data):
        # start new recording if its not running; 
        # just copy data to buffer here
        if( self.sampleInfo.doesChannelNeedUpdate(self.plotIndex) ):
            self.sampleInfo.resetChannelUpdateFlag(self.plotIndex)
            rec = self.sampleInfo.getChannelLive(self.plotIndex)
            if(self.is_recording and not rec): # stop
                self.stopRecording()
                self.sampleBuffer = []
            elif(not self.is_recording and rec): # start
                self.startRecording()
            self.is_recording = rec

        if(not self.is_recording):
            return

        self.recieving = True
        self.sampleBuffer.append(data.copy())
        self.recieving = False

    def run(self):
        # write from buffer to file
        # only running wile recording is active.
        # Assume: if raw, each data list element contains row data - otherwise its considered channel data - see size below
        while(not self.end_thread):
            time.sleep(0.1)
            while(self.is_recording):
                time.sleep(0.05)

                if(len(self.sampleBuffer)>0):
                        self.writeData()

                    #print("Writer " + str(self.plotIndex) + ": " + str(np.shape(tDt)))
                    #for dt in tDt:
                    #    print(  str(np.shape(dt)) + " " + str(np.size(dt)) )
                    # TODO: write to file


    def getChnDat(self,ch):
        
        ixi = self.idLst_reordered[0] == ch
        chInUse = self.idLst_reordered[2][ixi]
        isComplex = self.idLst_reordered[1][ixi]
        isComplex = isComplex[0]>=0

        return (chInUse,isComplex)

    def writeData(self):

        while( len(self.sampleBuffer)>0 ):
            tDt = self.sampleBuffer.pop(0)
            cnt = 0 # x-counter

            for i,dt in enumerate(tDt):
                if(np.size(dt)<2):
                    dt = [dt]
                ch = self.usedChannels[i]
                (chInUse,isComplex) = self.getChnDat(ch)
                if(isComplex):
                    cCnt = 0
                    for el in dt: # first ABS
                        if(chInUse[cCnt]):
                            self.blockData[self.set_sample_counter,cnt] = np.abs(el)
                            cnt+=1
                        cCnt+=1 
                    for el in dt: # seconf phase
                        if(chInUse[cCnt]):
                            self.blockData[self.set_sample_counter,cnt] = np.angle(el)
                            cnt+=1
                        cCnt+=1
                else:
                    for k,el in enumerate(dt):
                        if(chInUse[k]):
                            self.blockData[self.set_sample_counter,cnt] = el
                            cnt+=1

            self.set_sample_counter += 1 # y-counter
            #if( self.set_sample_counter % 100 <= 0 ):
            #    print(self.set_sample_counter/100)

            if(self.set_sample_counter>=self.samples_per_block):
                self.backupLastSampleData()
                np.save(self.generateFilename(),self.blockData)
                np.save
                self.set_sample_counter = 0
                self.set_counter += 1


            # TODO: select channels/ extract data according to setting in sample info
            #       add to np array -> check sample number -> write  .tofile/ increment/reset count

# Writer 2: (3,)
# (4,) 4
# () 1
# () 1

# Writer 3: (2, 150)
# (150,) 150
# (150,) 150