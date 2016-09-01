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

    #smooth_x=np.linspace(0,len(data), len(data)*10)

    if plot:
        print popt
        plt.plot(x, data, 'o')
        plt.plot(x, my_sin(x, *popt))
        plt.show()

    return popt
                 
