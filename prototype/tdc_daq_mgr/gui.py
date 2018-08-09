import config
import tdc_daq_mgr
import phase_im_processing
import gui


import os
import numpy as np
import scipy
from PyQt4 import QtGui
import sys 
import colorcet
import scipy.stats as st
from mpl_toolkits.axes_grid1 import make_axes_locatable
import struct 
# import multiprocessing 

# import matplotlib.style as mplstyle
# mplstyle.use('fast')




from PyQt4 import QtCore

import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import random

mcp_hitmap_cmap = colorcet.m_rainbow


# coords of the mcp that are struck by ions ejected from the
# center of the trap 
mcp_center_coords = np.array( [ 5., 5. ] ) 


use_kde = 1 # use kernel density estimation 
kde_min = -5
kde_max = 5
n_kde_data = 100



class TDCPlotter( object ) :

    def __init__( self, tdc_data_handler ) :

        self.tdc_data_handler = tdc_data_handler
        self.mcp_hitmap_plot = None
        self.tof_plot= None
        
    def update_tof_plot( self ) :
        # print( self.tdc_data_handler.tof_data )

        # self.current_tof_plot_data = self.tof_plot.hist( self.tdc_data_handler.tof_data )
        self.tof_plot.clear() 
        self.tof_plot.hist( self.tdc_data_handler.candidate_tofs, bins = 'fd', log = 1  ) 
        # hist, bins = np.histogram( self.tdc_data_handler.tof_data, bins = 'auto' )
        # self.tof_plot.plot( bins[:-1], hist, ls = 'steps-mid' ) 
        self.tof_plot.set_title( 'TOF histogram'  )
        self.tof_plot.set_xlabel( 'TOF' )
        self.tof_plot.set_ylabel( 'Counts' ) 

        
    def init_tof_plot( self, ax ) :
        # print( self.tdc_data_handler.tof_data ) 
        self.tof_plot = ax
        # self.current_tof_plot_data = self.tof_plot.hist( self.tdc_data_handler.tof_data )
        
        
    def update_mcp_hitmap( self ) :

        # print( self.tdc_data_handler.mcp_positions ) 
        # self.mcp_hitmap_plot.clear()
        # self.mcp_hitmap_plot.clear()
        # self.mcp_hitmap_fig
        
        if not use_kde :
            image, xedges, yedges = np.histogram2d( self.tdc_data_handler.candidate_mcp_positions[0],
                                                    self.tdc_data_handler.candidate_mcp_positions[1] )
            # print( image )
            im = self.mcp_hitmap_plot.imshow( image, cmap = mcp_hitmap_cmap, origin = 'lower' )
            # self.mcp_hitmap_plot.set_yticklabels( yedges )
            # self.mcp_hitmap_plot.set_xticklabels( xedges ) 

        else :
            # kernel = scipy.stats.gaussian_kde( self.tdc_data_handler.candidate_mcp_positions )
            kernel = scipy.stats.gaussian_kde( self.tdc_data_handler.candidate_mcp_positions, bw_method = 0.01 )
            x = np.linspace( kde_min, kde_max, n_kde_data + 1 )
            y = np.linspace( kde_min, kde_max, n_kde_data + 1 )

            # print( x )
            
            xx, yy = np.meshgrid( x, y )
            positions = np.vstack([xx.ravel(), yy.ravel()])
            f = np.reshape( kernel( positions ).T, xx.shape)
            print(f ) 
            im = self.mcp_hitmap_plot.imshow( f , cmap = mcp_hitmap_cmap ) 

            tick_spacing = n_kde_data // 5
            ticks = np.arange( 0, n_kde_data + 1, tick_spacing )
            tick_labels = [ '%.2f' % x[ tick ] for tick in ticks ]

            self.mcp_hitmap_plot.set_xticks( ticks )
            self.mcp_hitmap_plot.set_xticklabels( tick_labels )
            
            # self.mcp_hitmap_plot.set_xticklabels( x )
            # self.mcp_hitmap_plot.set_yticks( ticks )

            
        divider = make_axes_locatable( self.mcp_hitmap_plot ) 
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.mcp_hitmap_f.colorbar( im, cax = cax )
        

        title = 'MCP Hitmap'
        if use_kde :
            title += ': KDE'
        else :
            title += ' : binned'
        self.mcp_hitmap_plot.set_title( title )
        self.mcp_hitmap_plot.set_xlabel( 'X' )
        self.mcp_hitmap_plot.set_ylabel( 'Y' ) 
        
        
        
    def init_mcp_hitmap( self, ax, f ) :
        self.mcp_hitmap_plot = ax
        self.mcp_hitmap_f = f

        title = 'MCP Hitmap'
        if use_kde :
            title += ': KDE'
        else :
            title += ' : binned'

        ax.set_title( title )
        ax.set_xlabel( 'X' )
        ax.set_ylabel( 'Y' ) 
        
        # im = self.mcp_hitmap.imshow( self.tdc_data_handler.mcp_positions, cmap = mcp_hitmap_cmap ) 
        # self.update_mcp_hitmap() 
        # self.mcp_hitmap_plot.imshow( [ [ np.nan, np.nan ] ] ) 



    def init_r_plot( self, ax ) :
        self.r_plot = ax 

    def update_r_plot( self ) :
        self.r_plot.set_title( 'r' )
        # r = np.linalg.norm( self.tdc_data_handler.candidate_mcp_positions - mcp_center_coords,
        #                     axis = 0 ) 

    
    def init_theta_plot( self, ax ) :
        self.theta_plot = ax 

    def update_theta_plot( self ) :
        self.theta_plot.set_title( r'Angle (deg)' ) 

    
        
    def init_coords_plots( self, axarr ) :
        self.coords_plots = axarr

        
    def update_coords_plots( self ) :

        titles = [ [ 'X1', 'X2' ], [ 'Y1', 'Y2' ] ]

        for i in range(2) :
            for j in range(2) :
                self.coords_plots[i,j].clear()
                self.coords_plots[i,j].set_title( titles[i][j] ) 
                
        

        
class tabdemo( QtGui.QTabWidget ):
    def __init__(self, parent = None):
        super(tabdemo, self).__init__(parent)

        self.tdc_mgr = tdc_daq_mgr.TDC_Mgr()
        # time.sleep(5.0)
        # tdc_mgr.read()

        self.tdc_data_processor = phase_im_processing.tdc_processor( self.tdc_mgr ) 
        # tdc_data_processor.extract_candidates() 


        # self.tdc_data_handler = TDCDataHandler( data_path )
        self.tdc_plotter = TDCPlotter( self.tdc_data_processor ) 
        
        self.tab1 = QtGui.QWidget()
        self.tab2 = QtGui.QWidget()
        self.tab3 = QtGui.QWidget()

        self.addTab(self.tab1,"Data Stream")
        self.addTab(self.tab2,"Coordinates")
        self.addTab(self.tab3,"Tab 3")
        
        self.tab_updaters = [ None for i in range(3) ] 
        self.canvases = [ None for i in range(3) ] 
        
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.setWindowTitle("tab demo")
        self.resize( 1200, 800 )

        # self.tab1_axarr = None
        # self.canvas = None
        # self.toolbar = None
        # self.button = None
        
        # self.tab1_updaters = []
        # self.tab2_updaters = []
        # self.tab3_updaters = []
        
        current_tab = self.currentIndex()
        print( 'current_tab', current_tab )

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000) #trigger every second.


        
        
      
    def tab1UI( self ):
        # layout = QtGui.QFormLayout()
        # layout.addRow("Name", QtGui.QLineEdit() )
        # layout.addRow("Address", QtGui.QLineEdit() )
        # self.setTabText(0,"Contact Details")
        # self.tab1.setLayout(layout)

        f, axarr = plt.subplots( 2, 2 )

        f.subplots_adjust( hspace = 0.5 )

        self.tdc_plotter.init_mcp_hitmap( axarr[0][0], f )
        self.tdc_plotter.init_tof_plot( axarr[0][1] )
        self.tdc_plotter.init_r_plot( axarr[1][0] )
        self.tdc_plotter.init_theta_plot( axarr[1][1] )
        
        self.tab_updaters[0] = [ self.tdc_plotter.update_mcp_hitmap, self.tdc_plotter.update_tof_plot,
                                 self.tdc_plotter.update_r_plot, self.tdc_plotter.update_theta_plot ]
        
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvases[0] = FigureCanvas( f )

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        # self.toolbar = NavigationToolbar(self.canvas, self)

        # self.button = QtGui.QPushButton('Plot')
        # self.button.clicked.connect( self.update )

        # set the layout
        layout = QtGui.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvases[0])
        # layout.addWidget(self.button)
        self.tab1.setLayout(layout)

        
        
    def tab2UI( self ):

        f, axarr = plt.subplots( 2, 2 )
        self.tdc_plotter.init_coords_plots( axarr )
        self.canvases[1] = FigureCanvas( f ) 
        self.tab_updaters[1] = [ self.tdc_plotter.update_coords_plots ]
        
        # set the layout
        layout = QtGui.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        layout.addWidget(self.canvases[1])
        # layout.addWidget(self.button)
        self.tab2.setLayout(layout)
        
        # layout = QtGui.QFormLayout()
        # sex = QtGui.QHBoxLayout()
        # sex.addWidget( QtGui.QRadioButton("Male"))
        # sex.addWidget( QtGui.QRadioButton("Female"))
        # layout.addRow( QtGui.QLabel("Sex"),sex)
        # layout.addRow("Date of Birth", QtGui.QLineEdit() )
        # self.setTabText(1,"Personal Details")
        # self.tab2.setLayout(layout)
   
        
        
        
    def tab3UI( self ):
        layout = QtGui.QHBoxLayout()
        layout.addWidget( QtGui.QLabel("subjects") ) 
        layout.addWidget( QtGui.QCheckBox("Physics"))
        layout.addWidget( QtGui.QCheckBox("Maths"))
        self.setTabText( 2, "Education Details" )
        self.tab3.setLayout(layout)


    # def update_tab_1( self ) :
    #     print( 'updating tab 1 ' )
    #     data = [random.random() for i in range(10)]
    #     ax = self.tab1_axarr[0,0]
        
    #     # discards the old graph
    #     ax.clear()

    #     # plot data
    #     ax.plot(data, '*-')

    #     # refresh canvas
    #     self.canvas.draw()


    # def update_tab_2( self ) :
    #     print( 'updating tab 2' )
        

    # def update_tab_3( self ) :
    #     print( 'updating tab 3' ) 
        
    def update( self ) :

        # get the current index and update that tab 
        current_tab = self.currentIndex()

        # self.tdc_data_handler.read_data()
        self.tdc_mgr.read()
        self.tdc_data_processor.extract_candidates()
    
        
        print( 'updating tab: ', current_tab ) 

        for updater in self.tab_updaters[ current_tab ] :
            updater() 

        self.canvases[ current_tab ].draw() 

        
      
def main():
   app = QtGui.QApplication(sys.argv)
   ex = tabdemo()
   ex.show()
   sys.exit(app.exec_())


   
   
if __name__ == '__main__':  
    main()
