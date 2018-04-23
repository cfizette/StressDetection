"""
Cody Fizette
2/2/2018
Signal Collection
Simple program to allow user to take PPG samples, calculate average HR and DFA, and then save to excel file for 
further analysis.
All work is done in the animate function
"""
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename
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
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from signal_processing import process_signal
from excel_writer import XlWriter

# Constants
COM_PORT = 'COM9'                           # COM port for communication with Arduino
SAMP_FREQ = 250
#TODO: MAKE SURE THIS IS SET CORRECTLY!!!!
SAMPLE_TIME = 5                             # Sample time in seconds
NUM_SAMPS = SAMPLE_TIME * SAMP_FREQ         # Pre-calculate number of samples needed
BAUD = 19200
MAX_DATA_LENGTH = 1000                      # Length of data displayed on graph
C_LOC_SCALE = 0.1                           # Scale for recording indicator positioning
                                            # Icon will appear 10% in from top right corner
WINDOW_TITLE = "Data Collection"            # Base window title
VALID_FILE_EXTENSIONS = ('.xlsx', '.xlsm')  # Valid Excel file extensions
DATA_LABEL_WIDTH = 5                        # Width for labels containing calculated values
PADX = 10                                   # Cell padding
PADY=6                                      # Cell padding
ICON_LOC = 'assets/bingicon.ico'            # Cool little window icon for style points

# Should probably be in GUI class.... Figure to display signal
f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
a.set_yticks(np.arange(0, 1024, 200))


class Gui:
    def __init__(self, master):
        self.master = master

        # Set title
        # Title displays program name as well as what file is currently open
        master.title(WINDOW_TITLE + ' (NO FILE CHOSEN)')

        # Try to load icon
        try:
            master.iconbitmap(ICON_LOC)
        except Exception as e:
            print('Icon could not be found')

        # Initialize variables
        self.filename = ''                  # Current open file
        self.saved_data = []                # Recorded data from Arduino
        self.collect = False                # Used to turn collection on and off
        self.on = False                     # Used to turn signal display on and off
        self.data = [0] * MAX_DATA_LENGTH   # Holds buffer of incoming data from Arduino
        self.connected = False              # Is the computer successfully connected to Arduino?
        self.hr_str_var = StringVar()       # Used to display HR from recorded signal
        self.dfa_str_var = StringVar()      # Used to display DFA from recorded signal

        # Create menu------------------------------------------------------------------------
        '''Holds less commonly used actions.
        File
            -Open
                Opens a Excel file for editing
            -Connect
                Attempts connection to Arduino
        '''
        menu = Menu(self.master)
        self.master.config(menu=menu)
        file = Menu(menu)
        file.add_command(label='Open', command=self.choose_file)
        file.add_command(label='Connect', command=self.connect)
        menu.add_cascade(label='File', menu=file)
        #------------------------------------------------------------------------------------

        # Main UI----------------------------------------------------------------------------
        
        # Label
        '''Displays a message to user about ensuring a clean signal.'''

        self.label = Label(master, text="Please ensure a clean signal before pressing record", pady=5)
        self.label.pack()

        # Entry Box
        '''Used to set patient number.
        entry_frame (Frame)
            entry_label (Label)
                Label for entry box
            subject_entry (Entry)
                Holds patient number for use when saving data
        '''
        self.entry_frame = Frame(master)
        self.entry_label = Label(self.entry_frame, text='Patient Number:')
        self.subject_entry = Entry(self.entry_frame, bd=5)
        self.entry_label.pack(side=LEFT)
        self.subject_entry.pack(side=RIGHT)
        self.entry_frame.pack()

        # Buttons
        '''
        button_frame (Frame)
            on_button (Button)
                Toggles signal plot.
            start_button (Button)
                Starts recording.
            stop_button (Button)
                Stops recording (in case signal gets messed up).
            save_button (Button)
                Saves data to Excel file.
        '''
        self.button_frame = Frame(master)
        self.on_button = Button(self.button_frame, text='OFF', command=self.toggle)
        self.on_button.grid(row=0, column=0, padx=PADX, pady=PADY)
        self.start_button = Button(self.button_frame, text="Record", command=self.collect_data)
        self.start_button.grid(row=0, column=1, padx=PADX, pady=PADY)
        self.stop_button = Button(self.button_frame, text="Stop", command=self.stop_collection)
        self.stop_button.grid(row=0, column=2, padx=PADX, pady=PADY)
        self.save_button = Button(self.button_frame, text="Save", command=self.save_data)
        self.save_button.grid(row=0, column=3, padx=PADX, pady=PADY)
        self.button_frame.pack()

        # HR and DFA display
        '''Displays HR and DFA from recorded signal.
        var_frame (Frame)
            hr_label (Label)
                Label for HR data.
            hr_dat_label (Label)
                Displays current HR value for recoded signal.
            dfa_label (Label)
                Label for DFA data.
            dfa_dat_label (Label)
                Displays current DFA value for recorded signal.
        '''
        self.var_frame = Frame(master)
        self.hr_label = Label(self.var_frame, text='HR:')
        self.hr_dat_label = Label(self.var_frame, textvariable=self.hr_str_var, bg='white', borderwidth=1,
                                  relief='solid', width=DATA_LABEL_WIDTH)
        self.space_label = Label(self.var_frame, text='')
        self.dfa_label = Label(self.var_frame, text='DFA:')
        self.dfa_dat_label = Label(self.var_frame, textvariable=self.dfa_str_var, bg='white', borderwidth=1,
                                   relief='solid', width=DATA_LABEL_WIDTH)
        self.hr_label.grid(row=0, column=0, pady=PADY)
        self.hr_dat_label.grid(row=0, column=1, pady=PADY)
        self.space_label.grid(row=0, column=2, padx=PADX, pady=PADY)
        self.dfa_label.grid(row=0, column=3, pady=PADY)
        self.dfa_dat_label.grid(row=0, column=4, pady=PADY)
        self.var_frame.pack()

        #--------------------------------------------------------------------------------------


        # Other Things-------------------------------------------------------------------------
        
        # Graph
        canvas = FigureCanvasTkAgg(f, master)
        canvas.show()
        canvas.get_tk_widget().pack()
#TODO: See if changing interval makes it more responsive.
        self.ani = animation.FuncAnimation(f, self.animate, interval=1)

        # Begin serial communication
        self.connect()

        master.mainloop()


    # Predicates
    def is_valid(self, path):
        """Check if an Excel file was chosen

        Args:
            path (string): Path to file
            
        Returns:
            True if path ends with valid extension False otherwise
        """
        
        return path.lower().endswith(VALID_FILE_EXTENSIONS)


    def is_valid_patient_str(self, patient):
        """Check if an patient number is valid

        Args:
            patient (string): Patient number
            
        Returns:
            True if patient is a positive integer False otherwise
        """
        return patient.isdigit() and (int(patient) > 0)


    # Setters
    def set_filename(self, filename):
        """Sets filename

        Args:
            filename (string): Path to file.
        """
        
        self.filename = filename
        

    def set_title(self):
        """Display filename and connection status in window title.
        title format: WINDOW_TITLE + open file name + connection status
        """

        title = WINDOW_TITLE

        if self.filename:
            filename = self.filename.split("/")[-1]  # Get just the filename not the whole path
            title += (' (' + filename + ')')

        if self.connected:
            title += ' (Connected)'

        self.master.title(title)



    def set_excel_writer(self, filename):
        """Change XlWriter 

        Args:
            filename (string): Path to file.
        """
        self.writer = XlWriter(filename)

    def update_var_display(self):
        """Update the HR and DFA values displayed"""
        
        if self.saved_data:
            hr, dfa = self.process_data()
            self.hr_str_var.set(str(round(hr,1)))
            self.dfa_str_var.set(str(round(dfa,2)))


    # Menu Functions
    def choose_file(self):
        """Choose file to be saved to."""

        filename = askopenfilename()  # Opens nifty dialog to choose file
        #print(filename)

        # Error if filename is invalid, pass if no file chosen
        while (not self.is_valid(filename)) and filename:
            messagebox.showerror('Error', filename + ' is not a valid Excel file')
            filename = askopenfilename()
            print(filename)

        if filename:
            self.set_filename(filename)     # Set filename for later reference
            self.set_title()                # Update title
            self.set_excel_writer(filename) # Create XlWriter
            #print(self.writer)


    def connect(self):
        """Attempt to make serial connection to device."""
        
        try:
            self.ser = serial.Serial(port=COM_PORT, baudrate=BAUD)
            self.connected = True
            self.set_title()
        except serial.SerialException as e:
            print('Trouble opening serial port\n' + str(e))
            messagebox.showerror('Connection error', 'Unable to connect to device.\n' + \
                                 'Please ensure device is connected to proper USB port and' + \
                                 ' reconnect.')


    # Button Functions
    def toggle(self, tog=[0]):
        """Toggle signal reading on and off"""

        # Got this from StackOverflow, I guess tog is a 1 element list containing a flag.
        # Not sure why it has to be a list........
        if self.connected:
            tog[0] = not tog[0]
            if tog[0]:
                self.on_button.config(text='ON')
                self.on = True
                # clear serial buffer before new data received
                self.ser.flushInput()
            else:
                self.on_button.config(text='OFF')
                self.on = False

            
    def stop_collection(self):
        """Stop collecting data and clear saved data"""
        
        self.collect = False  # Toggle self.collect to false, should stop collection in animate function
        self.saved_data = []  # Clear saved data


    def collect_data(self):
        """Begin collecting data"""
        
        if self.connected:
            print("Collecting data from serial")
            self.collect = True
            self.switched = True  # Used to initialize some variables in collection


    # Data processing and saving functions
    def process_data(self):
        """Process data and calculate HR and DFA"""
        
        if self.saved_data:
            hr, dfa = process_signal(self.saved_data, SAMP_FREQ)
            return (hr, dfa)


    def save_data(self):
        """Save data to Excel sheet"""
        
        if self.filename:                               # Check if file open
            if self.saved_data:                         # Check if any data saved
                patient = self.subject_entry.get()      # Get patient name/number
                if self.is_valid_patient_str(patient):  # Check if subject/patient number entered and is valid
                    patient = int(patient)              # Convert to int
                    hr, dfa = self.process_data()       # Process data
                    self.writer.save_patient_data(patient, hr, dfa)
                else:
                    messagebox.showerror('Patient error','Invalid patient number.\nUse whole number larger than 0.')
            else:
                messagebox.showerror('Signal error','No signal collected.\nPlease collect a signal.')
        else:
            messagebox.showerror('Save error','Please choose a file to save to')
        
    
    def animate(self,i):
        """
        :param i: StackOverflow told me this is needed
        :return: None
        """
        '''This is always running. Handles two main things.
            1) Plotting incoming signal
            2) Saving sample of data when start button pressed
        This works by constantly reading incoming data from the serial port.
        A MAX_DATA_LENGTH long list (self.data) is populated and updated with new incoming data.
        This list is plotted.
        When start button is pressed, incoming data is also saved to another list (self.saved_data)
        
        '''
        if self.connected and self.on:

            # Read and decode data from serial
            new_data = self.ser.read(250)
            new_data = new_data.strip()
##            print(new_data)
            new_data = new_data.decode('utf-8')
            new_data = new_data.split('\r\n')
            
            if new_data:
                # Try converting to integer
                try:
                    new_data = [int(d) for d in new_data]
                # Sometimes weird shit happens and a wild ValueError appears (usually during the beginning)
                # Just ignore this data and collect more.
                except ValueError as e:
                    new_data=[0]

                # Append new data to displayed data
                self.data += new_data
                
                # Remove excess old data
                if len(self.data) > MAX_DATA_LENGTH:
                    self.data = self.data[-MAX_DATA_LENGTH:]

                # Clear plot and plot new data
                a.clear()
                a.plot(self.data)

                '''Begin collecting data if start button pressed
                When start is pressed, self.collect is toggled to True'''
                if self.collect:
                    # Clear old saved data
                    if self.switched:
                        print('Collecting Data...')
                        self.switched = False           # Reset switched so this block only executed once
                        self.saved_data = []            # Clear old data
                        
                    '''A predetermined number of samples are collected. This number is calculated using sample rate
                    and desired sample time. Data is collected until it is long enough.
                    Once enough data is collected, it is saved.'''
                    if len(self.saved_data) < NUM_SAMPS:
                        self.saved_data += new_data                             # Append new data
                        print('Saved data length: ' + str(len(self.saved_data)))

                        # Add recording circle,
                        min_x, max_x = a.get_xlim()                    # Get plot dimensions
                        min_y, max_y = a.get_ylim()
                        x_cord = max_x - C_LOC_SCALE*(max_x - min_x)   # Use C_LOC_SCALE to place circle
                        y_cord = max_y - C_LOC_SCALE*(max_y - min_y)
                        a.plot(x_cord, y_cord, 'r.', markersize = 20)  # Plot circle
                        
                    # End collection and update var_display
                    else:
                        self.collect = False
                        # Update and display data
                        self.update_var_display()
                        print('Done')


my_gui = Gui(Tk())

