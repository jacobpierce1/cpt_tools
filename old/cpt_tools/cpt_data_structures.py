# this module provides two classes which contain all the relevant information
# required to process data obtained in the CPT. the live class is used for DAQ.

import numpy as np 
import dill
import time
import config

from cpt_tools import z_to_element, element_to_z, tabor_params, DEFAULT_STORAGE_DIRECTORY



_default_buf_size = 2**22

MCP_CAL_X = 1.29
MCP_CAL_Y = 1.31

mcp_center_coords = np.array( [ -1.6, 3.0 ] )

class CPTdata( object ) :

    def __init__( self, buf_size = _default_buf_size ) :

        self.Z = np.nan
        self.N = np.nan
        
        # self.clear()
        # self.start_time = time.time()
        self.duration = 0 
        self.num_events = 0
        self.is_live = 0

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
        
        ret.Z = data[0]
        ret.N = data[1]
        ret.duration = data[2]
        ret.num_mcp_hits = data[3]
        ret.num_penning_ejects = data[4]
        ret.tabor_params = tabor.TaborParams.unflatten( data[ 5 : 5 + num_tabor_params ] )
        
        ret.all_data = data[ 5 + num_tabor_params : ].reshape( len( all_data ) // 4, 4 ) 
        
        ret.tofs = ret.all_data[:,0]
        ret.timestamps = ret.all_data[:,1]
        ret.mcp_positions = ret.all_data[:,2:]

        ret.num_events = len( ret.tofs )
        ret.num_penning_ejects = 0
        ret.num_mcp_hits = 0 
        # tmp.num_penning_ejects = np.sum( np.where( tmp. == 6 ) )
        # tmp.num_mcp_hits = np.sum( np.where( tmp == 7 ) )

        ret.compute_polar()
        ret.apply_cuts()

        # tmp.load( path ) 
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
        pass


    # # the sum of channels 0,1 and 2,3 should always add up to the same number.
    # # return 0 if the data does not satisfy this 
    # def satisfies_delay_sum_cut( self ) :
    #     pass


    # # check if tof of the data point falls in range of a tof 
    # def satisfies_tof_cut( self, tof ) :        
    #     if tof > self.tof_cut_lower and tof < self.tof_cut_upper :
    #         return 1
    #     return 0 

    
    # def satisfies_r_cut( self, r ) :
    #     if r < self.r_cut_upper and r > self.r_cut_lower : 
    #         return 1
    #     return 0 


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



        

        
class LiveCPTdata( CPTdata ) :

    def __init__( self, tdc ) :
        super().__init__() 
        self.tdc = tdc
        self.clear()
        self.is_live = 1 
        
        # track here all tofs, including ones without valid mcp pos 
        self.all_tofs = np.zeros( _default_buf_size ) 
        
        
    
    def clear( self ) :
        self.first_pass = 1

        self.num_events = 0 
        self.num_events_prev = 0 
        self.num_cut_data = 0 
        self.num_cut_data_prev = 0

        self.num_mcp_hits = 0
        self.num_penning_ejects = 0

        self.tdc.clear() 
        
        # self.num_data = 0 

        
        # duration of session in seconds 
        self.duration = 0

        
    # @jit
    def extract_candidates( self ) :
        
        # self.duration = time.time() - self.start_time

        if self.tdc.num_data_in_buf == 0 : 
            return
    
        if config.BENCHMARK :
            start = time.time() 
            
        rollovers = self.tdc.rollovers[ : self.tdc.num_data_in_buf ] 

        channel_indices = np.where( rollovers == 0 )[0]

        # self.sort_data()
        
        cur_trig_idx = -1

        # times of channels 0, 1, 2, 3 (channels giving position data)
        # to be stored here 
        pos_channel_buf = np.zeros( 4, dtype = 'int32' )
        mcp_trigger_reached = 0
        mcp_trigger_time = 0
        num_pos_channels_detected = 0 

        i = 0
        while( i < len( channel_indices ) ) :         
            idx = channel_indices[i]

            chan = self.tdc.channels[ idx ]
            hit_time = self.tdc.times[ idx ]

            # print( 'chan: ', chan )
            # print( 'time: ', time ) 
            
            # skip to first 6
            if self.first_pass : 
                if chan != 6 :
                    i += 1 
                    continue
                print( 'first pass complete' )
                self.first_pass = 0

            # new trigger reached (automatically happens after first pass)
            if chan == 6 :
                # print( '\n\ncpt trig reached' )
                # print( time ) 
                self.current_trig_time = self.tdc.times[ idx ]
                mcp_trigger_reached = 0
                self.num_penning_ejects += 1 
                
            # new mcp hit: found an event candidate 
            elif chan == 7 :
                mcp_trigger_time = hit_time
                tof = self.compute_tof( self.current_trig_time, mcp_trigger_time )
                self.all_tofs[ self.num_mcp_hits ] = tof 
                self.num_mcp_hits += 1
                
                # if self.satisfies_tof_cut( tof ) :
                pos_channel_buf[:] = 0 
                num_pos_channels_detected = 0
                mcp_trigger_reached = 1
                    
                # else :
                #     pass
                #     # print( 'failed tof_cut' )
                                    
            # channels 0, 1, 2, 3: handle position data if the appropriate triggers
            # have been observed.
            else :
                if mcp_trigger_reached :
                    
                    # don't add data if it's already there
                    if not pos_channel_buf[ chan ] : 
                        pos_channel_buf[ chan ] = hit_time
                        num_pos_channels_detected += 1 

                    # found enough data for a calculation 
                    if num_pos_channels_detected == 4 :

                        cur_mcp_positions = self.compute_mcp_positions( pos_channel_buf )
                                                
                        self.mcp_positions[ self.num_events ] = cur_mcp_positions
                        self.tofs[ self.num_events ] = tof
                        self.num_events += 1 
                        mcp_trigger_reached = 0 

            i += 1

        self.compute_polar()
        self.apply_cuts()
        self.num_cut_data_prev = self.num_cut_data
        self.num_events_prev = self.num_events
        self.duration = self.tdc.duration 
                
        if config.BENCHMARK :
            end = time.time()
            diff = ( end - start ) * 1000 
            print( 'BENCHMARK: processed %d hits in %f ms'
                   % ( self.tdc.num_data_in_buf, diff ) )
            
        self.tdc.num_data_in_buf = 0 

    
    
    # @jit( nopython = 1 ) 
    def compute_mcp_positions( self, pos_channel_buf ) :
        # print( pos_channel_buf ) 
        mcp_pos = np.zeros(2) 
        mcp_pos[0] =  0.5 * MCP_CAL_X * 25 * ( pos_channel_buf[0] - pos_channel_buf[1] ) * 1e-3
        mcp_pos[1] =  0.5 * MCP_CAL_Y * 25 * ( pos_channel_buf[2] - pos_channel_buf[3] ) * 1e-3
        return mcp_pos
        

    # def compute_sums( self, pos_channel_buf ) :
    #     ret = np.zeros(2) 
    #     ret[0] = pos_channel_buf[0] + pos_channel_buf[1]
    #     mcp_pos[1] = 0.5 * MCP_CAL_Y * ( pos_channel_buf[2] - pos_channel_buf[3] ) * 0.001

    
    def compute_tof( self, current_trig_time, mcp_trigger_time ) :
        if mcp_trigger_time > current_trig_time : 
            return  ( mcp_trigger_time - current_trig_time ) * 25.0 / 1e6 
        else :
            return ( mcp_trigger_time + 2**24 - current_trig_time ) * 25.0 / 1e6 
        

    def compute_timestamep( self ) :
        pass


    def apply_radius_cut( self ) :
        pass
    
    # apply cuts to the candidates found in process_candidates and store the results.
    def apply_cuts( self ) :

        # detect request for cut reset 
        if self.num_cut_data == 0 :
            start_idx = 0
        else :
            start_idx = self.num_events_prev 
        
        radii = self.radii[ start_idx : self.num_events ]
        tofs = self.tofs[ start_idx : self.num_events ]

        radius_mask = ( radii > self.r_cut_lower ) & ( radii < self.r_cut_upper )
        tof_mask = ( tofs > self.tof_cut_lower ) & ( tofs < self.tof_cut_upper ) 

        mask = radius_mask & tof_mask
        indices = np.where( mask )[0] + self.num_events_prev 
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

        
    def save( self, path = None, name = None ) :

        if path is None :
            path = DEFAULT_STORAGE_DIRECTORY

        if name is None :
            name = create_data_name( self.tabor_params, self.Z, self.A ) 
        
        with open( path, 'wb' ) as f :
            header = np.array( [ self.Z, self.N,
                                 self.duration, self.num_penning_ejects, self.num_mcp_hits,
                                 self.tabor_params.flatten() ] )
            tmp = np.concatenate( ( header, self.all_data[ : self.num_events ].flatten() ) )
            tmp.tofile( f )  

    

# default data name 
def create_data_name( tabor_params_array, Z, A ) :
    if not isinstance( Z, str ) :
        Z = z_to_element( Z ) 
    Z[0] = Z[0].upper()
    
    data_name = '%d%s_%s_%duswc_%dustacc' % ( A, Z, tabor_params.freqs[2], tabor_params.tacc )
    return data_name 

                  # 133Cs_234.030mswc_2018-08-24_260ms_wcloops-228_w+pulse-50-0.22Vpp_tofF-400V_w-amp-0.0075

    
            
# def load( path ) :
#     tmp = CPTdata( buf_size = 0 ) 
#     tmp.load( path ) 
#     return tmp
