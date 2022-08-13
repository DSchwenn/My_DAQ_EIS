
from ntpath import altsep
import sys


from PyQt5.QtWidgets import QApplication, QWidget, QListWidget, QVBoxLayout, QListWidgetItem
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5 import QtCore

from checkablecombobox import *
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar

import numpy as np
import matplotlib.pyplot as plt

from qt_for_python.uic.sampling_ui_01 import *
from function_gen import *
from daq_device_infos import *
from qt_matlibplot_handler import *
from my_file_writer import *
from ni_data_handler import *
from channel_sample_info import *
from serial_uc_com import *

from channel_sample_info import *

import traceback
import pickle


# TODO:
# k Test correlation of raw
# k Test correlation of Means
# k Test correlation of FFT with mean
# k Test correlation of FFt with FFT
# Consider prerequisite to add more methods for signal processing -> specifically FFT to component signal(s)
# Recording functions
# Save & load functions...
#  Sample/writing rates, Hold f, Device, Frequencies, channels, plot settings, recording paths
# Plot settings: Toolbar, Primary, Type, N, Channel select, Manual Lim, Vmin, Vmax
# Start and stop into Menus
#
# k Recording functions: select & uise paths
# k  Check recordings. Why was one of them not started when kill was called...?
# Menu functions...
# overwritePlotSettingListAbstr
# set up Git?
#
# ??: After changing device -> channels are invalid...? Reset? Ask?
#

class MyMainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MyMainWindow, self).__init__(*args, **kwargs)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Signal writing setup code
        self.writingFrequency = []  # np.array([1])
        self.writingPhase = []  # np.array([2])
        self.writingAmplitude = []  # np.array([3])
        self.isStarted = False
        self.writingTotalAmplitude = self.ui.writing_amplitude_SpinBox.value()

        self.ui.add_frequency_button.clicked.connect(self.writingAddFrequency)
        self.ui.remove_frequency_button.clicked.connect(
            self.writingRemoveFrequency)
        self.ui.clear_frequencies_button.clicked.connect(
            self.writingClearFrequencies)
        self.ui.apply_frequency_changes_button.clicked.connect(
            self.writingApplyFrequencies)
        self.ui.preview_writing_signal_button.clicked.connect(
            self.writingPreviewSignal)

        self.ui.write_frequencies_list.currentRowChanged.connect(
            self.writingUpdateFPA)

        # Device tab
        self.devicesInfo = NiDevices()
        self.ui.refresh_device_pb.clicked.connect(self.deviceRefreshDeviceInfo)
        self.ui.device_comboBox.currentIndexChanged.connect(
            self.deviceUpdateDeviceInfo)
        self.deviceRefreshDeviceInfo()

        # Read tab
        self.ui.tabWidget.currentChanged.connect(
            self.updateTab)  # Read Tab: update combos
        self.ui.readChannelcomboBox.currentIndexChanged.connect(
            self.readUpdateTerminalRef)

        self.ui.readAddChannelPushButton.clicked.connect(self.readAddChannel)
        self.ui.readRemovePushButton.clicked.connect(self.readRemoveChannel)
        self.ui.readClearPushButton.clicked.connect(self.readClearList)
        self.readChannels = []

        # Top plot:
        self.ui.top_plot_primary_comboBox.currentIndexChanged.connect(
            self.topPlotSelChange)
        self.ui.top_plot_processing_comboBox.currentIndexChanged.connect(
            self.topPlotTypeChange)
        self.ui.top_show_toolbar_checkBox.stateChanged.connect(
            self.updateTopPlotDistribution)
        self.ui.top_plot_live_checkBox.stateChanged.connect(
            self.updateTopPlotDistribution)
        self.ui.top_plot_NspinBox.valueChanged.connect(
            self.updateTopPlotDistribution)
        self.ui.top_useManLim_checkBox.stateChanged.connect(
            self.updateTopPlotDistribution)
        self.ui.top_lowerLimit_doubleSpinBox.valueChanged.connect(
            self.updateTopPlotDistribution)
        self.ui.top_upperLimit_doubleSpinBox.valueChanged.connect(
            self.updateTopPlotDistribution)
        self.top_IsUpdating = False

        self.top_channel_cb = CheckableComboBox()
        self.ui.top_comboBoxWidgetLayout.addWidget(self.top_channel_cb)
        self.top_channel_cb.contentChanged.connect(
            self.updateTopPlotDistribution)

        # Bottom plot
        self.ui.btm_plot_primary_comboBox.currentIndexChanged.connect(
            self.btmPlotSelChange)
        self.ui.btm_plot_processing_comboBox.currentIndexChanged.connect(
            self.btmPlotTypeChange)
        self.ui.btm_show_toolbar_checkBox.stateChanged.connect(
            self.updateBtmPlotDistribution)
        self.ui.btm_plot_live_checkBox.stateChanged.connect(
            self.updateBtmPlotDistribution)
        self.ui.btm_plot_NspinBox.valueChanged.connect(
            self.updateBtmPlotDistribution)
        self.ui.btm_useManLim_checkBox.stateChanged.connect(
            self.updateBtmPlotDistribution)
        self.ui.btm_lowerLimit_doubleSpinBox.valueChanged.connect(
            self.updateBtmPlotDistribution)
        self.ui.btm_upperLimit_doubleSpinBox.valueChanged.connect(
            self.updateBtmPlotDistribution)
        self.btm_IsUpdating = False

        self.btm_channel_cb = CheckableComboBox()
        self.ui.btm_comboBoxWidgetLayout.addWidget(self.btm_channel_cb)
        self.btm_channel_cb.contentChanged.connect(
            self.updateBtmPlotDistribution)


        # plot graphs
        # TODO: inject matlibplots in top_plt_widget and btm_plt_widget
        self.sampleInfo = ChannelSampleInfo()
        self.UpdateChannelSampleInfo()  # must fill list according to "plotIndex"
        # matlibplot handling inside; Data needed inside ~ aniline -> ?singleton data handler/ distributor?
        self.topplot = QtMatLibPlotHandler(
            targetWidget=self.ui.top_plt_widget, parent=self, plotIndex=0, sampleInfo=self.sampleInfo)
        self.btmplot = QtMatLibPlotHandler(
            targetWidget=self.ui.btm_plt_widget, parent=self, plotIndex=1, sampleInfo=self.sampleInfo)
        self.raw_recorder = MyFileWriter(2,self.sampleInfo,'R')
        self.calc_recorder = MyFileWriter(3,self.sampleInfo,'C')
        self.updateRecorderPaths()
        self.sampleInfo.addRecipient(self.topplot.updateData, plotIndex=self.topplot.getPlotIndex())
        self.sampleInfo.addRecipient(self.btmplot.updateData, plotIndex=self.btmplot.getPlotIndex())
        self.sampleInfo.addRecipient(self.raw_recorder.updateData, plotIndex=self.raw_recorder.getPlotIndex())
        self.sampleInfo.addRecipient(self.calc_recorder.updateData, plotIndex=self.calc_recorder.getPlotIndex())
        self.datahandler = NiDataHandler(self.sampleInfo)
        # Not aniline... timer to read buffer in data handler -> call plot updates via callback


        # recorders updateRecorderStatus
        self.ui.enable_raw_recording_checkBox.stateChanged.connect(self.updateRecorderStatus)
        self.ui.enable_fft_recording_checkBox.stateChanged.connect(self.updateRecorderStatus)
        self.ui.raw_data_folder_lineEdit.textChanged.connect(self.updateRecorderPaths)
        self.ui.fft_data_folder_lineEdit.textChanged.connect(self.updateRecorderPaths)
        self.ui.select_fft_folder_pushButton.clicked.connect(self.getCalcPath)
        self.ui.select_raw_folder_pushButton.clicked.connect(self.getRawPath)


        # Serial/ uC
        self.ui.stimRefreshSerialpushButton.clicked.connect(self.refreshSerialList)
        self.ui.stimSetpushButton.clicked.connect(self.setData2uC)
        self.ui.stimLinkRGBBrightcheckBox.stateChanged.connect(self.updateRGBStatus)
        self.ui.stimBrughtRspinBox.valueChanged.connect(self.updateRGBStatus)
        self.ui.stimClosepushButton.clicked.connect(self.closeData2uC)
        self.sc = SerialuCCom()
        self.refreshSerialList()

        # Menu items
        self.ui.actionLoad_settings.triggered.connect(self.loadSettings)
        self.ui.actionSave_settings.triggered.connect(self.saveSettings)
        self.ui.actionExit.triggered.connect(self.exitApp)
        self.ui.actionRun.triggered.connect(self.activateRecordingFromMenu)
        self.ui.actionProcessed_Data.triggered.connect(self.startRecordingCalculated)
        self.ui.actionRaw_data.triggered.connect(self.startRecordingRaw)
        self.ui.actionAll.triggered.connect(self.startRecordingAll)

        # gogogo
        self.ui.start_device_pb.clicked.connect(self.startAll)
        self.populateWriteList()

        self.show()


    def populateWriteList(self):
        self.writingFrequency = [100.0, 500.0, 1500.0, 3000.0]
        self.writingPhase = [0.0, 0.0, 0.0, 0.0]
        self.writingAmplitude = [0.7, 0.8, 0.9, 1.0]
        self.updateFrequencyList()

    def UpdateChannelSampleInfo(self):  # TODO: for both plots...
        fg = self.generateFunctionGenerator()
        plotSettingList = self.generatePlotSettingList(fg)
        readRate = self.ui.readSampleRateSpinBox.value()
        writeRate = self.ui.writeSampleRateSpinBox.value()
        ix = self.ui.device_comboBox.currentIndex()
        device = self.devicesInfo.getDevice(ix-1)
        v_range = self.ui.readVoltageRangeSpinBox.value()
        corrTime = self.ui.readCorrelationTimeSpinBox.value()
        fg.set_sample_rate(readRate)
        self.sampleInfo.updateInfo(
            fg, self.readChannels, plotSettingList, readRate, writeRate, v_range, corrTime, device)
        print("SI: " + str(plotSettingList))

    def generatePlotSettingListAbstr(self, fg, prim_cb, proc_cb, tb_cb, lve_cb, n_sb, man_cb, min_sb, max_sb, ch_cb):
        chList = []

        # Top plot
        chn = [-1]
        type = -1
        nData = [0, 0]
        if(len(self.readChannels) > 0):
            chn = [prim_cb.currentIndex()]
            type = proc_cb.currentIndex()
            chnInfo = self.readChannels[chn[0]]
            chnInfoS = chnInfo[2][0]
            if(chnInfoS == 'F'):  # FFT
                nData = [fg.getNofF(), 1]
            elif(chnInfoS == 'R'):  # raw -> also just one channel...
                nData = [1, fg.getDataSize()]
            elif(chnInfoS == 'C'): # for correlation, if there are 2 references and only one is FFT: 1 channel per F
                nData = [1, 1]
                chRefIx = chnInfo[3]
                if(len(chRefIx)>1):
                    chnInfo2 = self.readChannels[chRefIx[0]]
                    chnInfoS2 = chnInfo2[2][0]
                    chnInfo3 = self.readChannels[chRefIx[1]]
                    chnInfoS3 = chnInfo3[2][0]
                    if( (chnInfoS2=='F') != (chnInfoS3=='F')):
                        nData = [fg.getNofF(), 1]
            else:
                nData = [1, 1]

        tlbr = tb_cb.isChecked()
        lve = lve_cb.isChecked()
        n = n_sb.value()
        useMan = man_cb.isChecked()
        minV = min_sb.value()
        maxV = max_sb.value()
        chChk = ch_cb.itemCheckedList()
        chList = [chn, type, nData, tlbr, lve, n, useMan, minV, maxV, chChk]

        return chList

    def overwritePlotSettingListAbstr(self, overWriteData, proc_cb, tb_cb, lve_cb, n_sb, man_cb, min_sb, max_sb, ch_cb):
        #chn = overWriteData[0]
        type = overWriteData[1]
        #nData = overWriteData[2]
        tlbr = overWriteData[3]
        lve = overWriteData[4]
        n = overWriteData[5]
        useMan = overWriteData[6]
        minV = overWriteData[7]
        maxV = overWriteData[8]
        chChk = overWriteData[9]

        if(len(self.readChannels) > 0):
        #    prim_cb.setCurrentIndex(chn[0])
            proc_cb.setCurrentIndex(type)

        tb_cb.setChecked(tlbr)
        lve_cb.setChecked(lve)
        n_sb.setValue(n)
        man_cb.setChecked(useMan)
        min_sb.setValue(minV)
        max_sb.setValue(maxV)
        ch_cb.setItemsChecked(chChk)
        

    def generateRecorderSettings(self,type,fg):
        # type R=raw C=calculated
        # nsmp number of samples from fg
        # nData [channels,samples per channel]
        if( type == 'R' ):
            nsmp = fg.getDataSize()
            chn = [] # all raw channels
            for ix,ch in enumerate(self.readChannels): # [['Dev1/ai0', 'RSE', 'FFT', [0]]]
                if(ch[2][0] == 'R'):
                    chn.append(ix)
            nData = [len(chn),nsmp] # [number of raw chanels, samples per sampling from fg]
            lve = self.ui.enable_raw_recording_checkBox.isChecked() # True if recording checkbox is checked
        else:
            nn = fg.getNofF()
            chn = []
            chCount = 0
            for ix,ch in enumerate(self.readChannels): 
                if(ch[2][0] == 'F'):
                    chn.append(ix)
                    chCount = chCount+nn
                elif(ch[2][0] != 'R' ): #ch[2][0] == 'C' ):
                    chn.append(ix)
                    chCount = chCount+1
            nData = [chCount,1]# [number of non raw chanels (FFT counts N*), 1]
            lve = self.ui.enable_fft_recording_checkBox.isChecked()# True if recording checkbox is checked


        type = -1 # 0 ABS, 1 Phase -> -1 complex
        
        tlbr = False
        n = -1 # number of sdamples per screen is invalid
        useMan = False # not limits to be applied during recording
        minV = 0 # not used
        maxV = 0 # not used
        chChk = [True] # not used - all channels, always

        chList = [chn, type, nData, tlbr, lve, n, useMan, minV, maxV, chChk]
        return chList


    def generatePlotSettingList(self, fg):
        
        # Order in chList must match plotindex in channelSampleInfo

        # per plot: channel index (relative to channelList) + complex preference (abs or phase) + N data is channels or samples
        chList = []

        tchList = self.generatePlotSettingListAbstr(fg, self.ui.top_plot_primary_comboBox, self.ui.top_plot_processing_comboBox, self.ui.top_show_toolbar_checkBox,
                                                    self.ui.top_plot_live_checkBox, self.ui.top_plot_NspinBox, self.ui.top_useManLim_checkBox, self.ui.top_lowerLimit_doubleSpinBox,
                                                    self.ui.top_upperLimit_doubleSpinBox, self.top_channel_cb)
        chList.append(tchList)

        # Bottom plot (TODO)
        tchList = self.generatePlotSettingListAbstr(fg, self.ui.btm_plot_primary_comboBox, self.ui.btm_plot_processing_comboBox, self.ui.btm_show_toolbar_checkBox,
                                                    self.ui.btm_plot_live_checkBox, self.ui.btm_plot_NspinBox, self.ui.btm_useManLim_checkBox, self.ui.btm_lowerLimit_doubleSpinBox,
                                                    self.ui.btm_upperLimit_doubleSpinBox, self.btm_channel_cb)
        chList.append(tchList)


        tchList = self.generateRecorderSettings('R',fg) # recorder for raw data
        chList.append(tchList)

        tchList = self.generateRecorderSettings('C',fg) # recorder for calculated data
        chList.append(tchList)

        return chList

    # uC / serial callbacks
    @QtCore.pyqtSlot()
    def refreshSerialList(self):
        #self.ui.stimSerialcomboBox
        (lst,hasPort) = self.sc.getPortList()
        self.ui.stimSerialcomboBox.clear()
        self.ui.stimSerialcomboBox.addItems(lst)
        self.ui.stimSetpushButton.setEnabled(hasPort)

    
    @QtCore.pyqtSlot()
    def updateRGBStatus(self):
        val = self.ui.stimBrughtRspinBox.value()
        if( self.ui.stimLinkRGBBrightcheckBox.isChecked() ):
            self.ui.stimBrughtGspinBox.setValue(val)
            self.ui.stimBrughtGspinBox.setEnabled(False)
            self.ui.stimBrughtBspinBox.setValue(val)
            self.ui.stimBrughtBspinBox.setEnabled(False)
        else:
            self.ui.stimBrughtGspinBox.setEnabled(True)
            self.ui.stimBrughtBspinBox.setEnabled(True)
    
    @QtCore.pyqtSlot()
    def closeData2uC(self):
        self.sc.closeConnection()

    def getStiumSettings(self):
        f = self.ui.stimFrequencydoubleSpinBox.value()
        w = self.ui.stimWaveformcomboBox.currentIndex()

        oor = self.ui.stimOnOffRatiodoubleSpinBox.value()
        lrPhase = self.ui.stimLRPhasedoubleSpinBox.value()

        r = self.ui.stimBrughtRspinBox.value()
        g = self.ui.stimBrughtGspinBox.value()
        b = self.ui.stimBrughtBspinBox.value()

        linkRGB = self.ui.stimLinkRGBBrightcheckBox.isChecked()
        prt = self.ui.stimSerialcomboBox.currentIndex()

        return [f,w,oor,lrPhase,r,g,b,prt,linkRGB]

    @QtCore.pyqtSlot()
    def setData2uC(self):
        dat = self.getStiumSettings()
        port = self.ui.stimSerialcomboBox.currentText()
        self.sc.sendMessage(port,dat[0],dat[1],dat[2],dat[3],dat[4],dat[5],dat[6])

    # general callbacks

    def closeEvent(self, event):
        print("Closing main window")
        if(self.datahandler.isRunnung() or self.isStarted):
            self.startAll()

        self.raw_recorder.killThread()
        self.raw_recorder.join()
        self.calc_recorder.killThread()
        self.calc_recorder.join()

        self.topplot.stopPlotting()
        self.btmplot.stopPlotting()
        self.btmplot.join()
        self.topplot.join()

    @QtCore.pyqtSlot()
    def updateTab(self):
        ix = self.ui.tabWidget.currentIndex()
        print(ix)
        if(ix == 1):  # Read tab
            ix_dev = self.ui.device_comboBox.currentIndex()-1
            chns = self.devicesInfo.getChannelList(ix_dev)
            self.ui.readChannelcomboBox.clear()
            self.ui.readChannelcomboBox.addItems(chns)
            self.readUpdateTerminalRef()
            self.readUpdateChannelList()
        elif(ix == 3 or ix == 4):  # Top plot or brm plot
            self.updatePlotTabs()

    # plot function
    def updatePlotTabs(self):
        1  # refresh channel list from self.readChannels

    # read functions
    def readUpdateChannelList(self):
        self.ui.readChannelList.clear()
        sLst = []
        for i in range(len(self.readChannels)):
            txt = self.readChannels[i][0] + ": " + \
                self.readChannels[i][1] + "; " + self.readChannels[i][2]
            sLst.append(txt)
        self.ui.readChannelList.addItems(sLst)

    @QtCore.pyqtSlot()
    def readAddChannel(self):
        ix_dev = self.ui.device_comboBox.currentIndex()
        if(ix_dev < 1):
            return
        ch = self.ui.readChannelcomboBox.currentText()
        ter = self.ui.terminaCVonfiguration_comboBox.currentText()
        type = self.ui.channelDataTypeComboBox.currentText()
        ref = [0]
        if("Corr" in type):
            ref = [x.row() for x in self.ui.readChannelList.selectedIndexes()]
            if(ref == []):
                ref = [self.ui.readChannelList.currentRow()]
        if(ref[0] < 0):
            QMessageBox.about(self, "Adding Corr type channel",
                              "For this channel type, one valid reference must be selected to correlate raw data - 2 entries to correlate against each other.")
            return
        elif(len(ref) > 2):
            QMessageBox.about(self, "Adding Corr type channel",
                              "For this channel type, a maximum of 2 channels to correlate may be selected.")
            return
        if("Corr" in type and len(ref) == 2):
            ter = ""
            ch = "Corr " + str(ref)
        self.readChannels.append([ch, ter, type, ref])

        print(self.readChannels)

        self.readUpdateChannelList()
        self.updatePlotLists()

    def updatePlotLists(self):
        self.top_IsUpdating = True
        # self.updatePlotList(self.ui.top_plot_primary_comboBox,self.ui.top_plot_processing_comboBox,-1)
        self.updatePlotList(self.topplot.getIndex(), self.ui.top_plot_primary_comboBox,
                            self.ui.top_plot_processing_comboBox, -1, self.top_channel_cb, self.updateTopPlotDistribution)
        self.top_IsUpdating = False

        self.btm_IsUpdating = True
        self.updatePlotList(self.btmplot.getIndex(), self.ui.btm_plot_primary_comboBox,
                            self.ui.btm_plot_processing_comboBox, -1, self.btm_channel_cb, self.updateBtmPlotDistribution)
        self.btm_IsUpdating = False

        self.updateTopPlotDistribution()

    def updatePlotList(self, ix, prim_lst, type_lst, sel, chCb, updFkt):
        if(sel < 0):
            prim_lst.clear()
            type_lst.clear()
            for chn in self.readChannels:
                prim_lst.addItem(chn[0] + " " + chn[2])
            sel = 0

        if(len(self.readChannels) > sel):
            prim_lst.setCurrentIndex(sel)
            type_lst.clear()
            tp = self.readChannels[sel][2]
            if(tp[0] == 'F'):
                type_lst.addItems(["FFT ABS", "FFT Phase"])

        updFkt()  # updates self.sampleInfo to get legend
        chCb.clear()
        lgd = self.sampleInfo.getPlotLegend(ix)
        for i, lg in enumerate(lgd):
            chCb.addItem(lg)
            chCb.setItemChecked(i, True)
        updFkt()  # updates again to add checked channel list

    def getPath(self,pth):
        pth = QFileDialog.getExistingDirectory(self,"Choose Directory",pth)
        if(len(pth)<1):
            return (pth,False)
        if(pth[-1]!='\\' and pth[-1]!='/'):
            if "\\" in pth:
                pth += "\\"
            else:
                pth += "/"
        return (pth,True)

    @QtCore.pyqtSlot()
    def getCalcPath(self):
        (pth,ok) = self.getPath(self.ui.fft_data_folder_lineEdit.text())
        if(ok):
            self.ui.fft_data_folder_lineEdit.setText(pth)
            self.updateRecorderPaths()

    @QtCore.pyqtSlot()
    def getRawPath(self):
        (pth,ok) = self.getPath(self.ui.raw_data_folder_lineEdit.text())
        if(ok):
            self.ui.raw_data_folder_lineEdit.setText(pth)
            self.updateRecorderPaths()


    @QtCore.pyqtSlot()
    def updateRecorderPaths(self):
        calc_pth = self.ui.fft_data_folder_lineEdit.text()
        raw_pth = self.ui.raw_data_folder_lineEdit.text()
        self.raw_recorder.setPath(raw_pth)
        self.calc_recorder.setPath(calc_pth)
        #self.ui.fft_data_folder_lineEdit.setText(self.calc_recorder.getPath())
        #self.ui.raw_data_folder_lineEdit.setText(self.raw_recorder.getPath())


    @QtCore.pyqtSlot()
    def topPlotSelChange(self):
        if(self.top_IsUpdating):
            return
        self.updatePlotList(self.topplot.getIndex(), self.ui.top_plot_primary_comboBox, self.ui.top_plot_processing_comboBox,
                            self.ui.top_plot_primary_comboBox.currentIndex(), self.top_channel_cb, self.updateTopPlotDistribution)

    @QtCore.pyqtSlot()
    def btmPlotSelChange(self):
        if(self.btm_IsUpdating):
            return
        self.updatePlotList(self.btmplot.getIndex(), self.ui.btm_plot_primary_comboBox, self.ui.btm_plot_processing_comboBox,
                            self.ui.btm_plot_primary_comboBox.currentIndex(), self.btm_channel_cb, self.updateBtmPlotDistribution)

    @QtCore.pyqtSlot()
    def topPlotTypeChange(self):
        if(self.top_IsUpdating):
            return
        self.updateTopPlotDistribution()

    @QtCore.pyqtSlot()
    def btmPlotTypeChange(self):
        if(self.btm_IsUpdating):
            return
        self.updateBtmPlotDistribution()

    @QtCore.pyqtSlot()
    def updateTopPlotDistribution(self):
        self.UpdateChannelSampleInfo()
        # self.sampleInfo.channelNeedsUpdate(self.topplot.getIndex())
        self.sampleInfo.allChannelNeedUpdate()  # update both to stay synced
        if(not self.datahandler.isRunnung()):
            self.topplot.updatePlot()

    @QtCore.pyqtSlot()
    def updateBtmPlotDistribution(self):
        self.UpdateChannelSampleInfo()
        # self.sampleInfo.channelNeedsUpdate(self.btmplot.getIndex())
        self.sampleInfo.allChannelNeedUpdate()  # update both to stay synced
        if(not self.datahandler.isRunnung()):
            self.btmplot.updatePlot()

    @QtCore.pyqtSlot()
    def updateRecorderStatus(self):
        self.UpdateChannelSampleInfo()
        self.sampleInfo.allChannelNeedUpdate()  # update both to stay synced
        self.syncRecordingCbWithMenu(True)


    @QtCore.pyqtSlot()
    def readRemoveChannel(self):
        val = self.ui.readChannelList.currentRow()
        if(val < 0):
            return
        del self.readChannels[val]
        self.readUpdateChannelList()

    @QtCore.pyqtSlot()
    def readClearList(self):
        self.readChannels = []
        self.readUpdateChannelList()

    @QtCore.pyqtSlot()
    def readUpdateTerminalRef(self):
        ix_dev = self.ui.device_comboBox.currentIndex()-1
        ix_ch = self.ui.readChannelcomboBox.currentIndex()
        terms = self.devicesInfo.getTerminalConfig(ix_dev, ix_ch)
        self.ui.terminaCVonfiguration_comboBox.clear()
        self.ui.terminaCVonfiguration_comboBox.addItems(terms)

    # Device selection function

    @QtCore.pyqtSlot()
    def deviceRefreshDeviceInfo(self):
        self.ui.device_comboBox.clear()
        dev = self.devicesInfo.getDevices()
        self.ui.device_comboBox.addItems(dev)
        if len(dev) > 1:
            self.ui.device_comboBox.setCurrentIndex(1)
            self.deviceUpdateDeviceInfo()

    @QtCore.pyqtSlot()
    def deviceUpdateDeviceInfo(self):
        ix = self.ui.device_comboBox.currentIndex()
        info = self.devicesInfo.getDeviceInfo(ix-1)
        self.ui.device_info_label.setText(info)

    # Signal writing functions

    def updateFrequencyList(self):
        self.ui.write_frequencies_list.clear()
        for (f, p, a) in zip(self.writingFrequency, self.writingPhase, self.writingAmplitude):
            tStr = "F = %.2f Hz, Phase = %.2f deg, amp = %.2f" % (f, p, a)
            # print(tStr)
            self.ui.write_frequencies_list.addItem(tStr)
        self.updateFrequencies()

    @QtCore.pyqtSlot()
    def writingAddFrequency(self):
        f = self.ui.frequencySpinBox.value()
        p = self.ui.phaseSpinBox.value()
        a = self.ui.amplitude_spinBox.value()
        self.writingFrequency.append(f)
        self.writingPhase.append(p)
        self.writingAmplitude.append(a)
        self.updateFrequencyList()

    def updateFrequencies(self):
        if(self.ui.device_hold_checkBox.isChecked):
            fg = self.generateFunctionGenerator()
            self.ui.writeSampleRateSpinBox.setValue(fg.getSampleRate())
            # *2 led to async between reqad and write...
            self.ui.readSampleRateSpinBox.setValue(fg.getSampleRate())

    @QtCore.pyqtSlot()
    def writingRemoveFrequency(self):
        val = self.ui.write_frequencies_list.currentRow()
        del self.writingFrequency[val]
        del self.writingPhase[val]
        del self.writingAmplitude[val]
        self.updateFrequencyList()

    @QtCore.pyqtSlot()
    def writingClearFrequencies(self):
        self.ui.write_frequencies_list.clear()
        self.writingFrequency = []
        self.writingPhase = []
        self.writingAmplitude = []

    @QtCore.pyqtSlot()
    def writingApplyFrequencies(self):
        val = self.ui.write_frequencies_list.currentRow()
        f = self.ui.frequencySpinBox.value()
        p = self.ui.phaseSpinBox.value()
        a = self.ui.amplitude_spinBox.value()
        self.writingFrequency[val] = f
        self.writingPhase[val] = p
        self.writingAmplitude[val] = a
        self.updateFrequencyList()

    @QtCore.pyqtSlot()
    def writingUpdateFPA(self):
        val = self.ui.write_frequencies_list.currentRow()
        self.ui.frequencySpinBox.setValue(self.writingFrequency[val])
        self.ui.phaseSpinBox.setValue(self.writingPhase[val])
        self.ui.amplitude_spinBox.setValue(self.writingAmplitude[val])

    @QtCore.pyqtSlot()
    def writingPreviewSignal(self):
        if(len(self.writingFrequency) < 1):
            return

        fg = self.generateFunctionGenerator()
        sig = fg.getSignal()
        print("Sig: " + str(np.size(sig)) + " at " + str(fg.getSampleRate()))

        plt.plot(np.linspace(0, 1, np.size(sig)), sig[0, :])
        plt.show()

    def generateFunctionGenerator(self):
        ff = np.array(self.writingFrequency)
        pp = np.array(self.writingPhase)
        aa = np.array(self.writingAmplitude)
        allAmpl = self.ui.writing_amplitude_SpinBox.value()
        fg = FunctionGen(ff, pp, aa, allAmpl)
        return fg

    def changeUIStartStop(self, isStarted):
        if(self.isStarted):
            self.ui.start_device_pb.setText("Stop")
            self.ui.read_tab.setEnabled(False)
            self.ui.write_tab.setEnabled(False)
            self.ui.device_comboBox.setEnabled(False)
            self.ui.refresh_device_pb.setEnabled(False)
            self.ui.readSampleRateSpinBox.setEnabled(False)
            self.ui.writeSampleRateSpinBox.setEnabled(False)
            self.ui.device_hold_checkBox.setEnabled(False)
        else:
            self.ui.start_device_pb.setText("Start")
            self.ui.read_tab.setEnabled(True)
            self.ui.write_tab.setEnabled(True)
            self.ui.device_comboBox.setEnabled(True)
            self.ui.refresh_device_pb.setEnabled(True)
            self.ui.readSampleRateSpinBox.setEnabled(True)
            self.ui.writeSampleRateSpinBox.setEnabled(True)
            self.ui.device_hold_checkBox.setEnabled(True)

    @QtCore.pyqtSlot()
    def startAll(self):

        try:
            if(self.datahandler.isRunnung() or self.isStarted):
                self.datahandler.stopSamplingAndWriting()
                self.isStarted = False
                self.changeUIStartStop(False)
                return

            ix = self.ui.device_comboBox.currentIndex()
            if(len(self.readChannels)<1 or ix<1):
                return

            # readRate = self.ui.readSampleRateSpinBox.value()
            # writeRate = self.ui.writeSampleRateSpinBox.value()
            # ix = self.ui.device_comboBox.currentIndex()
            # device = self.devicesInfo.getDevice(ix-1)
            # v_range = self.ui.readVoltageRangeSpinBox.value()
            # fg = self.generateFunctionGenerator()
            # fg.set_sample_rate(writeRate)
            # self.datahandler.setupSampling(readRate,fg.getDataSize(),self.readChannels,v_range)
            # self.datahandler.setupWriting( device, [0], fg )

            self.UpdateChannelSampleInfo()
            self.datahandler.setupSampling_si(self.readChannels)
            self.datahandler.setupWriting_si([0])

            self.datahandler.startSamplingAndWriting()

            self.isStarted = True
            self.changeUIStartStop(True)

        except (RuntimeError, TypeError, NameError) as err:
            traceback.print_exc()
            print(err)


    # Menu callbacks

    @QtCore.pyqtSlot()
    def loadSettings(self):

        (fileName,filter) = QFileDialog.getOpenFileName(self,"Load Status","default.stf","Status file (*.stf)")
        if( len(fileName)<=0 ):
            return

        with open(fileName, 'rb') as f: 
            mylist = pickle.load(f)

            chLst = mylist[0]
            fLst = mylist[1]
            pLst = mylist[2]
            aLst = mylist[3]
            elementsLst = mylist[4]
            plotLst = mylist[5]
            stimLst = mylist[6]

            self.readChannels = chLst
            self.readUpdateChannelList() # update channel list
            self.writingFrequency = fLst
            self.writingPhase = pLst
            self.writingAmplitude = aLst
            self.updateFrequencyList() # update frequency list
            self.setUIelements(elementsLst,stimLst)

            self.updatePlotLists()
            # update plot settings
            # according to generatePlotSettingListAbstr() -> set UI, then call self.UpdateChannelSampleInfo()
            # Frequency lists must be restored already
            fg = self.generateFunctionGenerator()
            # Also self.readChannels must be set also updatePlotLists
            # Top plot
            if(len(self.readChannels) > 0): # make sure channel lists are present before setting them
                self.ui.top_plot_primary_comboBox.setCurrentIndex(plotLst[0][0][0])
                self.ui.btm_plot_primary_comboBox.setCurrentIndex(plotLst[1][0][0])
            self.overwritePlotSettingListAbstr(plotLst[0], self.ui.top_plot_processing_comboBox, self.ui.top_show_toolbar_checkBox,
                                                    self.ui.top_plot_live_checkBox, self.ui.top_plot_NspinBox, self.ui.top_useManLim_checkBox, self.ui.top_lowerLimit_doubleSpinBox,
                                                    self.ui.top_upperLimit_doubleSpinBox, self.top_channel_cb)
            # Bottom plot
            self.overwritePlotSettingListAbstr(plotLst[1], self.ui.btm_plot_processing_comboBox, self.ui.btm_show_toolbar_checkBox,
                                                    self.ui.btm_plot_live_checkBox, self.ui.btm_plot_NspinBox, self.ui.btm_useManLim_checkBox, self.ui.btm_lowerLimit_doubleSpinBox,
                                                    self.ui.btm_upperLimit_doubleSpinBox, self.btm_channel_cb)
            self.UpdateChannelSampleInfo()



        
    @QtCore.pyqtSlot()
    def saveSettings(self):
        (fileName,filter) = QFileDialog.getSaveFileName(self,"Save Status","default.stf","Status file (*.stf)")
        if( len(fileName)<=0 ):
            return

        chLst = self.readChannels #[['Dev1/ai0', 'RSE', 'FFT', [0]]]
        fLst = self.writingFrequency
        pLst = self.writingPhase
        aLst = self.writingAmplitude
        fg = self.generateFunctionGenerator()
        plt_set = self.generatePlotSettingList(fg) # Plot settings are 0 and 1:
        plotLst = plt_set
        # per plot: channel index (relative to channelList) + complex preference (abs or phase) + 
        # N data [channels,samples per channel] +
        # Then also: use toolbar + isLive + N samples per screen
        # Followed by: useManualLimit + min limit + max limit + selected channels list
        rec_cal_pth = self.ui.fft_data_folder_lineEdit.text()
        rec_raw_pth = self.ui.raw_data_folder_lineEdit.text()

        dev_ix = self.ui.device_comboBox.currentIndex() # -> if possible
        sr = self.ui.readSampleRateSpinBox.value()
        wr = self.ui.writeSampleRateSpinBox.value()
        hld_f = self.ui.device_hold_checkBox.isChecked()

        elementsLst = [rec_cal_pth,rec_raw_pth,dev_ix,sr,wr,hld_f]

        stimLst = self.getStiumSettings() # [f,w,oor,lrPhase,r,g,b,prt,linkRGB]
        

        mylist = [chLst,fLst,pLst,aLst,elementsLst,plotLst,stimLst]

        print(mylist)

        with open(fileName, 'wb') as f: 
            pickle.dump(mylist, f)
            
    
    def setUIelements(self,elementsLst,stimLst):
        # Recording paths
        rec_cal_pth = elementsLst[0]
        rec_raw_pth = elementsLst[1]
        self.ui.fft_data_folder_lineEdit.setText(rec_cal_pth)
        self.ui.raw_data_folder_lineEdit.setText(rec_raw_pth)

        # device settings
        dev_ix = elementsLst[2]
        sr = elementsLst[3]
        wr = elementsLst[4]
        hld_f = elementsLst[5]
        if(dev_ix<self.ui.device_comboBox.count()):
            self.ui.device_comboBox.setCurrentIndex(dev_ix)
        self.ui.readSampleRateSpinBox.setValue(sr)
        self.ui.writeSampleRateSpinBox.setValue(wr)
        self.ui.device_hold_checkBox.setChecked(hld_f)


        # Stim settings
        f = stimLst[0]
        w = stimLst[1]
        oor = stimLst[2]
        lrPhase = stimLst[3]
        r = stimLst[4]
        g = stimLst[5]
        b = stimLst[6]
        prt = stimLst[7]
        linkRGB = stimLst[8]

        self.ui.stimFrequencydoubleSpinBox.setValue(f)
        self.ui.stimWaveformcomboBox.setCurrentIndex(w)
        self.ui.stimOnOffRatiodoubleSpinBox.setValue(oor)
        self.ui.stimLRPhasedoubleSpinBox.setValue(lrPhase)
        self.ui.stimBrughtRspinBox.setValue(r)
        self.ui.stimBrughtGspinBox.setValue(g)
        self.ui.stimBrughtBspinBox.setValue(b)
        if(prt<self.ui.stimSerialcomboBox.count()):
            self.ui.stimSerialcomboBox.setCurrentIndex(dev_ix)
        self.ui.stimLinkRGBBrightcheckBox.setChecked(linkRGB)



    @QtCore.pyqtSlot()
    def exitApp(self):
        print("Exit Called from Menu")
        self.close()
        sys.exit()

    @QtCore.pyqtSlot()
    def activateRecordingFromMenu(self):
        self.startAll()
        self.ui.actionRun.setChecked(self.isStarted)

    def syncRecordingCbWithMenu(self,toMenu):
        if(toMenu):
            r_calc = self.ui.enable_fft_recording_checkBox.isChecked()
            r_raw = self.ui.enable_raw_recording_checkBox.isChecked()
            self.ui.actionProcessed_Data.setChecked(r_calc)
            self.ui.actionRaw_data.setChecked(r_raw)
            self.ui.actionAll.setChecked(r_calc and r_raw)
        else:
            m_calc = self.ui.actionProcessed_Data.isChecked()
            m_raw = self.ui.actionRaw_data.isChecked()
            self.ui.actionAll.setChecked(m_calc and m_raw)
            self.ui.enable_fft_recording_checkBox.setChecked(m_calc) # if changed, schold call changed callback
            self.ui.enable_raw_recording_checkBox.setChecked(m_raw)

    @QtCore.pyqtSlot()
    def startRecordingCalculated(self):
        ckd = self.ui.actionProcessed_Data.isChecked()
        self.ui.actionProcessed_Data.setChecked(ckd)
        self.syncRecordingCbWithMenu(False)

    @QtCore.pyqtSlot()
    def startRecordingRaw(self):
        ckd = self.ui.actionRaw_data.isChecked()
        self.ui.actionRaw_data.setChecked(ckd)
        self.syncRecordingCbWithMenu(False)

    @QtCore.pyqtSlot()
    def startRecordingAll(self):
        ckd = self.ui.actionAll.isChecked()
        self.ui.actionAll.setChecked(ckd)
        self.ui.actionProcessed_Data.setChecked(ckd)
        self.ui.actionRaw_data.setChecked(ckd)
        self.syncRecordingCbWithMenu(False)


app = QtWidgets.QApplication(sys.argv)
MainWindow = MyMainWindow()
# MainWindow.show()
app.exec_()