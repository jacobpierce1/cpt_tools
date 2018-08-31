import config 
import ctypes 
import os 

import numpy as np


code_path = os.path.abspath( os.path.dirname( __file__ ) )
_dll_path = code_path + '\Load_big_tabor\Debug\Load_big_tabor.dll' # '\Load_big_tabor.dll'
print( _dll_path ) 


class TaborParams( object ) :

    def __init__( self, tacc, nsteps, freqs, phases, amps, loops, lengths ) :
        self.tacc = tacc
        self.nsteps = nsteps
        self.freqs = freqs
        self.phases = phases
        self.amps = amps
        self.loops = loops
        self.lengths = lengths

        
    def flatten( self ) :
        ret = np.zeros( 17 )
        ret[0] = self.tacc
        ret[1] = self.nsteps

        data = [ self.freqs, self.phases, self.amps, self.loops, self.lengths ]
        for i in range(5) :
            ret[ 2 + i*3 : 2 + (i+1) * 3 ] = data[i]

        return ret 

    
    @classmethod
    def unflatten( cls, data ) :
        tacc = data[0]
        nsteps = data[1]
        return cls( tacc, nsteps, * data[2:].reshape(5,3) )
        

    

class Tabor( object ) : 
    
    def __init__( self ) : 
        if config.USE_TABOR : 
            print( 'INFO: loading tabor dll: ', _dll_path ) 
            self.dll = ctypes.CDLL ( _dll_path )
            types = [ ctypes.c_int ] * 2 + [ ctypes.c_double ] * 9 +  [ ctypes.c_int] * 6
            self.dll.load_tabor.argtypes = types
           
    # plus, minus, cyclotron
    def load_params( self, tabor_params ) : 
        if not config.USE_TABOR : 
            print('INFO: conf.USE_TABOR is 0' )
            return 
            
        args = ( tabor_params.tacc, tabor_params.nsteps,
                 * tabor_params.freqs, * tabor_params.phases,
                 * tabor_params.amps, * tabor_params.loops, * tabor_params.lengths )

        self.dll.load_tabor( *args )
        
