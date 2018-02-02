import serial
import numpy as np
import matplotlib
matplotlib.use('GTKAgg')
from matplotlib import pyplot as plt

from timeit import default_timer as timer
import time

ser = serial.Serial('COM3', 9600)
FREQ = 0.01
 
plt.ion() # set plot to animated

MAXLENGTH = 500
 
ydata = [0] * 500
ax1=plt.axes()  
 
# make plot
line, = plt.plot(ydata)
plt.ylim([0,1200])
 
# start data collection
start = timer()
while True:
    current = timer()
    data = ser.read(100).strip().split('\r\n')# read data from serial 

                                   # port and strip line endings

    if data:
        data = [int(d) for d in data]
        ydata += data

        if len(ydata) > MAXLENGTH:
            ydata = ydata[-MAXLENGTH:]
        #del ydata[0]
        #print(data)
        #print(ydata)
        

    if current - start > FREQ:
        print(current - start)
        #print('plotting')
        start = timer()      
        line.set_xdata(np.arange(len(ydata)))
        line.set_ydata(ydata)  # update the data
        plt.draw() # update the plot
        plt.pause(0.1)

        
        
        
        
