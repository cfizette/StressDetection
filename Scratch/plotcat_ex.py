import serial
from plotcat import *

p = plotter()

#init serial device
ser = serial.Serial('COM3', 9600)

#the callback function for plotting
@p.plot_self
def update_plot():

  data = [ser.readline() for i in range(100)]
  p.lines[0][0].set_data(p.currentAxis[0], data)

p.set_call_back(update_plot)
plotter.show()
