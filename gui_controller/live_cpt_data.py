import controller_config as config
import cpt_tools

import numpy as np 
from datetime import datetime
import time
import os


MCP_CAL_X = 1.29
MCP_CAL_Y = 1.31



class LiveCPTdata( cpt_tools.CPTdata ) :

    def __init__( self, tdc ) :
        super().__init__() 
        self.tdc = tdc
        self.clear()
        self.is_live = 1 

        self.Z = np.nan
        self.A = np.nan
        self.tabor_params = cpt_tools.TaborParams.empty()
        
        # # track here all tofs, including ones without valid mcp pos 
        # self.all_tofs = np.zeros( _default_buf_size ) 
        
        
    
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
                # print( 'first pass complete' )
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
                # self.all_tofs[ self.num_mcp_hits ] = tof 
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
                
                    # self.tdc.print_bin( self.tdc.data_buf[ idx ] )
                    
                    # don't add data if it's already there
                    try : 
                        if not pos_channel_buf[ chan ] : 
                            pos_channel_buf[ chan ] = hit_time
                            num_pos_channels_detected += 1 
                    except : 
                        self.tdc.print_bin( self.tdc.data_buf[ idx ] )
                        print( 'chan: ', chan )
                        

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
                                   - cpt_tools.mcp_center_coords  )
        radii = np.linalg.norm( centered_mcp_positions, axis = 1 )
        angles = np.degrees( np.arctan2( centered_mcp_positions[:,1],
                                        centered_mcp_positions[:,0] ) )

        self.radii[ self.num_events_prev : self.num_events ] = radii
        self.angles[ self.num_events_prev : self.num_events ] = angles

        
    def save( self, path = None, name = None, prefix = None ) :

        if prefix is None :
            prefix = create_element_prefix( self.Z, self.A ) 
        
        if path is None :
            path = cpt_tools.DEFAULT_STORAGE_DIRECTORY
            path += '/data/' + prefix + '/' 

        if name is None :
            name = create_data_name( self.tabor_params, prefix ) 

        file_path = path + name

        print( 'INFO: saving file: ', file_path )

        try :
            self._save( file_path )
        except( OSError ) :
            os.makedirs( path, exist_ok = 1 ) 
            self._save( file_path )
            
            
    def _save( self, file_path ) :

                
        #with open( file_path, 'wb' ) as f :
        header_prefix = np.array( [ self.Z, self.A, self.timestamp, self.duration,
                                    self.num_penning_ejects, self.num_mcp_hits ] )
            
        tmp = np.concatenate( ( header_prefix, self.tabor_params.flatten(), cpt_tools.cpt_header_key,
                                self.all_data[ : self.num_events ].flatten() ) )

        try :
            os.remove( file_path )
        except OSError :
            pass
            
        tmp.tofile( file_path )
        cpt_tools.lock_file( file_path ) 

            

def create_element_prefix( Z, A ) :
    if np.isnan( Z ) :
        prefix = 'unknown'
        if not np.isnan( A ) :
            prefix = str(A) + prefix 
    
    else :
        if not isinstance( Z, str ) :
            Z = z_to_element( Z )
        print( Z ) 
        Z = Z.capitalize()
        prefix = str(A) + Z 
    return prefix 



# default data name 
def create_data_name( tabor_params, prefix = None ) :

    if prefix is None : 
        prefix = create_element_prefix( Z, A )

    date_str = datetime.now().strftime( '%Y-%m-%d_%H-%M' ) 
        
    data_name = '%s_%s' % ( date_str, prefix )

    w_c = tabor_params.freqs[2]
    if not np.isnan( w_c ) :
        data_name += '_%.0fuswc' % w_c

    tacc = tabor_params.tacc
    if not np.isnan( tacc ) :
        data_name += '_%dustacc' % tacc

    data_name += '.cpt'
    
    return data_name 

                  # 133Cs_234.030mswc_2018-08-24_260ms_wcloops-228_w+pulse-50-0.22Vpp_tofF-400V_w-amp-0.0075

    
            
# def load( path ) :
#     tmp = CPTdata( buf_size = 0 ) 
#     tmp.load( path ) 
#     return tmp
