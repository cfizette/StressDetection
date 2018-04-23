# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 13:48:21 2018

@author: Cody Fizette
"""

import pandas as pd
import numpy as np
from scipy import signal
#import heartbeat_detection as hb
import heartbeat as hb

import dfa
import sqlite3
from sampen import sampen2

# Calculation of sample entropy from Wikipedia
'''
Input:
    U: Signal data (list)
    m: 2
    r: 0.1*std
'''
def SampEn(U, m, r):

    def _maxdist(x_i, x_j):
        return max([abs(ua - va) for ua, va in zip(x_i, x_j)])

    def _phi(m):
        # Collection of all length m subsets of U
        x = [[U[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
        C = [(len([1 for x_j in x if _maxdist(x_i, x_j) <= r])) - 1 for x_i in x]
        return sum(C)

    N = len(U)

    return np.log(_phi(m)/_phi(m+1))

'''
Convert numpy array or list to formatted dataframe
'''
def to_dataframe(data):
    return pd.DataFrame(data,columns=['hart'])

'''
Load csv and format into dataframe
'''
def load_csv(file):
    return to_dataframe(np.genfromtxt(file))

'''
ew
'''
def csv_to_frame(file):
    frame = pd.read_csv(file,header=None).transpose().rename(columns={0:'hart'})
    return frame

'''
Calculate R-R intervals
Input: Dataframe of recorded values and frequency of recording
Output: Numpy array of individual R-R intervals in ms
'''
def get_rr(sig, freq):
    hb.process(sig,1,freq)
    return hb.measures['RR_list']

'''
Calculate average heartrate
Input: Dataframe of R-R intervals in ms
Output: average heartrate in bpm (int)
'''
def get_average_hr(rr_ints):
    print(rr_ints)
    if not rr_ints:
        return 6969
    avg_rr = np.mean(rr_ints)
    if avg_rr == 0:
        return 14
    return int(round(60000/avg_rr))
    
'''
Calcualte STDNN
Input: Dataframe of R-R intervals
Output: STDNN of signal (float)
'''
def get_stdnn(rr_ints):
    return round(np.std(rr_ints),2) # 2 decimal places
    
'''
Calculate DFA
Input: Dataframe of recorded values 
Output: DFA output (whatever it is called) (float)
'''
def get_dfa(sig):
    foo, bar, dfa_var = dfa.dfa(sig.values)
    return dfa_var
    
'''
Calculate sample entropy
Input: Dataframe of recorded values
Output: Sample entropy (float)
'''
def get_ent(sig):
    std = np.std(sig)
##    return SampEn(sig, 2, 0.1*std)
    return sampen2(sig, r=0.1*std)[2][1]
    

    
'''
Process signal and calculate all variables
'''
def process_signal(sig, freq):
    
    print('Calculating entropy')
    sig2 = sig.hart.tolist()
    #sig2 = [int(x) for x in sig2]
##    print('Length of sig 2 is:' + str(len(sig2)))
##    print(sig2[:100])
##    entropy = get_ent(sig2)#return
##    entropy=1

    print('Calculating dfa')
    dfa_val = get_dfa(sig)#return

    try:

        measures = hb.process(3*sig.hart.values-(3*min(sig.hart.values)), freq)
    
    ##    print('Calculating R-R intervals')
    ##    rr_ints = get_rr(list(sig), freq)
    ##    rr_ints=[]
        
        print('Calculating average heartrate')
    ##    avg_hr = get_average_hr(rr_ints) #return
    ##    avg_hr = 0
        avg_hr = measures['bpm']
        
        print('Calculating STDNN')
    ##    stdnn = get_stdnn(rr_ints) #return
    ##    stdnn = 0
        stdnn = measures['sdnn']
        
    except:
        print('Unable to calculate hr')
        avg_hr=0
        stdnn=0
    
    return (avg_hr, stdnn, dfa_val)

    

def process_db(file):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute('SELECT * FROM StressData')
    for row in c:
        data = row[2].split(',')
        data = [int(d) for d in data]
        df = pd.DataFrame(data,columns=['hart'])
##        df_short = df.loc[:3000,:]
##        df_short = df_short.reset_index(drop=True)
        indicators = process_signal(df,250)
        print('')
        print(indicators)
        print('')
        print('Writing to database')

# Update all variables 
##        c2.execute('UPDATE StressData SET hr=?, stdnn=?, dfa=?, ent=? WHERE id=?',(indicators[0],indicators[1],indicators[2],indicators[3], row[0]))
# Update all but entropy
        c2.execute('UPDATE StressData SET hr=?, stdnn=?, dfa=? WHERE id=?',(indicators[0],indicators[1],indicators[2], row[0]))

        conn.commit()

    conn.close()
    
        
        
  














