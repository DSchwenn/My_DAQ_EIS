

from channel_sample_info import *
import numpy as np



class DataHistoryStorage: # Not to use with raw signal...
    def __init__(self,sampleInfo):
        self.sampleInfo = sampleInfo
        self.idList = []
        self.historicDataList1 = []
        self.historicDataList2 = []

    def clearAllData(self):
        self.idList = []
        self.historicDataList1 = []
        self.historicDataList2 = []

    def getHistoricDataCorr(self,ix1,ix2,newDat1,newDat2):
        ix = self.getHistoricDataSetIndex(ix1,ix2)
        dat1 = np.array(newDat1)
        dat1 = dat1.flatten()
        dat1 = np.reshape(dat1,(np.size(dat1),1))

        dat2 = np.array(newDat2)
        dat2 = dat2.flatten()
        dat2 = np.reshape(dat2,(np.size(dat2),1))

        if(ix<0):
            ix = self.makeNewHistoricDataSetCorr(ix1,ix2,dat1,dat2)
        else:
            hDat1 = self.historicDataList1[ix]
            hDat2 = self.historicDataList2[ix]
            self.historicDataList1[ix] = np.concatenate((hDat1[:,1:],dat1),1)
            self.historicDataList2[ix] = np.concatenate((hDat2[:,1:],dat2),1)

        return (self.historicDataList1[ix],self.historicDataList2[ix])


    def makeNewHistoricDataSetCorr(self,ix1,ix2,dat1,dat2):
        a = [ix1,ix2]
        n = int(self.sampleInfo.getCorrTime()*self.sampleInfo.getSampleRate()/self.sampleInfo.getDataSize())
        hd1 = np.zeros((np.size(dat1),n-1))
        hd1 = np.concatenate((hd1,dat1),1)

        hd2 = np.zeros((np.size(dat2),n-1))
        hd2 = np.concatenate((hd2,dat2),1)

        self.idList.append(a)
        self.historicDataList1.append(hd1)
        self.historicDataList2.append(hd2)

        return len(self.idList)-1


    def getHistoricDataSetIndex(self,ix1,ix2):
        a = [ix1,ix2]
        if( a in self.idList  ):
            ix = self.idList.index(a)
            return ix
        return -1




# ci = ChannelSampleInfo()
# dh = DataHistoryStorage(ci)
# ci.updateInfo(None,[],[],15000,15000,2.5,2.0,'meh')

# d1 = dh.getHistoricData(1,-1,[1,2,3])
# d2 = dh.getHistoricData(1,-1,[4,5,6])

# print(d2)

