
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 13:48:21 2018

@author: Cody Fizette
"""

import pandas as pd
import numpy as np
from scipy import signal
import heartbeat_detection as hb
import dfa
import sqlite3

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
    avg_rr = np.mean(rr_ints)
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
    return SampEn(sig, 2, 0.1*std)
    

    
'''
Process signal and calculate all variables
'''    
def process_signal(sig, freq):
    
    print('Calculating entropy')
    sig2 = sig.hart.tolist()
    entropy = get_ent(sig2)#return
    print(entropy)

    print('Calculating dfa')
    dfa_val = get_dfa(sig)#return
    
    print('Calculating R-R intervals')
    rr_ints = get_rr(sig, freq)
    
    print('Calculating average heartrate')
    avg_hr = get_average_hr(rr_ints) #return
    
    print('Calculating STDNN')
    stdnn = get_stdnn(rr_ints) #return
    
    return (avg_hr, stdnn, dfa_val, entropy)

    

def process_db(file):
    conn = sqlite3.connect(file)
    c = conn.cursor()
    c2 = conn.cursor()
    c.execute('SELECT * FROM StressData')
    for row in c:
        data = row[2].split(',')
        data = [int(d) for d in data]
        df = pd.DataFrame(data,columns=['hart'])
        df_short = df.loc[:4000,:]
        indicators = process_signal(df_short,200)
        c2.execute('UPDATE StressData SET hr=?, stdnn=?, dfa=?, ent=? WHERE id=?',(indicators[0],indicators[1],indicators[2],indicators[3], row[0]))
        
    conn.commit()
        
        
##        print(process_signal(df_short,200))
##        print(df[:10])
    













