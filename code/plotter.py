import numpy as np
import matplotlib.pyplot as plt
import colorcet
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.stats

# import matplotlib.style as mplstyle
# mplstyle.use('fast')

plt.rc( 'font', ** { 'size' : 6 } ) 


kde_min = -5
kde_max = 5
n_kde_data = 100
n_cbar_ticks = 5

mcp_hitmap_cmap = colorcet.m_rainbow


use_kde = 0 # use kernel density estimation 

class Plotter( object ) :

    def __init__( self, cpt_data ) :

        self.f, self.axarr = plt.subplots( 2, 2 )
        self.f.subplots_adjust( hspace = 0.5, wspace = 0.5 )
        
        self.init_mcp_hitmap( self.axarr[0][0], self.f )
        self.init_tof_plot( self.axarr[0][1] )
        self.init_r_plot( self.axarr[1][0] )
        self.init_theta_plot( self.axarr[1][1] )
        
        self.cpt_data = cpt_data
        self.mcp_hitmap_plot = None
        self.tof_plot= None

        self.plot_with_cuts = 0

        self.use_kde = 0 
        self.kde_bandwidth = 0.003
        self.mcp_bin_width = 0.5
        self.mcp_x_bounds = [ -5.0, 5.0 ]
        self.mcp_y_bounds = [ -5.0, 5.0 ]

        self.tof_hist_nbins = 0
        self.r_hist_nbins = 0
        self.angle_hist_nbins = 0



    # deallocate matplotlib resources 
    def release( self ) : 
        self.f.clear() 
        
    def update_tof_plot( self ) :

        self.tof_plot = self.axarr[0][1]
        
        if self.plot_with_cuts : 
            valid_indices = self.cpt_data.cut_data_indices[ : self.cpt_data.num_cut_data ]    
            data = self.cpt_data.tofs[ valid_indices ]
        else :
            # valid_indices = self.cpt_data.candidate_indices[ : self.cpt_data.num_candidate_data ]
            # data = self.cpt_data.all_tofs[ : self.cpt_data.num_mcp_hits ]
            data = self.cpt_data.tofs[ : self.cpt_data.num_events ]
                                
        # self.current_tof_plot_data = self.tof_plot.hist( self.cpt_data.tof_data )
        self.tof_plot.clear()

        bins = self.tof_hist_nbins
        if bins == 0 :
            bins = 'fd'
        
        self.tof_plot.hist( data, bins = bins, log = 1  ) 
        # hist, bins = np.histogram( self.cpt_data.tof_data, bins = 'auto' )
        # self.tof_plot.plot( bins[:-1], hist, ls = 'steps-mid' ) 
        self.tof_plot.set_title( 'TOF histogram'  )
        self.tof_plot.set_xlabel( 'TOF' )
        # self.tof_plot.set_ylabel( 'Counts' ) 

        
    def init_tof_plot( self, ax ) :
        # print( self.cpt_data.tof_data ) 
        pass
        # self.current_tof_plot_data = self.tof_plot.hist( self.cpt_data.tof_data )
        
        
    def update_mcp_hitmap( self ) :

        self.mcp_hitmap_plot = self.axarr[0][0]
        
        if self.plot_with_cuts : 
            valid_indices = self.cpt_data.cut_data_indices[ : self.cpt_data.num_cut_data ]
            data = self.cpt_data.mcp_positions[ valid_indices ] 
        else :
            # valid_indices = self.cpt_data.candidate_indices[ : self.cpt_data.num_candidate_data ]

            data = self.cpt_data.mcp_positions[ : self.cpt_data.num_events ]

        xbins = np.arange( self.mcp_x_bounds[0], self.mcp_x_bounds[1]  + self.mcp_bin_width / 2,
                           self.mcp_bin_width )
        ybins = np.arange( self.mcp_y_bounds[0], self.mcp_y_bounds[1]  + self.mcp_bin_width / 2,
                           self.mcp_bin_width )

        if self.rebuild_mcp_plot :
            self.rebuild_mcp_plot = 0
            self.mcp_hitmap_plot.clear()
            if  self.mcp_hitmap_cbar : 
                self.mcp_hitmap_cbar.ax.clear() 
            # if self.mcp_hitmap_cbar is not None : 
            #     self.mcp_hitmap_cbar.clear() 
            
            title = 'MCP Hitmap'
            self.mcp_hitmap_plot.set_title( title )
            self.mcp_hitmap_plot.set_xlabel( 'X' )
            self.mcp_hitmap_plot.set_ylabel( 'Y' ) 

            image, xedges, yedges, self.mcp_hitmap_im = self.mcp_hitmap_plot.hist2d(
                data[:,0], data[:,1], ( xbins, ybins ),
                cmap = mcp_hitmap_cmap # , range = ( (-100,100), (-100,100) )
            )
            
            xticks = xedges[:: len(xedges) // 5 ]
            yticks = yedges[:: len(yedges) // 5 ]
            
            self.mcp_hitmap_plot.set_xticks( xticks ) 
            self.mcp_hitmap_plot.set_yticks( yticks ) 
            self.mcp_hitmap_plot.set_xlim( xedges[0], xedges[-1] ) 
            self.mcp_hitmap_plot.set_ylim( yedges[0], yedges[-1] )
            
        
            self.mcp_hitmap_plot.grid()

            if not self.mcp_hitmap_cbar :
                divider = make_axes_locatable( self.mcp_hitmap_plot ) 
                self.mcp_hitmap_cax = divider.append_axes("right", size="5%", pad=0.05)
                self.mcp_hitmap_cbar = self.mcp_hitmap_f.colorbar( self.mcp_hitmap_im,
                                                               cax = self.mcp_hitmap_cax )
            else :
                self.mcp_hitmap_cbar = self.mcp_hitmap_f.colorbar( self.mcp_hitmap_im,
                                                               cax = self.mcp_hitmap_cbar.ax )
                
            # self.mcp_hitmap_cbar.set_ticks( np.arange( n_cbar_ticks ) )
            # self.mcp_hitmap_cbar.set_clim( 0, 0 )
        
        else : 
            if not self.use_kde :
                # xbins = np.linspace( * self.mcp_x_bounds, self.mcp_bin_width + 1 ) 
                # ybins = np.linspace( * self.mcp_y_bounds, self.mcp_bin_width + 1 )                
                xbins = np.arange( self.mcp_x_bounds[0], self.mcp_x_bounds[1]  + self.mcp_bin_width / 2,
                                   self.mcp_bin_width )
                ybins = np.arange( self.mcp_y_bounds[0], self.mcp_y_bounds[1]  + self.mcp_bin_width / 2,
                                   self.mcp_bin_width )
                image, xedges, yedges = np.histogram2d( data[:,0], data[:,1], bins = ( xbins, ybins ) )
                
            else :
                # kernel = scipy.stats.gaussian_kde( [ [1]*4, [1]*4 ], bw_method = 0.005 )
                try : 
                    kernel = scipy.stats.gaussian_kde( data, bw_method = 0.003 )
                except :
                    print( 'Warning: KDE computation failed...' )
                    return
            
                x = np.linspace( kde_min, kde_max, n_kde_data + 1 )
                y = np.linspace( kde_min, kde_max, n_kde_data + 1 )
            
                xx, yy = np.meshgrid( x, y )
                positions = np.vstack([xx.ravel(), yy.ravel()])
                image = ( np.reshape( kernel( positions ).T, xx.shape)
                          * len( self.cpt_data.candidate_mcp_positions[0] ) )

            self.mcp_hitmap_im.set_data( image.T ) 
            
        image_min = np.min( image )
        image_max = np.max( image ) 
        ticks = np.linspace( image_min, image_max, n_cbar_ticks, dtype = int )
        
        self.mcp_hitmap_cbar.set_clim( image_min, image_max )
        self.mcp_hitmap_cbar.set_ticks( ticks )
        self.mcp_hitmap_cbar.draw_all()


         
        
        
    def init_mcp_hitmap( self, ax, f ) :
        
        self.mcp_hitmap_f = self.f
        self.rebuild_mcp_plot = 1
        self.mcp_hitmap_cbar = None
        self.mcp_hitmap_cax = None


    def init_r_plot( self, ax ) :
        pass 

        
    def update_r_plot( self ) :
        self.r_plot = self.axarr[1][0]
        self.r_plot.clear() 
        self.r_plot.set_title( 'r' )

        if self.plot_with_cuts : 
            valid_indices = self.cpt_data.cut_data_indices[ : self.cpt_data.num_cut_data ]
            data = self.cpt_data.radii[ valid_indices ] 
        else :
            # valid_indices = self.cpt_data.candidate_indices[ : self.cpt_data.num_candidate_data ]

            data = self.cpt_data.radii[ : self.cpt_data.num_events ]
        
        bins = self.r_hist_nbins
        if bins == 0 :
            bins = 'rice'

        self.r_plot.hist( data, bins = bins )
        
    
    def init_theta_plot( self, ax ) :
        pass 

        
    def update_theta_plot( self ) :
        self.theta_plot = self.axarr[1][1]
        self.theta_plot.clear()

        if self.plot_with_cuts : 
            valid_indices = self.cpt_data.cut_data_indices[ : self.cpt_data.num_cut_data ]
            data = self.cpt_data.angles[ valid_indices ] 
        else :
            # valid_indices = self.cpt_data.candidate_indices[ : self.cpt_data.num_candidate_data ]
            data = self.cpt_data.angles[ : self.cpt_data.num_events ]
            
        bins = self.angle_hist_nbins
        if bins == 0 :
            bins = 'rice'

        self.theta_plot.set_title( r'Angle (deg)' ) 
        self.theta_plot.hist( data, bins = bins )


    def update_all( self ) :
        self.update_mcp_hitmap()
        self.update_tof_plot()
        self.update_r_plot()
        self.update_theta_plot() 
        
    # def init_coords_plots( self, axarr ) :
    #     self.coords_plots = axarr

        
    # def update_coords_plots( self ) :

    #     titles = [ [ 'X1', 'X2' ], [ 'Y1', 'Y2' ] ]

    #     for i in range(2) :
    #         for j in range(2) :
    #             self.coords_plots[i,j].clear()
    #             self.coords_plots[i,j].set_title( titles[i][j] ) 
                
        

