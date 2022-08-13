#!/usr/bin/python

import numpy as np
import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx import *



class NiWriter:
    def __init__(self, sample_rate, data, device, channels):
        self.sample_rate = sample_rate
        self.data = data.flatten()
        self.samples = np.size(data)
        print("Writing: " + str(np.size(data)) + " " + str(sample_rate))
        self.task = None
        self.writer = None
        self.min_v, self.max_v = self.getMinMax()
        self.device = device
        self.channels = channels
    

    def startWriting(self):
        if(self.task is not None):
            self.stopWriting()

        self.task = nidaqmx.Task()

        for ch in self.channels:
                channel_name = self.device + "/ao" + str(ch) # 'Dev1/ai0:3' - comma separation works
                self.task.ao_channels.add_ao_voltage_chan(channel_name, min_val = self.min_v, max_val = self.max_v)

        self.task.timing.cfg_samp_clk_timing(rate=self.sample_rate, sample_mode= AcquisitionType.CONTINUOUS, samps_per_chan=self.samples) # CONTINUOUS FINITE
        self.writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(self.task.out_stream, auto_start=True)
        self.writer.write_many_sample(self.data) # 8,191 samples buffer

    def stopWriting(self):
        if(self.task is not None):
            self.task.stop()
            self.task.close()

    def getMinMax(self):
        mn = np.min(self.data)
        mx = np.max(self.data)

        return mn, mx; # tuple


