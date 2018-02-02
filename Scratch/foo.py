import serial
import numpy as np
from matplotlib import pyplot as plt
from timeit import default_timer as timer
import time

ser = serial.Serial('COM9', 9600)
FREQ = 0.1
 
plt.ion() # set plot to animated
 
ydata = [0] * 500
ax1=plt.axes()  
 
# make plot
line, = plt.plot(ydata)
plt.ylim([0,1200])
 
# start data collection
start = timer()
while True:
    current = timer()
    data = ser.readline().strip()# read data from serial 

                                   # port and strip line endings

    if data:
        data = int(data)
        ydata.append(data)
        del ydata[0]
        print(data)
        

    if current - start > FREQ:
        #print('plotting')
        start = timer()      
        line.set_xdata(np.arange(len(ydata)))
        line.set_ydata(ydata)  # update the data
        plt.draw() # update the plot
        plt.pause(0.1)

        
        
        
        
