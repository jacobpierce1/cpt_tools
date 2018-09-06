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
        
        self.current_mass_estimate = np.nan
        self.current_freq_estimate = np.nan
        
        self.data_list = [] 

        self.min_timestamp = np.nan

        # don't use numpy arrays for increased efficiency in deleting entries in the middle
        self.radii = []
        self.angles = []
        self.taccs = [] 
        self.timestamps = []

        # references are defined to have a tacc of 0.
        self.reference_mask = [] 
                
        self.f, self.axarr = plt.subplots( 3 ) 
        self.f.subplots_adjust( hspace = 0.8 )

        self.ref_drift_plot = self.axarr[0]
        self.radius_plot = self.axarr[1]
        self.residual_plot = self.axarr[2] 

        self.active_data_idx = None
        
        
    def delete_index( self, idx ) :

        del self.data_list[ idx ] 
        del self.radii[ idx ]
        del self.angles[ idx ]
        del self.taccs[ idx ]
        del self.timestamps[ idx ]
        del self.reference_mask[ idx ]

        self.num_data -= 1 
        # try : 
        #     self.reference_mask.remove( idx ) 
        # except :
        #     pass

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
            self.reference_mask.append( 1 )
        else :
            self.reference_mask.append( 0 ) 
            
        self.num_data += 1 
        # self.update() 
        
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
        self.ref_drift_plot.set_xlabel( 'Relative Timestamp' )
        self.ref_drift_plot.set_ylabel( 'Absolute Angle' )
        self.ref_drift_plot.set_title( 'Reference Drift' )

        if np.sum( self.reference_mask ) == 0 :
            return 
        
        references = np.array( self.reference_mask, dtype = bool ) 
        
        ref_phase = np.array( self.angles )[ references ]
        ref_timestamps = np.array( self.timestamps )[ references ]
        ref_timestamps -= min( ref_timestamps )

        # print( 'plotting ref_drift_plot' )
        # print( self.reference_mask ) 
        # print( ref_timestamps )
        # print( ref_phase ) 

        self.ref_drift_plot.scatter( ref_timestamps, ref_phase, s = 1, c = 'r',
                                     zorder = 2 ) 
        
        # if len( self.reference_timestamps ) < 0 :
        #     return
        
        # min_timestamp = min( self.reference_timestamps ) 
        # self.references


    def update_radius_plot( self ) :        
        self.radius_plot.clear()
        self.radius_plot.set_xlabel( 'Accumulation Time' )
        self.radius_plot.set_ylabel( 'Radius' )
        self.radius_plot.set_title( 'Radius vs. Accumulation Time' ) 

        if self.num_data == 0 :
            return
        
        # print( 'plotting radii' ) 
        # print( self.taccs )
        # print( self.radii ) 

        self.radius_plot.scatter( self.taccs, self.radii, s = 1, zorder = 2 ) 

        
    def update_residual_plot( self ) :
        self.residual_plot.clear()
        self.residual_plot.set_xlabel( 'Accumulation Time' )
        self.residual_plot.set_ylabel( 'Residual' ) 
        self.residual_plot.set_title( 'Mass Fit Residuals' ) 
        
        
    def update( self ) :

        self.update_ref_drift_plot()
        self.update_radius_plot()
        self.update_residual_plot() 
        self.update_mass_estimate()
        

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
    def update_mass_estimate( self ) :

        reference_mask = np.array( self.reference_mask, dtype = bool ) & ( ~ np.isnan( self.angles ) )
        non_reference_mask = ( ~ reference_mask ) & ( ~ np.isnan( self.angles ) )

        # print( reference_mask )
        # print( non_reference_mask )
        # print( self.timestamps ) 

        reference_indices = np.where( reference_mask == 1 )[0] 
        non_reference_indices = np.where( non_reference_mask == 1 )[0]

        print( reference_indices )
        print( non_reference_indices )
        
        if np.sum( reference_mask ) == 0 or np.sum( non_reference_mask ) == 0 :
            self.current_mass_estimate = np.nan
            self.current_freq_estimate = np.nan
            return 

        #
        # print( self.timestamps.shape )
        # print( self.reference_mask.shape ) 
        
        reference_timestamps = np.array( self.timestamps )[ reference_mask ] 
        
        num_non_references = len( non_reference_indices )
        measured_phases = np.zeros( num_non_references ) 
        
        
        for i in range( num_non_references ) :

            #find closest reference
            idx = non_reference_indices[i]  # index in self.timestamps 
            timestamp = self.timestamps[ idx ]
            rel_ref_idx = np.argmin( np.abs( reference_timestamps - timestamp ) )  # index in reference_timestamps
            ref_idx = reference_indices[ rel_ref_idx ] 

            phase = self.angles[ idx ] - self.angles[ ref_idx ]
            measured_phases[i] = phase 

        taccs = np.array( self.taccs )[ non_reference_mask ]

        # return 
        ret = scipy.optimize.leastsq( freq_estimate_resid, [ self.ame_freq ],
                                      args = ( taccs, measured_phases ), full_output = 1  )
            
        print( ret ) 
        
        
                                
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
        print( x_cut )
        print( params ) 
        print( 'dof: ', dof ) 
        
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
    
        
    

def freq_estimate_resid( frequency, taccs, phases ) :
    
    phase_predictions = cpt_tools.freq_to_phase( frequency, taccs )
    print( taccs ) 
    print( phases )
    print( phase_predictions ) 
    ret = phases - phase_predictions
    print( ret )
    return ret 
    
