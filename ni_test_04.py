
from os import TMP_MAX
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import time

from ni_writer import NiWriter
from ni_reader import NiReader
from function_gen import FunctionGen

f_list = np.array([100.,700.,2500.,5000.])
phase_list = np.array([0.0,0.0,0.0,0.0])
amp_list = np.array([1.,1.,1.,1.])
v_amplitude = 2.5

fg = FunctionGen(f_list,phase_list,amp_list,v_amplitude)
sig = fg.getSignal()

sample_rate_write = fg.getSampleRate()
sample_rate_read = sample_rate_write*2
sample_size = int(np.size(sig)*sample_rate_read/sample_rate_write)

niw = NiWriter(sample_rate_write,sig,'Dev1',[0])

nir = NiReader(sample_rate_read,sample_size,[0],'Dev1',10)

fft_freq = fft.fftfreq(sample_size)*sample_rate_read

ixi = np.zeros(shape=(1, np.size(f_list)))
for i in range(np.size(f_list)):
    dff = np.abs(fft_freq-f_list[i])
    ix = np.where(dff == np.amin(dff))
    ixi[0,i] = ix[0][0]
ixi = ixi.astype(int)

# plot only values at ixi ~ abs of given frequencies 

for f in f_list:
    nm = 'F='+str(f)+'Hz'
    plt.plot([], [], label=nm)

ylim_low = 0
ylim_high = 1

def animate(i):
    global ixi
    global nir
    global sample_rate_read
    global ylim_low
    global ylim_high
    
    while nir.bufferSize() < 1:
        time.sleep(0.05)

    while nir.bufferSize() > 0:
        ax = plt.gca()
        x_vals = ax.lines[0].get_xdata()

        x_time = 20
        n_max = x_time/(sample_size/sample_rate_read)/2
        if(np.size(x_vals)>=n_max):
            i1 = int(n_max/2)
            x_vals = x_vals[i1:-1]
            x_vals -= x_vals[0]
            for l in ax.lines:
                y_dat = l.get_ydata()
                y_dat = y_dat[i1:-1]
                l.set_data(x_vals, y_dat)

        if(np.size(x_vals)>0):
            xx = x_vals[-1]+sample_size/sample_rate_read*2
            x_vals = np.append(x_vals, xx)
        else:
            x_vals = np.append(x_vals, 0)

        while nir.bufferSize() >= 1:
            data = nir.getData()
        
        #f1 = np.log(abs(fft.fft(data)))
        f1 = abs(fft.fft(data))

        yMax = 0.
        yMin = 999999.

        for i in range(np.size(ax.lines)):
            l = ax.lines[i]
            y_dat = l.get_ydata()
            y_dat = np.append(y_dat,f1[0][ixi[0][i]] )
            l.set_data(x_vals, y_dat)
            tmx = y_dat.max()
            tmn = y_dat.min()
            if( tmx>yMax ):
                yMax = tmx
            if( tmn<yMin ):
                yMin = tmn
        
        # TODO: fixed x-lim, ylim only increase/ no decrease - to max y.
        ax.set_xlim(0, x_time)
        # tylim_low, tylim_high = ax.get_ylim()
        # if(tylim_low < ylim_low):
        #     ylim_low = tylim_low-0.5
        # if(tylim_high>ylim_high):
        #     ylim_high=tylim_high+0.5

        ax.set_ylim(yMin-2, yMax+2)

        #xx = np.arange(start=0,stop=np.size(f1),dtype=np.float64)
        #plt.bar(fft_freq[1:], f1[0,1:])


# V source as second Ni input - also plot fft; subplot
# Heart rate as input (~electronics) -> also plot
# Recording function
# Stimulus - as input & Light

ani = FuncAnimation(plt.gcf(), animate, interval=0.05)

niw.startWriting()
nir.start()

plt.legend(loc='upper left')
plt.tight_layout()
plt.show()

nir.stopReading()
nir.join()

niw.stopWriting()
