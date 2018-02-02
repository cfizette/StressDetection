import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import serial
from timeit import default_timer as timer
from tkinter import *
import csv
import datetime
import matplotlib
import matplotlib.animation as animation

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

COM_PORT = 'COM9'   # COM port for communication with Arduino
SAMPLE_TIME = 5     # sample time in seconds
BAUD = 9600
MAX_DATA_LENGTH = 100

f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
a.set_yticks(np.arange(0, 1024, 200))

signal = []

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
            print('Troule opening serial port\n' + str(e))

        #ani = animation.FuncAnimation(f, self.animate, interval=1)

        master.mainloop()

    # Collect Data function
    def collect_data(self):
        if self.connected:
            print("Collecting data from serial")
            saved_data = []
            start = timer()
            current = timer()

            # Collect data for specified number of time
            while current - start < SAMPLE_TIME:
                point = self.ser.readline().strip()
                saved_data.append(point)
                #point = self.data[-1]
                #saved_data.append(point)
                print(point)
                current = timer()

            print('Saving data')

            # Save data to csv file
            with open('data' + datetime.datetime.now().strftime("%B%d%I%M%S") +\
                      '.csv', 'w') as file:
                wr = csv.writer(file)
                wr.writerow(saved_data)

            plt.plot(saved_data)
            plt.show()

    def animate(self,i):
        if self.connected:
            point = self.ser.read()
            self.data.append(point)
            self.data_count += 1
            print(point)

            if len(self.data) > MAX_DATA_LENGTH:
                self.data.pop(0)
            if self.data_count > 100:
                a.clear()
                a.plot(self.data)
                a.set_yticks(np.arange(0, 1024, 200))
                self.data_count = 0

my_gui = Gui(Tk())

