#############################################################
import os.path

calibration_dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)) + '/'
calibration_dir = calibration_dir_path + 'calibrations/' 
calibration_filename = calibration_dir + 'surf_calibrations.json' #file where calibration data is saved

#############################################################

surf_channels = 12 #channels (no. of LAB4D chips)
surf_event_buffer = 1024 #samples
surf_default_vped = 1900 # DAC counts (millivolts = surf_default_vped * 2000/4096)
surf_dac_counts_per_mv = 2.0

#FPGA output data packed in a 16 bit word per sample:
lab4d_data_mask = 0x0FFF
lab4d_buffer_mask = 0xC000
lab4d_window_mask = 0x2000

#LAB4D asic specific:
lab4d_adc_bits = 12 #bits
lab4d_sampling_rate = 3.200 #gigasamples-per-second
lab4d_nominal_dt = 1./lab4d_sampling_rate #nanoseconds
lab4d_primary_sample_cells = 128 #samples
lab4d_storage_cells = 4096 #samles

#############################################################

##LAB4D register addresses
lab4d_register={}
lab4d_register['vboot'] = 0

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
lab4d_default['dt_trim'] = 1600 
lab4d_default['vtrim_fb']= 1350 
lab4d_default['vadjp']   = 2700
lab4d_default['vadjn']   = 1671

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


