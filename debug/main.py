import config
import tdc_daq_mgr
import phase_im_processing
import gui

import numpy as np 
import time 

USE_FAKE_DATA = 1 





tdc_mgr = tdc_daq_mgr.TDC_Mgr()
# time.sleep(5.0)
tdc_mgr.read()

ndata = 100 

for i in range(100 ) :
    tdc_mgr.print_bin( tdc_mgr.data_buf[i] ) 

print( tdc_mgr.data_buf[:ndata] )
print( tdc_mgr.num_data_in_buf ) 

print( tdc_mgr.channels[:ndata] ) 
print( tdc_mgr.times[:ndata] )
print( tdc_mgr.rollovers[:ndata] ) 

# time_mask = np.sum( 2 ** np.arange( 0, 24, dtype = 'int' ) )
# tdc_mgr.print_bin( time_mask )
# tdc_mgr.print_bin( 2198919763 )
# tdc_mgr.print_bin( tdc_mgr.get_times( 2198919763 ) )
# tdc_mgr.print_bin( 39448 ) 

# print( 'computing rising' )
# rising = tdc_mgr.get_rising( tdc_mgr.data_buf )
# print( rising )
# print( np.sum( rising ) )

# for i in range( 100 ) :
#     tdc_mgr.print_bin( tdc_mgr.data_buf[i] )
#     print( rising[i] ) 



processor = phase_im_processing.tdc_processor( tdc_mgr ) 
processor.extract_candidates() 



# tmp1 = np.zeros( 15000, dtype = 'uint32' )
# tmp2 = tdc_mgr.data_buf[ ~ rising ]
# tmp1[ : len(tmp2) ] = tmp2 

# print( tmp1 )

# np.save( 'test_data_tabor_on.npy', tmp1 ) 

# np.save( 'test_data_tabor_on', tdc_mgr.data_buf )
