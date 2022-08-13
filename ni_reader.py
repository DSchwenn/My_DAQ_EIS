#!/usr/bin/python

import numpy as np
import threading
from nidaqmx.stream_readers import AnalogMultiChannelReader
import nidaqmx
from nidaqmx import *
from regex import R
from sympy import RealNumber


class NiReader(threading.Thread):

    def __init__(self, sample_rate, sample_size, channels, ref_types, v_range):    
        threading.Thread.__init__(self)
        self.sample_rate = sample_rate
        self.sample_size = int(sample_size)
        self.channels = channels # 'Dev1/ai0,...'
        self.ref_types = self.readRefType(ref_types)
        self.v_range = v_range

        print("Reading: " + str(self.sample_size) + " " + str(sample_rate))

        self.is_running = False
        self.is_paused = False
        self.is_stopped = True

        self.task = None
        self.reader = None

        self.input = np.empty(shape=(len(channels), self.sample_size))

        self.buffer = []
        self.n_buffer = 0


    def readRefType(self,ref_types):
        res = []

        for ref in ref_types:
            if( ref[0] == 'R' ):
                res.append(nidaqmx.constants.TerminalConfiguration.RSE)
            elif( ref[0] == 'N' ):
                res.append(nidaqmx.constants.TerminalConfiguration.NRSE)
            elif( ref[0] == 'D' ):
                res.append(nidaqmx.constants.TerminalConfiguration.DIFFERENTIAL)

        return res


    def run(self):
        self.init_task()
        self.task.start()
        self.reader = AnalogMultiChannelReader(self.task.in_stream)
        self.is_running = True
        self.is_stopped = False

        while self.is_running:
            if not self.is_paused:
                try:
                    self.reader.read_many_sample(data=self.input,number_of_samples_per_channel=self.sample_size) # nidaqmx.constants.READ_ALL_AVAILABLE
                    self.buffer.append( np.copy(self.input) )
                    self.n_buffer+=1
                    #print(self.n_buffer)
                except Exception as e:
                    print("Error with read_many_sample")
                    print(e)
                    break
        self.task.stop()

        self.task.wait_until_done()
        self.task.close()

        self.is_stopped = True

        return None


    def init_task(self):

        self.task = nidaqmx.Task("Reader Task")
        for i in range(len(self.channels)):

                channel_name = self.channels[i] # self.dev_name + "/ai" + str(ch) # 'Dev1/ai0:3' - comma separation works

                self.task.ai_channels.add_ai_voltage_chan(physical_channel=channel_name,
                    terminal_config=self.ref_types[i],
                    min_val=(self.v_range*-1), max_val=self.v_range)

        self.task.timing.cfg_samp_clk_timing(rate=self.sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)#,samps_per_chan=self.sample_size*20) 
        


    def getData(self):
        if(self.n_buffer>0):
            self.is_paused = True
            dat = self.buffer[0]
            del self.buffer[0]
            self.n_buffer-=1
            self.is_paused = False
            return dat

        return None

    def bufferSize(self):
        return self.n_buffer

    def stopReading(self):
        self.is_running = False

    def pauseReading(self,pause):
        self.is_paused = pause

    def isStopped(self):
        return self.is_stopped

    def restart(self):
        print("Restarting the task")
        # Closing
        self.is_paused = True
        self.task.stop()
        self.task.close()

        # Starting
        self.create_task()
        self.task.start()
        self.reader = AnalogMultiChannelReader(self.task.in_stream)
        self.is_paused = False



# import matplotlib.pyplot as plt

# nr = NiReader(100, 20, [0], 'Dev1',10)
# nr.start()
# count = 0

# while count<20:
#     dat = nr.getData()
#     if(dat is not None):
#         plt.clf()
#         plt.plot(np.linspace(0,1,np.size(dat)),dat[0,:])
#         count += 1
#         plt.show()

# nr.stopReading()

