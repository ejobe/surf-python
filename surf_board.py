
import surf
import sys
import calibrations.surf_calibrations as surf_cal

#sys.path.insert(0, '/home/anita/astroparticlelab/')

def do(board):

    dev=surf.Surf()
    print 'identify:'
    dev.identify()
    print 'path:', dev.path
    dev.labc.run_mode(0)
    dev.labc.reset_fifo()
    dev.labc.reset_ramp()
    dev.labc.dll(15)
    
    dev.i2c.default_config()
    dev.clock(dev.internalClock)
    
    dev.labc.default()
    dev.set_phase(2)
    dev.labc.automatch_phab(15)

    if not surf_cal.check_board(board, dev.dna()):
        print 'adding board to calibration json file..'
        surf_cal.add_board(board, dev.dna())
    else:
        print 'cal file entry already exists for board: ', board

#    
#    if surf_cal.read_vadjn(dev.dna()) == None:
#        print 'scanning for Vadjn..'
#        vadjn = []
#        for i in range(12):
#            vadjn.append(dev.labc.autotune_vadjn(i))
#
#        surf_cal.save_vadjn(dev.dna(), vadjn)
#    
#    dev.labc.default()
#
#    if surf_cal.read_vadjp(dev.dna()) == None:
#        print 'scanning for Vadjp..'
#        vadjp = []
#        for i in range(12):
#            vadjp.append(dev.labc.autotune_vadjp(i))
#
#        surf_cal.save_vadjp(dev.dna(), vadjp)  
#    
    #re-initialize the lab4d register loading
    dev.labc.default()
    '''

    dev.labc.dll(15, mode=True)
    dev.status()

    return dev

if __name__ == '__main__':
            
    board = 'CANOES'

    if len(sys.argv) > 1:
        board = sys.argv[1]
        
    print '************************'
    print 'boarding SURFv5:', board
    print '************************'

    do(board)

