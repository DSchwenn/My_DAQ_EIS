
import random
from itertools import count
#import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import numpy.fft as fft

plt.style.use('fivethirtyeight')

x_vals = np.array([1, 2, 3, 4, 5])
y1_vals = np.array([0.1, 0.3, 0.2, 0.3, 0.5])
y2_vals = np.array([0.1, 0.3, 0.2, 0.3, 0.5])

plt.plot([], [], label='Channel 1')
plt.plot([], [], label='Channel 2')

index = count()

def animate(i):
    global x_vals
    global y1_vals
    global y2_vals

    #r1 = np.array(random.randint(0, 5))
    #r2 = np.array(random.randint(0, 5))
    r1 = np.random.rand(1,256)
    r2 = np.random.rand(1,256)
    f1 = abs(fft.fft(r1))
    f2 = abs(fft.fft(r2))

    xx = x_vals[-1]+1

    x_vals = np.append(x_vals, xx)#np.array(next(index))+5 )
    y1_vals = np.append(y1_vals, f1[0,5] )
    y2_vals = np.append(y2_vals, f2[0,10] )
    
    # plt.cla()
    # plt.plot(x,y1,label='Channel 1')
    # plt.plot(x,y2,label='Channel 2')

    ax = plt.gca()
    line1,line2 = ax.lines
    line1.set_data(x_vals, y1_vals)
    line2.set_data(x_vals, y2_vals)

    xlim_low, xlim_high = ax.get_xlim()
    ylim_low, ylim_high = ax.get_ylim()

    ax.set_xlim(xlim_low, (x_vals.max() + 1))

    y1max = y1_vals.max()
    y2max = y2_vals.max()
    current_ymax = y1max if (y1max > y2max) else y2max

    y1min = y1_vals.min()
    y2min = y2_vals.min()

    current_ymin = y1min if (y1min < y2min) else y2min

    ax.set_ylim((current_ymin - 1), (current_ymax + 1))
    #print( y1_vals )



ani = FuncAnimation(plt.gcf(), animate, interval=500) # run animate function every 1000 ms

plt.legend(loc='upper left')
plt.legend()
plt.tight_layout()
plt.show()


# data = pd.read_csv('data.csv')
# x = data['x_value']
# y1 = data['total_1']
# y2 = data['total_2']