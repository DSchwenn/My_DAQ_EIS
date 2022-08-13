import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader
import nidaqmx.system
from nidaqmx import *


write_Task = nidaqmx.Task()

chan_args = {
             "min_val": -10,
             "max_val": 10,
             }

write_Task.ao_channels.add_ao_voltage_chan('Dev1/ao0',**chan_args)
write_Task.timing.cfg_samp_clk_timing(rate= 40, sample_mode= AcquisitionType.FINITE, samps_per_chan= 120) # CONTINUOUS FINITE
test_Writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(write_Task.out_stream, auto_start=True)


task = nidaqmx.Task("Reader Task")
chan_args = {
             "min_val": -10,
             "max_val": 10,
             "terminal_config": nidaqmx.constants.TerminalConfiguration.RSE
             }
channel_name = 'Dev1/ai0'  # 'Dev1/ai0:3'
task.ai_channels.add_ai_voltage_chan(channel_name,**chan_args)
task.timing.cfg_samp_clk_timing(rate=40, sample_mode=AcquisitionType.CONTINUOUS) 


samples = np.append(np.append(5*np.ones(40), np.zeros(40)),-5*np.ones(40))
test_Writer.write_many_sample(samples) # 8,191 samples buffer


task.start()
reader = AnalogMultiChannelReader(task.in_stream)
input = np.empty(shape=(1, 25))
for x in range(5):
    reader.read_many_sample(data=input,number_of_samples_per_channel=25) # nidaqmx.constants.READ_ALL_AVAILABLE
    print( input )




write_Task.wait_until_done( timeout=5 )
write_Task.stop()
write_Task.close()


task.stop()
task.close()
