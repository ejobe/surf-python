'''
module to calculate zero-crossings and period from sine-wave data

author: Eric Oberla
ejo@uchicago.edu
'''
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np

from utils.surf_constants import *

prim_cells = lab4d_primary_sample_cells
nominal_dt = lab4d_nominal_dt

def zeroCrossings(data, lab, return_cell_profile=False):
    '''
    zero crossings counter
    data: should be numpy array
    prim_cell_zero_mean: flag to calculate mean of each cell from full dataset and subtract cell-by-cell
    return_cell_profile: return profile of each cell (a list of 128 lists)

    zero crossing for primary sampling cell n defined as the waveform crossing 0 volts between cell n and n-1
    
    added 8/22/2016: returns sine-wave period information as well
    '''    

    zero_crossings_all={} #dict of arrays
    period_cells={}       #dict of list of lists

    t_nom = np.linspace(0, prim_cells * nominal_dt , prim_cells)

    if not isinstance(lab, list):
        lab=[lab]

    for l in lab:

        zero_cross = np.zeros(prim_cells, dtype=float)
        period_cells[l] = []
        
        num_entries = 0
        num_entries_wrap = 0

        cell_profile = []
        for c in range(prim_cells):
            cell_profile.append([])
            period_cells[l].append([])

        for i in range(len(data)):
            d=data[i,l,:]
            for buf in range(0, 8):
                for k in range(0, prim_cells):
                    cell_profile[k].append( d[k+(buf*prim_cells)])
        
        cell_profile_mean=np.zeros(prim_cells, dtype=float)

        for c in range(prim_cells):
            cell_profile_mean[c] = sum(cell_profile[c]) / float(len(cell_profile[c]))
            
        ##this returns the cell profile data for all cells in a SINGLE channel
        if return_cell_profile:
            return cell_profile
        
        for i in range(len(data)):       
            d = data[i,l,:]

            #if mean_subtract and not prim_cell_zero_mean:
            #    d = d-np.mean(d)

            last_falling = -1
            last_rising = -1
            time_last_falling = -1.
            time_last_rising  = -1.

            for buf in range(0, 8):
                num_entries = num_entries + 1

                ##loop over all cells, exluding DLL wraparound (cell 127->0)
                for k in range(prim_cells-1):
                    
                    ##subtract mean from cell profile plots, each sample
                    v_samp    = float(d[k+(buf*prim_cells)]) - cell_profile_mean[k]
                    v_samp_p1 = float(d[k+(buf*prim_cells)+1])- cell_profile_mean[k+1]
                        
                    ##rising edge condition
                    if (v_samp <= 0.) and (v_samp_p1 > 0.):
                        zero_cross[k+1] = zero_cross[k+1] + 1.                       
                        
                        interp_time = t_nom[k+1] - abs(nominal_dt * v_samp_p1/(v_samp_p1-v_samp))

                        if last_rising > -1:
                            if last_rising > k+1: # or last_rising == 0:
                                period_cells[l][k+1].append( interp_time - time_last_rising + (prim_cells + 1) * nominal_dt)
                            else:
                                period_cells[l][k+1].append( interp_time - time_last_rising )
                                

                        last_rising = k+1
                        time_last_rising = interp_time

                    ##falling edge condition
                    if (v_samp >= 0.) and (v_samp_p1 < 0.):
                        zero_cross[k+1] = zero_cross[k+1] + 1.

                        interp_time = t_nom[k+1] - abs(nominal_dt * v_samp_p1/(v_samp_p1-v_samp))

                        if last_falling > -1:
                            if last_falling > k+1: # or last_falling == 0:
                                period_cells[l][k+1].append( interp_time - time_last_falling + (prim_cells + 1) * nominal_dt)
                            #    if k+1 == 12:
                            #        print 'last falling', last_falling, 't last fall', time_last_falling, 't_nom last', t_nom[last_falling-1], \
                            #            't interp now', interp_time, 't nom', t_nom[k], 'period',  interp_time - time_last_falling + (prim_cells + 1) * nominal_dt

                            else:
                                period_cells[l][k+1].append( interp_time - time_last_falling )
                            #    if k+1 == 50:
                            #        print 'last falling', last_falling, 't last fall', time_last_falling, 't_nom last', t_nom[last_falling-1], \
                            #            't interp now', interp_time, 't nom', t_nom[k], 'period', interp_time - time_last_falling 

                        last_falling = k+1
                        time_last_falling = interp_time

                ## handle wraparound (cell 127->0) separately here
                if  (buf < 7):
                    
                    num_entries_wrap = num_entries_wrap + 1

                    v_samp    = float(d[prim_cells-1+(buf*prim_cells)]) - cell_profile_mean[prim_cells-1]
                    v_samp_p1 = float(d[prim_cells+(buf*prim_cells)]) - cell_profile_mean[0]
                    
                    ## rising edge condition for DLL seam
                    if  (v_samp <= 0.) and (v_samp_p1 > 0.):
                        zero_cross[0] = zero_cross[0] + 1.
                        
                        interp_time = t_nom[0] - abs(nominal_dt * v_samp_p1/(v_samp_p1-v_samp))

                        ## time in the DLL seam is defined as: (primary_cells-1)*nominal_dt -> 0.0 
                        if last_rising > -1:
                            period_cells[l][0].append( interp_time - time_last_rising + (prim_cells + 1) * nominal_dt )
        
                        last_rising = 0
                        time_last_rising = interp_time

                    ## falling edge condition for DLL seam
                    if  (v_samp >= 0.) and (v_samp_p1 < 0.):
                        zero_cross[0] = zero_cross[0] + 1.

                        interp_time = t_nom[0] - abs(nominal_dt * v_samp_p1/(v_samp_p1-v_samp))

                        if last_falling > -1:
                            period_cells[l][0].append( interp_time - time_last_falling + (prim_cells + 1) * nominal_dt )
                            
                        last_falling = 0
                        time_last_falling = interp_time


        num_entries_array=np.ones(prim_cells, dtype=float) * num_entries * 2
        num_entries_array[0] = num_entries_wrap * 2
        zero_crossings_all[l] = np.divide(zero_cross, num_entries_array)
        
    return zero_crossings_all, period_cells

if __name__=='__main__':

    import matplotlib.pyplot as plt

    lab = 5

    #d = np.loadtxt('test210MHz.dat')
    d = np.loadtxt('test210MHz_1000events.dat')
    new_data=np.zeros((len(d)/1024, 12, 1024))
    
    for i in range(0, len(d), 1024):
        new_data[i / 1024,:,:] = np.transpose(d[i:i+1024,:])
        
    plt.figure()
    plt.plot(new_data[2][lab][:])
    
    crossings, period = zeroCrossings(new_data[1:,:,:], lab)

    plt.figure()
    plt.plot(crossings[lab], '-', drawstyle='steps')
    plt.xlabel('primary cell number')
    plt.ylabel('fraction occupancy')

    plt.figure()
    plt.hist(crossings[lab] * 1.e6/ 210.0, bins=range(250, 391, 8))
    plt.xlabel('dT [ps]')

    period_mean=np.zeros(prim_cells, dtype=float)
    for i in range(prim_cells):
        period_mean[i] = np.mean(period[lab][i])


    plt.figure()
    #plt.hist(period[lab][0], alpha=0.5)
    plt.hist(period[lab][1], alpha=0.5, bins=np.arange(4.2, 5.4, 0.01))
    plt.hist(period[lab][30], alpha=0.5, bins=np.arange(4.2, 5.4, 0.01))
    plt.hist(period[lab][50], alpha=0.5, bins=np.arange(4.2, 5.4, 0.01))
    plt.hist(period[lab][100], alpha=0.5, bins=np.arange(4.2, 5.4, 0.01))
    #plt.hist(period[lab][120], alpha=0.5, bins=np.arange(4.0, 5.4, 0.01))

    plt.figure()
    plt.plot(period_mean, 'o-')
    plt.plot([0,128], [1/.210, 1/.210], '--')
    plt.plot([0,128], [np.mean(period_mean), np.mean(period_mean)], '--')

    plt.show()
