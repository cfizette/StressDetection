import serial
import numpy as np
from matplotlib import pyplot as plt
from timeit import default_timer as timer
import time
import threading
import multiprocessing


ser = serial.Serial('COM9', 9600)
FREQ = 0.1
 
plt.ion() # set plot to animated
 
ydata = [0] * 500
ax1=plt.axes()  
 
# make plot
line, = plt.plot(ydata)
plt.ylim([0,1200])



def collect_data():
    while True:
        
        data = ser.readline().strip()# read data from serial 

        print(data)                          # port and strip line endings
        if data:
            data = int(data)
            ydata.append(data)
            del ydata[0]
    
def plot_data():
    # set up timers
    start = timer()
    current = timer()
    while True:
        current = timer()
        #ydata.append(100)
        #ydata.pop(0)
        #print('im the plotter')
        if current - start > FREQ:
            print('plotting')
            start = timer()      
            line.set_xdata(np.arange(len(ydata)))
            line.set_ydata(ydata)  # update the data
            plt.draw() # update the plot
            plt.pause(0.1)
def test():
    print('aksdfkjafkafsadfjasf')
    


#plotter = multiprocessing.Process(target=plot_data)
collecter = multiprocessing.Process(target=test, args=())
#plotter.start()
collecter.start()
collecter.join()
time.sleep(1)
        
#collect_data()
plot_data()
        
        
        
        
