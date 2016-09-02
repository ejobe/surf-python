#############################################################
'''
SurfData class to log and handle SURFv5 data

Eric Oberla
ejo@uchicago.edu
7/12/2016
'''
#############################################################

import surf
from utils.surf_constants import *
import calibrations.surf_calibrations as surf_cal

import numpy as np
import time
import sys

#import h5py --someday will include a compressed data format

EVENT_BUFFER = surf_event_buffer
LAB_ADC_BITS = lab4d_adc_bits

class SurfData:
    def __init__(self):
        self.dev=surf.Surf()
        self.pedestals=np.zeros(((lab4d_storage_cells, surf_channels)), dtype=np.int)

    ################################################################   
    # set some configurations for data taking
    def start(self, startup_wait=0.2):
        self.pedestals=np.zeros((EVENT_BUFFER*4, 12), dtype=np.int)
        self.lab_lut = np.zeros((2**LAB_ADC_BITS, 12), dtype=float)
        self.dev.labc.run_mode(0)
        self.dev.labc.reset_fifo()
        self.dev.labc.testpattern_mode(0)
        self.dev.labc.run_mode(1)
        time.sleep(startup_wait)
     
    ################################################################   
    # log data
    ## numevent = number of events to save
    ## lab = channels to save (default = 15 == all channels; **not sure if any other input will actually work**)
    ## filename = flat data file name
    ## save = save to file (default = true)
    ## subtract_ped = pedestal subtract data (default = true)
    ## unwrap = unwrap data specified by trigger location (default = true)
    ## force_trig = software trigger (default = true)
    ####
    def log(self, numevent, lab=15, filename='temp.dat', save=True, subtract_ped=True, 
            unwrap=True, single_channel=False, save_channel=0, force_trig=True):
        
        self.start()
        
        data=[]
        if subtract_ped:
            self.loadPed()
        
        for i in range(numevent):
            _data = self.dev.log_lab(lab, samples=EVENT_BUFFER, force_trig=force_trig)

            for k in range(surf_channels):
                end_of_buf_flag=-1
                datbuf = (_data[k][0] & lab4d_buffer_mask) >> 14 #check the LAB4D buffer only on the 0th sample 
                                                                 #(should be the same for all samples...if it's working correctly)
                for j in range(EVENT_BUFFER):
                    #datbuf = (_data[k][j] & lab4d_buffer_mask) >> 14
                    while(((_data[k][j] & lab4d_window_mask) >> 13) and (end_of_buf_flag < 0)):
                        end_of_buf_flag=j
                        break

                _data[k] = np.subtract(np.bitwise_and(_data[k][:], lab4d_data_mask), self.pedestals[datbuf*EVENT_BUFFER:(datbuf+1)*EVENT_BUFFER, k])

                if unwrap and (end_of_buf_flag >= 0):
                    _data[k] = np.roll(_data[k], -int(end_of_buf_flag + lab4d_primary_sample_cells))

            data.append(_data)

            if (i+1)%10==0:
                sys.stdout.write('logging event...{:}\r'.format(i+1))
                sys.stdout.flush()

        if save:
            sys.stdout.write('saving to file...{:}\n'.format(filename))
            if single_channel == True:
                d= np.array(data)
                np.savetxt(filename, d[:,save_channel,:].reshape(numevent*EVENT_BUFFER, 1))

            else:
                #np.savetxt(filename, np.array(data, dtype=int).reshape(len(data[0]), numevent*EVENT_BUFFER))
                with open(filename, 'w') as filew:
                    for i in range(numevent):
                        for j in range(0, len(data[0][0])):
                       
                            for k in range(0, len(data[0])):
                                filew.write(str(data[i][k][j]))
                                filew.write('\t')

                            filew.write('\n')
        return data
    
    ################################################################
    #take a pedestal run
    def pedestalRun(self, numruns=160, filename='peds.temp', save=True, update_cal_file=True):

        self.start()

        if (numruns % 4) > 0:
            print 'pedestal run requires numruns be a multiple of 4'
            return 1

        data = self.log(numruns, save=False, subtract_ped=False, unwrap=False)
        ped_data=np.zeros((lab4d_storage_cells, surf_channels), dtype=np.int)
        
        for i in range(0, len(data)):
            for j in range(0, EVENT_BUFFER):
                for k in range(0, len(data[0])):
                    ped_data[j+(i%4)*EVENT_BUFFER,k] += (data[i][k][j] & lab4d_data_mask)

        '''the above process should probably be numpy-fied to run faster'''
        #ped_data = np.transpose(np.sum(np.bitwise_and(np.array(data).reshape((numruns/4, 12, 4096)), 0x0FFF), axis=0))
        ped_data /= (numruns / 4)
        
        if save:
            np.savetxt(calibration_dir + filename, ped_data)
            
            if update_cal_file:
                surf_cal.save_pedestals(self.dev.dna(), ped_data.tolist()) 
                
        return ped_data
    
    ################################################################
    #load pedestal data from calibration file
    def loadPed(self, from_ascii_file=False, ascii_filename='peds.temp'):

        if from_ascii_file:
            #load pedestals from flat text file
            self.pedestals = np.loadtxt(calibration_dir + ascii_filename)
            
        else:
            #default load from calibration json file
            self.pedestals = np.array(surf_cal.read_pedestals(self.dev.dna()))
            
    
    ################################################################
    # DC pedestal scan: specify 'start' DAC value, 'stop' DAC value, and DAC increment ('incr')
    def pedestalScan(self, start=0, stop=4096, incr=100, evts_per=120, filename='pedscan.temp', save=True):
        
        scan_ped=[]
        scan_val=[]
        
        for val in range(start, stop, incr):
            sys.stdout.write('pedestal level is.......{:}\r'.format(val))
            sys.stdout.flush()

            self.dev.i2c.set_vped(val, eeprom=False)
            pedestals = self.pedestalRun(evts_per, save=False)
            scan_ped.append(pedestals)
            scan_val.append(val)

        sys.stdout.write('\n')
        scan_ped =np.array(scan_ped)

        if save:
            filename=calibration_dir + filename
            with open(filename, 'w') as filew:
                for j in range(0, len(scan_val)):
                    filew.write(str(scan_val[j]))
                    filew.write('\t')
                    for k in range(surf_channels):
                        for cell in range(0, 2**LAB_ADC_BITS):
                            filew.write(str(scan_ped[j][cell][k]))
                            filew.write('\t')
                    filew.write('\n')

        return scan_val, scan_ped
    
    ################################################################
    # Make a look-up-table using linear interpolation based on pedestalScan file
    def makeSurfLUT(self, filename, pedscan_start=0, pedscan_interval=100, save=True):

        ##single lut for each channel'''
        surf_lut = -1.*np.ones((surf_channels, 2**LAB_ADC_BITS), dtype=float)

        pedscan = np.loadtxt(filename)
        num_steps_in_scan = pedscan.shape[0]

        dac_voltage = np.arange(pedscan_start, pedscan_start+pedscan_interval*num_steps_in_scan, pedscan_interval)*1./surf_dac_counts_per_mv
        
        ##simple linear interpolation
        for i in range(surf_channels):
            for j in range(num_steps_in_scan):

                lab_value = int(np.mean(pedscan[j,i*lab4d_storage_cells+1:(i*lab4d_storage_cells+1+lab4d_storage_cells)]))
                surf_lut[i, lab_value] = dac_voltage[j]
                if j > 0 and lab_value < 2**LAB_ADC_BITS:
                    slope = (surf_lut[i, lab_value] - surf_lut[i, last_lab_value]) / (lab_value - last_lab_value)
                    surf_lut[i, last_lab_value:lab_value] = np.array(range(lab_value-last_lab_value))*slope + surf_lut[i, last_lab_value]
                    
                last_lab_value = lab_value    

        return surf_lut

    @staticmethod
    def readPedScan(self, lab, firstcell=0, cells=1, lo=0, hi=20,filename='pedscan.dat',
                      fit=True, fit_order=3, plot=False, plot_color='green'):

        import matplotlib
        import matplotlib.pyplot as plt
        matplotlib.rc('xtick', labelsize=14)
        matplotlib.rc('ytick', labelsize=14)

        with open(filename, 'r') as filer:
            pedscan=[x.strip().split('\t') for x in filer]

        pedscan=np.array(pedscan, dtype=int)

        if fit==False:
            return pedscan
        
        params=[]
        print pedscan[int(lo),0]/2
        print pedscan[int(hi),0]/2

        cell_stack=np.zeros(128)

        for cell in range(firstcell, firstcell+cells):
            index=int(cell+lab*4096+1)
            fitx = pedscan[int(lo):int(hi),0]
            fity = pedscan[int(lo):int(hi),index]
            params.append(np.polyfit(fitx, fity, deg=fit_order))
            linefit=np.poly1d(params[int(cell-firstcell)])

            cell_stack[cell % 128] += params[int(cell-firstcell)][0]
        
            if plot:
                f, (a0, a1) = plt.subplots(2,1, gridspec_kw={'height_ratios':[3,1]})
           
                a0.plot(pedscan[:,0]/2,pedscan[:,index], 'o', color=plot_color)
                a0.plot(pedscan[:,0]/2, linefit(pedscan[:,0]))
                a0.set_ylim([-100, 4200])
                a0.set_ylabel('LAB4 output code', size=16)
           
                a1.plot(pedscan[:,0]/2, pedscan[:,index]-linefit(pedscan[:,0]),'o')
                a1.set_ylim([-150, 300])
                a1.set_ylabel('Fit res., ADC counts', size=16)
                a1.set_xlabel('DAC pedestal voltage [mV]', size=16)
                
                return f

        return params, cell_stack

    @staticmethod
    def getSampleCorrelation(data, lab, sampl, sampl_interval=1, transfer_bank=None, mean_subtract=True, from_file=False):
        
        all_sums=[]
        all_subs=[]

        if not isinstance(lab, list):
            lab=[lab]

        for l in lab:
            corr_add = []
            corr_sub = []

            if from_file:
                '''data imported from flat text file has different array shape'''
                for i in range(0,len(data), 1024):       
                    d = data[i:(i+1024),l]

                    if mean_subtract:
                        d = d-np.mean(d)
            
                    for k in range(128, 1024-sampl_interval): #start at 128 case unwrapping issues in firmware
                        if transfer_bank == 0  and (k % 128) == sampl and (k % 256) < 128:
                            v_samp_0 = d[k]
                            v_samp_1 = d[k+sampl_interval]
                            corr_add.append(v_samp_0 + v_samp_1)
                            corr_sub.append(v_samp_0 - v_samp_1)
                    
                        elif transfer_bank == 1  and (k % 128) == sampl and (k % 256) >= 128:
                            v_samp_0 = d[k]
                            v_samp_1 = d[k+sampl_interval]
                            corr_add.append(v_samp_0 + v_samp_1)
                            corr_sub.append(v_samp_0 - v_samp_1)

                        elif (k % 128) == sampl and transfer_bank==None:
                            v_samp_0 = d[k]
                            v_samp_1 = d[k+sampl_interval]
                            corr_add.append(v_samp_0 + v_samp_1)
                            corr_sub.append(v_samp_0 - v_samp_1)

            else:
                for i in range(len(data)):       
                    d = data[i,l,:]
                    if mean_subtract:
                        d = d-np.mean(d)

                    for k in range(128, 1024-sampl_interval):
                        if (k % 128) == sampl:

                            v_samp_0 = d[i][k]
                            v_samp_1 = d[i][k+sampl_interval]

                            corr_add.append(v_samp_0 + v_samp_1)
                            corr_sub.append(v_samp_0 - v_samp_1)         
   
            all_sums.append(corr_add)
            all_subs.append(corr_sub)

        return all_sums, all_subs


if __name__ == '__main__':

    run_options = {'log'      : 'log data to file [num_events, filename]',
                   'pedestal' : 'take pedestal data',
                   'scope'    : 'plot some data in real-time like a scope',
                   'lin'      : 'do a DC pedestal scan',
                   }

    import matplotlib.pyplot as plt
    import sys

    plt.ion()
    
    dev=SurfData()

    if len(sys.argv) < 2:
        print 'doing nothing'
        print 'here are your options:'
        print
        for key in run_options:
            print '  argument:', key, '   ::', run_options[key]
    
    elif sys.argv[1] == 'log':
        if len(sys.argv) == 4:
            num_events = int(sys.argv[2])
            filename = sys.argv[3]

            dev.log(num_events, filename=filename)

    elif sys.argv[1] == 'pedestal':
        dev.pedestalRun()
    
    elif sys.argv[1] == 'lin':
        if len(sys.argv) == 5:
            #2 = DAC start
            #3 = DAC stop
            #4 = DAC interval
            dev.pedestalScan(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        
        else:
            dev.pedestalScan()
    
    elif sys.argv[1] == 'scope':
        
        refresh = 0.1
        
        if len(sys.argv) == 3:
            lab = [int(sys.argv[2])]

        elif len(sys.argv) == 4:
            lab = range(int(sys.argv[2]),int(sys.argv[3]),1)

        else:
            lab = range(12)
        
        fig=plt.figure(1)

        while(1):
            plt.clf()

            d=dev.log(1, save=False)

            for i in lab:
                plt.plot(d[0][i], 'o--', ms=2, label='LAB{}'.format(i))

            #plt.legend()
            plt.pause(refresh)

    else:
        print 'doing nothing'
                 

