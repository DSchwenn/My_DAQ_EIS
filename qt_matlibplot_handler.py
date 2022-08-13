from cmath import nan
import sys
import matplotlib
from matplotlib import pyplot
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QListWidgetItem

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from channel_sample_info import *

import threading
import time

import numpy as np


class QtMatLibPlotHandler(FigureCanvasQTAgg,threading.Thread):
    def __init__(self, targetWidget, parent, plotIndex, sampleInfo, width=5, height=4, dpi=100,  ):
        threading.Thread.__init__(self)

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(QtMatLibPlotHandler, self).__init__(self.fig)

        #self.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        pyplot.ion() # ...?

        self.toolbar = NavigationToolbar(self, parent)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self)

        self.last_draw_ms = int(round(time.time() * 1000))
        self.dtDraw = 100 # min time between draws

        targetWidget.setLayout(self.layout)

        self.plotIndex = plotIndex
        self.sampleInfo = sampleInfo

        self.isLive = False
        #self.tp = ""
        self.smpl_count = 0
        self.initData()

        self.isupdating = False
        self.newData = False
        self.is_running = True
        self.start()

    def getPlotIndex(self):
        return self.plotIndex

    def stopPlotting(self):
        self.is_running = False

    def run(self):
        
        while self.is_running:
            time.sleep(0.05)
            ms = int(round(time.time() * 1000))
            if( self.newData and ms-self.last_draw_ms > self.dtDraw ):

                while(self.isupdating):
                    time.sleep(0.001)

                self.draw()
                self.last_draw_ms = int(round(time.time() * 1000))
            


    def getIndex(self):
        return self.plotIndex

    def updatePlot(self):
        print("Update plot...")

        self.layout.removeWidget(self.toolbar)
        self.layout.removeWidget(self)

        if(self.sampleInfo.getChannelToolbar(self.plotIndex)):
            self.layout.addWidget(self.toolbar)

        self.layout.addWidget(self)
        self.isLive = self.sampleInfo.getChannelLive(self.plotIndex)
        
        self.initData()


    def initData(self):
        nchn = self.sampleInfo.getDataPerChannel(self.plotIndex)
        names = self.sampleInfo.getPlotLegend(self.plotIndex)
        ndata = self.sampleInfo.getChannelNperPlot(self.plotIndex)
        print("Plt Upd: " + str(nchn))

        self.axes.cla()
        self.smpl_count = 0
        tdat_x = np.empty(nchn[1]*ndata) # 1, same, xval for all plots
        tdat_x = np.arange(np.size(tdat_x))
        if(nchn[1]>0):
            F = self.sampleInfo.getSampleRate()/self.sampleInfo.getDataSize() * nchn[1]
        else:
            F = self.sampleInfo.getSampleRate()/self.sampleInfo.getDataSize()
        tdat_x = tdat_x * (1/F)
        
        for nm in names:
            tdat_y = np.empty(nchn[1]*ndata) # different yval for all plots
            tdat_y[:] = np.NaN
            self.axes.plot(tdat_x, tdat_y, label=nm)
        self.axes.legend()



# TODO name has to be given - elements must match number of data to review; recieved data to add to line as plot -> x axis filling here
    def updateData(self,data):
        #print(len(data) + " " + str(self.sampleInfo.doesChannelNeedUpdate(self.plotIndex)) + " " + self.isLive )
        self.isupdating = True
        if( self.sampleInfo.doesChannelNeedUpdate(self.plotIndex) ):
            self.sampleInfo.resetChannelUpdateFlag(self.plotIndex)
            self.updatePlot()

        if( self.isLive ):
            # TODO: Plot -> btm plot -> correlate FFT with mean...? - need buffer in handler...
            #print("mpl called: " + str(self.plotIndex) + " " + str(type(data)) + " " + str(np.size(data)))
            self.updateLines(data)
            self.newData = True
        self.isupdating = False

            

    def processComplex(self,dat):
        pref = self.sampleInfo.getComplexPref( self.plotIndex )
        if(pref==1):
            dat = np.angle(dat)
        else:
            dat = np.abs(dat)
        return dat

    def updateLines(self,dat):

        ndata = self.sampleInfo.getChannelNperPlot(self.plotIndex)
        nchn = self.sampleInfo.getDataPerChannel(self.plotIndex )

        if( np.size(dat)>nchn[0]*nchn[1] ): # happend during switching channels or for FFT correlated with mean
            nchn[0] = np.size(dat)
        
        ni = (ndata*nchn[1])
        di = int(ni/20)
        if(di<1 and ndata>2):
            di=1
        

        dat = np.array(dat)
        a = np.shape(dat)

        if(len(a)>0):
            dt0 = dat[0]
        else: # scalar - not array...
            dt0 = dat

        if(len(a)>1):
            dt0 = dt0[0]
            if(a[1] == nchn[0] and a[0] == nchn[1] ): # dat arrives as list - dimensions may not be alligned: chanely in y, samples in x.
                dat = np.transpose(dat)
        if(isinstance(dt0, complex)):
            dat = self.processComplex(dat)

        yMax = -999999.
        yMin = 999999.

        x_vals = self.axes.lines[0].get_xdata()
        #cnt = 0
        #print("Dat: " + str(dat))
        manLim = self.sampleInfo.useManualLimit(self.plotIndex)

        #for i in range(len(self.axes.lines)):
        for lnum,line in enumerate(self.axes.lines):
            if(not self.sampleInfo.getSelChnStatus(self.plotIndex,lnum)):
                continue

            #x_vals = line.get_xdata()
            y_dat = line.get_ydata()
            #print("In " + str(line) + " " + str(lnum) + ": " + str(y_dat))
            i1 = nchn[1]*self.smpl_count
            i2 = i1+nchn[1]
            i3 = i2 + di

            if(i2>ni):
                i2=ni-1
            if(i3>ni):
                i3=ni-1

            if(len(a)<=0): # scalar: 1 channel, 
                y_dat[i1] = dat
            elif(len(a)<=1): # ???
                if(nchn[0]>1):
                    y_dat[i1] = dat[lnum]
                else:
                    y_dat[i1:i2] = dat
            else:
                y_dat[i1:i2] = dat[lnum,:] # raw: dat 1,150 -> here dat[lnum,:]; FFT: 1,4 where 4 is channel

            y_dat[i2:i3] = nan

            #line.set_data(x_vals, y_dat)
            line.set_ydata(y_dat)
            #print("Out " + str(line) + " " + str(lnum) + ": " + str(y_dat))
            #y_dat = line.get_ydata()
            #print("Check " + str(line) + " " + str(i) + ": " + str(y_dat))
            #cnt = cnt+1
            if(not manLim):
                tmx = np.nanmax(y_dat)
                tmn = np.nanmin(y_dat)
                if( tmx>yMax ):
                    yMax = tmx
                if( tmn<yMin ):
                    yMin = tmn

            #l.set_data(np.arange(10), np.random.rand(10))
            #yMax = 1.0
            #yMin = 0.0

        if(manLim):
            yMin = self.sampleInfo.getMinLimit( self.plotIndex )
            yMax = self.sampleInfo.getMaxLimit( self.plotIndex )


        x_time = x_vals[-1]
        self.axes.set_xlim(0, x_time)

        dy = yMax-yMin
        if(dy<0.01):
            dy = 0.01
        self.axes.set_ylim(yMin-dy*0.03, yMax+dy*0.03)


        self.smpl_count = self.smpl_count+1
        if( self.smpl_count>= ndata ):
            self.smpl_count = 0

