import config
import tdc_daq_mgr
import phase_im_processing
import gui

import sys 
import scipy.stats as st
from mpl_toolkits.axes_grid1 import make_axes_locatable
import struct 
import multiprocessing
import threading

import os
import numpy as np
import scipy
import time

import colorcet

from PyQt4 import QtGui
from PyQt4 import QtCore



import matplotlib.style as mplstyle
mplstyle.use('fast')




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


use_kde = 0 # use kernel density estimation 
kde_min = -5
kde_max = 5
n_kde_data = 100
n_cbar_ticks = 5


class TDCPlotter( object ) :

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
                
        

                
        
class tabdemo( QtGui.QTabWidget ):

    def __init__(self, parent = None):
        super(tabdemo, self).__init__( parent )

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
        self.setWindowTitle("Phase Imaging DAQ and Real-Time Analysis")
        self.resize( 1300, 900 )
                
        self.kill_update_thread = 0
        self.update_thread = threading.Thread( target = self.update_loop )
        self.update_thread.start()
        

    # automatically is called when the window is closed.
    def closeEvent(self, event): 
        print( "Closing" )
        self.kill_update_thread = 1 # self.destroy()
        
        
    def tab0UI( self ) :

        tabor_layout = QtGui.QFormLayout()
        tabor_layout.addRow( "Tabor Controls" ) 

        daq_layout = QtGui.QFormLayout()
        daq_Layout.addRow( "DAQ Controls" )

        grid_layout = QtGui.QGridLayout()
        grid_layout.addLayout( tabor_layout, 0, 0, 1, 1 )
        grid_layout.addLayout( daq_layout, 0, 1, 1, 1 ) 
        
        self.tab0.setLayout( grid_layout )
        
      
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

        mcp_hitmap_buttons = QtGui.QHBoxLayout()
        mcp_hitmap_buttons.addWidget( QtGui.QRadioButton( "KDE" ) )
        mcp_hitmap_buttons.addWidget( QtGui.QRadioButton( "Hist" ) )

        # controls_layout = QtGui.QVBoxLayout()
        # controls_layout.addLayout( mcp_hitmap_buttons )

        controls_layout = QtGui.QFormLayout()
        controls_layout.addRow( "Hitmap Display:", mcp_hitmap_buttons ) 
        
        # controls_groupbox = QGroupBox()

        # controls_groupbox.setLayout(

        grid_layout = QtGui.QGridLayout()
        grid_layout.addLayout( controls_layout, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        grid_layout.setColumnStretch( 0, 0.5 ) 
        grid_layout.addWidget( self.canvases[0], 0, 1, 1, 1 )
        grid_layout.setColumnStretch( 1, 1 ) 
        
        # set the layout
        # layout = QtGui.QHBoxLayout()
        # layout.addWidget( controls_layout )
        # layout.addWidget( self.canvases[0] )
        
        # self.tab1.setLayout(layout)
        # self.tab1.addWidget( self.canvases[0] ) 
        self.tab1.setLayout( grid_layout ) 
        
        
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

        
    def update_loop( self ) :
        while( not self.kill_update_thread ) :
            time.sleep(1)
            self.update()

        else :
            print( 'INFO: successfully killed update thread.' ) 

      
def main():
   app = QtGui.QApplication(sys.argv)
   ex = tabdemo()
   ex.show()
   sys.exit(app.exec_())


   
   
if __name__ == '__main__':  
    main()
