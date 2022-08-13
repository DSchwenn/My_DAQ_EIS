import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader
import nidaqmx.system
from nidaqmx import *


system = nidaqmx.system.System.local()


print(system.driver_version)

for device in system.devices:
    print(device)

sample_size = 20
n_channels = 1
sampleRate = 10


test_Task = nidaqmx.Task()

chan_args = {
             "min_val": -10,
             "max_val": 10,
             }

test_Task.ao_channels.add_ao_voltage_chan('Dev1/ao0',**chan_args)
test_Task.timing.cfg_samp_clk_timing(rate= 80, sample_mode= AcquisitionType.FINITE, samps_per_chan= 80) # CONTINUOUS FINITE

test_Writer = nidaqmx.stream_writers.AnalogSingleChannelWriter(test_Task.out_stream, auto_start=True)

samples = np.append(5*np.ones(60), np.zeros(20))

test_Writer.write_many_sample(samples) # 8,191 samples buffer

test_Task.wait_until_done( timeout=5 )
test_Task.stop()
test_Task.close()
