# this module provides two classes which contain all the relevant information
# required to process data obtained in the CPT. the live class is used for DAQ.

import dill

_default_buf_size = 2**22

class cpt_data( object ) :

    def __init__( self, path = None, buf_size = 0 ) :

        if path :
            self.load( path )
            return

        self.clear()

        if buf_size == 0 :
            buf_size = _default_buf_size 

        self.candidate_tofs = np.zeros( buf_size )
        self.candidate_radii = np.zeros( buf_size )
        self.candidate_angles = np.zeros( buf_size )
        self.candidate_mcp_positions = np.zeros( ( buf_size, 2 ) )

        self.candidate_radii[:] = np.nan
        self.candidate_angles[:] = np.nan
        self.candidate_mcp_positions[:] = np.nan
        
        # store indices of data that have been computed to be valid.
        # when cuts are changed, the candidate data is unchanged and
        # processed_indices is reconstructed to satisfy the new cuts.
        self.processed_indices = np.zeros( buf_size, dtype = int )
        self.candidate_indices = np.zeros( buf_size, dtype = int ) 
        
        self.tof_cut_lower = 0
        self.tof_cut_upper = 40

        self.r_cut_lower = -1
        self.r_cut_upper = 40
        
        
    def clear( self ) :
        self.first_pass = 1

        self.num_penning_ejects = 0
        self.num_mcp_hits = -1
        self.num_processed_data = 0
        self.num_candidate_data = 0

        self.session_start_time = time.time()

        
    def save( self, path ) :
        with open( path, 'wb' ) as f :
            dill.dump( f, self ) 

    def save_txt( self ) :
        pass
            
    def load( self, path ) :
        with open( path, 'rb' ) as f :
            return dill.load( f ) 

    def load_txt( self, path ) :
        pass



        
class live_cpt_data( cpt_data ) :

    def __init__( self, tdc ) :

        self.tdc = tdc
        super().__init__( bufsize = _default_buf_size ) 


    def extract_candidates( self ) :
        pass
        
    def save( self ) :
        pass

    def save_txt( self ) :
        pass
