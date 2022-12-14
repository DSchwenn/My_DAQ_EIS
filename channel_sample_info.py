from function_gen import *

from enum import Enum

class FFTWinTp(Enum):
    NONE = 0
    HAM = 1
    HAN = 2
    BLK = 3
    BRT = 4
    KAI = 5


class ChannelSampleInfo:
    def __init__(self):
        self.functionGen = None
        self.channelList = [] # readChannels.append([ch,ter,type,ref])
        self.plotSettingList = [] # per plot: channel index (relative to channelList) + complex preference (abs or phase) + 
        self.trainIdList = []
        # N data [channels,samples per channel]
        # Then also: use toolbar, isLive, N samples per screen
        # Followed by: useManualLimit, min limit, max limit, selected channels list
        self.dataCallbacks = []

        self.sampleRate = -1.0
        self.writeRate = -1.0
        self.device = ""
        self.channelUpdateRequest = []
        self.v_range = 10.0
        self.datareading = False
        self.corrTime = 2.
        self.fftWinType = 0
        
    def setTrainIdList(self,lst):
        print("New Train list: " + str(lst))
        self.trainIdList = lst

    def getTrainIdList(self):
        return self.trainIdList

    def addRecipient(self,callbackFkt,plotIndex):
        self.dataCallbacks.append([plotIndex,callbackFkt])

    def removeRecipient(self, callbackFkt):
        for i in range(len(self.dataCallbacks)):
            dcb = self.dataCallbacks[i]
            if( dcb[1] == callbackFkt):
                self.dataCallbacks.pop(i)
                return

    def updateInfo(self,functionGen,channelList,plotSettingList,sampleRate,writeRate,v_range,corrTime,device):
        self.functionGen = functionGen
        self.channelList = channelList
        self.plotSettingList = plotSettingList
        self.sampleRate = sampleRate
        self.writeRate = writeRate
        self.v_range = v_range
        self.corrTime = corrTime
        self.device = device
        updReq = []
        for i in range(0, len(plotSettingList)):
            updReq.append(False)
        self.channelUpdateRequest = updReq


    def getPlotSetting(self,index):
        return self.plotSettingList[index]


    def getPlotLegend(self,index,forHeader = False):
        if(len(self.plotSettingList)<=index):
            return []
        psi = self.plotSettingList[index]
        
        legend = []
        f_list = self.functionGen.get_f_list()

        for ch in psi[0]:
            if(ch>=0):
                tlgd = self.getChannelLegend(ch,f_list,forHeader)
                legend = legend + tlgd

        return legend

    def getChannelLegend(self,channel,f_list,forHeader):

        ci = self.channelList[channel]
        
        corrWithFFT = 0
        divWithFFT = 0
        txt1 = ""
        if(len(ci)>0 and (ci[2][0] == 'C' or ci[2][0] == 'D') ):
            ch1 = ci[3][0]
            ch2 = ci[3][1]
            ci1 = self.channelList[ch1]
            ci2 = self.channelList[ch2]
            if( ci[2][0] == 'C'  and (ci1[2][0] == 'F') !=  (ci2[2][0] == 'F') ): # if only one of them is FFT (otherwise means will be used)
                corrWithFFT = 1
                txt1 = "Cor:" + str(ch1) + "," + str(ch2) + " "
            elif( ci[2][0] == 'D'  and (ci1[2][0] == 'F') or  (ci2[2][0] == 'F') ):
                divWithFFT = 1
                txt1 = "Div:" + str(ch2) + "/" + str(ch1) + " "

        legend = []
        # 2 cases: 1 or N sample per channel, one channel -> one legend entry
        #           1 sample  for N channels - one channel pre frequency -> N legend entries
        if(len(ci)>0 and (ci[2][0] == 'F' or corrWithFFT or divWithFFT)): #nDat>1):  -> only add frequency for FFT...
            for f in f_list:
                if( corrWithFFT or divWithFFT ):
                    tstr = txt1 + str(f) + "Hz"
                else:
                    tstr = ci[0] + " " + str(f) + "Hz"
                tstr = self.addHeaderInfo(tstr,ci,forHeader)
                legend.append(tstr)
        elif(len(ci)>0 and ci[2][0] == 'A'):
            tlst = ["HR red","HR IR","Acc X","Acc Y","Acc Z"]
            for s in tlst:
                tstr = ci[0] + " " + s
                tstr = self.addHeaderInfo(tstr,ci,forHeader)
                legend.append(tstr)
        elif(len(ci)>0 and ci[2][0] == 'T'):
            tlst = ["Dir X","Dir Y","Dir Z"]
            for s in tlst:
                tstr = ci[0] + " " + s
                tstr = self.addHeaderInfo(tstr,ci,forHeader)
                legend.append(tstr)
        elif(len(ci)>0):
            tstr = ci[0]
            tstr = self.addHeaderInfo(tstr,ci,forHeader)
            legend.append(tstr)

        return legend

    def addHeaderInfo(self,tstr,ci,forHeader):
        if(forHeader):
            tstr = tstr + " " + ci[2] + " " + ci[1]
        return tstr

    def type2num(self,typeStr):
        if( typeStr[0] == 'F' ): # FFT
            return 1
        elif( typeStr[0] == 'C' ): # Correlation
            return 2
        elif( typeStr[0] == 'D' ): # Division
            return 6
        elif( typeStr[0] == 'M' ): # Mean Max Min
            if( typeStr[1] == 'a' ):
                return 4
            elif( typeStr[1] == 'i' ):
                return 5
            else: # Mean
                return 3
        elif( typeStr[0] == 'S' ): # Serial
            return 7
        elif( typeStr[0] == 'A' ): # Accelleration & HR via uC
            return 8
        elif( typeStr[0] == 'T' ): # Training target
            return 9
        else: # Raw
            return 0


    def isChannelUsed(self,ix):
        # index relative to self.channelList 
        # used only if linked to a callback self.dataCallbacks
        for i in range(len(self.plotSettingList)):
            rec = self.plotSettingList[i]
            
            if(len(rec[0])>0):
                refLst = self.channelList[rec[0][0]][3]
                # TODO: may lead to false positive in correlations with one reference
                if( ix in rec[0] or ix in refLst ):
                    return True
        return False

    def getRecipientList(self):
        #return callbacks
        clst = []
        for rec in self.dataCallbacks:
            clst.append(rec[1])
        return clst

    def getRecipiensUsedChannels(self,ix):
        if(ix>=len(self.plotSettingList)):
            return []
        return self.plotSettingList[ix][0]

    def allChannelNeedUpdate(self):
        for i in range(len(self.channelUpdateRequest)):
            self.channelUpdateRequest[i] = True
        #print( "All set: " + str(self.channelUpdateRequest) )

    def channelNeedsUpdate(self,ix):
        if( ix>=len(self.channelUpdateRequest) ):
            return
        self.channelUpdateRequest[ix] = True

    def doesChannelNeedUpdate(self,ix):
        if( ix>=len(self.channelUpdateRequest) ):
            return False
        return self.channelUpdateRequest[ix]

    def resetChannelUpdateFlag(self,ix):
        if( len(self.channelUpdateRequest)<=ix ):
            return
        #print( "Reset: " + str(ix) + " " + str(self.channelUpdateRequest) )
        self.channelUpdateRequest[ix] = False

    def getChannelInfo(self,ix):
        if( ix>=len(self.channelList) ):
            return []
        return self.channelList[ix]

    def getPlotSetting(self,ix):
        if( ix>=len(self.plotSettingList) ):
            return []
        return self.plotSettingList[ix]
    
    def getChannelLive(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return False
        return ci[4]

    def getChannelToolbar(self, ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return False
        return ci[3]

    def getChannelNperPlot(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return 10
        return ci[5]

    def getComplexPref(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return 0
        return ci[1]

    def getDataPerChannel(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return [0,0]
        return ci[2]

    def getUsedChannelList(self):
        usedList = []
        for i in range(len(self.dataCallbacks)):
            dcb = self.dataCallbacks[i]
            if( dcb[0]>=0 and dcb[0]<len(self.plotSettingList ) ): # one channel per plot channel
                pltSet = self.plotSettingList[dcb[0]]
                usedList.append(pltSet[0])
        return usedList
    
    def get_f_list(self):
        return self.functionGen.get_f_list()

    def getSampleRate(self):
        return self.sampleRate

    def getVRange(self):
        return self.v_range

    def getDataSize(self):
        if(self.functionGen is None):
            return 150
        return self.functionGen.getDataSize()

    def getprocessSR(self):
        return self.getSampleRate()/self.getDataSize()

    def getFunctionGen(self):
        return self.functionGen

    def getDevice(self):
        return self.device

    def useManualLimit(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return False
        return ci[6]

    def getMinLimit(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return 0.0
        return ci[7]

    def getMaxLimit(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return 1.0
        return ci[8]

    def getSelChnList(self,ix):
        ci = self.getPlotSetting(ix)
        if( len(ci)<1 ):
            return []
        return ci[9]

    def getSelChnStatus(self,plt_ix,chn_ix):
        ci = self.getPlotSetting(plt_ix)
        if( len(ci)<=9 or len(ci[9])<=chn_ix ):
            return True
        return ci[9][chn_ix]

    def setDataReadingStatus(self,stat):
        self.datareading = stat
    
    def isDataReading(self):
        return self.datareading

    def getCorrTime(self):
        return self.corrTime


    def setFFTWin(self,win):
        self.fftWinType = win # id according to order in MainWindow Menu.

    def getFFTWin(self):
        return self.fftWinType