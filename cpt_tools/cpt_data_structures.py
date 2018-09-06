# this module provides two classes which contain all the relevant information
# required to process data obtained in the CPT. the live class is used for DAQ.

import numpy as np 
import dill
import time
# import config
import os
from datetime import datetime

import numpy as np 

from cpt_tools import ( z_to_element, element_to_z, DEFAULT_STORAGE_DIRECTORY,
                        lock_file, unlock_file, mcp_center_coords, cpt_header_key )




_default_buf_size = 2**22


# this translates in ascii codes to CPT. this will be written
# when files are saved and always verified to make sure the header
# is lined up correctly. this will prevent bugs which may arise if
# the file format is changed and someone tries to read an old file
# with an incompatible function, unless the new header is the same length
# as the old one.



class CPTexception( Exception ) :
    pass
    




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
        

    @classmethod
    def empty( cls ) :
        tmp = np.empty(17)
        tmp[:] = np.nan
        return cls.unflatten( tmp ) 

    


    


class CPTdata( object ) :

    def __init__( self, buf_size = _default_buf_size ) :

        # self.clear()
        # self.start_time = time.time()
        self.Z = np.nan
        self.A = np.nan
        self.tabor_params = TaborParams.empty()

        self.timestamp = time.time() 
        self.duration = 0 
        self.num_events = 0
        self.is_live = 0
        self.num_cut_data = 0
        
        self.num_penning_ejects = 0
        self.num_mcp_hits = 0
        self.num_events = 0
        
        self.all_data = np.zeros( (buf_size, 4) )

        # self.tofs = np.zeros( buf_size )
        # self.timestamps = np.zeros( buf_size )
        # self.mcp_positions = np.zeros( ( buf_size, 2 ) )
        
        self.tofs = self.all_data[:,0]
        self.timestamps = self.all_data[:,1]
        self.mcp_positions = self.all_data[:,2:]

        self.radii = np.zeros( buf_size )
        self.angles = np.zeros( buf_size ) 
        
        self.cut_data_indices = np.zeros( buf_size, dtype = int )
        
        self.tof_cut_lower = 0
        self.tof_cut_upper = 40

        self.r_cut_lower = -1
        self.r_cut_upper = 40

        
    # def save( self, path ) :
    #     with open( path, 'wb' ) as f :
    #         self.all_data.tofile( f )      

    @classmethod
    def load( cls, path ) :
        ret = cls( buf_size = 0 ) 

        num_tabor_params = 17
        # header_size = 2 + 3 + 17
        
        data = np.fromfile( path, float, -1 )
        
        # ret.Z = int( data[0] )
        # ret.N = int( data[1] )
        ret.Z = data[0]
        ret.A = data[1]
        ret.timestamp = data[2]
        ret.duration = data[3]
        ret.num_mcp_hits = int( data[4] )
        ret.num_penning_ejects = int( data[5] )
        ret.tabor_params = TaborParams.unflatten( data[ 6 : 6 + num_tabor_params ] )

        cpt_header = data[ 6 + num_tabor_params : 9 + num_tabor_params ]
        if not np.all( cpt_header == cpt_header_key ) :
            raise CPTexception( 'ERROR: the cpt header in %s does not match the cpt header key. the most likely source is that the file format has been changed and this file has the old format.' % path )

        all_data = data[ 9 + num_tabor_params : ]
        ret.all_data = all_data.reshape( len( all_data ) // 4, 4 ) 
        
        ret.tofs = ret.all_data[:,0]
        ret.timestamps = ret.all_data[:,1]
        ret.mcp_positions = ret.all_data[:,2:]
        
        ret.num_events = len( ret.tofs )
        # ret.num_cut_data = len( ret.cut_data ) 
        print( 'ret.num_events: ', ret.num_events ) 
        # ret.num_penning_ejects = 0
        # ret.num_mcp_hits = 0 

        ret.compute_polar()
        ret.apply_cuts()

        return ret

    
    # def load( self, path ) : 
    #     tmp_data = np.fromfile( path, float, -1 )
    #     self.duration = tmp_data[0]
    #     all_data = tmp_data[1:]
    #     self.all_data = all_data.reshape( len( all_data ) // 4, 4 ) 
        
    #     self.tofs = self.all_data[:,0]
    #     self.timestamps = self.all_data[:,1]
    #     self.mcp_positions = self.all_data[:,2:]

    #     self.num_events = len( self.tofs )
    #     self.num_penning_ejects = 0
    #     self.num_mcp_hits = 0 
    #     # self.num_penning_ejects = np.sum( np.where( self. == 6 ) )
    #     # self.num_mcp_hits = np.sum( np.where( self == 7 ) )

    #     self.compute_polar()
    #     self.apply_cuts()
        
    
    def set_tof_cut_lower( self, x ) :
        self.tof_cut_lower = x 

        
    def set_tof_cut_upper( self, x ) :
        self.tof_cut_upper = x 

    def set_r_cut_lower( self, x ) :
        self.r_cut_lower = x 
        
    def set_r_cut_upper( self, x ) :
        self.r_cut_upper = x 

    def apply_cuts( self ) :
        radius_mask = ( self.radii > self.r_cut_lower ) & ( self.radii < self.r_cut_upper )
        tof_mask = ( self.tofs > self.tof_cut_lower ) & ( self.tofs < self.tof_cut_upper ) 

        mask = radius_mask & tof_mask
        self.cut_data_indices = np.where( mask )[0]
        self.num_cut_data = len( self.cut_data_indices ) 
        

    # compute polar for all data. this function is implemented differently for the
    # live subclass so that only the radii that are yet to be computed
    # get computed on each iteration.
    def compute_polar( self ) :
        centered_mcp_positions = self.mcp_positions - mcp_center_coords 
        radii = np.linalg.norm( centered_mcp_positions, axis = 1 )
        angles = np.degrees( np.arctan2( centered_mcp_positions[:,1],
                                        centered_mcp_positions[:,0] ) )

        self.radii = radii
        self.angles = angles



        

        
empty_cpt_data = CPTdata( 0 ) 
