from itertools import count
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import numpy.fft as fft

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader
import nidaqmx.system
from nidaqmx import *


plt.style.use('fivethirtyeight')


write_Task = nidaqmx.Task()

chan_args = {
             "min_val": -10,
             "max_val": 10,
             }

write_Task.ao_channels.add_ao_voltage_chan('Dev1/ao0',**chan_args)
write_Task.timing.cfg_samp_clk_timing(rate= 5000, sample_mode= AcquisitionType.CONTINUOUS, samps_per_chan= 500) # CONTINUOUS FINITE
test_Writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(write_Task.out_stream, auto_start=True)


task = nidaqmx.Task("Reader Task")
chan_args = {
             "min_val": -10,
             "max_val": 10,
             "terminal_config": nidaqmx.constants.TerminalConfiguration.RSE
             }
channel_name = 'Dev1/ai0'  # 'Dev1/ai0:3'
task.ai_channels.add_ai_voltage_chan(channel_name,**chan_args)
task.timing.cfg_samp_clk_timing(rate=1000, sample_mode=AcquisitionType.CONTINUOUS) 

#samples = np.append(np.append(5*np.ones(40), np.zeros(40)),-5*np.ones(40))



task.start()
reader = AnalogMultiChannelReader(task.in_stream)


def animate(i):
    global reader
    n_read = 100
    plt.clf()
    #r1 = np.random.rand(1,256)
    #f1 = abs(fft.fft(r1))
    input = np.empty(shape=(1, n_read))
    reader.read_many_sample(data=input,number_of_samples_per_channel=n_read)
    
    f1 = np.log(abs(fft.fft(input)))
    xx = np.arange(start=0,stop=np.size(f1),dtype=np.float64)
    plt.bar(xx[1:], f1[0,1:])

    #xx = np.arange(start=0,stop=n_read,dtype=np.float64)
    #plt.plot(xx,input[0,:])

aa = np.linspace(0,2*np.pi*(1-1/500),500)
samples = np.sin(aa)+np.sin(aa*10)
test_Writer.write_many_sample(samples) # 8,191 samples buffer


ani = FuncAnimation(plt.gcf(), animate, interval=1) # run animate function every xxx ms

plt.tight_layout()
plt.show()


#write_Task.wait_until_done( timeout=60 )
write_Task.stop()
write_Task.close()

task.stop()
task.close()
