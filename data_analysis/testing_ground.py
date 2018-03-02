# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 13:34:42 2017

@author: Cody
"""

import pandas as pd
import numpy as np
from pyentrp import entropy as ent
from sampen import sampen2
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import matplotlib.ticker as tik
from scipy import signal
import heartbeat_detection as hb
from scipy import stats

# Import data from test file
data = pd.read_table('ECG_dat.txt', delim_whitespace = True)
data2 = pd.read_csv('heartbeat.csv')
data_short = data.iloc[:1000]
fs = 200 #Hz

# Plot the signal
data_short.plot(x='Time', y='hart')
data2.plot()

# Sample Entropy---------------------------------------------------------------

# Standard deviation of signal
std = np.std(data_short.hart)

# Pyentrp package calculation
entropy = ent.sample_entropy(data_short.ECG, 3)

# Calculation of sample entropy from Wikipedia
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

etropy2 = SampEn(data_short.ECG, 1, 0.1*np.std(data_short.ECG)) 
entropy3 = SampEn(data2.hart, 1, 0.1*np.std(data2.hart))

# Sampen package calculation
sampen_ent = sampen2(data_short.ECG, r=0.1*std)


def test_fxns():
    
#    start = timer()
#    pyentrp_ent = ent.sample_entropy(data_short.hart, 3)
#    end = timer()
#    elapsed = end-start
#    print('Pyentrp took %f seconds to execute \n' % elapsed)
    dat = data_short.hart.tolist()
    
    start = timer()
    wiki_ent = SampEn(dat, 2, 0.1*std)
    print(wiki_ent)
    end = timer()
    elapsed = end-start
    print('Wiki version took %f seconds to execute \n' % elapsed)
    
#    start = timer()
#    sampen_ent = sampen2(data_short.hart, r=0.1*std)
#    end = timer()
#    elapsed = end-start
#    print('Sampen took %f seconds to execute \n' % elapsed)
 ''' 
# It appears that the wikipedia version is the fastest, though its results
# differ very slightly from the other two methods (0.001) probably won't 
# matter though
# Run on i5-4200U <--------------------------- See if faster on other computer
  '''  
# Lets plot their performance as a function of time series length
def plot_performance():
    wiki_arr = []
    pyentrp_arr = []
    sampen_arr = []
    x = [10,100,200,500,1000,1500]
    for i in x:
        dat = data.hart.iloc[:i].tolist()
        print(i)
        
#        start = timer()
#        pyentrp_ent = ent.sample_entropy(dat, 3)
#        end = timer()
#        pyentrp_arr.append(end-start)
#        
        start = timer()
        wiki_ent = SampEn(dat, 2, 0.1*std)
        end = timer()
        wiki_arr.append(end-start)        

        start = timer()
        sampen_ent = sampen2(dat, r=0.1*std)
        end = timer()
        sampen_arr.append(end-start)
        
    plt.plot(x, pyentrp_arr, label = 'Pyentrp')
    plt.plot(x, wiki_arr, label = 'Wiki')
    plt.plot(x, sampen_arr, label='Sampen')
    plt.xlabel('Time-series length')
    plt.ylabel('Time to execute (s)')
    plt.title('Comparison of different methods for calculating Sample Entropy')
    plt.legend()
    
    
        
plot_performance()
    
# DFA------------------------------------------------------------------------

dfa_dat = dfa.dfa(data_short.ECG.values)
dfa_dat2 = dfa.dfa(data2.hart[:1000].values)
#DFA[2] represents the exponent

# White noise should be around 0.5
w_noise = np.random.normal(size=10000)
wnoise_dfa = dfa.dfa(w_noise)


# Frequency Power Analysis-----------------------------------------------------

#1 Cubic Spline Interpolation 
# Probably not needed since we'll be using a light sensor
#from scipy.interpolate import interp1d
#y = data_short.ECG
#x = data_short.Time
#f = interp1d(x, y, kind='cubic')
#x2 = np.linspace(0, max(x), 20)
#y2 = f(x2)
#plt.plot(x2,y2)
#plt.plot(x,y)

# Use Welch peridogram to calculate power spectral density
f, P_dens = signal.welch(data.ECG, fs)
plt.plot(f, P_dens)
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()

# Power Spectrum
f2, P_dens2 = signal.welch(data.ECG, 2, 'flattop', 1024, scaling='spectrum')
plt.plot(f2, np.sqrt(P_dens2))
plt.xlabel('frequency [Hz]')
plt.ylabel('Linear Spectrum [V RMS]')
plt.show()

# Test on oximeter signal
f3, P_dens3 = signal.welch(data2.hart, 100)
plt.plot(f3, P_dens3)
plt.xlabel('frequency [Hz]')
plt.ylabel('PSD [V**2/Hz]')
plt.show()
'''
This particular oximeter signal does not appear to capture the HF components.
We may not be able to use this variable in the final product.
Also worth looking into just using the LF component.
ALSO the frequencies do not appear to be in the proper range, they should be 
less than 1... idk why....
'''


# RQA -------------------------------------------------------------------------
    
print 'hello'










# Algorithm complexity analysis------------------------------------------------
data2 = pd.read_csv('heartbeat.csv')
data2_long = pd.concat([data2]*200, ignore_index = True)

# Heartbeat detection (should be linear???) nah it's constant?????ish????

lengths = np.linspace(10,300000,15).astype(int)
times = []

for l in lengths:
    print(l)
    sample = data2_long.iloc[:l,:]
    start = timer()
    hb.process(sample,1,100)
    rr_int = hb.measures['RR_list']
    stop = timer()
    times.append((stop-start)) #s
    
FONTSIZE = 30
fig = plt.figure(1)
ax = fig.add_subplot(1,1,1)
plt.style.use('fivethirtyeight')
ax.plot(lengths, times, label = 'y = 2.94e-5t - 0.11')
ax.tick_params(axis='both', which='major', labelsize = 20)
ax.get_xaxis().set_major_formatter(
    tik.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.xlabel('Array length', fontsize = FONTSIZE)
plt.ylabel('Time (s)',fontsize = FONTSIZE)
plt.title('Running time of R-R Interval calculation',fontsize = FONTSIZE + 10)
ax.legend()
slope, intercept, r, p, err = stats.linregress(lengths, times)


# STDNN calculation (linear???) nah looks constant????
lengths = np.linspace(1000,10000,25).astype(int)
times = []

for l in lengths:
    print(l)
    sample = data2_long.iloc[:l,:]
    hb.process(sample,1,100)
    rr_int = hb.measures['RR_list']
    start = timer()
    stdnn = np.std(rr_int)
    stop = timer()
    times.append((stop-start)*1000) #ms
    
FONTSIZE = 30
fig = plt.figure(1)
ax = fig.add_subplot(1,1,1)
plt.style.use('fivethirtyeight')
ax.scatter(lengths, times, s=80)
ax.tick_params(axis='both', which='major', labelsize = 20)
ax.get_xaxis().set_major_formatter(
    tik.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.xlabel('Array length', fontsize = FONTSIZE)
plt.ylabel('Time (ms)',fontsize = FONTSIZE)
plt.title('Running time of STDNN calculation',fontsize = FONTSIZE + 10)

slope, intercept, r, p, err = stats.linregress(lengths, times)
line = lengths*slope + intercept
ax.plot(lengths, line, color = 'red', label = 'y = 5.01e-7x + 0.112')
ax.legend(fontsize=30)



# DFA 
import dfa

lengths = np.linspace(1000,100000,15).astype(int)
times = []

for l in lengths:
    print(l)
    sample = data2_long.iloc[:l,:]
    start = timer()
    dfa_sample = dfa.dfa(sample.values)
    stop = timer()
    times.append((stop-start)) #s
    
FONTSIZE = 30
fig = plt.figure(1)
ax = fig.add_subplot(1,1,1)
plt.style.use('fivethirtyeight')
ax.plot(lengths, times, label='y = 4.11e-5x + 0.046')
ax.tick_params(axis='both', which='major', labelsize = 20)
ax.get_xaxis().set_major_formatter(
    tik.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.xlabel('Array length', fontsize = FONTSIZE)
plt.ylabel('Time (s)',fontsize = FONTSIZE)
plt.title('Running time of DFA calculation',fontsize = FONTSIZE + 10)
ax.legend(fontsize = 20)
slope, intercept, r, p, err = stats.linregress(lengths, times)



# Power spectrum---------------------------------------------------------------
lengths = np.linspace(1000,100000,15).astype(int)
times = []

for l in lengths:
    print(l)
    sample = data2_long.iloc[:l,:]
    start = timer()
    f3, P_dens3 = signal.welch(sample.hart, 100)
    stop = timer()
    times.append((stop-start)) #s
    
FONTSIZE = 30
fig = plt.figure(1)
ax = fig.add_subplot(1,1,1)
plt.style.use('fivethirtyeight')
ax.scatter(lengths, times, s=80)
ax.tick_params(axis='both', which='major', labelsize = 20)
ax.get_xaxis().set_major_formatter(
    tik.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.xlabel('Array length', fontsize = FONTSIZE)
plt.ylabel('Time (s)',fontsize = FONTSIZE)
plt.title('Running time of Power Spectrum calculation',fontsize = FONTSIZE + 10)
slope, intercept, r, p, err = stats.linregress(lengths, times)
line = lengths*slope + intercept
ax.plot(lengths, line, color = 'red', label = 'y = 8.75e-8x + 0.001')
ax.legend(fontsize = 20)











