'''
Some code to tune the LAB4D ASIC timebase
For use with the SURFv5's

Eric Oberla
ejo@uchicago.edu
'''

import numpy as np
import time
import sys

import fit
import zero_crossings 
import trim_minimization_curve as trim_min

from utils.surf_constants import *

#sort-of arbitrary limit for trim-dac (anecdotal evidence suggests VCDL fails slightly above this trim-dac value)
max_trim   = 2540

#####################################################
## set trim dac values in a number of ways (scaler, default initial values, or send an list of 128 elements)
##
def setTrimDacs(dev, lab, fbtrim=None, sstoutfb=lab4d_default['sstoutfb'], dt_trims=None, write=True):

    dev.dev.labc.dll(lab, mode=True, sstoutfb=sstoutfb)
    time.sleep(2)

    if fbtrim != None:
        dev.dev.labc.l4reg(lab, 11, int(fbtrim))   
        print 'manually setting fbtrim to', fbtrim

    trims=np.ones(lab4d_primary_sample_cells, dtype=np.int)
    
    if dt_trims == None:
        '''if non initial values specified, go with some initial even/odd guesses'''
        for i in range(lab4d_primary_sample_cells):
            if i%2==0:
                trims[i] = 1750 #2310 
            else:
                trims[i] = 1350
        trims[127]= 300 #last sample always seems to be a little slow, perhaps due to less loading
        trims[0]  = 1950   #don't touch trim dac0, set fast as possible [7/2016] or maybe not [9/2016]

    else:
        if isinstance(dt_trims, list):
            if len(dt_trims) != lab4d_primary_sample_cells:
                print 'trim list needs to include 128 elements, dt trims DACs not updated'
                return 

            for i in range(len(dt_trims)):
                trims[i] = dt_trims[i]
        else:
            ##option for handling a scalar to set all trims identically
            trims = trims + int(dt_trims) - 1
        
    if write:
        writeTrimDacs(dev, lab, trims)

    return trims

#####################################################
## write trim DAC values to the LAB4D registers
##
def writeTrimDacs(dev, lab, trims):
    
    for i in range(lab4d_primary_sample_cells):
        time.sleep(0.01)
        dev.dev.labc.l4reg(lab, i+256, int(trims[i]) & 0xFFF)

    time.sleep(2.0)

#####################################################
## run a single iteration, calculate zero crossings and periods
##
def singleRun(dev, lab, num_events=1000, save=False, filename='temp.dat'):

    data=np.array(dev.log(num_events, save=save, filename=filename, unwrap=True))
    c, p = zero_crossings.zeroCrossings(data, lab)

    return c, p

#####################################################
## individual sample dt tuning 
##
def tune(dev, lab, dt_crossings, trims, verbose=False):
    
    dev.dev.labc.run_mode(0)
        
    ## new trim dac values to be assigned
    updated_trims=np.zeros(lab4d_primary_sample_cells, dtype=np.int)
    ## keep trim-dac 0 the same value
    updated_trims[0] = trims[0]

    for i in range(0, lab4d_primary_sample_cells):

        ##use LUT made in trim_minimization_curve.py
        dt_diff_lut_index = np.where(trim_min.minimizer_dt_diff_lut > (dt_crossings[i]-lab4d_nominal_dt_ps))[0][-1]
        trim_adjustment = trim_min.minimizer_trim_adj_lut[dt_diff_lut_index]

        updated_trims[i] = trims[i] + trim_adjustment
     
        if verbose:
            print 'sample:', i, '| dt value [ps]:', dt_crossings[i], ' | new trim val:', updated_trims[i], '| prev trim val:', trims[i]

        ## latch min/max if overrange
        if updated_trims[i] > max_trim:
            if verbose:
                print i, 'is maxed out', dt_crossings[i]
            updated_trims[i] = max_trim-20

        elif updated_trims[i] < 0:
            updated_trims[i] = 20 

    writeTrimDacs(dev, lab, updated_trims)

    return updated_trims

#####################################################
def scanFeedbackPeriodogram(dev, lab, sine_freq, scan_range):
    
    fbscan={}
    fbscan[lab]={}
    fbscan[lab]['freq'] = []
    fbscan[lab]['trim'] = []
    fbscan[lab]['trim'] = scan_range
    
    max_iterations = len(fbscan[lab]['trim'])

    current_iter = 0
    
    while current_iter < max_iterations:
        
        dev.dev.labc.run_mode(0)
        dev.dev.labc.l4reg(lab, 11, int(fbscan[lab]['trim'][current_iter]))   
        time.sleep(2.0)  
        
        data=np.array(dev.log(100, save=False))
        _, period_crossings = zero_crossings.zeroCrossings(data, lab)

        _period_mean=np.zeros(lab4d_primary_sample_cells, dtype=float)
        for j in range(lab4d_primary_sample_cells):
            _period_mean[j] = np.mean(period_crossings[lab][j])
    
        period_mean=np.mean(_period_mean)*1.e-9 

        fbscan[lab]['freq'].append(1./period_mean)
        #print 'difference: input freq - fitted freq = (kHz)', (sine_freq - 1./period_mean)*1.e-3, \
        #    'trim', int(fbscan[lab]['trim'][current_iter])
        
        print 1./period_mean, int(fbscan[lab]['trim'][current_iter])
        
        current_iter = current_iter + 1

    return fbscan

#####################################################
def scanFeedbackFit(dev, lab, current_dac_value, sine_freq, sine_amp=100.):
            
    freq_fit_init = 2*np.pi*sine_freq
    
    fbscan={}
    fbscan[lab]={}
    fbscan[lab]['freq']   = []
    fbscan[lab]['trim'] = []

    #probably specify a large scan_range on the intial pass, since intial guesses change DLL by a lot
    #for subsequent tunes, just scan in region around current dac value
    #----
    if scan_range == None:
        fbscan[lab]['trim'] = range(current_dac_value-50, current_dac_value+51, 5)
    else:
        fbscan[lab]['trim'] = scan_range

    max_iterations = len(fbscan[lab]['trim'])
    current_iter = 0
    
    while current_iter < max_iterations:
        
        dev.dev.labc.run_mode(0)
        dev.dev.labc.l4reg(lab, 11, int(fbscan[lab]['trim'][current_iter]))   
        time.sleep(2.0)  
        
        data=dev.log(10, save=False)

        fit_freq = []
        for i in range(1,10):
            for j in range(0, 1024, 128):
                fit_params = fit.fit_sin(data[i][lab][j:j+lab4d_primary_sample_cells], sine_amp, freq_fit_init, np.pi/2, 
                                         dt=lab4d_nominal_dt, use_timebase=True)
                '''try a different initial phase if poorly fitted'''
                ph=0
                while((abs(fit_params[0]) < (sine_amp/2.)) and (ph < 5)):
                    fit_params = fit.fit_sin(data[i][lab][j:j+lab4d_primary_sample_cells], sine_amp, freq_fit_init, (np.pi/(ph+1)), 
                                             dt=lab4d_nominal_dt, use_timebase=True)
                    ph = ph + 1
                        
                if abs(fit_params[0]) < (sine_amp/2.):
                    print 'probably a fit error', lab, i , j, fit_params
                else:
                    fit_freq.append(fit_params[1]/(2. * np.pi))

        if len(fit_freq) < 2:
            print 'something went wrong here..'
        
        else:
            fbscan[lab]['freq'].append(np.mean(np.array(fit_freq)))
            print 'difference: input freq - fitted freq = (kHz)', (sine_freq - np.mean(np.array(fit_freq)))*1.e-3, \
                'trim', int(fbscan[lab]['trim'][current_iter])
            current_iter = current_iter + 1

    return fbscan

#####################################################
def tuneFeedback(dev, lab, fbscan, freq, forder=4, plot=False):
    
    #check to see if actual frequency is contained in the scan
    if (fbscan[lab]['freq'][0] < freq) and (fbscan[lab]['freq'][len(fbscan[lab]['freq'])-1] < freq):
        print 'missed nominal freq in scan: it is ABOVE the scan range'
    elif (fbscan[lab]['freq'][0] > freq) and (fbscan[lab]['freq'][len(fbscan[lab]['freq'])-1] > freq):
        print 'missed nominal freq in scan: it is BELOW the scan range'

    p = np.poly1d(np.polyfit(fbscan[lab]['freq'], np.array(fbscan[lab]['trim']), deg=forder))
    p_deriv = np.polyder(p, m=1)
    print 'lab:', lab, ', VtrimFB dac for 3.2 GSPS from fit:', p(freq), ' derivative, counts/kHz', p_deriv(freq)*1e3

    #fbscan[lab]['polyfit']=p
    fbscan[lab]['updated_trim']=int(p(freq))

    dev.dev.labc.run_mode(0)
    if (fbscan[lab]['updated_trim'] < 10) or (fbscan[lab]['updated_trim'] > 3000):
        print 'fitted VtrimFB value OUT OF RANGE, setting previous value..'
        dev.dev.labc.l4reg(lab, 11, int(fbscan[lab]['current_trim']))   
        fbscan[lab]['updated_trim'] = fbscan[lab]['current_trim']
    else:
        print 'setting VtrimFB to..', fbscan[lab]['updated_trim']
        dev.dev.labc.l4reg(lab, 11, int(fbscan[lab]['updated_trim']))


    if plot:
        import matplotlib.pyplot as plt
        plt.plot(fbscan[lab]['freq'], np.array(fbscan[lab]['trim']),'o')
        plt.plot(fbscan[lab]['freq'], p(np.array(fbscan[lab]['freq'])), '--')
        plt.show()

    time.sleep(2) #let DLL settle

def rms(x):
    return np.sqrt(np.sum(x**2) / float(len(x)))

if __name__=='__main__':
    
    import surf_data
    import json

    dev=surf_data.SurfData()
    
    freq=210.000e6
    print 'using sine wave frequency', freq*1e-6, 'MHz'

    num_iter  = 20
    num_events= 8000

    lab=0
    #initial_fb_value = 1300

    trims = []
    dt_crossings = []
    dt_period = []
    dt_period_std = []

    fbscan_dict = []
      
    basefilename = '210MHz_tune_run_0914_CH0_noFeedback_v3_fixPeriods'
    
    flat_trims = setTrimDacs(dev, lab, fbtrim=1320, dt_trims=lab4d_default['dt_trim'])
    trims.append(flat_trims)
    ##fbscan = scanFeedbackFit(dev, lab, initial_fb_value, sine_freq=freq, sine_amp=300., scan_range=range(1230, 1411, 10))
    #fbscan = scanFeedbackPeriodogram(dev, lab, sine_freq=freq, scan_range=range(1210, 1461, 10))

    #tuneFeedback(dev, lab, fbscan, freq)

    flat_crossings, flat_period = singleRun(dev, lab, num_events=100, save=True, filename=basefilename+'100evts_flat.dat')
    
    _period_mean=np.zeros(lab4d_primary_sample_cells, dtype=float)
    _period_std=np.zeros(lab4d_primary_sample_cells, dtype=float)
    for j in range(lab4d_primary_sample_cells):
        _period_mean[j] = np.mean(flat_period[lab][j])
        _period_std[j] = np.std(flat_period[lab][j])
                
    dt_period.append(_period_mean)
    dt_period_std.append(_period_std)
    
    dt_crossings.append( flat_crossings[lab] * 1.e12 / freq)

    init_trims = setTrimDacs(dev, lab, fbtrim=1320)
    trims.append(init_trims)

    ## run scan
    _rms=100.
    i=0

    while (i < (num_iter+1)):

        if i>0:
            trims.append(tune(dev, lab, dt_crossings[i], trims[i]))
        
        #print 'tuning feedback trim...'
        ##fbscan = scanFeedbackFit(dev, lab, initial_fb_value, sine_freq=freq, sine_amp=300., scan_range=range(1210, 1461, 10))
        #fbscan = scanFeedbackPeriodogram(dev, lab, sine_freq=freq, scan_range=range(1210, 1461, 10))

        #tuneFeedback(dev, lab, fbscan, freq)
        #current_fb_value = fbscan[lab]['updated_trim']
        #fbscan_dict.append(fbscan)
        
        savedatfile = basefilename + '_data_iter%d.dat' % i

        crossings, periods = singleRun(dev, lab, num_events=num_events, save=False, filename=savedatfile)
        mean_crossings = np.mean(crossings[lab], dtype=np.float64) 
        avg_sample_dt = mean_crossings * 1.e12 / freq 
        dt_crossings.append( crossings[lab] * 1.e12 / freq)

        _period_mean=np.zeros(lab4d_primary_sample_cells, dtype=float)
        _period_std=np.zeros(lab4d_primary_sample_cells, dtype=float)
        for j in range(lab4d_primary_sample_cells):
            _period_mean[j] = np.mean(periods[lab][j])
            _period_std[j] = np.std(periods[lab][j])
                
        dt_period.append(_period_mean)
        dt_period_std.append(_period_std)

        _rms=np.std(dt_crossings[i])

        print '---------------------------------'
        print 'on iteration..', i, '-- dT RMS [ps]:' , _rms, \
            '-- avg dT [ps]', avg_sample_dt, '-- DLL wrap dT [ps]', dt_crossings[i][0]
        print '---------------------------------'
        i = i+1

    np.savetxt('crossings_'+basefilename+'.dat', np.array(dt_crossings))
    np.savetxt('mean_periods_'+basefilename+'.dat', np.array(dt_period))
    np.savetxt('std_periods_'+basefilename+'.dat', np.array(dt_period_std))
    np.savetxt('trims_' + basefilename+'.dat', np.array(trims))

    with open('fbdict_'+basefilename+'.dat', 'w') as outfile:
        json.dump(fbscan_dict, outfile)
