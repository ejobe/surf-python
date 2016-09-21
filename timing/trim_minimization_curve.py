import scipy.interpolate as spint
import numpy

##########################################
## original values used 7/2016:
##
##dt_fast        = [-40., -20., -5., -3.5, -2., -0.5] #ps fast
##trim_adj_fast  = [50, 25, 15, 7, 4, 2]
##
##dt_slow        = [70., 40., 20., 5., 3.5, 2., 1., 0.5] #ps slow
##trim_adj_slow  = [-80, -50, -25, -15, -11, -7, -4, -2]    

##########################################
## more linear curve:
##
##dt_fast        = [-100,-40., -20., -5., -3.5, -2., -0.5, 0.0] #ps fast
##trim_adj_fast  = [140, 50, 25, 10, 7, 4, 2, 0]
##
##dt_slow        = [120, 70., 40., 20., 5., 3.5, 2., 1., 0.5, 0.0] #ps slow
##trim_adj_slow  = [-140, -80, -50, -25, -10, -7, -4, -3, -2, 0]    

dt_slow        = [180, 120, 70., 40., 20., 7., 3.5, 2., 1., 0.2, 0.0] #ps slow
trim_adj_slow  = [-200, -110, -50, -20, -10, -6, -4, -3, -2, -1, 0] 
  
dt_fast = [dt*-1 for dt in dt_slow]
trim_adj_fast = [trim*-1 for trim in trim_adj_slow]

trim_adj_slow = [trim*2 for trim in trim_adj_slow] #sitting on an exponential curve

trim_adj_fast_lut =  numpy.arange(0, max(trim_adj_fast))
trim_adj_slow_lut =  numpy.arange(min(trim_adj_slow),0)

dt_fast_lut = spint.interp1d(trim_adj_fast[::-1], dt_fast[::-1], kind='linear', axis=0)(trim_adj_fast_lut)
dt_slow_lut = spint.interp1d(trim_adj_slow, dt_slow, kind='linear', axis=0)(trim_adj_slow_lut)

minimizer_trim_adj_lut = numpy.hstack(( trim_adj_slow_lut, trim_adj_fast_lut))
minimizer_dt_diff_lut  = numpy.hstack(( dt_slow_lut, dt_fast_lut ))

##########################################
if __name__=='__main__':

    import matplotlib.pyplot as plt

    #plt.plot(dt_fast, trim_adj_fast, 'o', color='red')
    plt.plot(dt_fast_lut, trim_adj_fast_lut, '--', color='red')

    #plt.plot(dt_slow, trim_adj_slow, 'o--')
    plt.plot(dt_slow_lut, trim_adj_slow_lut, '--', color='black')
    
    plt.plot(minimizer_dt_diff_lut, minimizer_trim_adj_lut, 'o', color='blue', ms=2)
    plt.grid()

    plt.xlabel('picoseconds from nominal')
    plt.ylabel('adjustment to trim dac (counts)')
    
    plt.show()
