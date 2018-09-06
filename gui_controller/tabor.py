import controller_config 
import ctypes 
import os 

import numpy as np
from cpt_tools import TaborParams

code_path = os.path.abspath( os.path.dirname( __file__ ) )
_dll_path = code_path + '\Load_big_tabor\Debug\Load_big_tabor.dll' # '\Load_big_tabor.dll'
print( _dll_path ) 

    

class Tabor( object ) : 
    
    def __init__( self ) : 
        if controller_config.USE_TABOR : 
            print( 'INFO: loading tabor dll: ', _dll_path ) 
            self.dll = ctypes.CDLL ( _dll_path )
            types = [ ctypes.c_int ] * 2 + [ ctypes.c_double ] * 9 +  [ ctypes.c_int] * 6
            self.dll.load_tabor.argtypes = types
           
    # plus, minus, cyclotron
    def load_params( self, tabor_params ) : 
        if not controller_config.USE_TABOR : 
            print('INFO: conf.USE_TABOR is 0' )
            return 
        
        args = ( tabor_params.tacc, tabor_params.nsteps,
                 * tabor_params.freqs, * tabor_params.phases,
                 * tabor_params.amps, * tabor_params.loops, * tabor_params.lengths )

        self.dll.load_tabor( *args )
        
