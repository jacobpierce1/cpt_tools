import numpy as np
import scipy
import scipy.stats as st
import scipy.optimize as opt



class CPTanalyzer( object ) :

    def __init__( self ) :

        # this will store CPTdata objects 
        self.data_list = [] 


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

    # print( x )
    # print( y ) 
    # print( bounds )
    # print( indices ) 

    x_cut = x[ indices ]
    y_cut = y[ indices ]

    if len( x_cut ) == 0 :
        print( 'WARNING: no data available in the specified bounds...' )
        return None

    dy_cut = np.sqrt( y_cut )
    dy_cut[ dy_cut == 0 ] = 1

    # mu_guess = np.argmax( y_cut )
    # A_guess = float( y[ mu_guess ] )
    # mu_guess = float( mu_guess )
    # sigma_guess = 1.0

    mu_idx = np.argmax( y_cut )
    mu_guess = mu_idx + bounds[0]
    A_guess = float( y[ mu_idx ] )
    mu_guess = float( mu_guess )
    sigma_guess = 4.0

    params_guess = np.array( [ A_guess, mu_guess, sigma_guess ] ) 
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
    
        
    
