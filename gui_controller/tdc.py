# this is a class written for general usage of the TDC.
# there is no phase-imaging related processing here, that is 
# handled in tdc_analysis_mgr.py. this class handles all 
# communication with the TDC and maintains a  buffer 
# as well as operations for interacting with this buffer.

import controller_config

import numpy as np
import ctypes 
import time 
import atexit
import collections 
import sys
import os 

_max_tdc_buf_size = 2**16

code_path = os.path.abspath( os.path.dirname( __file__ ) )
os.chdir( code_path ) 
_dll_path = code_path + '\hptdc_driver_3.4.3_x86_c_wrap.dll'
print( 'INFO: loading TDC dll: ', _dll_path ) 
fake_data_path = os.path.join( code_path, '..', 'debug', 'test_data_tabor_on.npy' )

SAVE_FAKE_DATA = 0


# falling_transition_mask = 2**31 
# rising_transition_mask = 2**31 + 2**30 


# amount of time in micro-seconds represented by one rollover.
# each rollover is an absence of hits on any of the TDC channels for this amount of time. 
ROLLOVER_DURATION = 512  


rising_mask = 3
falling_mask = 2
rollover_mask = 2**28
channel_mask = np.sum( 2 ** np.arange( 24, 31, dtype = 'int' ) )
time_mask = np.sum( 2 ** np.arange( 0, 24, dtype = 'int' ) )
group_mask = np.sum( 2 ** np.arange( 24, 32, dtype = 'int' ) )



class TDC( object ) :
    
    def __init__( self ) :
        
        # load the TDC c API
        if not controller_config.USE_FAKE_DATA :
            self.tdc_driver_lib = ctypes.CDLL( _dll_path )
            
            self.tdc_ctx = self.tdc_driver_lib.TDCManager_New()
            
            # connect to the tdc and start DAQ
            self.tdc_driver_lib.TDCManager_Init( self.tdc_ctx )
            self.tdc_driver_lib.TDCManager_Start( self.tdc_ctx )
                
            # verify that the TDC is functioning as expected
            # state = self.get_state()
            # print( 'state: ', state )
            self.collecting_data = 1
                
            # register this function to be called when the program 
            # terminates
            atexit.register( self.disconnect )

        else :
            self.collecting_data = 1 
            
        # hits from the TDC are stored here prior to processing. 
        self.data_buf = np.zeros( _max_tdc_buf_size, dtype = 'uint32' )

        # the data in data_buf is processed and inserted into these arrays 
        self.channels = np.zeros( _max_tdc_buf_size, dtype = 'uint8' )
        self.times = np.zeros( _max_tdc_buf_size, dtype = 'int32' )
        self.timestamps = np.zeros( _max_tdc_buf_size, dtype = float )
        self.rollovers = np.zeros( _max_tdc_buf_size, dtype = 'uint8' )
        self.groups = np.zeros( _max_tdc_buf_size, dtype = 'uint8' )

        self.start_time = time.time()
        self.duration = 0

        # increment if the rollover counter resets. that will occur in a session of more than 143
        # minutes. it's not a problem, just needs to be accounted for here.
        self.num_rollover_loops = 0 
        
        self.num_data_in_buf = 0
                
                
    def disconnect( self ) : 
        print( 'INFO: deleting tdc_ctx' )
        if not controller_config.USE_FAKE_DATA : 
            self.tdc_driver_lib.TDCManager_CleanUp( self.tdc_ctx )
            self.tdc_driver_lib.TDCManager_Delete( self.tdc_ctx )
        self.collecting_data = 0

        
    def toggle( self ) :
        if self.collecting_data :
            self.pause()
        else :
            self.resume()
        return self.collecting_data
                
        
    # pause data collection
    def pause( self ) :
        if not controller_config.USE_FAKE_DATA : 
            self.tdc_driver_lib.TDCManager_Pause( self.tdc_ctx )
        self.collecting_data = 0

        
    def resume( self ) :
        if not controller_config.USE_FAKE_DATA : 
            self.tdc_driver_lib.TDCManager_Continue( self.tdc_ctx )
        # self.start_time = time.time()
        self.collecting_data = 1

    def clear( self ) :
        # if not controller_config.USE_FAKE_DATA :
        #     self.tdc_driver_lib.TDCManager_ClearBuffer( self.tdc_ctx )
        self.start_time = time.time() 
        self.num_data_in_buf = 0
        self.prev_rollover_count = 0
        self.num_rollover_loops = 0 
        
        
    def get_state( self ) :
        state = -1
        if not controller_config.USE_FAKE_DATA : 
            state = self.tdc_driver_lib.TDCManager_GetState( self.tdc_ctx )
        return state
                
    def read( self ) :

        if not controller_config.USE_TDC :
            return 
        
        if controller_config.BENCHMARK :
            start = time.time()
            
        if SAVE_FAKE_DATA : 
            time.sleep(5)
            
        if controller_config.USE_FAKE_DATA :
            # print( self.collecting_data )
            
            if self.collecting_data : 
                self.data_buf = np.load( fake_data_path )
                self.num_data_in_buf = np.where( self.data_buf == 0 )[0][0]

        else : 
            # pass
            self.num_data_in_buf = self.tdc_driver_lib.TDCManager_Read( 
                self.tdc_ctx,
                self.data_buf.ctypes.data_as( ctypes.POINTER( ctypes.c_uint ) ), 
                _max_tdc_buf_size );
                
            # print( self.data_buf )
            # print( self.num_data_in_buf )

        if self.num_data_in_buf == 0 :
            return
        
        tmp = self.data_buf[ : self.num_data_in_buf ]
        
        self.channels[ : self.num_data_in_buf ] = self.get_channels( tmp ) 
        self.times[ : self.num_data_in_buf ] = self.get_times( tmp ) 
        self.rollovers[ : self.num_data_in_buf ] = self.get_rollovers( tmp ) 
        self.groups[ : self.num_data_in_buf ] = self.get_groups( tmp ) 

        # print( 'num rollovers: ', np.sum( self.rollovers[ : self.num_data_in_buf]))
        
        # self.compute_timestamps() 

        rollovers = self.rollovers[ : self.num_data_in_buf ] 
        
        rollover_start, rollover_end = self.get_rollover_boundaries( rollovers )

        self.sort_data( rollover_start, rollover_end )
        self.compute_timestamps( rollover_start, rollover_end )
        self.update_time()
        # print( self.duration )
        
        if controller_config.BENCHMARK :
            end = time.time()
            diff = ( end - start ) * 1000 
            print( 'BENCHMARK: read %d hits in %f ms'
                   % ( self.num_data_in_buf, diff ) )
            print( 'Num rollovers: %d ' % np.sum( self.rollovers[ : self.num_data_in_buf ] ))
            # print( 'State: %d' % self.get_state() )
            # print( 'num data in buf', self.num_data_in_buf )
        
        if SAVE_FAKE_DATA : 
            print( 'INFO: saving fake tdc data.' )
            
            out = np.vstack( ( self.channels[ : self.num_data_in_buf ],
                self.rollovers[ : self.num_data_in_buf ],
                self.times[ : self.num_data_in_buf ] ) )
            np.savetxt( 'debug_tdc_data.tsv', out, delimiter = '\t' )
            sys.exit(0) 

        return self.num_data_in_buf



    
    # input: mask stating whether each hit in the array is a rollover or not (1 or 0 respectively)
    # 
    # output: returns two equal-size arrays, 'start' and 'end', such that the range start[i] : end[i]
    # are NOT hits. so start gives the indices of each block of non-rollover data, and end gives
    # the indices of the first rollover in any sequence of consecutive rollovers.
    # 
    # for example, suppose the rollover mask looks like this:    0 1 1 1 0 0 0 1 1 0 0 0 0
    # let s = start, e = end. then the start / end indices are:  s e     s     e   s     e
    #
    # thus, start = ( 0, 4, 9 ) and end = ( 1, 7, 12 ).
    # 
    # note that if the first hit is not a rollover or the last hit is not a rollover (both of
    # wich are the case in the above example), then start or end is designated accordingly.
    
    def get_rollover_boundaries( self, rollovers ) :

        tmp = np.roll( rollovers, 1 )
        tmp[0] = rollovers[0]

        start = np.where( rollovers < tmp )[0]
        end = np.where( rollovers > tmp )[0]

        if not rollovers[0] :
            start = np.insert( start, 0, 0 ) 

        if not rollovers[-1] :
            end = np.append( end, len( rollovers ) ) 

        return start, end

    
    
    # the data is only partially sorted when it comes out of the TDC.
    # complete the sorting between each group of consecutive rolloovers.
    # @jit
    def sort_data( self, rollover_start, rollover_end ) :

        num_data = self.num_data_in_buf

        rollovers = self.rollovers[ : num_data ]
        channels = self.channels[ : num_data ]
        times =  self.times[ : num_data ]
        
        if controller_config.PRINT_TDC_DATA : 
            print( 'rollovers: ')
            print( rollovers )
            print( '\nchannels:' )
            print( channels ) 
            print( '\ntimes:')
            print( times )
            print( '\nrollover start and end:' ) 
            print( rollover_start, rollover_end ) 

        # print( rollovers )
        # print( rollover_start )
        # print( rollover_end )

        # sys.exit(0 ) 
        
        for i in range( len( rollover_start ) ) :

            start = rollover_start[i]
            end = rollover_end[i]

            # print( start ) 

            # print( times[ start - 1 : end + 1 ] )
            
            sort_indices = start + np.argsort( times[ start : end ] )
            times[ start : end ] = times[ sort_indices ]
            channels[ start : end ] = channels[ sort_indices ]

            # print( times[ start - 1 : end + 1 ] )


            
    # set the absolute timestamp of aech event.

    def compute_timestamps( self, rollover_start, rollover_end ) :

        if len( rollover_start ) == 0 :
            return
    
        num_data = self.num_data_in_buf 
        times = self.times[ : num_data ]
        # timestamps = self.timestamps[ : num_data ] 

        # this array will contain the absolute time of the rollover corresponding to each
        absolute_rollover_times = np.zeros( num_data )

        for i in range( len( rollover_start ) ) :

            start = rollover_start[i]
            end = rollover_end[i]

            if start > 0 :
                rollover_count = times[ start - 1 ]
                if rollover_count < self.prev_rollover_count :
                    self.num_rollover_loops += 1
            else :
                rollover_count = self.prev_rollover_count
                # rollover_idx = self.prev_rollover_idx 
            
            # note that times[ start ] is the rollover count.
            absolute_rollover_times[ start : end ] = (
                ( self.num_rollover_loops * ( 2 ** 24 ) + rollover_count ) * ( 2 **24 ) ) 

        # now compute the absolute time of each hit by adding its time to the associated absolute
        # rollover time. the timestamps of the rollovers will be nonsense, that could be corrected
        # if one so desired but there is no reason to preserve them once they have been used for
        # sorting and absolute time computation.
        self.timestamps[ : num_data ] = ( absolute_rollover_times + times ) * 25 / 1e6

        self.prev_rollover_count = rollover_count
        
    def reset( self ) :
        self.num_data_in_buf = 0
        self.duration = 0 
        self.start_time = time.time() 
        
    def get_channels( self, hits ) :
        return np.right_shift( np.bitwise_and( hits, channel_mask ), 24 )

    def get_times( self, hits ) :
        return np.bitwise_and( hits, time_mask )

    def get_rollovers( self, hits ) :
        return np.bitwise_and( hits, rollover_mask ) == rollover_mask

    def get_groups( self, hits ) :
        # return np.right_shift( np.bitwise_and( hits, group_mask ), 24 ) == 0
        return np.right_shift( hits, 24 ) == 0

    def get_rising( self, hits ) :
        return np.right_shift( hits, 30 ) == rising_mask

    def get_falling( self, hits ) :
        return np.right_shift( hits, 30 ) == falling_mask 
        
            
    def print_bin( self, x ) :
        print( format( x, '#034b' ) )

    def update_time( self ) :
        if self.collecting_data : 
            self.duration = time.time() - self.start_time 
