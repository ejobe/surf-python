#############################################################
'''
python module to handle Surf calibration data

authors: Patrick Allison (allison.122@osu.edu)
         Eric Oberla (ejo@uchicago.edu)
'''
#############################################################

import json
from utils.surf_constants import *

cal = {}

try:
    with open(calibration_filename,"r") as infile:
        cal = json.load(infile)

except IOError:
    print 'calibration file does not exist'
 
def save_vadjp(dna, vadjp):
    for key in cal:
        if cal[key]['DNA'] == dna:
            print "Saving VadjP for board %s" % key
            board_cal = cal[key]
            board_cal['vadjp'] = vadjp
            with open(calibration_filename,"w") as outfile:
                json.dump(cal, outfile)
            return
    print "No board found with DNA %x" % dna

def read_vadjp(dna):
    for key in cal:
        if cal[key]['DNA'] == dna:
            board_cal = cal[key]
            if 'vadjp' in board_cal:
                return board_cal['vadjp']
            else:
                return None
    return None
    
def save_vadjn(dna, vadjn):
    for key in cal:
        if cal[key]['DNA'] == dna:
            print "Saving VadjN for board %s" % key
            board_cal = cal[key]
            board_cal['vadjn'] = vadjn
            with open(calibration_filename,"w") as outfile:
                json.dump(cal, outfile)
            return
    print "No board found with DNA %x" % dna            
    
def read_vadjn(dna):
    for key in cal:
        if cal[key]['DNA'] == dna:
            board_cal = cal[key]
            if 'vadjn' in board_cal:
                return board_cal['vadjn']
            else:
                return None
    return None

def save_vtrimfb(dna, vtrimfb):
    for key in cal:
        if cal[key]['DNA'] == dna:
            print "Saving Vtrimfb for board %s" % key
            board_cal = cal[key]
            board_cal['vtrimfb'] = vtrimfb
            with open(calibration_filename,"w") as outfile:
                json.dump(cal, outfile)
            return
    print "No board found with DNA %x" % dna            
    
def read_vtrimfb(dna):
    for key in cal:
        if cal[key]['DNA'] == dna:
            board_cal = cal[key]
            if 'vtrimfb' in board_cal:
                return board_cal['vtrimfb']
            else:
                return None
    return None

def save_pedestals(dna, pedestals):
    for key in cal:
        if cal[key]['DNA'] == dna:
            print "Saving pedestals for board %s..." % key
            board_cal = cal[key]
            board_cal['pedestals'] = pedestals
            with open(calibration_filename,"w") as outfile:
                json.dump(cal, outfile)
            return
    print "No board found with DNA %x" % dna            

def read_pedestals(dna):
    for key in cal:
        if cal[key]['DNA'] == dna:
            board_cal = cal[key]
            if 'pedestals' in board_cal:
                return board_cal['pedestals']
            else:
                return None
    return None

#############################################################
#add board by specifying board name ('serial') and dna
def add_board(serial, dna):
    cal[serial] = {}
    cal[serial]['DNA'] = dna
    with open(calibration_filename,"w") as outfile:
        json.dump(cal, outfile)

#############################################################
#check if board exists in cal file by specifying board name ('serial') and dna
def check_board(serial, dna):
    for key in cal:
        if key == serial:
            if cal[key]['DNA'] == dna:
                return True
            else:
                print 'board exists, but does not match device DNA'
                print 'trying re adding board to cal file'
                return None
    return False



    


