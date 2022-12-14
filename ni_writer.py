#!/usr/bin/python

import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx import *



class NiWriter:
    def __init__(self, sample_rate, data, device, channels):
        self.sample_rate = sample_rate
        self.samples = np.size(data[0])
        self.channels = channels
        self.data = self.formatData(data) # data.flatten()
        print("Writing: " + str(np.size(data)) + " " + str(sample_rate))
        self.task = None
        self.writer = None
        self.min_v, self.max_v = self.getMinMax()
        self.device = device
        
    
    def formatData(self,data):
        if(len(data)<2):
            return data

        dat2 = np.zeros((len(data),np.size(data[0])))
        for i,d in enumerate(data):
            dat2[i,] = d.flatten()
        return dat2

    def startWriting(self):
        if(self.task is not None):
            self.stopWriting()

        self.task = nidaqmx.Task()

        if(len(self.channels)<2):
            #for ch in self.channels:
            channel_name = self.device + "/ao" + str(self.channels[0]) # 'Dev1/ai0:3' - comma separation works
            self.task.ao_channels.add_ao_voltage_chan(channel_name, min_val = self.min_v, max_val = self.max_v)

            self.task.timing.cfg_samp_clk_timing(rate=self.sample_rate, sample_mode= AcquisitionType.CONTINUOUS, samps_per_chan=self.samples) # CONTINUOUS FINITE
            self.writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(self.task.out_stream, auto_start=True)
            self.writer.write_many_sample(self.data[0].flatten()) # 8,191 samples buffer
        else:
            for ch in self.channels:
                channel_name = self.device + "/ao" + str(ch) # 'Dev1/ai0:3' - comma separation works
                self.task.ao_channels.add_ao_voltage_chan(channel_name, min_val = self.min_v, max_val = self.max_v)

            self.task.timing.cfg_samp_clk_timing(rate=self.sample_rate, sample_mode= AcquisitionType.CONTINUOUS, samps_per_chan=self.samples) # CONTINUOUS FINITE
            self.writer = nidaqmx.stream_writers.AnalogMultiChannelWriter(self.task.out_stream, auto_start=True)
            self.writer.write_many_sample(self.data) # 8,191 samples buffer - 2d np array rpw per channel -> formatData()

    def stopWriting(self):
        if(self.task is not None):
            self.task.stop()
            self.task.close()

    def getMinMax(self):
        mn = np.min(self.data)
        mx = np.max(self.data)

        return mn, mx; # tuple


