import timing
import calibrations.surf_calibrations as sc
from utils.surf_constants import *

def tune(dev, lab, freq, amplitude, scan_range=range(1160, 1411, 10)):

    fbscan = timing.scanFeedbackFit(dev, lab, sine_freq=freq, sine_amp=amplitude, scan_range=scan_range)

    return fbscan

def do(lab, sine_frequency, sine_amplitude):
    import surf_data
    dev=surf_data.SurfData()

    fbdict={}

    for l in lab:
        print '--------------'
        print 'tuning LAB', l
        print '--------------'
        fbscan = tune(dev, l, sine_frequency, sine_amplitude)
        timing.tuneFeedback(dev, l, fbscan, sine_frequency)
        
        fbdict[str(l)] = fbscan[l]['updated_trim']
    
    return fbdict

def save(fbdict, dna):
    for key in fbdict:
        print key, fbdict[key]
        sc.save_vtrimfb(dna, int(key), fbdict[key])

    print 'reading back cal file:'
    a=sc.read_cal(dna, 'vtrimfb')
    print 'vtrimfb', a

def load(dna):
    fbtrims=[]
    try:
        a=sc.read_cal(dna, 'vtrimfb')
    except KeyError:
        print 'setting default values'

        for i in range(12):
            fbtrims.append(lab4d_default['vtrim_fb'])
        
        return fbtrims

    for i in range(12):
        try:
            fbtrims.append(a[str(i)])
        except KeyError:
            fbtrims.append(lab4d_default['vtrim_fb'])
                
    return fbtrims
        
