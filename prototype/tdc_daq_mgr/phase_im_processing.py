# this class connects to a tdc_daq_mgr and processes the data in real time 

import numpy as np
import sys


MCP_CAL_X = 1.29
MCP_CAL_Y = 1.31


# allow maximum storage of 4,194,304 hits
tdc_processor_buf_size = 2 ** 22 

mcp_center_coords = np.array( [ -1.6, 3.0 ] )



    
class tdc_processor( object ) :

    def __init__( self, tdc_daq_mgr = None ) :

        self.tdc_daq_mgr = tdc_daq_mgr
        self.first_pass = 1
        self.current_trig_time = 0

        # record how much of the buffers have been filled 
        self.num_processed_data = 0
        self.num_candidate_data = 0
        
        # self.candidate_mcp_positions = np.zeros( tdc_processor_buf_size )
        self.candidate_tofs = np.zeros( tdc_processor_buf_size )

        # this will be populated after applying cuts to the data.
        # as cuts may change in real time (e.g. tof) the original candidate data is
        # preserved for reprocessing
        self.processed_mcp_positions = np.zeros( ( tdc_processor_buf_size, 2 ) )
        self.processed_tofs = np.zeros( tdc_processor_buf_size )
        self.processed_r = np.zeros( tdc_processor_buf_size )
        self.processed_angles = np.zeros( tdc_processor_buf_size )
        
        self.tof_cut_bounds = None

        
    def reset( self ) :
        self.first_pass = 1

        self.num_processed_data = 0
        self.num_candidate_data = 0

        # to be set by user
        self.tof_cut_bounds = None
        
        
    def extract_candidates( self ) :

        rollovers = self.tdc_daq_mgr.rollovers[ : self.tdc_daq_mgr.num_data_in_buf ] 

        channel_indices = np.where( rollovers == 0 )[0]

        self.sort_data()
        
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

            chan = self.tdc_daq_mgr.channels[ idx ]
            time = self.tdc_daq_mgr.times[ idx ]

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
                self.current_trig_time = self.tdc_daq_mgr.times[ idx ]
                mcp_trigger_reached = 0 
                
            # new mcp hit: found an event candidate 
            elif chan == 7 :
                mcp_trigger_time = time
                tof = self.compute_tof( self.current_trig_time, mcp_trigger_time )

                self.candidate_tofs[ self.num_candidate_data ] = tof 
                self.num_candidate_data += 1 

                # print( 'mcp trig reached' )
                # print( time ) 
                # print( 'tof: ', tof )

                if self.satisfies_tof_cut( tof ) :
                    pos_channel_buf[:] = 0 
                    num_pos_channels_detected = 0
                    mcp_trigger_reached = 1
                    
                else :
                    pass
                    # print( 'failed tof_cut' )
                                    
            # channels 0, 1, 2, 3: handle position data if the appropriate triggers
            # have been observed.
            else :
                if mcp_trigger_reached :
                    
                    # don't add data if it's already there
                    if not pos_channel_buf[ chan ] : 
                        pos_channel_buf[ chan ] = time
                        num_pos_channels_detected += 1 

                    # found enough data for a calculation 
                    if num_pos_channels_detected == 4 :

                        mcp_positions = self.compute_mcp_positions( pos_channel_buf )

                        centered_mcp_positions = mcp_positions - mcp_center_coords 

                        r = np.linalg.norm( centered_mcp_positions )

                        if self.satisfies_r_cut( r ) :

                            angle = np.degrees( np.arctan2( centered_mcp_positions[1], centered_mcp_positions[0] ) )

                            self.processed_angles[ self.num_processed_data ] = angle
                            self.processed_r[ self.num_processed_data ] = r
                            self.processed_mcp_positions[ self.num_processed_data ] = mcp_positions
                                                    
                            # print( 'mcp_positions: ', mcp_positions )
                            # print( 'r: ', r )
                            # print( 'angle: ', angle ) 

                            self.num_processed_data += 1

                        # sums = self.compute_sums( pos_channel_buf ) 
                        # print( sums ) 
                        

                        mcp_trigger_reached = 0 

            i += 1


    # the data is only partially sorted when it comes out of the TDC.
    # complete the sorting between each group of consecutive rolloovers.
    def sort_data( self ) :

        num_data = self.tdc_daq_mgr.num_data_in_buf

        rollovers = self.tdc_daq_mgr.rollovers[ : num_data ]
        channels = self.tdc_daq_mgr.channels[ : num_data ]
        times =  self.tdc_daq_mgr.times[ : num_data ]

        rollover_start, rollover_end = self.get_rollover_boundaries( rollovers )

        # print( rollovers )
        # print( rollover_start )
        # print( rollover_end )

        # sys.exit(0 ) 
        
        for i in range( len( rollover_start ) ) :

            start = rollover_start[i]
            end = rollover_end[i]

            # print( start ) 

            # print( times[ start - 1 : end + 1 ] )

            
            sort_indices = start + np.argsort( times[ start : end ] )
            times[ start : end ] = times[ sort_indices ]
            channels[ start : end ] = channels[ sort_indices ]

            
            # print( times[ start - 1 : end + 1 ] )
            
            

    def get_rollover_boundaries( self, rollovers ) :

        tmp = np.roll( rollovers, 1 )
        tmp[0] = np.nan

        # diff = rollovers - tmp
        # diff[0] = np.nan

        # # start is the index of a non-rollover after a group of consecutive rollovers
        # start = np.where( diff == -1 )

        # # end is the index of the first rollover in a group of consecutive rollovers
        # end = np.where( diff == 1 ) 

        start = np.where( rollovers < tmp )[0]
        end = np.where( rollovers > tmp ) [0]
        
        return start, end

            
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


    # apply cuts to the candidates found in process_candidates and save the results.
    def process_candidates( self ) :
        pass


    # the sum of channels 0,1 and 2,3 should always add up to the same number.
    # return 0 if the data does not satisfy this 
    def satisfies_delay_sum_cut( self ) :
        pass


    # check if tof of the data point falls in range of a tof 
    def satisfies_tof_cut( self, tof ) :
        return 1 
        # if tof > 20 and tof < 40 :
        #     return 1
        # return 0 

    def satisfies_r_cut( self, r ) :
        if r < 40 :
            return 1 
