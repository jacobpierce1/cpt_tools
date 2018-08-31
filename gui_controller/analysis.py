import numpy as np
import scipy
import scipy.stats as st
import scipy.optimize as opt
import matplotlib.pyplot as plt 



class CPTanalyzer( object ) :

    def __init__( self ) :

        # this will store CPTdata objects 
        self.data_list = [] 

        self.min_timestamp = np.nan
    
        self.radii = []
        self.angles = []
        self.taccs = [] 
        self.timestamps = []

        # references are defined to have a tacc of 0.
        self.reference_indices = None
                
        self.f, self.axarr = plt.subplots( 3 ) 
        self.f.subplots_adjust( hspace = 0.5 )

        self.ref_drift_plot = self.axarr[0]
        self.radius_plot = self.axarr[1]

        
    def __del__( self ) :
        pass


    # apply fits and update plots 
    def append( self, cpt_data ) :

        self.data_list.append( cpt_data ) 
        
        # if cpt_data.tacc == 0 :
        #     self.reference_timestamps.append( cpt_data.timestamp )
        #     # self.reference_radii.append( cpt_data.fit[0][1] )
        #     # self.reference_

        # else :
        #     self.timestamps.append( cpt_data.timestamp )
            
        
        self.update() 
        pass 


    def update_min_timestamp( self ) :
        self.min_timestamp = np.inf

        if self.timestamps :
            self.min_timestamp = min( self.min_timestamp, min( self.timestamps ) )

        if self.reference_timestamps :
            self.min_timestamp = min( self.min_timestamp, min( self.reference_timestamps ) )
            
    
    def update_ref_drift_plot( self ) :

        self.ref_drift_plot.clear()
        self.ref_drift_plot.set_xlabel( 'Timestamp' )
        self.ref_drift_plot.set_ylabel( 'Absolute Angle' )
        self.ref_drift_plot.set_title( 'Reference Drift' )
                
        if len( self.reference_timestamps ) < 0 :
            return
        
        min_timestamp = min( self.reference_timestamps ) 
        self.references


    def update_radius_plot( self ) :
        self.radius_plot.clear()
        self.radius_plot.set_xlabel( 'Accumulation Time' )
        self.radius_plot.set_ylabel( 'Radius' )
        self.radius_plot.set_title( 'Radius vs. Accumulation Time' ) 

        if len( self.timestamps ) > 0 :
            pass 

        
    def update( self ) :
        pass
    
        
def gaussian( params, x ) :
    return params[0] * np.exp( - ( x - params[1] ) ** 2
                               / ( 2 * params[2] ** 2 ) )


def normalized_gaussian( mu, sigma, x ) :
    sigma_sqr = sigma ** 2 
    return ( ( 1 / np.sqrt( 2 * np.pi * sigma_sqr ) )
             * np.exp( - ( x - mu ) ** 2
                       / ( 2 * sigma ** 2 ) ) )

        
def _resid( params, func, x, y, dy ) :
    return ( y - func( params, x ) ) / dy 


def fit_gaussian( x, y, bounds ) :

    indices = ( x >= bounds[0] ) & ( x <= bounds[1] )

    x_cut = x[ indices ]
    y_cut = y[ indices ]

    if len( x_cut ) == 0 :
        print( 'WARNING: no data available in the specified bounds...' )
        return None

    dy_cut = np.sqrt( y_cut )
    dy_cut[ dy_cut == 0 ] = 1
        
    # print( y_cut ) 
    
    max_idx = np.argmax( y_cut )
    mu_guess = float( x_cut[ max_idx ] )#  + bounds[0]
    A_guess = float( y_cut[ max_idx ] )
    sigma_guess = 4.0

    params_guess = np.array( [ A_guess, mu_guess, sigma_guess ] )

    print( 'params_guess: ', params_guess )
    
    ret = scipy.optimize.leastsq( _resid, params_guess, full_output = 1,
                                  args = ( gaussian, x_cut, y_cut, dy_cut ) )

    params, cov, info, mesg, success = ret

    

    if success > 0 :

        dof = len( x_cut ) - len( params ) 
        
        redchisqr = ( np.sum( _resid( params, gaussian, x_cut, y_cut, dy_cut ) ) ** 2
                      / dof ) 
                                    
        if cov is not None :
            params_errors = np.sqrt( redchisqr * np.diag( cov ) )
        else :
            params_errors = None
            
        return params, params_errors, redchisqr # pvalue

    else :
        print( 'WARNING: fit failed...' )
        return None
    
        
    
