import numpy as np
from numpy import fft as fft

from channel_sample_info import *
from data_history_storage import *

class MyDataProcessing:
    def __init__(self,dat):
        self.allDat = dat
        self.dat = []

    def doFFT(self,f_list,sr,win): # 2 lists: abs and phase values of fft for frequency in f_list
        N = np.size(self.dat)
        dat = self.dat
        if(win != FFTWinTp.NONE):
            dat = self.applyWindow(dat,N,win)
        f1 = fft.fft( dat )
        ixi=self.getFrequencyIndex(f_list,N,sr)
        fres = f1[ixi]
        return fres

    def applyWindow(self,dat,N,win):

        if( win == FFTWinTp.HAM ): # according to order in MainWindow Menu
            wDat = np.hamming(N)
        elif( win == FFTWinTp.HAN ):
            wDat = np.hanning(N)
        elif( win == FFTWinTp.BLK ):
            wDat = np.blackman(N)
        elif( win == FFTWinTp.BRT ):
            wDat = np.bartlett(N)
        else: #( win == FFTWinTp.KAI ):
            wDat = np.kaiser(N,14)
        dat = np.copy(dat)
        dat = np.multiply(dat,wDat)
        return dat


    def getFrequencyIndex(self,f_list,ss,sr):
        fft_freq = fft.fftfreq(ss)*sr
        ixi = np.zeros(shape=(np.size(f_list)))
        for i in range(np.size(f_list)):
            dff = np.abs(fft_freq-f_list[i])
            ix = np.where(dff == np.amin(dff))
            ixi[i] = ix[0][0]
        ixi = ixi.astype(int)
        return ixi

    def doDivision(self,nDat1,nDat2):
        #return np.divide(nDat1,nDat2)
        return np.divide(nDat2,nDat1)

    def doCorrelationHist(self,nDat1,nDat2,ix1,ix2,histDat):
        # nDat can have multiple channels...
        # if nDat 1 and 2 have multiple channels, average
        if(np.size(nDat1)>1 and np.size(nDat2)>1):
            nDat1 = np.mean(nDat1)
            nDat2 = np.mean(nDat2)
        # Otherwise: do N to 1 correlations -> N results.

        (hd1,hd2) = histDat.getHistoricDataCorr(ix1,ix2,nDat1,nDat2)

        cc = np.corrcoef(hd1,hd2) # TODO: hows it working with fft data -> is fft corr data channel number correct... plot...?
        cc = cc[0,1:]
        # if(np.shape(cc)[0]>2):
        # else:
        #     cc = cc[0,1]
        if(True in np.isnan(cc)):
            cc = np.zeros(np.shape(cc))
        return cc

    def doCorrelation(self,dat2):
        cc = np.corrcoef(self.dat,dat2) # TODO: hows it working with fft data -> is fft corr data channel number correct... plot...?
        cc = cc[0,1]
        if(np.isnan(cc)):
            cc = 0
        return cc


    def doMean(self):
        mn = np.mean(self.dat)
        return mn

    def doMax(self):
        mx = np.max(self.dat)
        return mx

    def doMin(self):
        mn = np.min(self.dat)
        return mn

    def getRaw(self):
        return self.dat

    def processData(self,tp,ix1,ix2,channelSampleInfo):
        self.dat = self.allDat[ix1]

        if( tp==0 ):
            return self.getRaw()
        elif( tp == 1 ):
            return self.doFFT( channelSampleInfo.get_f_list(), channelSampleInfo.getSampleRate(), channelSampleInfo.getFFTWin() ) # according to frequencies in function generator
        elif(tp == 2):
            return self.doCorrelation(self.allDat[ix2])
        elif(tp == 3): # mean
            return self.doMean()
        elif(tp == 4): # max
            return self.doMax()
        elif(tp == 5): # min
            return self.doMin()
        #elif(tp == 6): # Division
        #    return self.doDivision()
        return []

    def processData2ndDegree(self,tp,nDat1,nDat2,ixRef,histDat):
        if(tp == 2): # correlation
            nDat1=np.abs(nDat1)
            nDat2=np.abs(nDat2)
            return self.doCorrelationHist(nDat1,nDat2,ixRef[0],ixRef[1],histDat)
        elif(tp == 6): # Division
            nDat1=np.abs(nDat1)
            nDat2=np.abs(nDat2)
            return self.doDivision(nDat1,nDat2)
# #dp = MyDataProcessing(np.zeros(shape=(40)))
# dp = MyDataProcessing(np.random.rand(40))
# ff = dp.doFFT([500,1000],3000)
# print(ff)
# #cc = dp.doCorrelation(np.ones(shape=(40)))
# cc = dp.doCorrelation(np.random.rand(40))
# print(cc)

#dp = MyDataProcessing(np.random.rand(40))
#print(dp.doMean())