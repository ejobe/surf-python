#############################################################
import os.path
import numpy

calibration_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)) + '/'
calibration_dir = calibration_dir_path + 'calibrations/' 
calibration_filename = calibration_dir + 'surf_calibrations.json' #file where calibration data is saved
pedestal_filename = calibration_dir + 'surf_pedestals.json' #file where pedestal data is saved

#############################################################

surf_channels = 12 #channels (no. of LAB4D chips)
surf_event_buffer = 1024 #samples
surf_default_vped = 1900 # DAC counts (millivolts = surf_default_vped * 2000/4096)
surf_dac_counts_per_mv = 2.0

#FPGA output data packed in a 16 bit word per sample:
lab4d_data_mask = 0x0FFF    #low 12 bits are the digitized data
lab4d_buffer_mask = 0xC000  #which of 4 buffers event is stored
lab4d_window_mask = 0x2000  #which of 8 windows the trigger occured (used to un-wrap event)

#LAB4D asic specific:
lab4d_adc_bits = 12 #bits
lab4d_sampling_rate = 3.200 #gigasamples-per-second
lab4d_nominal_dt = 1./lab4d_sampling_rate #nanoseconds
lab4d_nominal_dt_ps = lab4d_nominal_dt*1.e3 #picoseconds
lab4d_primary_sample_cells = 128 #samples
lab4d_storage_cells = 4096 #samlpes
lab4d_nominal_time = \
    numpy.linspace(0, lab4d_primary_sample_cells*lab4d_nominal_dt, lab4d_primary_sample_cells+1)

#############################################################

##LAB4D register addresses
lab4d_register={}
lab4d_register['vboot'] = 0
lab4d_register['vbsx'] = 1
lab4d_register['van_n'] = 2
lab4d_register['vbs'] = 4
lab4d_register['vbias'] = 5
lab4d_register['vbias2'] = 6
lab4d_register['cmpbias'] = 7
lab4d_register['qbias'] = 9
lab4d_register['isel'] = 10
lab4d_register['dt_trim'] = range(256, lab4d_primary_sample_cells+256)
lab4d_register['vtrim_fb'] = 11
lab4d_register['vadjp'] = 8
lab4d_register['vadjn'] = 3
lab4d_register['testpattern'] = 13
lab4d_register['wr_strb_le'] = 384
lab4d_register['wr_strb_fe'] = 385
lab4d_register['sstoutfb'] = 386
lab4d_register['wr_addr_sync'] = 387
lab4d_register['tmk_s1_le'] = 388
lab4d_register['tmk_s1_fe'] = 389
lab4d_register['tmk_s2_le'] = 390
lab4d_register['tmk_s2_fe'] = 391
lab4d_register['phase_le'] = 392
lab4d_register['phase_fe'] = 393
lab4d_register['sspin_le'] = 394
lab4d_register['sspin_fe'] = 395

##initial LAB4D register values:
lab4d_default={}
lab4d_default['vboot']   = 1024
lab4d_default['vbsx']    = 1024
lab4d_default['van_n']   = 1024
lab4d_default['vbs']     = 1024
lab4d_default['vbias']   = 1100   
lab4d_default['vbias2']  = 950
lab4d_default['cmpbias'] = 1024
lab4d_default['qbias']   = 1000
#lab4d_default['isel']    = 2780 # ~20 us ramp   
#lab4d_default['isel']    = 2350 # ~ 5 us ramp  
lab4d_default['isel']    = 2580  # ~10 us ramp  
lab4d_default['dt_trim'] = 1750 
lab4d_default['vtrim_fb']= 1350 
lab4d_default['vadjp']   = 2680
lab4d_default['vadjn']   = 1721

lab4d_default['testpattern'] = 0xBA6

###timing registers:
lab4d_default['wr_strb_le']  = 95
lab4d_default['wr_strb_fe']  = 0
lab4d_default['sstoutfb']    = 104
lab4d_default['wr_addr_sync']= 0
lab4d_default['tmk_s1_le']   = 55
lab4d_default['tmk_s1_fe']   = 86
lab4d_default['tmk_s2_le']   = 7
lab4d_default['tmk_s2_fe']   = 32
lab4d_default['phase_le']    = 35
lab4d_default['phase_fe']    = 75
lab4d_default['sspin_le']    = 100
lab4d_default['sspin_fe']    = 6

def mapLab4dRegs():

    lab4dreg={}
    
    print '******************************'
    print 'LAB4D serial program registers'
    print '******************************'
    for key in lab4d_default:
        for reg_key in lab4d_register:
            if key == reg_key:
                lab4dreg[str(lab4d_register[key])] = (key, lab4d_default[key])
                #print 'addr:', lab4d_register[key], '  ', key, '-- default value is: ', lab4d_default[key]
    
    for key in lab4dreg:
        try:
            int(key)
        except:
            list(key)
    
    for i in range(512):
        for key in lab4dreg:
            try:
                _key = int(key)
            except:
                _key = int(key[1:4])

            if int(_key) == i:
                print 'addr:', key, '  ', lab4dreg[key][0], '-- default value is: ', lab4dreg[key][1]
                
    return lab4dreg
