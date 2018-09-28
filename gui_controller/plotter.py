import controller_config
import analysis 
import cpt_tools

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
n_kde_data = 200
n_cbar_ticks = 5

hitmap_cmap = colorcet.m_rainbow
# mcp_hitmap_cmap = colorcet.m_rainbow_bgyrm_35_85_c69
# mcp_hitmap_cmap = colorcet.m_linear_kryw_0_100_c71_r
# mcp_hitmap_cmap = colorcet.m_linear_bmw_5_95_c86_r
# mcp_hitmap_cmap = colorcet.m_linear_bgyw_15_100_c68_r
# mcp_hitmap_cmap = colorcet.m_inferno
hitmap_cmap.set_bad( alpha = 0 ) 




# all 3 1d histograms have the same functionality.
# it is all implemented here.
class PlotterHist( object ) :

    def __init__( self, ax, title, data, cpt_data = None ) :

        self.ax = ax 
        self.title = title
        self.data = data
        self.cpt_data = cpt_data
        
        # self.cut_data_indices = cut_data_indices 
        self.plot = None
        #self.num_cut_data = 0
        #self.num_events = 0
        self.n_bins = 0
        self.fit = None
        
        self.plot_with_cuts = 0
        

    def update( self, num_cut_data, num_total_data, use_cuts ) : 
        self.ax.clear() 
        self.ax.set_title( self.title )

        print( num_cut_data, num_total_data, use_cuts ) 

        # if self.cpt_data is None :
        #     return 

        if use_cuts :
            # use_cuts : 
            valid_indices = self.cpt_data.cut_data_indices[ : num_cut_data ]
            # else :
            #     valid_indices = self.cpt_data.cut_data_indices
            data = self.data[ valid_indices ]

        else :
            data = self.data[ : num_total_data ]
        
        bins = self.n_bins
        if bins == 0 :
            bins = 'doane'

        if self.fit is not None :
            x = np.linspace( * self.fit.bounds, 100 ) 
            self.ax.plot( x, analysis.gaussian( self.fit.params, x ), c = 'r', linewidth = 1.0, zorder = 1 )            
            self.hist, self.bins = np.histogram( data, bins = bins )
            self.ax.scatter( self.bins[:-1], self.hist, s = 1, zorder = 2 ) 
        
        else :
            self.hist, self.bins, _ = self.ax.hist( data, bins = bins )

        # print( self.title )
        # print( data ) 

        
    def set_data_params( self, num_events, num_cut_data ) :
        self.num_events = num_events
        self.num_cut_data = num_cut_data

        
    def apply_fit( self, bounds ) :

        if self.cpt_data.num_events == 0 :
            print( 'WARNING: no cpt data available for fit' )
            return None
        
        ret = analysis.fit_gaussian( self.bins[:-1], self.hist, bounds )
        
        if ret is None :
            self.fit_params = None
            self.fit_bounds = None
            return None
        
        # self.fit_params = ret.params
        # self.fit_bounds = bounds
        self.fit = ret
        
        return ret 

    
    def remove_fit( self ) :
        self.fit_params = None

    def clear( self )  :
        self.ax.clear() 






        

class PlotterHist2D( object ) :

    def __init__( self, f, ax, title, xdata, ydata, cpt_data, default_bounds = None,
                  scatter_point_coords = None )  :
        self.f = f
        self.ax = ax
        self.title = title
        self.xdata = xdata
        self.ydata = ydata
        self.cpt_data = cpt_data
        self.scatter_point_coords = scatter_point_coords

        self.use_kde = 0 
        self.kde_bandwidth = 0.03 
        self.bin_width = 0.25
        self.bounds = default_bounds
        # self.xbounds = default_bounds[0]
        # self.ybounds = default_bounds[1]
        self.rebuild = 1
        self.cbar = None
        self.cax = None 

        
    def clear( self )  :
        self.ax.clear()
        if self.cbar :
            self.cax.clear() 
            self.cbar.ax.clear()
            self.cbar.remove()
            self.cbar = None
        self.rebuild = 1 

    
    def update( self, num_cut_data, num_total_data, use_cuts ) :
        # self.cax = self.axarr[0][0]

        # if self.cpt_data is None :
        #     # self.rebuild_mcp_plot = 0
        #     self.cax.clear()
        #     if  self.cbar : 
        #         self.cbar.ax.clear() 

        
        if use_cuts :
            # if self.cpt_data.is_live : 
            valid_indices = self.cpt_data.cut_data_indices[ : num_cut_data ]
            data = [ self.xdata[ valid_indices ], self.ydata[ valid_indices ] ]  
        else :
            data = [ self.xdata[ : num_total_data ], self.ydata[ : num_total_data ] ]

        if self.bounds : 
            xbins = np.arange( self.bounds[0][0], self.bounds[0][1]
                               + self.bin_width / 2,
                               self.bin_width )
        
            ybins = np.arange( self.bounds[1][0], self.bounds[1][1]
                               + self.bin_width / 2,
                               self.bin_width )
            bins = ( xbins, ybins )
        else :
            bins = 20
            
        if self.rebuild :
            self.rebuild = 0

            if self.scatter_point_coords is not None : 
                self.ax.scatter( * self.scatter_point_coords,
                                 marker = 'x', c = 'tab:pink', s = 10, linewidths = 1  ) 

            self.ax.set_title( self.title )

            image, xedges, yedges, self.im = self.ax.hist2d(
                data[0], data[1], bins,
                cmap = hitmap_cmap # , range = ( (-100,100), (-100,100) )
            )
            image = image.T
            
            xticks = xedges[:: len(xedges) // 5 ]
            yticks = yedges[:: len(yedges) // 5 ]
                        
            self.ax.set_xticks( xticks ) 
            self.ax.set_yticks( yticks ) 
            self.ax.set_xlim( xedges[0], xedges[-1] ) 
            self.ax.set_ylim( yedges[0], yedges[-1] )
            
        
            self.ax.grid( linewidth = 0.25 )

            if not self.cbar :
                divider = make_axes_locatable( self.ax ) 
                self.cax = divider.append_axes("right", size="5%", pad=0.05)
            self.cbar = self.f.colorbar( self.im, cax = self.cax )
                                    
        # else : 
        if not self.use_kde :
            # xbins = np.linspace( * self.mcp_x_bounds, self.mcp_bin_width + 1 ) 
            # ybins = np.linspace( * self.mcp_y_bounds, self.mcp_bin_width + 1 )                
            # xbins = np.arange( self.xbounds[0], self.mcp_x_bounds[1]  + self.mcp_bin_width / 2,
            #                    self.mcp_bin_width )
            # ybins = np.arange( self.mcp_y_bounds[0], self.mcp_y_bounds[1]  + self.mcp_bin_width / 2,
            #                    self.mcp_bin_width )
            
            image, xedges, yedges = np.histogram2d( data[0], data[1], bins )
            image = image.T
            
        else :
            # kernel = scipy.stats.gaussian_kde( [ [1]*4, [1]*4 ], bw_method = 0.005 )
            try : 
                kernel = scipy.stats.gaussian_kde( data.T, bw_method = self.kde_bandwidth )
            except :
                print( 'Warning: KDE computation failed...' )
                return

            x = np.linspace( kde_min, kde_max, n_kde_data + 1 )
            y = np.linspace( kde_min, kde_max, n_kde_data + 1 )

            xx, yy = np.meshgrid( x, y )
            positions = np.vstack([xx.ravel(), yy.ravel()])
            image = np.reshape( kernel( positions ).T, xx.shape)

        # print( self.title )
        # print( image )
        # print( np.sum( image ) ) 
        
        image_min = np.min( image )
        image_max = np.max( image ) 
        ticks = np.linspace( image_min, image_max, n_cbar_ticks, dtype = int )

        image[ image == 0 ] = np.nan
        self.im.set_data( image ) 

        self.cbar.set_clim( image_min, image_max )
        self.cbar.set_ticks( ticks )
        self.cbar.draw_all()

        
        




    
class Plotter( object ) :

    def __init__( self, cpt_data ) :

        self.active_fig = 0 
        
        self.cpt_data = cpt_data
        
        self.f, self.axarr = plt.subplots( 2, 2, figsize = ( 6,6 ) )
        self.f.subplots_adjust( hspace = 0.5, wspace = 0.5 )
        
        # for i in range(2) :
        #    for j in range(2) : 
                
                # xmin, xmax = self.axarr[i,j].get_xlim()
                # ymin, ymax = self.axarr[i,j].get_ylim()
                # print((xmax-xmin)/(ymax-ymin))
                # self.axarr[i,j].set_aspect(abs((xmax-xmin)/(ymax-ymin)) * 1, adjustable='box-forced' )
                # self.axarr[i,j].set_aspect( 1, adjustable = 'box-forced' )
                # im = self.axarr[i,j].get_images()
                # extent =  im[0].get_extent()
                # self.axarr[i,j].set_aspect(abs((extent[1]-extent[0])/(extent[3]-extent[2]))/ 1)

        center = cpt_tools.mcp_center_coords.astype( int )
        # print( 'center: ', center ) 
        self.mcp_x_bounds = np.array( [ center[0] - 5.0, center[0] + 5.0 ] )
        self.mcp_y_bounds = np.array( [ center[1] - 5.0, center[1] + 5.0 ] )

        
        # self.init_mcp_hitmap( self.axarr[0][0], self.f )

        # print( 'plotter: self.cpt_data.num_events', self.cpt_data.num_events ) 

        # main
        self.rectangular_hitmap = PlotterHist2D( self.f, self.axarr[0,0],
                                                 'Rectangular Hitmap (mm vs. mm)',
                                                 self.cpt_data.mcp_positions.T[0],
                                                 self.cpt_data.mcp_positions.T[1],
                                                 self.cpt_data,
                                                 [ self.mcp_x_bounds, self.mcp_y_bounds ],
                                                 cpt_tools.mcp_center_coords )
        
        self.polar_hitmap = PlotterHist2D( self.f, self.axarr[0,1], 'Polar Hitmap (mm vs. deg)',
                                           self.cpt_data.angles,
                                           self.cpt_data.radii,
                                           self.cpt_data ) # , [ [-180, 180], [0,10] ] )
        
        
        self.tof_hist = PlotterHist( self.axarr[1,0], 'TOF ($\mu$s)', self.cpt_data.tofs,
                                     self.cpt_data )

        # projections 
        self.radius_hist = PlotterHist( self.axarr[1,0], 'Radius (mm)', self.cpt_data.radii, 
                                        self.cpt_data ) 
        
        self.angle_hist = PlotterHist( self.axarr[1,1], 'Angle (deg)', self.cpt_data.angles,
                                       self.cpt_data ) 

        self.x_hist = PlotterHist( self.axarr[0,0], 'X (mm)',
                                   self.cpt_data.mcp_positions.T[0], self.cpt_data )

        self.y_hist = PlotterHist( self.axarr[0,1], 'Y (mm)',
                                   self.cpt_data.mcp_positions.T[1], self.cpt_data )

        # diagnostics
        self.sumx_hist = PlotterHist( self.axarr[0,0], 'Sum X ($\mu$s)', self.cpt_data.sums.T[0],
                                      self.cpt_data )
        self.sumy_hist = PlotterHist( self.axarr[0,1], 'Sum Y ($\mu$s)', self.cpt_data.sums.T[1],
                                      self.cpt_data )

        self.sumx_vs_x_plot = PlotterHist2D( self.f, self.axarr[1,0], 'Sum X vs. X',
                                             self.cpt_data.mcp_positions.T[0], self.cpt_data.sums.T[0],
                                             self.cpt_data ) # , [[-10,10],[0,100]])

        self.sumy_vs_y_plot = PlotterHist2D( self.f, self.axarr[1,1], 'Sum Y vs. Y',
                                             self.cpt_data.mcp_positions.T[1], self.cpt_data.sums.T[1],
                                             self.cpt_data ) # , [[-10,10],[0,100]])

        # diagnostics 2 
        self.diff_xy_plot = PlotterHist( self.axarr[0,0], 'X - Y (mm)', self.cpt_data.diff_xy,
                                         self.cpt_data )
        
        tdc_plot_titles  = [ [ 'X1 ($\mu$s)', 'X2 ($\mu$s)' ], [ 'Y1 ($\mu$s)', 'Y2 ($\mu$s)' ] ]

        # tdc 
        self.tdc_plots = [ None for i in range(4) ]

        k = 0 
        for i in range(2) :
            for j in range(2) : 
                self.tdc_plots[k] = PlotterHist( self.axarr[i,j], tdc_plot_titles[i][j],
                                            self.cpt_data.delay_times.T[k], self.cpt_data )
                k += 1 


        # timing 
        self.abs_time_plot = PlotterHist( self.axarr[0,0], 'Absolute MCP Timestamp ($\mu$s)',
                                          self.cpt_data.timestamps, self.cpt_data )

        self.time_diff_plot = PlotterHist( self.axarr[0,1], 'MCP Time Difference ($\mu$s)',
                                           self.cpt_data.timestamp_diffs, self.cpt_data )


        # currently a misnomer. this should be renamed "fit_hists". these are the
        # hists that fits can be applied to.
        self.all_hists = [ self.tof_hist, self.radius_hist, self.angle_hist ] 

        self.plots = [ [ self.rectangular_hitmap, self.polar_hitmap, self.tof_hist ],
                       [ self.radius_hist, self.angle_hist, self.x_hist, self.y_hist ],
                       [ self.sumx_hist, self.sumy_hist, self.sumx_vs_x_plot, self.sumy_vs_y_plot ],
                       [ self.diff_xy_plot ],
                       self.tdc_plots,
                       [ self.abs_time_plot, self.time_diff_plot ]
        ]
        
        self.plot_titles = [ 'Main', 'Projections', 'Diagnostics', 'Diagnostics 2',
                             'TDC', 'Timing' ]

        
        self.plot_with_cuts = 0

        self.use_kde = 0 
        self.kde_bandwidth = 0.1
        self.mcp_bin_width = 0.25
        
        self.tof_hist_nbins = 0
        self.r_hist_nbins = 0
        self.angle_hist_nbins = 0

        self.tof_fit_params = None
        self.radius_fit_params = None
        self.angle_fit_params = None


    def clear( self ) :
        for x in self.plots[ self.active_fig ] :
            x.clear() 
        
        
        
        
    def update_all( self ) :

        # print( self.active_fig ) 
        args = ( self.cpt_data.num_cut_data, self.cpt_data.num_events, self.plot_with_cuts )

        # print( args ) 
        
        for x in self.plots[ self.active_fig ] :
            x.update( * args ) 
        
        # if self.active_fig == 0 :
            
        #     # self.update_mcp_hitmap()
        #     self.rectangular_hitmap.update( * args )
        #     self.polar_hitmap.update( * args ) 
        #     self.tof_hist.update( * args )
                            
        # elif self.active_fig == 1 :
        #     self.radius_hist.update( * args ) 
        #     self.angle_hist.update( * args )
        #     self.x_hist.update( * args )
        #     self.y_hist.update( * args ) 

        # elif self.active_fig == 2 :
        #     self.sumx_hist.update( * args )
        #     self.sumy_hist.update( * args )
        #     self.sumx_vs_x_plot.update( * args )
        #     self.sumy_vs_y_plot.update( * args )

            
    def set_plot_with_cuts( self, plot_with_cuts ) :
        self.plot_with_cuts = plot_with_cuts 
        for hist in self.all_hists :
            hist.plot_with_cuts = plot_with_cuts 

            
    def set_cpt_data( self, cpt_data ) :
        self.cpt_data = cpt_data
        
        for plot_list in self.plots :
            for plot in plot_list : 
                plot.cpt_data = cpt_data

        if cpt_data is None :
            return

        # main 
        self.rectangular_hitmap.xdata = cpt_data.mcp_positions.T[0]
        self.rectangular_hitmap.ydata = cpt_data.mcp_positions.T[1]
        self.polar_hitmap.xdata = cpt_data.angles
        self.polar_hitmap.ydata = cpt_data.radii
        self.tof_hist.data = cpt_data.tofs

        # projections 
        self.x_hist.data = cpt_data.mcp_positions.T[0]
        self.y_hist.data = cpt_data.mcp_positions.T[1]
        self.radius_hist.data = cpt_data.radii
        self.angle_hist.data = cpt_data.angles

        # diagnostics
        self.sumx_hist.data = cpt_data.sums.T[0]
        self.sumy_hist.data = cpt_data.sums.T[1]
        self.sumx_vs_x_plot.xdata = cpt_data.mcp_positions.T[0]
        self.sumx_vs_x_plot.ydata = cpt_data.sums.T[0]
        self.sumy_vs_y_plot.xdata = cpt_data.mcp_positions.T[1]
        self.sumy_vs_y_plot.ydata = cpt_data.sums.T[1]
                
        # diagnostics 2
        self.diff_xy_plot.data = cpt_data.diff_xy

        # tdc
        for i in range(4) :
            self.tdc_plots[i].data = cpt_data.delay_times.T[i]

        # timing 
        self.abs_time_plot.data = cpt_data.timestamps
        self.time_diff_plot.data = cpt_data.timestamp_diffs 
