import numpy as np
import matplotlib.pyplot as plt
import colorcet
from mpl_toolkits.axes_grid1 import make_axes_locatable

import matplotlib.style as mplstyle
mplstyle.use('fast')



kde_min = -5
kde_max = 5
n_kde_data = 100
n_cbar_ticks = 5

mcp_hitmap_cmap = colorcet.m_rainbow


use_kde = 0 # use kernel density estimation 

class plotter( object ) :

    def __init__( self, tdc_data_handler ) :
        self.tdc_data_handler = tdc_data_handler
        self.mcp_hitmap_plot = None
        self.tof_plot= None

        
    def update_tof_plot( self ) :
        # print( self.tdc_data_handler.tof_data )

        data = self.tdc_data_handler.candidate_tofs[ : self.tdc_data_handler.num_candidate_data ]

        # self.current_tof_plot_data = self.tof_plot.hist( self.tdc_data_handler.tof_data )
        self.tof_plot.clear() 
        self.tof_plot.hist( data, bins = 'fd', log = 1  ) 
        # hist, bins = np.histogram( self.tdc_data_handler.tof_data, bins = 'auto' )
        # self.tof_plot.plot( bins[:-1], hist, ls = 'steps-mid' ) 
        self.tof_plot.set_title( 'TOF histogram'  )
        self.tof_plot.set_xlabel( 'TOF' )
        # self.tof_plot.set_ylabel( 'Counts' ) 

        
    def init_tof_plot( self, ax ) :
        # print( self.tdc_data_handler.tof_data ) 
        self.tof_plot = ax
        # self.current_tof_plot_data = self.tof_plot.hist( self.tdc_data_handler.tof_data )
        
        
    def update_mcp_hitmap( self ) :

        # print( self.tdc_data_handler.mcp_positions ) 
        # self.mcp_hitmap_plot.clear()
        # self.mcp_hitmap_plot.clear()
        # self.mcp_hitmap_fig

        data = self.tdc_data_handler.processed_mcp_positions[ : self.tdc_data_handler.num_processed_data ] 

        # print( data[:,0] )
        
        if not use_kde :
            image, xedges, yedges = np.histogram2d( data[:,0], data[:,1], bins = 20 )
            im = self.mcp_hitmap_im.set_data( image )

        else :
            # kernel = scipy.stats.gaussian_kde( [ [1]*4, [1]*4 ], bw_method = 0.005 )
            kernel = scipy.stats.gaussian_kde( data, bw_method = 0.003 )
            x = np.linspace( kde_min, kde_max, n_kde_data + 1 )
            y = np.linspace( kde_min, kde_max, n_kde_data + 1 )
            
            xx, yy = np.meshgrid( x, y )
            positions = np.vstack([xx.ravel(), yy.ravel()])
            image = ( np.reshape( kernel( positions ).T, xx.shape)
                      * len( self.tdc_data_handler.candidate_mcp_positions[0] ) )
            
            self.mcp_hitmap_im.set_data( image ) 
            
        image_min = np.min( image )
        image_max = np.max( image ) 
        ticks = np.linspace( image_min, image_max, n_cbar_ticks, dtype = int )
            
        self.mcp_hitmap_cbar.set_clim( image_min, image_max )
        self.mcp_hitmap_cbar.set_ticks( ticks )
        self.mcp_hitmap_cbar.draw_all()

            # print( len( self.tdc_data_handler.candidate_mcp_positions) )
            
        
    def init_mcp_hitmap( self, ax, f ) :
        self.mcp_hitmap_plot = ax
        self.mcp_hitmap_f = f

        title = 'MCP Hitmap'
        if use_kde :
            title += ': KDE'
        else :
            title += ': binned'

        ax.set_title( title )
        ax.set_xlabel( 'X' )
        ax.set_ylabel( 'Y' ) 

        self.mcp_hitmap_im = self.mcp_hitmap_plot.imshow( np.zeros( ( n_kde_data, n_kde_data ) ),
                                                          cmap = mcp_hitmap_cmap,
                                                          # interpolation = 'nearest',
                                                          origin = 'lower' )
        
        divider = make_axes_locatable( self.mcp_hitmap_plot ) 
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.mcp_hitmap_cbar = self.mcp_hitmap_f.colorbar( self.mcp_hitmap_im, cax = cax )

        tick_spacing = n_kde_data // 5
        ticks = np.arange( 0, n_kde_data + 1, tick_spacing )
        x = np.linspace( kde_min, kde_max, n_kde_data + 1 )
        tick_labels = [ '%.2f' % x[ tick ] for tick in ticks ]

        self.mcp_hitmap_plot.set_xticks( ticks )
        self.mcp_hitmap_plot.set_xticklabels( tick_labels )
        self.mcp_hitmap_plot.set_yticks( ticks )
        self.mcp_hitmap_plot.set_yticklabels( tick_labels )

        self.mcp_hitmap_cbar.set_ticks( np.arange( n_cbar_ticks ) )
        self.mcp_hitmap_cbar.set_clim( 0, 0 )

        # print( self.mcp_hitmap_cbar.get_ticks() )
        
        # self.mcp_hitmap_cbar.set_xticklabels( np.zeros( n_cbar_ticks, dtype = int ) )
        
        # im = self.mcp_hitmap.imshow( self.tdc_data_handler.mcp_positions, cmap = mcp_hitmap_cmap ) 
        # self.update_mcp_hitmap() 
        # self.mcp_hitmap_plot.imshow( [ [ np.nan, np.nan ] ] ) 



    def init_r_plot( self, ax ) :
        self.r_plot = ax 

        
    def update_r_plot( self ) :
        self.r_plot.clear() 
        self.r_plot.set_title( 'r' )
        data = self.tdc_data_handler.processed_r[ : self.tdc_data_handler.num_processed_data ]
        self.r_plot.hist( data, bins = 'fd' ) 
        
        # r = np.linalg.norm( self.tdc_data_handler.candidate_mcp_positions - mcp_center_coords,
        #                     axis = 0 ) 

    
    def init_theta_plot( self, ax ) :
        self.theta_plot = ax 

        
    def update_theta_plot( self ) :
        self.theta_plot.clear() 
        data = self.tdc_data_handler.processed_angles[ : self.tdc_data_handler.num_processed_data ] 
        self.theta_plot.set_title( r'Angle (deg)' ) 
        self.theta_plot.hist( data, bins = 'fd' )
    
        
    def init_coords_plots( self, axarr ) :
        self.coords_plots = axarr

        
    def update_coords_plots( self ) :

        titles = [ [ 'X1', 'X2' ], [ 'Y1', 'Y2' ] ]

        for i in range(2) :
            for j in range(2) :
                self.coords_plots[i,j].clear()
                self.coords_plots[i,j].set_title( titles[i][j] ) 
                
        

