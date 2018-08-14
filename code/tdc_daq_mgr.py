# this is a class written for general usage of the TDC.
# there is no phase-imaging related processing here, that is 
# handled in tdc_analysis_mgr.py. this class handles all 
# communication with the TDC and maintains a  buffer 
# as well as operations for interacting with this buffer.

import config

import numpy as np
import ctypes 
import time 
import atexit
import collections 
import sys


_dll_path = 'hptdc_driver_3.4.3_x86_c_wrap.dll'
_max_tdc_buf_size = 2**14
# fake_data_path = 'test_data_tabor_on_with_rising.npy' 
fake_data_path = 'test_data_tabor_on.npy'  

SAVE_FAKE_DATA = 0 


# falling_transition_mask = 2**31 
# rising_transition_mask = 2**31 + 2**30 

rising_mask = 3
falling_mask = 2
rollover_mask = 2**28
channel_mask = np.sum( 2 ** np.arange( 24, 31, dtype = 'int' ) )
time_mask = np.sum( 2 ** np.arange( 0, 24, dtype = 'int' ) )
group_mask = np.sum( 2 ** np.arange( 24, 32, dtype = 'int' ) )



class TDC_Mgr( object ) :
    def __init__( self ) : 
        
        # load the TDC c API
        if not config.USE_FAKE_DATA :
            self.tdc_driver_lib = ctypes.CDLL( _dll_path )
            
            self.tdc_ctx = self.tdc_driver_lib.TDCManager_New()
            
            # connect to the tdc and start DAQ
            self.tdc_driver_lib.TDCManager_Init( self.tdc_ctx )
            # self.tdc_driver_lib.TDCManager_ClearBuffer( self.tdc_ctx )
            self.tdc_driver_lib.TDCManager_Start( self.tdc_ctx )
                
            # verify that the TDC is functioning as expected
            state = self.get_state()
            print( 'state: ', state )
            self.collecting_data = 1
                
            # register this function to be called when the program 
            # terminates
            atexit.register( self.disconnect )
                
        # hits from the TDC are stored here sequentially with no processing.
        self.data_buf = np.zeros( _max_tdc_buf_size, dtype = 'uint32' )
        self.channels = np.zeros( _max_tdc_buf_size, dtype = 'uint8' )
        self.times = np.zeros( _max_tdc_buf_size, dtype = 'int32' )
        self.rollovers = np.zeros( _max_tdc_buf_size, dtype = bool )
        self.groups = np.zeros( _max_tdc_buf_size, dtype = bool )
        
        self.num_data_in_buf = 0
                
                
    def disconnect( self ) : 
        print( 'deleting tdc_ctx' )
        self.tdc_driver_lib.TDCManager_CleanUp( self.tdc_ctx )
        self.tdc_driver_lib.TDCManager_Delete( self.tdc_ctx )

        
    # pause data collection
    def pause( self ) :
        self.tdc_driver_lib.TDCManager_Pause( self.tdc_ctx )
        self.collecting_data = 0

        
    def resume( self ) : 
        self.tdc_driver_lib.TDCManager_Continue( self.tdc_ctx )
        self.collecting_data = 1

        
    def get_state( self ) :
        state = self.tdc_driver_lib.TDCManager_GetState( self.tdc_ctx )
        return state
                
    def read( self ) :

        if config.USE_FAKE_DATA :
            self.data_buf = np.load( fake_data_path )
            self.num_data_in_buf = np.where( self.data_buf == 0 )[0][0]

        else : 
            self.num_data_in_buf = self.tdc_driver_lib.TDCManager_Read( 
                self.tdc_ctx,
                self.data_buf.ctypes.data_as( ctypes.POINTER( ctypes.c_uint ) ), 
                _max_tdc_buf_size );
        
        # for i in range( self.num_data_in_buf ) :
        #       print( bin( self.data_buf[i+3] ) )
        
        tmp = self.data_buf[ : self.num_data_in_buf ]
        
        self.channels[ : self.num_data_in_buf ] = self.get_channels( tmp ) 
        self.times[ : self.num_data_in_buf ] = self.get_times( tmp ) 
        self.rollovers[ : self.num_data_in_buf ] = self.get_rollovers( tmp ) 
        self.groups[ : self.num_data_in_buf ] = self.get_groups( tmp ) 
        
        return self.num_data_in_buf

        
    def reset( self ) :
        self.num_data_in_buf = 0 

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
