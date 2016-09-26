import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('xtick', labelsize=15)
matplotlib.rc('ytick', labelsize=15)

import fit
import json

basefilename='235MHz_tune_run_0919TEST'

cfiles=['dt_crossings'+basefilename+'.json']
tfiles=['trimdacs_'+basefilename+'.json']
pfiles=['mean_periods'+basefilename+'.json', 'w']
psigfiles=['std_periods'+basefilename+'.json', 'w']

freq = 235.00e6

lab_to_plot=4

#leg=['run0','run1', 'run2']

first=0 #first event to plot
last=-1 #last event to plot (-1 = last in python indexing magic)

if __name__=="__main__":

    with open(cfiles[0],'r') as infile:
        crossings = json.load(infile)
    #crossings=np.loadtxt(cfiles[f])
    with open(tfiles[0],'r') as infile:
        trims = json.load(infile)
    #trims = np.loadtxt(tfiles[f])
    with open(pfiles[0],'r') as infile:
        mean_periods = json.load(infile)
    #mean_periods = np.loadtxt(pfiles[f])
    with open(psigfiles[0],'r') as infile:
        std_periods = json.load(infile)

    if(1):

        crossings = np.array(crossings[str(lab_to_plot)])
        mean_periods = np.array(mean_periods[str(lab_to_plot)])
        trims = np.array(trims[str(lab_to_plot)])
        std_periods = np.array(std_periods[str(lab_to_plot)])

        rms=[]
        mean_mean_periods=[]
        for i in range(len(crossings)):
            rms.append(np.std(crossings[i,0:]))
            mean_mean_periods.append(np.mean(mean_periods[i,:]))
            
        #plt.hist(crossings[first,:], bins=range(240, 401, 5), alpha=0.4, label='first iteration (flat)')
        ##plt.hist(crossings[1,:], bins=range(220, 401, 5), alpha=0.4, label='1st iteration (initial guess)')
        #plt.hist(crossings[last,:], bins=range(220, 401, 5), alpha=0.4, label='best iteration')
        #plt.legend()
        #plt.xlabel('Measured sample dt [ps]', size=16)
        #plt.ylabel('Entries / 5 ps', size=16)

        #####################################################################

        plt.figure(1)
        bin_size=1.7
        
        n, bins, patches = plt.hist(crossings[last,:], bins=np.arange(294, 350, bin_size), alpha=0.4, label='best iteration', color='black')
        bin_centers = np.array(bins[:-1], dtype=float)+bin_size/2
        a = fit.fit_gaus(bin_centers, np.array(n), amp=np.max(n), mu=np.mean(crossings[last,:]), sig=np.std(crossings[last:])) 

        fine_bins = np.arange(bins[0], bins[-2], (bins[1]-bins[0])/10)
        
        plt.plot(fine_bins, fit.my_gaus(fine_bins, *a), '--', color='red', lw=3, label='Fit')
        
        plt.text(325, np.max(n)/3, 'All Cells:\n mean: {:.2f} ps\n RMS: {:.2f} ps\n\nFit Parameters:\n mean: {:.2f} ps\n sigma: {:.2f} ps'.format(np.mean(crossings[last,:]), np.std(crossings[last,:]), a[1], a[2]), size=16)

        plt.xlim([296, 345])

        print 'trim dacs, initial guess:', np.mean(crossings[0,:]), np.std(crossings[first,:])
        print 'all cells, last:', np.mean(crossings[last,:]), np.std(crossings[last,:])
        print 'excluding last sample, last', np.mean(crossings[last,:-1]), np.std(crossings[last,:-1])
        
        plt.xlabel('Measured sample dt [ps]', size=16)
        plt.ylabel('Entries / {:.2f} ps'.format(bin_size), size=16)
        
        plt.legend()
        
        #####################################################################
        
        plt.figure(2)
        plt.plot(rms[first:last], 'o--', color='black')
        plt.xlim([first-1, len(rms)+last+3])
        plt.xlabel('Iteration', size=16)
        plt.ylabel('RMS of calculated dTs [ps]', size=16)
        plt.grid()
        #plt.yscale('log')
            
        #####################################################################
        plt.figure(3)
        plt.plot(crossings[first,:], 'o-', ms=3, lw=3, alpha=0.4, label='initial values')
        plt.plot(crossings[last,:], 'o-', ms=3, lw=2, alpha=0.8, color='black', label='best iter')
        plt.plot([0,128],[312.5, 312.5], label='3.2 GSa/s', lw=4, alpha=0.5)
        plt.ylim([270,400])
        plt.xlim([-2, 135])
        plt.ylabel('Measured sampling cell dt [ps]', size=17)
        plt.xlabel('Primary sampling cell no.', size=17)
        plt.legend(ncol=3, loc='upper left')
            
        #####################################################################
        plt.figure(11)
        plt.plot(trims[1,:], 'o-', lw=2, alpha=0.6, label='initial guess')
        plt.plot(trims[last,:], 'o--', color='black',label='last iteration')
        print 'mean trim dac value,', 'first (guess):', np.mean(trims[1,:]), 'last:', np.mean(trims[last,:])
        #print trims[last,:]
        plt.xlabel('Sample no.', size=16)
        plt.ylabel('Trim DAC value', size=16)
        plt.legend(loc='lower left', numpoints=1)
        plt.xlim([-2,130])
        
        plt.figure(12, figsize=(12,8))
        for cell in range(128):
            if cell==0:
                plt.plot(trims[0,cell],crossings[0,cell],'+',   markersize=9, lw=3, color='black', label='initial guess')
                plt.plot(trims[last,cell],crossings[last,cell], 'o', ms=4, alpha=0.9, color='black', label='last iteration')
                
                plt.plot(trims[0::len(trims)+last,cell],crossings[0::len(trims)+last,cell], '-',  lw=1, color='black', alpha=0.7, label='sample 0-1')
            elif cell==127:
                plt.plot(trims[0,cell],crossings[0,cell],'+',   markersize=9, color='green')
                plt.plot(trims[last,cell],crossings[last,cell],'o',  alpha=0.7, ms=4,color='green')
                plt.plot(trims[0::len(trims)+last,cell],crossings[0::len(trims)+last,cell],'-', lw=1, alpha=0.7, color='green', label='sample 127-0')
                    #print trims[:,cell]
                    #print trims[1::len(trims)+last-1, cell], trims[last, cell]
                    #print crossings[:,cell]
                    #print crossings[1::len(trims)+last-1, cell], crossings[last, cell]

            elif cell%2==0:
                plt.plot(trims[0,cell],crossings[0,cell],'+',   alpha=0.4,markersize=7, color='blue')
                plt.plot(trims[last,cell],crossings[last,cell],'o',  ms=4, alpha=0.5, color='blue')
                if cell == 126:
                    plt.plot(trims[0::len(trims)+last,cell],crossings[0::len(trims)+last,cell],'-',  lw=1, alpha=0.25, label='even sample pairs', color='blue')
                else:
                    plt.plot(trims[0::len(trims)+last,cell],crossings[0::len(trims)+last,cell],'-',  lw=1, alpha=0.25, color='blue')

            else:
                plt.plot(trims[0,cell],crossings[0,cell],'+',   alpha=0.4,markersize=7,  color='red')
                plt.plot(trims[last,cell],crossings[last,cell],'o',  ms=4, alpha=0.5, color='red')
                if cell == 125:
                    plt.plot(trims[0::len(trims)+last,cell],crossings[0::len(trims)+last,cell],'-',  lw=1, alpha=0.25, label='odd sample pairs', color='red')
                else:
                    plt.plot(trims[0::len(trims)+last,cell],crossings[0::len(trims)+last,cell],'-',  lw=1, alpha=0.25, color='red')


        plt.ylim([200, 380])
        plt.xlim([0, 2600])
        plt.legend(loc='lower left', numpoints=1)
            #plt.grid()
        plt.xlabel('Trim DAC value', size=16)
        plt.ylabel('Sample dt [ps]', size=16)
        #####################################################################
        plt.figure(6)
        plt.plot(mean_periods[first,:], 'o-', ms=3, lw=4, alpha=0.4, label='first iter') 
        #plt.plot([0,128],[np.mean(mean_periods[first,:]),np.mean(mean_periods[first,:])], '--', color='blue')
            
        plt.plot(mean_periods[last,:], 'o-', ms=3, lw=2, alpha=0.8, color='black', label='best iter')
        #plt.plot([0,128],[np.mean(mean_periods[last,:]),np.mean(mean_periods[last,:])], '--', color='black')

        plt.plot([0,128],[1.e9/freq, 1.e9/freq], label='input Period', lw=4, alpha=0.5)
        plt.ylabel('Measured Sine Wave Period [ns]', size=17)
        plt.xlabel('Primary sampling cell no.', size=17)
        plt.xlim([-2, 138])
        plt.ylim([1.e9/freq-.1, 1.e9/freq+.12])

        plt.legend()

        #####################################################################
        '''
        plt.figure(7)
        plt.plot(1.e3*(np.array(mean_mean_periods)-1.e9/freq), 'o--', color='black')#, label='mean period measured\nper iteration')
        #plt.plot(np.ones(len(mean_mean_periods))*1.e9/freq, '-', label='input Period', lw=3)
        #plt.ylabel('Sine Wave Period [ns]', size=17)
        plt.ylabel('Difference Mean Measured - Actual [ps]', size=17)
        plt.xlabel('Iteration no.', size=17)
        #plt.ylim([1.e9/freq-0.001,1.e9/freq+0.0015])
        #plt.ticklabel_format(style='sci', axis='y')
        plt.grid()
        plt.legend(numpoints=1)
        '''

        plt.figure(21)
        plt.plot(std_periods[first,:])
        plt.plot(std_periods[last,:])

    timesum=np.cumsum(crossings[:,0:], axis=1)

    #####################################################################
    '''
    plt.figure(4)
    plt.plot(40.0-timesum[:,127]*1e-3, 'o--', label='sum of 128 dts - 40 ns', lw=3,color='black')
    plt.grid()
    
    plt.xlabel('Interation no.', size=16)
    plt.ylabel('Phase closure [ns]', size=16)
    plt.ylim([-.02, .02])
    '''
    
    '''
    plt.figure(5)
    plt.plot(np.mean(crossings[:,1:], axis=1), 'o--', label='avg., samples 1-127')
    plt.plot(crossings[:,0], 'o--', label='sample 0')
    plt.xlabel('Interation no.', size=16)
    plt.ylabel('Sample Delay [ps]', size=16)
    plt.legend(loc='lower right')

    plt.figure(4)
    plt.legend(loc='upper right')
    '''

#with open('fbdict_210MHz_tune_run_0913_CH0_v2.dat','r') as infile:
#    fbfile = json.load(infile)

#for key in fbfile:
#    print key

#####################################################################
'''
plt.figure(10)
plt.plot(fbfile[0][u'0'][u'trim'],np.array(fbfile[0][u'0'][u'freq'])*1e-6, '--', label='iter 0')
plt.plot(fbfile[1][u'0'][u'trim'],np.array(fbfile[1][u'0'][u'freq'])*1e-6, '--', label='iter 1')
plt.plot(fbfile[2][u'0'][u'trim'],np.array(fbfile[2][u'0'][u'freq'])*1e-6, '--', label='iter 2')
plt.plot(fbfile[5][u'0'][u'trim'],np.array(fbfile[2][u'0'][u'freq'])*1e-6, '--', label='iter 5')
plt.plot(fbfile[10][u'0'][u'trim'],np.array(fbfile[10][u'0'][u'freq'])*1e-6, '--', label='iter 10')
plt.plot(fbfile[20][u'0'][u'trim'],np.array(fbfile[10][u'0'][u'freq'])*1e-6, '--', label='iter 20')
plt.xlabel('Feedback trim DAC value', size=16)
plt.ylabel('Fitted frequency of recorded sine wave [MHz]', size=16)
plt.xlim([1210, 1450])
plt.grid()
plt.legend(loc='lower right')
'''

plt.show()

    
    
