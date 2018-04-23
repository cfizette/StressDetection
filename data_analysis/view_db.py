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

DATABASE_NAME = 'testing_data.db'
TABLE_NAME = 'StressData'
COLUMN_NAMES = '(id VARCHAR, state VARCHAR, data VARCHAR, datetime VARCHAR)'

# Should probably be in GUI class....
f = Figure(figsize=(10,10), dpi=100)
a = f.add_subplot(111)
a.set_yticks(np.arange(0, 1024, 200))

class Gui:
    def __init__(self, master):
        self.master = master

        # Set title and icon
        master.title("View Data")
        try:
            master.iconbitmap('bingicon.ico')
        except Exception as e:
            print('Icon could not be found')

        self.dat_name = StringVar()

        self.label = Label(master, textvariable=self.dat_name, pady=5)
        self.label.pack()

        # Buttons
        self.button_frame = Frame(master)
        self.up_button = Button(self.button_frame, text='UP', command = self.up_db)
        self.up_button.grid(row=0 ,column=0, padx=10, pady=3)
        self.down_button = Button(self.button_frame, text="Down", command=self.down_db)
        self.down_button.grid(row=0 ,column=2 ,padx=10, pady=3)
        self.button_frame.pack()

        # Graph
        canvas = FigureCanvasTkAgg(f, master)
        canvas.show()
        canvas.get_tk_widget().pack()

        # Initialize Database
        self.table = self.connect_database(DATABASE_NAME)
        self.cursor = self.table.cursor()

        self.cursor.execute('SELECT data from {}'.format(TABLE_NAME))
        self.data = self.cursor.fetchall()
        self.cursor.execute("SELECT id from {}".format(TABLE_NAME))
        self.dat_names = self.cursor.fetchall()
 ##       print(type(self.data))
 ##       print(type(self.data[0]))
 ##       print(len(self.data[0]))
 ##       print([int(x) for x in self.data[0][0].split(',')])


        self.dat_names = [row for row in self.dat_names]
        self.data = [[int(e) for e in row[0].split(',')] for row in self.data]

        self.index=0

##        a.plot(self.data[self.index])


        self.ani = animation.FuncAnimation(f, self.animate, interval=1)

        master.mainloop()

    # Connect to database function
    def connect_database(self, loc):
        try:
            conn = sql.connect(loc)
            return conn
        except Exception as e:
            print('Trouble connecting to database')
            print(e)


    # Toggle function
    # Turns serial recording on and off to increase responsiveness when inputting data
    def up_db(self):
        if self.index > 0:
            self.index -= 1
            self.dat_name.set(self.dat_names[self.index])

    # Collect Data function
    def down_db(self):
        if self.index < len(self.data):
            print(self.index)
            self.index += 1
            self.dat_name.set(self.dat_names[self.index])


    def animate(self,i):
        a.clear()
        a.plot(self.data[self.index])

# def run():
#    my_gui = Gui(Tk())

my_gui = Gui(Tk())