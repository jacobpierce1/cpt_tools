# this module implements a subclass of CPTdata which is particularly suited
# for live stream. it is essentially the same as the CPTdata, except the
# functions for processing data track which indices have thus far been
# computed and only process indices corresponding to new data
# whenever extract_candidates() is called. 


import controller_config as config
import cpt_tools

import numpy as np 
from datetime import datetime
import time
import os



# header_labels = np.concatenate( ( ['Z', 'A', 'timestamp', 'duration',
#                                    'num_penning_ejects', 'num_mcp_hits' ],
#                                   cpt_tools.TaborParams.flattened_header_labels(),
#                                   [ 'header_key' ] ) )
# header_labels = ', '.join( header_labels ) 

 # self.Z, self.A, self.timestamp, self.duration,
 #                                    self.num_penning_ejects, self.num_mcp_hits

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

        self.num_rollovers = 0 
        self.last_rollover = 0

        self.tdc.clear()
        # self.start_time = time.time() 
        
        # self.num_data = 0 

        
        # duration of session in seconds 
        self.duration = 0
        self.date_str = datetime.now().strftime( '%Y-%m-%d_%H-%M-%S' ) 

        
    # @jit
    def extract_candidates( self ) :
        
        # self.duration = time.time() - self.start_time

        if self.tdc.num_data_in_buf == 0 : 
            return
    
        if config.BENCHMARK :
            start = time.time() 

        # rollovers would more appropriately be named "rollover_mask".
        # for each hit of the TDC, this is 1 if the hit was a rollover,
        # otherwise 0.
        rollovers = self.tdc.rollovers[ : self.tdc.num_data_in_buf ] 

        channel_indices = np.where( rollovers == 0 )[0]
        
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
                mcp_trigger_timestamp = self.tdc.timestamps[ idx ] 
                
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

                    # catch unknown errors issued by the TDC. i have observed
                    # that ignoring them doesn't cause any problems. 
                    except : 
                        # self.tdc.print_bin( self.tdc.data_buf[ idx ] )
                        # print( 'chan: ', chan )
                        pass

                    # found enough data for a calculation 
                    if num_pos_channels_detected == 4 :

                        # cur_mcp_positions = self.compute_mcp_positions( pos_channel_buf )
                        # sums = self.compute_sums( pos_channel_buf, mcp_trigger_time )
                        
                        self.delay_times[ self.num_events ] = self.compute_delay_times(
                            pos_channel_buf, mcp_trigger_time )

                        self.penning_eject_indices[ self.num_events ] = self.num_penning_ejects

                        self.timestamps[ self.num_events ] = mcp_trigger_timestamp
                        
                        # self.mcp_positions[ self.num_events ] = cur_mcp_positions
                        self.tofs[ self.num_events ] = tof

                        # self.sums[ self.num_events ] = self.compute_sums( pos_channel_buf,
                        #                                                   mcp_trigger_time ) 

                        self.num_events += 1 
                        mcp_trigger_reached = 0 

            i += 1

        # compute everything that can be computed in tandem from delay data
        self.compute_mcp_positions()
        self.compute_timestamp_differences() 
        self.compute_polar()
        self.compute_sums()
        self.compute_diff_xy() 
        
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


        
    # comupte tofs in micro seconds 
    def compute_tof( self, current_trig_time, mcp_trigger_time ) :
        if mcp_trigger_time > current_trig_time : 
            return  ( mcp_trigger_time - current_trig_time ) * 25.0 / 1e6 
        else :
            return ( mcp_trigger_time + 2**24 - current_trig_time ) * 25.0 / 1e6 

        
    # compute delay times in micro seconds
    def compute_delay_times( self, delay_time_buf, mcp_trigger_time ) :
        mask = ( mcp_trigger_time > delay_time_buf ).astype( int ) 
        return ( delay_time_buf - mcp_trigger_time + mask * 2**24 ) * 25 / 1e6

    

        
    def save( self, path = None, name = None, prefix = None, suffix = None ) :

        if prefix is None :
            prefix = create_element_prefix( self.Z, self.A ) 
        
        if path is None :
            path = cpt_tools.DEFAULT_STORAGE_DIRECTORY
            path += '/data/' + prefix + '/' 

        if name is None :
            name = create_data_name( self.tabor_params, self.date_str, prefix, suffix ) 
            
        file_path = path + name 

        print( 'INFO: saving file: ', file_path )

        if os.path.exists( file_path ) :
            cpt_tools.unlock_file( file_path )
            os.remove( file_path ) 
        
        try :
            self._save( file_path )
        except( OSError ) :
            os.makedirs( path, exist_ok = 1 ) 
            self._save( file_path )
            


    def _save( self, file_path ) :
        
        # save_data = ( header_prefix, self.tabor_params.flatten(),
        #               self.tofs[ : self.num_events ], self.timestamps[ : self.num_events ],
        #               self.mcp_positions[ : self.num_events ], self.sums[ : self.num_events ],
        #               self.sums[ : self.num_events ] )

        tabor_params_labels = cpt_tools.TaborParams.flattened_header_labels() 
        tabor_params_array = self.tabor_params.flatten() 

        metadata_labels = [ 'Z', 'A', 'date', 'duration',
                            'num_penning_ejects', 'num_mcp_hits', 'num_events' ]

        metadata_array = [ self.Z, self.A, self.date_str, self.duration,
                           self.num_penning_ejects, self.num_mcp_hits ]
        
        with open( file_path, 'w' ) as f :

            # for i in range( len( metadata_labels ) ) :
            #     line = '%s\t%f\n' % ( metadata_labels[i], metadata_array[i] )
            #     f.write( line ) 

            f.write( 'Z\t' + str( self.Z ) + '\n' )
            f.write( 'A\t' + str( self.A ) + '\n' )
            f.write( 'date/time\t' + self.date_str + '\n' )
            f.write( 'duration (s)\t' + str( self.duration ) + '\n' )
            f.write( 'num_penning_ejects\t' + str( self.num_penning_ejects ) + '\n' )
            f.write( 'num_mcp_hits\t' + str( self.num_mcp_hits ) + '\n' )
            
            f.write( '\n' )
                
            for i in range( len( tabor_params_labels ) ) :
                line = '%s\t%f\n' % ( tabor_params_labels[i], tabor_params_array[i] )
                f.write( line )
                
            f.write( '\n' )
            f.write( 'x1\tx2\ty1\ty2\ttof\ttimestamp\tpenning_eject_index\n' ) 

            save_array = np.vstack( [ self.delay_times[ : self.num_events ].T,
                                      self.tofs[ : self.num_events ],
                                      self.timestamps[ : self.num_events ],
                                      self.penning_eject_indices[ : self.num_events ] ] ).T
            
            np.savetxt( f, save_array, delimiter = '\t', fmt = '%.8f\t%.8f\t%.8f\t%.8f\t%.4f\t%.4f\t%i' ) 
                
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
def create_data_name( tabor_params, date_str, prefix = None, suffix = None ) :

    if prefix is None : 
        prefix = create_element_prefix( Z, A )
        
    data_name = '%s_%s' % ( date_str, prefix )

    # w_c = tabor_params.freqs[2]
    # if not np.isnan( w_c ) :
    #     data_name += '_%.0fuswc' % w_c

    tacc = tabor_params.tacc
    if not np.isnan( tacc ) :
        data_name += '_%dustacc' % tacc

    if suffix is not None :
        data_name += '_' + suffix
        
    data_name += '.cpt'
    
    return data_name 

                  # 133Cs_234.030mswc_2018-08-24_260ms_wcloops-228_w+pulse-50-0.22Vpp_tofF-400V_w-amp-0.0075

    
            
# def load( path ) :
#     tmp = CPTdata( buf_size = 0 ) 
#     tmp.load( path ) 
#     return tmp
