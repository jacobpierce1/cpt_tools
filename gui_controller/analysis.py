import numpy as np
import scipy
import scipy.stats as st
import scipy.optimize as opt
import matplotlib.pyplot as plt 

import cpt_tools


class CPTanalyzer( object ) :

    def __init__( self ) :

        self.num_data = 0 

        self.Z = 0
        self.A = 0
        self.N = 0

        self.ame_mass = 0
        self.ame_freq = 0
        
        self.current_mass_estimate = 0 
        self.current_freq_estimate = 0 
        
        self.data_list = [] 

        self.min_timestamp = np.nan

        # don't use numpy arrays for increased efficiency in deleting entries in the middle
        self.radii = []
        self.angles = []
        self.taccs = [] 
        self.timestamps = []

        # references are defined to have a tacc of 0.
        self.reference_indices = [] 
                
        self.f, self.axarr = plt.subplots( 3 ) 
        self.f.subplots_adjust( hspace = 0.8 )

        self.ref_drift_plot = self.axarr[0]
        self.radius_plot = self.axarr[1]
        self.residual_plot = self.axarr[2] 

        self.active_data_idx = None
        
        
    def __del__( self, idx ) :

        del self.radii[ idx ]
        del self.angles[ idx ]
        del self.taccs[ idx ]
        del self.timestamps[ idx ]

        try : 
            self.reference_indices.remove( idx ) 
        except :
            pass

    # def compute_reference_indices( self ) :
    #     self.reference_indices = np.where( 
            
    
    # apply fits and update plots 
    def append( self, cpt_data ) :

        self.data_list.append( cpt_data )
        self.radii.append( np.nan )
        self.angles.append( np.nan )
        self.timestamps.append( cpt_data.timestamp )

        tacc = cpt_data.tabor_params.tacc
        self.taccs.append( tacc ) 

        if tacc == 0 :
            self.reference_indices.append( self.num_data )

        self.num_data += 1 
        self.update() 
        
    # def set_active_fit( self, params, errors, i ) :
        
        
        
        
    # def apply_fit( self, i, bounds ) :
        
        
        # if cpt_data.tacc == 0 :
        #     self.reference_timestamps.append( cpt_data.timestamp )
        #     # self.reference_radii.append( cpt_data.fit[0][1] )
        #     # self.reference_

        # else :
        #     self.timestamps.append( cpt_data.timestamp )
            
        
        # self.update() 
        # pass 


    # def update_min_timestamp( self ) :
    #     self.min_timestamp = np.inf

    #     if self.timestamps :
    #         self.min_timestamp = min( self.min_timestamp, min( self.timestamps ) )

    #     if self.reference_timestamps :
    #         self.min_timestamp = min( self.min_timestamp, min( self.reference_timestamps ) )
            
    
    def update_ref_drift_plot( self ) :

        self.ref_drift_plot.clear()
        self.ref_drift_plot.set_xlabel( 'Timestamp' )
        self.ref_drift_plot.set_ylabel( 'Absolute Angle' )
        self.ref_drift_plot.set_title( 'Reference Drift' )
                
        # if len( self.reference_timestamps ) < 0 :
        #     return
        
        # min_timestamp = min( self.reference_timestamps ) 
        # self.references


    def update_radius_plot( self ) :
        print( 'reached' ) 
        
        self.radius_plot.clear()
        self.radius_plot.set_xlabel( 'Accumulation Time' )
        self.radius_plot.set_ylabel( 'Radius' )
        self.radius_plot.set_title( 'Radius vs. Accumulation Time' ) 

        if self.num_data == 0 :
            return
        
        print( 'plotting radii' ) 
        print( self.taccs )
        print( self.radii ) 

        self.radius_plot.scatter( self.taccs, self.radii, s = 1, zorder = 2 ) 

        
    def update_residual_plot( self ) :
        self.residual_plot.clear()
        self.residual_plot.set_xlabel( 'Accumulation Time' )
        self.residual_plot.set_ylabel( 'Residual' ) 
        self.residual_plot.set_title( 'Residuals' ) 
        
        
    def update( self ) :

        self.update_ref_drift_plot()
        self.update_radius_plot()
        self.update_residual_plot() 
                

    def set_ion_params( self, Z, A, Q ) :
        self.Z = Z
        self.A = A
        self.q =  Q
        self.N = A - Z
        self.ame_mass = cpt_tools.nuclear_data.masses[ self.Z, self.N ]
        self.ame_freq = cpt_tools.mass_to_omega( self.ame_mass, self.q, atomic_mass = 1 ) 


    # def compute_ame_phase_estimate( self, tacc, ref_angle ) :

    #     return 

    

    # compute new mass estimate using all the aggregated data.
    def compute_new_mass_estimate( self ) :
        pass
        



class GaussianFit( object ) :

    def __init__( self, bounds, params, params_errors, redchisqr ) : 
        self.bounds = bounds
        self.params = params
        self.params_errors = params_errors
        self.redchisqr = redchisqr 
        
        

    
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
    print( 'called fit_gaussian' ) 
    
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

    # print( 'params_guess: ', params_guess )
    
    ret = scipy.optimize.leastsq( _resid, params_guess, full_output = 1,
                                  args = ( gaussian, x_cut, y_cut, dy_cut ) )

    params, cov, info, mesg, success = ret
    params[2] = np.abs( params[2] ) 
    

    if success > 0 :

        dof = len( x_cut ) - len( params ) 
        
        redchisqr = ( np.sum( _resid( params, gaussian, x_cut, y_cut, dy_cut ) ) ** 2
                      / dof ) 
                                    
        if cov is not None :
            params_errors = np.sqrt( redchisqr * np.diag( cov ) )
        else :
            params_errors = None
            
        return GaussianFit( bounds, params, params_errors, redchisqr ) # pvalue

    else :
        print( 'WARNING: fit failed...' )
        return None
    
        
    
