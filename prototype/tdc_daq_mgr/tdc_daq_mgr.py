# this is a class written for general usage of the TDC.
# there is no phase-imaging related processing here, that is 
# handled in tdc_analysis_mgr.py. this class handles all 
# communication with the TDC and maintains a  buffer 
# as well as operations for interacting with this buffer.


import numpy as np
import ctypes 
import time 
import atexit
import collections 


_dll_path = 'hptdc_driver_3.4.3_x86_c_wrap.dll'
_max_tdc_buf_size = 2**14


class TDC_Mgr( object ) : 

	def __init__( self ) : 
	
		# load the TDC c API 
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
		print( self.data_buf )
		self.num_data_in_buf = self.tdc_driver_lib.TDCManager_Read( 
			self.tdc_ctx, self.data_buf.ctypes.data_as( ctypes.POINTER( ctypes.c_uint ) ), 
				_max_tdc_buf_size );
		print( self.data_buf )
		
		for i in range( self.num_data_in_buf ) :
			print( bin( self.data_buf[i+3] ) )
		print( self.num_data_in_buf )
		return self.num_data_in_buf
			
	def clear_buf( self ) :
		self.num_data_in_buf = 0 
		
tdc_mgr = TDC_Mgr()
time.sleep(0.0)
tdc_mgr.read()