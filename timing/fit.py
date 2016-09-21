import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

nominal_sampling_dt = 0.3125 #ns

def my_sin( x, a,b,c):
    return a*np.sin(x*b+c)

def fit_sin( data, amp, freq, phase, dt=nominal_sampling_dt,
             use_timebase=False, plot=False):

    x=np.arange(len(data), dtype=float)
    
    if use_timebase:
        for i in range(len(x)):
            x[i] = i*dt*1.e-9

    y=my_sin(x, amp, freq, phase)
    popt, pfit = curve_fit(my_sin, x, data, p0=[amp, freq, phase])
                           #sigma=(np.zeros(len(x))+0.1))

    if plot:
        print popt
        plt.plot(x, data, 'o')
        plt.plot(x, my_sin(x, *popt))
        plt.show()

    return popt
                 
def my_gaus(x, norm, mu, sig):
    return norm * np.exp( -0.5 * np.power(x-mu,2) / ( sig**2 ))

def fit_gaus( bins, data, amp=1, mu=0, sig=1, plot=False):
    
    popt, pfit = curve_fit(my_gaus, bins, data, p0=[amp, mu, sig])

    if plot:
        print popt
        plt.figure()
        plt.plot(bins, data, 'o', color='black')
        #plt.plot(bins, data, '-', drawstyle='steps', color='black')
        plt.plot(bins, my_gaus(bins, *popt), '--', color='red')
        #fine_bins = np.arange(bins[0], bins[-1], (bins[1]-bins[0])/10)
        #plt.plot(fine_bins, my_gaus(fine_bins, *popt), '--', color='red')
        plt.show()
        
    return popt #constant, mean, sigma
