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


# linear calibration for mcp delay time difference -> position 
MCP_CAL_X = 1.29
MCP_CAL_Y = 1.31



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

    @classmethod
    def flattened_header_labels( cls ) :
        return [ 'tacc', 'nsteps',
                 'w_-', 'w_+', 'w_c',
                 'phase_-', 'phase_+', 'phase_c',
                 'amps_-', 'amps_+', 'amps_c',
                 'loops_-', 'loops_+', 'loops_c',
                 'lengths_-', 'lengths_+', 'lengths_c' ]


    


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
        
        # The following arrays are computed for each event. from these next 3 arrays
        # all the information can be computed. 

        # x1, x2, y1, y2 referenced to the mcp hit 
        self.delay_times = np.zeros( ( buf_size, 4 ) )

        # mcp hit referenced to penning eject, AKA the TOF
        self.tofs = np.zeros( buf_size )
        
        # absolute timestamp of the mcp hit 
        self.timestamps = np.zeros( buf_size )
        self.timestamp_diffs = np.zeros( buf_size )
        
        # this is the num_penning_ejects when the data is recorded.
        self.penning_eject_indices = np.zeros( buf_size ) 

        # these are either None if the cut is to be skipped (thus saving time),
        # or a list [ lower, upper ] which specifies the lower and upper bound of
        # the cut.
        
        self.tof_cut = None
        self.radius_cut = None 
        self.sum_x_cut = None
        self.sum_y_cut = None
        self.diff_xy_cut = None

        
        # these can be computed given cuts and data, so they aren't saved 
        self.mcp_positions = np.zeros( ( buf_size, 2 ) )
        self.radii = np.zeros( buf_size )
        self.angles = np.zeros( buf_size ) 
        self.cut_data_indices = np.zeros( buf_size, dtype = int )

        # x - y 
        self.diff_xy = np.zeros( buf_size )

        # x1 + x2, y1 + y2 
        self.sums = np.zeros( ( buf_size, 2 ) )

        
    # def save( self, path ) :
    #     with open( path, 'wb' ) as f :
    #         self.all_data.tofile( f )      


    def set_cuts( self, tof_cut = 0, radius_cut = 0,
                  sum_x_cut = 0, sum_y_cut = 0,
                  diff_xy_cut = 0 ) :

        if tof_cut != 0 :
            self.tof_cut = tof_cut
            
        if radius_cut != 0 :
            self.radius_cut = radius_cut
            
        if sum_x_cut != 0 :
            self.sum_x_cut = sum_x_cut
            
        if sum_y_cut != 0 :
            self.sum_y_cut = sum_y_cut
            
        if diff_xy_cut != 0 :
            self.diff_xy_cut = diff_xy_cut 



    @classmethod
    def load( cls, path ) :

        
        
        with open( path, 'r' ) as f :

            header = [ next( f ).rstrip( '\n' ).split( '\t' )[1] for i in range( 6 ) ] 
            
            next( f )

            tabor_params_arr = np.array( [ float( next( f ).rstrip( '\n' ).split( '\t' )[1] )
                                           for i in range( 17 ) ]  )
            
            next( f )  # newline
            next( f )  # header 

            tmp = np.loadtxt( f, delimiter = '\t' ).T

            num_events = len( tmp.T ) 
            
            ret = cls( buf_size = num_events ) 
            ret.num_events = num_events 
            
            ret.Z = int( header[0] )
            ret.A = int( header[1] ) 
            ret.date_str = header[2]
            ret.duration = float( header[3] )
            ret.num_penning_ejects = float( header[4] )
            ret.num_mcp_hits = float( header[5] )

            ret.tabor_params = TaborParams.unflatten( tabor_params_arr ) 
            
            ret.delay_times = tmp[0:4].T
            ret.tofs = tmp[4]
            ret.timestamps = tmp[5]
            ret.penning_eject_indices = tmp[6]

            ret.num_events_prev = 0
            ret.num_cut_data = 0
            
        ret.compute_mcp_positions()
        ret.compute_timestamp_differences() 
        ret.compute_polar()
        ret.compute_sums()
        ret.compute_diff_xy() 
        ret.apply_cuts()
        
        return ret 
            
   



    
    @classmethod
    def load_from_lmf( self ) :
        pass
    
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

                                
    def compute_mcp_positions( self ) :
        x1, x2, y1, y2 = self.delay_times[ self.num_events_prev : self.num_events ].T
        mcp_pos = self.mcp_positions[ self.num_events_prev : self.num_events ].T
        mcp_pos[0] =  0.5 * MCP_CAL_X * 1e3 * ( x1 - x2 )
        mcp_pos[1] =  0.5 * MCP_CAL_Y * 1e3 * ( y1 - y2 ) 

        

    def compute_timestamp_differences( self ) :

        if self.num_events == 0 :
            return

        # handle fencepost 
        if self.num_events_prev == 0 :
            self.timestamp_diffs[ self.num_events_prev : self.num_events - 1 ] = (
                np.ediff1d( self.timestamps[ self.num_events_prev : self.num_events ] ) )

        else :
            self.timestamp_diffs[ self.num_events_prev - 1 : self.num_events - 1 ] = (
                np.ediff1d( self.timestamps[ self.num_events_prev - 1 : self.num_events ] ) )

        
            
                             
    def compute_sums( self ) :
        x1, x2, y1, y2 = self.delay_times[ self.num_events_prev : self.num_events ].T

        sum_x, sum_y = self.sums[ self.num_events_prev : self.num_events ].T

        sum_x[:] = x1 + x2
        sum_y[:] = y1 + y2 
        
    
    def compute_diff_xy( self ) :
        x, y = self.mcp_positions[ self.num_events_prev : self.num_events ].T
        self.diff_xy[ self.num_events_prev : self.num_events ] = x - y
    
    
    # def compute_timestamep( self ) :
    #     pass

    
    # apply cuts to the candidates found in process_candidates and store the results.
    def apply_cuts( self ) :

        if not self.is_live :
            self.reset_cuts() 

        # detect request for cut reset 
        if self.num_cut_data == 0 :
            start_idx = 0
        else :
            start_idx = self.num_events_prev 
        
        radii = self.radii[ start_idx : self.num_events ]
        tofs = self.tofs[ start_idx : self.num_events ]
        sum_x, sum_y = self.sums[ start_idx : self.num_events ].T
        diff_xy = self.diff_xy[ start_idx : self.num_events ] 

        # data that cuts will be applied to 
        cut_arrays = [ radii, tofs, sum_x, sum_y, diff_xy ]

        # cuts to be applied 
        cuts = [ self.radius_cut, self.tof_cut,
                 self.sum_x_cut, self.sum_y_cut, self.diff_xy_cut ]

        # this start off as all 1s, and be set to 0 for each data point that
        # didn't satisfy each of the above cuts.
        mask = np.ones( self.num_events - start_idx, dtype = bool ) 

        # apply each cut sequentially.
        for i in range( len( cuts ) ) :

            cut = cuts[i]

            # skip cut if not specified 
            if cut is None :
                continue

            # otherwise set to 0 where the current cut_array is not satisfied
            # by the cut.
            cut_array = cut_arrays[i]
            mask &= ( cut_array >= cut[0] ) & ( cut_array <= cut[1] )

        indices = np.where( mask )[0] + start_idx
        num_added_cut_data = len( indices ) 
        
        self.cut_data_indices[ self.num_cut_data
                               : self.num_cut_data + num_added_cut_data ] = indices

        self.num_cut_data += num_added_cut_data

        

    def reset_cuts( self ) :
        self.num_cut_data = 0
        self.num_events_prev = 0 
        

    def compute_polar( self ) :
        
        centered_mcp_positions = ( self.mcp_positions[ self.num_events_prev : self.num_events ]
                                   - mcp_center_coords  )
        radii = np.linalg.norm( centered_mcp_positions, axis = 1 )
        angles = np.degrees( np.arctan2( centered_mcp_positions[:,1],
                                        centered_mcp_positions[:,0] ) )

        self.radii[ self.num_events_prev : self.num_events ] = radii
        self.angles[ self.num_events_prev : self.num_events ] = angles




        

        
empty_cpt_data = CPTdata( 0 ) 
