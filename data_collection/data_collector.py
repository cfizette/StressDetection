'''
Cody Fizette
2/2/2018
Signal Collector 3
Display data as collection is taking place
All work is done in the animate function
'''

import pandas as pd
import numpy  as np
import serial
import sqlite3 as sql
import os.path
from timeit import default_timer as timer
from tkinter import *
import csv
import datetime
import matplotlib
matplotlib.use("TkAgg") # idk what this does
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle

COM_PORT = 'COM3'   # COM port for communication with Arduino
SAMPLE_TIME = 5     # sample time in seconds
BAUD = 9600
MAX_DATA_LENGTH = 500
C_LOC_SCALE = 0.1
DATABASE_NAME = 'testing_data.db'
TABLE_NAME = 'StressData'
COLUMN_NAMES = '(id VARCHAR, state VARCHAR, data VARCHAR, datetime VARCHAR)'

f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
a.set_yticks(np.arange(0, 1024, 200))

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


        # Used to label data when saving to database
        self.dat_type = StringVar(value='Base')

        # Label
        self.label = Label(master, text="Please ensure a clean signal before "+\
                           "beginning data collection", pady=5)
        self.label.pack()

        # Entry Box
        self.entry_frame = Frame(master)
        self.entry_label = Label(self.entry_frame, text='Subject Label')
        self.subject_entry = Entry(self.entry_frame, bd=5)
        self.entry_label.pack(side=LEFT)
        self.subject_entry.pack(side = RIGHT)
        self.entry_frame.pack()

        # Radio Buttons
        self.dat_type_frame = Frame(master)
        Radiobutton(self.dat_type_frame, text='Relaxed', padx=10, pady=5, variable=self.dat_type, value='Relx').pack(side=LEFT)
        Radiobutton(self.dat_type_frame, text='Baseline', padx=10, pady=5, variable=self.dat_type, value='Base').pack(side=LEFT)
        Radiobutton(self.dat_type_frame, text='Stressed', padx=10, pady=5, variable=self.dat_type, value='Stress').pack(side=LEFT)
        self.dat_type_frame.pack()

        # Buttons
        self.button_frame = Frame(master)
        self.on_button = Button(self.button_frame, text='OFF', command = self.toggle)
        self.on_button.grid(row=0,column=0, padx=10, pady=3)
        self.start_button = Button(self.button_frame, text="Record", command=self.collect_data)
        self.start_button.grid(row=0,column=1,padx=10, pady=3)
        self.close_button = Button(self.button_frame, text="Close", command=master.quit)
        self.close_button.grid(row=0,column=2,padx=10, pady=3)
        self.button_frame.pack()

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

        # Initialize things
        self.ani = animation.FuncAnimation(f, self.animate, interval=1)
        self.collect = False
        self.on = False

        # Initialize Database
        self.table = self.connect_database(DATABASE_NAME)
        self.cursor = self.table.cursor()
            
            

        master.mainloop()

    # Connect to database function
    def connect_database(self, loc):
        if not os.path.isfile(loc):
            self.make_database(loc)
        try:
            conn = sql.connect(loc)
            return conn
        except Exception as e:
            print('Trouble connecting to database')
            print(e)

    # Create database function
    def make_database(self, loc):
        try:
            conn = sql.connect(loc)
            conn.execute("CREATE TABLE {} {}".format(TABLE_NAME, COLUMN_NAMES))
        except Exception as e:
            print('Trouble creating database')
            print(e)
        return None

    # Saves data to database
    def save_to_database(self, idee, state, data):
        str_data = [str(d) for d in data]
        data = ','.join(str_data)
        d_time = datetime.datetime.now().strftime("%B%d%I%M%S")
        self.cursor.execute('INSERT INTO {tn} '.format(tn=TABLE_NAME) + '(id, state, data, datetime) VALUES (?, ?, ?, ?)', (idee, state, data, d_time))
        self.table.commit()
        

    # Toggle function
    # Turns serial recording on and off to increase responsiveness when inputting data
    def toggle(self, tog=[0]):
        tog[0] = not tog[0]
        if tog[0]:
            self.on_button.config(text='ON')
            self.on = True
            # clear serial buffer before new data received
            self.ser.flushInput()
        else:
            self.on_button.config(text='OFF')
            self.on = False
    

    # Collect Data function
    def collect_data(self):
        if self.connected:
            print("Collecting data from serial")
            self.collect = True
            self.switched = True
                

    def animate(self,i):
        if self.connected and self.on:

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

                # Save data to list if button is pressed
                if self.collect:
                    # Initialize variables once
                    if self.switched:
                        print('Collecting Data...')
                        self.switched = False
                        self.start_time = timer()
                        self.current_time = timer()
                        self.saved_data = []
                        
                    # Collect for certain amount of time
                    if self.current_time - self.start_time < SAMPLE_TIME:
                        self.saved_data += new_data
                        self.current_time = timer()

                        # Add recording circle
                        min_x, max_x = a.get_xlim()
                        min_y, max_y = a.get_ylim()
                        x_cord = max_x - C_LOC_SCALE*(max_x - min_x)
                        y_cord = max_y - C_LOC_SCALE*(max_y - min_y)
##                        print((x_cord,y_cord))
                        a.plot(x_cord, y_cord, 'r.', markersize = 20)
                        
                    # Save data when done
                    else:
                        self.collect = False
                        print('Saving Data')
                        save_data_csv(self.saved_data)
                        # Get values from GUI
                        idee = self.subject_entry.get()
                        state = self.dat_type.get()
                        
                        self.save_to_database(idee, state, self.saved_data)
                        
#def run():
#    my_gui = Gui(Tk())

my_gui = Gui(Tk())

