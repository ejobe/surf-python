#!/usr/bin/env python

import sys
import timing
import json
import surf_data
import time
import numpy 

from utils.surf_constants import *

number_of_iterations = 25
events_per_iteration = 8000
save_rawdatafiles = False
basefilename = '235MHz_tune_run_0919TEST'

##handle input arguments [frequency] [channels to tune]
if len(sys.argv) is not 3:
    print 'python executable:', sys.argv[0]
    print 'needs 2 arguments: input frequency [MHz] and LABs to tune [syntax: 0 for single channel, or 0:5 to run LABs 0 thru 5]'

    sys.exit()

freq = float(sys.argv[1]) * 1.e6
print 'using sine wave frequency', freq*1e-6, 'MHz'

_lab=sys.argv[2]
lab=[]
for i, el in enumerate(_lab):
    if el == ':':
        lab=range(int(_lab[0:i]), int(_lab[i+1:])+1, 1)

if len(lab) < 1:
    lab = [int(_lab), int(_lab)+1]

dev=surf_data.SurfData()

trims={}          #dict for trim dac values
dt_crossings = {} #dict measured dt values
dt_period = {}    #dict for measured sine wave periods using interpolated zero crossings
dt_period_std={}  #dist for the std dev of measured sine wave periods

#initialize
print 'setting initial guesses / enabling DLL:'
for l in lab:
    print 'LAB4D', l
    init_trims = timing.setTrimDacs(dev, l)

    trims[str(l)]         = []
    dt_crossings[str(l)]  = []
    dt_period[str(l)]     = []
    dt_period_std[str(l)] = []

    trims[str(l)].append(list(init_trims))
print '---------------------------------'

##run scan
i=0
t0=time.time()

while(i < (number_of_iterations + 1)):

    if i > 0:
        for l in lab:
            trims[str(l)].append(list(timing.tune(dev, l, dt_crossings[str(l)][i-1], trims[str(l)][i-1])))
        
    savedatfile = basefilename + '_SineData_iter%d.dat' % i
    
    crossings, periods = timing.singleRun(dev, lab, num_events=events_per_iteration, save=save_rawdatafiles, filename=savedatfile)
    
    print '---------------------------------'

    for l in lab:

        mean_crossings = numpy.mean(crossings[l], dtype=numpy.float64) 
        avg_sample_dt = mean_crossings * 1.e12 / freq 
        dt_crossings[str(l)].append( list(crossings[l] * 1.e12 / freq))

        _period_mean=numpy.zeros(lab4d_primary_sample_cells, dtype=float)
        _period_std=numpy.zeros(lab4d_primary_sample_cells, dtype=float)
        
        for j in range(lab4d_primary_sample_cells):
            _period_mean[j] = numpy.mean(periods[l][j])
            _period_std[j] = numpy.std(periods[l][j])
                
        dt_period[str(l)].append(list(_period_mean))
        dt_period_std[str(l)].append(list(_period_std))

        _rms=numpy.std(dt_crossings[str(l)][i])
        print 'LAB', l, '-- on iteration..', i, '-- dT RMS [ps]:' , _rms, \
            '-- avg dT [ps]', avg_sample_dt, '-- DLL wrap dT [ps]', dt_crossings[str(l)][i][0] 


    print ' *** time since start [min]',  (time.time() - t0)/60.
    print '---------------------------------'
    
    i=i+1

##save to json files
print 'saving data to .json files...'
with open('dt_crossings'+basefilename+'.json', 'w') as outfile:
    json.dump(dt_crossings, outfile)
with open('mean_periods'+basefilename+'.json', 'w') as outfile:
    json.dump(dt_period, outfile)
with open('std_periods'+basefilename+'.json', 'w') as outfile:
    json.dump(dt_period_std, outfile)
with open('trimdacs_'+basefilename+'.json', 'w') as outfile:
    json.dump(trims, outfile)
