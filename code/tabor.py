import config 
import ctypes 
import os 

code_path = os.path.abspath( os.path.dirname( __file__ ) )
_dll_path = code_path + '\..\Load_big_tabor\Debug\Load_big_tabor.dll' # '\Load_big_tabor.dll'
print( _dll_path ) 

class Tabor( object ) : 
    
    def __init__( self ) : 
        if config.USE_TABOR : 
            self.dll = ctypes.CDLL ( _dll_path )
            types = [ ctypes.c_int ] * 2 + [ ctypes.c_double ] * 9 +  [ ctypes.c_int] * 6
            self.dll.load_tabor.argtypes = types
           
    # plus, minus, cyclotron
    def load_params( self, tacc, nsteps, freqs, phases, amps, loops, lengths ) : 
        if not config.USE_TABOR : 
            return 
            
        args = ( tacc, nsteps, *freqs, *phases, *amps, *loops, *lengths )
        self.dll.load_tabor( *args )
        
