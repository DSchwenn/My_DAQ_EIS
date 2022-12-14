
from cmath import nan
import time, threading

from qt_matlibplot_handler import *
from ni_reader import *
from ni_writer import NiWriter
from function_gen import *

from channel_sample_info import *
from my_data_processing import *
from data_history_storage import *

#import numpy as np



class NiDataHandler:
    def __init__(self,sampleInfo,serialCom = None,trainingUI=None):
        self.dataCallbacks = []
        self.dataCallbacksChannels = []
        self.sampleRate = 100.0
        self.sampleSize = 1000
        self.v_range = 10
        self.ch_ref_type = []
        self.ni_reader = None
        self.sampling = False
        self.dat_type = []
        self.channelIxi = []
        self.channelRefIxi = []

        self.wSampleRate = 100.0
        self.wData = []
        self.wDevice = ''
        self.wChannels = []
        self.ni_writer = None
        self.writing = False

        self.sampleInfo = sampleInfo

        self.ms_init = int(round(time.time() * 1000))
        self.histDat = DataHistoryStorage(sampleInfo,6)

        self.ser_com = serialCom
        self.trainUI = trainingUI


    # override utilizting self.sampleInfo
    def setupSampling_si(self,ch_ref_type):
        rate = self.sampleInfo.getSampleRate()
        sample_size = self.sampleInfo.getDataSize()
        v_range = self.sampleInfo.getVRange()
        self.setupSampling(rate,sample_size,ch_ref_type,v_range)

    def setupSampling(self,rate,sample_size,ch_ref_type,v_range):
        print("Sample setup: " + str(sample_size) + " " + str(rate))
        self.sampleRate = rate
        self.sampleSize = sample_size
        self.ch_ref_type = ch_ref_type
        self.v_range = v_range

    def setupSampling(self,rate,sample_size,ch_ref_type,v_range):
        print("Sample setup: " + str(sample_size) + " " + str(rate))
        self.sampleRate = rate
        self.sampleSize = sample_size
        self.ch_ref_type = ch_ref_type
        self.v_range = v_range

    # override utilizting self.sampleInfo
    def setupWriting_si(self, channels):
        device = self.sampleInfo.getDevice()
        self.setupWriting(device, channels)

    def setupWriting(self, device, channels):
        self.wDevice = device
        self.wChannels = channels
        
    def setupWriting_fg(self):
        device = self.sampleInfo.getDevice()
        fg = self.sampleInfo.getFunctionGen()
        channels = fg.availableChannelList()
        self.setupWriting(device, channels)

    def startWriting(self):
        if( self.writing ):
            return 0
        self.writing = True
        fg = self.sampleInfo.getFunctionGen()
        self.ni_writer = NiWriter(fg.getSampleRate(),fg.getSignals(),self.wDevice ,self.wChannels)
        self.ni_writer.startWriting()

    def startSamplingAndWriting(self):
        print("start sampling...")
        self.startSampling()
        print("start writing...")
        self.startWriting()
        print("running...")


    def startSampling(self):
        if( self.sampling ):
            return 0
        self.sampling = True
        
        self.histDat.clearAllData()
        
        chn = []
        ref = []
        realChanDict = [[],[]]
        self.channelIxi = []
        self.channelRefIxi = []
        self.dat_type = []
        for i,lne in enumerate(self.ch_ref_type):
            tpe = self.sampleInfo.type2num(lne[2])
            ix = -1
            if( lne[0] in chn): # only add channels once...
                ix = chn.index(lne[0])
            elif( (not "Corr" in lne[0]) and (not "Div" in lne[0]) and (not "Ser" in lne[0]) and (not "Train" in lne[0])): # if correlation -> channel is not for reading
                ix = len(chn)
                chn.append(lne[0])
                ref.append(lne[1])
            elif( "Ser" in lne[0]):
                ix = lne[3][0]
            (refIx,realChanDict) = self.correctRefix(realChanDict,lne[0],lne[3],i,ix)

            self.channelIxi.append( ix )
            self.channelRefIxi.append( refIx )
            self.dat_type.append(tpe)
        # self.channelIxi for distribution; only first ref type will be acknowledged
        # only channels in chn will be sampled
        # chanel index for distribution according to order in self.ch_ref_type

        self.ni_reader = NiReader(self.sampleRate,self.sampleSize,chn,ref,self.v_range)
        self.ni_reader.start()
        while( not self.ni_reader.is_running ):
            time.sleep(0.05)
        self.updateData()
        return 1

    def correctRefix(self,realChanDict,tpe,chRef,i,ix): # refIx must matchj the index in the data later recieved by distributeData...
        # TODO: does this still work with double ref...? "Corr"?
        refIx = chRef
        if( len(refIx)==1 and (not "Corr" in tpe) and (not "Div" in tpe) and (not "Ser" in tpe) and (not "Train" in tpe)):
                realChanDict[0].append(i)
                realChanDict[1].append(ix)
                if( refIx[0] in realChanDict[0] ):
                    tix = realChanDict[0].index(refIx[0])
                    refIx = [realChanDict[1][tix]]
        return (refIx,realChanDict)

    def stopSampling(self):
        if( not self.sampling ):
            return
        self.ni_reader.stopReading()

        while( not self.ni_reader.isStopped() ):
            time.sleep(0.05)

        del self.ni_reader
        self.ni_reader = None
        self.sampling = False

    def stopWriting(self):
        if( not self.writing ):
            return
        self.ni_writer.stopWriting()
        del self.ni_writer
        self.ni_writer = None
        self.writing = False

    def stopSamplingAndWriting(self):
        self.stopSampling()
        self.stopWriting()

    def isRunnung(self):
        return (self.writing or self.sampling)



    def distributeData(self,dat,datSerial,datTrain):
        #1 # TODO: process channels according to ch_ref_type[2] & distribute
        #print(str(type(dat)) + " " + str(dat.size) + " " + str(dat.shape))
        #sz = dat.shape

        # TODO: datSerial as additional channels in calculated data if Serial channel was selected
        
        # prepare all data -> get full list of used channel <-> data type pairs -> process       
        dp = MyDataProcessing(dat)
        usedData = []
        usedChannels = []

        # first process sampled Data 
        for i in range(0,len(self.channelIxi)): # for each registered channel
            ix2 = self.channelRefIxi[i]
            if( self.sampleInfo.isChannelUsed(i) and len(ix2)<2 ): # do not process channels with 2 references (correlation or division of 2 results)
                ix = self.channelIxi[i] # index in dat
                tp = self.dat_type[i] # processing type
                if( tp == 7 ): # Serial data
                    dat2 = datSerial[ix] # 0 is time...
                elif( tp == 9 ): # Training data
                    dat2 = datTrain
                else:
                    # process data
                    dat2 = dp.processData(tp,ix,ix2,self.sampleInfo,self.histDat) # TODO: to correlate FFT resultswith other fft results (? or raw), trhis must be iomplemented here - requires fft channel data buffer of N - N=??
                usedData.append(dat2)
                usedChannels.append(i)
        
        # Then process calculated data (~correlation with 2 references)
        for i in range(0,len(self.channelIxi)): # for each registered channel
            ix2 = self.channelRefIxi[i]
            if( self.sampleInfo.isChannelUsed(i) and len(ix2)>=2 ):
                if( ix2[0] in usedChannels and ix2[1] in usedChannels):
                    tp = self.dat_type[i] # processing type
                    tix1 = usedChannels.index(ix2[0])
                    tix2 = usedChannels.index(ix2[1])
                    dat2 = dp.processData2ndDegree(tp,usedData[tix1],usedData[tix2],ix2,self.histDat)
                    usedData.append(dat2)
                    usedChannels.append(i)
                else:
                    dat2 = nan


        # now, distribute usedData mapping chanels of recipients to processed data via usedChannels list
        rec = self.sampleInfo.getRecipientList()
        for ix in range(0,len(rec)):
            sendDat = []
            chlst = self.sampleInfo.getRecipiensUsedChannels(ix)
            if(len(chlst)>0):
                for ch in chlst:
                    if(ch in usedChannels):
                        ix2 = usedChannels.index(ch)
                        sendDat.append(usedData[ix2])
                #sendDat=np.array(sendDat)
                #sendDat = sendDat.transpose() # channels in y, elements in x
                rec[ix](sendDat)

        # TODO: generateRecorderSettings should set up sample info data for recording. Check "changes" flag & use for TODO below
        #       getRecipiensUsedChannels must return lists from recording recipients if recording is active;
        #       Either all raw (not dat) from channels or all calculated from channels.
        #       isChannelUsed must be adapted depending on whcih recorder is active
        #       --> from UI update channel sample info when activating/ deactivating.


    def updateData(self):
        # call timed if sampling, get data from ni_reader (loop), distribute data.
        if( (self.ni_reader is None) or (not self.ni_reader.is_running) ):
            return
        #self.sampleInfo.setDataReadingStatus(True)
        #cnt = 0
        datSer = []
        datTrain = []

        if( self.ni_reader is None ):
            return
        dat = self.ni_reader.getData()
        if( self.ser_com is not None  ):
            datSer = self.ser_com.getData(self.ni_reader.bufferSize(),self.sampleInfo.getprocessSR())

        if(self.trainUI is not None):
            datTrain = self.trainUI.getTrainingDir()

        while( dat is not None and self.ni_reader is not None ):
            #cnt = cnt+1
            #if(self.ni_reader.bufferSize < 1):
            #    self.sampleInfo.setDataReadingStatus(False)
            self.distributeData(dat,datSer,datTrain)
            if( self.ni_reader is None ):
                return
            dat = self.ni_reader.getData()
            if( self.ser_com is not None  ):
                datSer = self.ser_com.getData(self.ni_reader.bufferSize(),self.sampleInfo.getprocessSR())
            if(self.trainUI is not None):
                datTrain = self.trainUI.getTrainingDir()

        if( self.ser_com is not None  ):
            self.ser_com.resetData()

        #ms = int(round(time.time() * 1000))-self.ms_init
        #print("Distri: "+str(ms)+" "+str(cnt))

        if(self.sampling):
            threading.Timer(0.05, self.updateData).start()

