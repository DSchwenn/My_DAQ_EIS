import nidaqmx
import numpy as np
from nidaqmx.constants import AcquisitionType
from nidaqmx.stream_readers import AnalogMultiChannelReader
import nidaqmx.system

system = nidaqmx.system.System.local()


print(system.driver_version)



for device in system.devices:
    print(device.name)
    for ch in device.ai_physical_chans:
        print(ch.name)
        print(ch.ai_term_cfgs) # [<TerminalConfiguration.RSE: 10083>, <TerminalConfiguration.NRSE: 10078>, <TerminalConfiguration.DIFFERENTIAL: 10106>]
    device.ao_max_rate
    device.ao_min_rate
    device.ai_samp_modes # [<AcquisitionType.FINITE: 10178>, <AcquisitionType.CONTINUOUS: 10123>]
    device.ai_min_rate
    device.ai_max_single_chan_rate
    device.ai_max_multi_chan_rate
    device.ai_meas_types # [<UsageTypeAI.CURRENT: 10134>, <UsageTypeAI.RESISTANCE: 10278>, <UsageTypeAI.STRAIN_STRAIN_GAGE: 10300>, <UsageTypeAI.TEMPERATURE_RTD: 10301>, <UsageTypeAI.TEMPERATURE_THERMISTOR: 10302>, <UsageTypeAI.TEMPERATURE_THERMOCOUPLE: 10303>, <UsageTypeAI.TEMPERATURE_BUILT_IN_SENSOR: 10311>, <UsageTypeAI.VOLTAGE: 10322>, <UsageTypeAI.VOLTAGE_CUSTOM_WITH_EXCITATION: 10323>, <UsageTypeAI.ROSETTE_STRAIN_GAGE: 15980>]

sample_size = 20
n_channels = 1
sampleRate = 10

#input = np.empty(shape=(len(channels), self.sample_size))
input = np.empty(shape=(n_channels, sample_size))


task = nidaqmx.Task("Reader Task")
chan_args = {
             "min_val": -10,
             "max_val": 10,
             "terminal_config": nidaqmx.constants.TerminalConfiguration.RSE
             }


channel_name = 'Dev1/ai0'  # 'Dev1/ai0:3'
task.ai_channels.add_ai_voltage_chan(channel_name,**chan_args)

# Timing definition
task.timing.cfg_samp_clk_timing(rate=sampleRate, sample_mode=AcquisitionType.CONTINUOUS) # rate in samples per channel per second

task.start()
reader = AnalogMultiChannelReader(task.in_stream)

for x in range(3):
    reader.read_many_sample(data=input,number_of_samples_per_channel=sample_size) # nidaqmx.constants.READ_ALL_AVAILABLE
    print( input )


task.stop()
task.close()

