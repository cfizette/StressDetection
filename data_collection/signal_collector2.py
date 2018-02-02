'''
Signal Collector 2
Simpler attempt to disply data using matplotlib
'''


import pandas as pd
import numpy  as np

import serial
from timeit import default_timer as timer
from tkinter import *
import csv
import datetime

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

COM_PORT = 'COM3'   # COM port for communication with Arduino
SAMPLE_TIME = 5     # sample time in seconds
BAUD = 9600
MAX_DATA_LENGTH = 500

f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
a.set_yticks(np.arange(0, 1024, 200))

signal = []


# Save data to csv function
def save_data_csv(data):
    # Save data to csv file
        with open('data' + datetime.datetime.now().strftime("%B%d%I%M%S") +\
                  '.csv', 'w') as file:
            wr = csv.writer(file)
            wr.writerow(data)

#TODO: Implement saving to database

class Gui:
    def __init__(self, master):
        self.master = master
        master.title("Data Collection")

        # Label
        self.label = Label(master, text="Please ensure a clean signal before"+\
                           "beginning data collection")
        self.label.pack()

        # Buttons
        self.start_button = Button(master, text="Begin", command=self.collect_data)
        self.start_button.pack()
        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        # Graph
        canvas = FigureCanvasTkAgg(f, master)
        canvas.show()
        canvas.get_tk_widget().pack()

        # Data
        self.data = [0] * MAX_DATA_LENGTH

        # Begin serial communication
        self.connected= False
        try:
            self.ser = serial.Serial(port=COM_PORT, baudrate=BAUD)
            self.connected = True
        except serial.SerialException as e:
            print('Trouble opening serial port\n' + str(e))

        ani = animation.FuncAnimation(f, self.animate, interval=1)

        master.mainloop()

    # Collect Data function
    def collect_data(self):
        if self.connected:
            print("Collecting data from serial")
            saved_data = []
            start = timer()
            current = timer()

            self.data_count = 0

            # Collect data for specified number of time
            while current - start < SAMPLE_TIME:
                point = int(self.ser.readline().strip())
                saved_data.append(point)
                #point = self.data[-1]
                #saved_data.append(point)
                print(point)
                current = timer()

            print('Saving data')

            save_data_csv(saved_data)
            

            plt.plot(saved_data)
            plt.show()

    def animate(self,i):
        if self.connected:

            # Read all data from serial
            new_data = self.ser.read(100).strip().split('\r\n')

            if new_data:
                #Convert to integer
                new_data = [int(d) for d in new_data]

                #Append data to displayed data
                self.data += new_data

                if len(self.data) > MAX_DATA_LENGTH:
                    self.data = self.data[-MAX_DATA_LENGTH:]

                # Clear plot and plot new data
                a.clear()
                a.plot(self.data)




my_gui = Gui(Tk())

