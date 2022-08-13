

import threading
from datetime import datetime
import time

import os.path
from os import path

from channel_sample_info import *



class MyFileWriter(threading.Thread):
    def __init__(self,plotIndex,sampleInfo,type,pth=""):
        threading.Thread.__init__(self)

        self.plotIndex = plotIndex
        self.sampleInfo = sampleInfo
        self.separator = "\t"
        self.is_recording = False
        self.type = type # 'R' raw, 'C' calculated
        self.colums = 0
        self.samples_per_update = 0
        self.f = None # file
        self.sampleBuffer = []
        self.recieving = False
        self.end_thread = False
        self.path = pth
        self.start()
    
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
        date_time = now.strftime("%Y%m%d_%H%M%S")
        sr = str(int(self.sampleInfo.getSampleRate()))+"Hz"
        fn = self.path + date_time + "_" + sr + "_" + str(self.type) + ".txt"
        return fn

    def writeHeader(self):
        #print( self.sampleInfo.getPlotLegend(self.plotIndex,True) )
        hdrLst = self.sampleInfo.getPlotLegend(self.plotIndex,True)
        if(len(hdrLst)>0):
            txt = ""
            for hdr in hdrLst:
                txt += hdr + self.separator
            if(len(txt)>0):
                txt = txt[:-1] + "\n" # replace last separator with newline
            self.f.write(txt)


    def startRecording(self):
        if(self.is_recording):
            return
        print("Start Rec " + str(self.plotIndex) + " " + str(self.type))
        fn = self.generateFilename()# new file, init buffer,m write header -> start thread
        self.f = open(fn, "a")
        self.writeHeader()
        self.is_recording = True

    def stopRecording(self):
        if(not self.is_recording ):
            return
        print("Stopping Rec " + str(self.plotIndex) + " " + str(self.type))
        # stop when device is stopped (-> new file when restarted)
        self.is_recording = False
        self.f.close()

    def updateData(self,data):
        # start new recording if its not running; 
        # just copy data to buffer here
        if( self.sampleInfo.doesChannelNeedUpdate(self.plotIndex) ):
            self.sampleInfo.resetChannelUpdateFlag(self.plotIndex)
            rec = self.sampleInfo.getChannelLive(self.plotIndex)
            if(self.is_recording and not rec): # start
                self.stopRecording()
                self.sampleBuffer = []
            elif(not self.is_recording and rec): # stop
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
                    if(self.type=='R'):
                        self.writeRawData()
                    else:
                        self.writeChannelData()

                    #print("Writer " + str(self.plotIndex) + ": " + str(np.shape(tDt)))
                    #for dt in tDt:
                    #    print(  str(np.shape(dt)) + " " + str(np.size(dt)) )
                    # TODO: write to file


    def writeRawData(self):
        txt = ""

        while( len(self.sampleBuffer)>0 ):
            tDt = self.sampleBuffer.pop(0)
            sz = np.shape(tDt)
            for rw in range(sz[1]):
                for col in range(sz[0]):
                    txt += str(tDt[col][rw]) + self.separator
                txt += "\n"

        self.f.write(txt)
        


    def writeChannelData(self):
        txt = ""

        while( len(self.sampleBuffer)>0 ):
            tDt = self.sampleBuffer.pop(0)
            for dt in tDt:
                if(np.size(dt)>1):
                    for ddt in dt:
                        txt += str(ddt) + self.separator
                else:
                    txt += str(dt) + self.separator
                txt += "\n"

        self.f.write(txt)


# Writer 2: (3,)
# (4,) 4
# () 1
# () 1

# Writer 3: (2, 150)
# (150,) 150
# (150,) 150