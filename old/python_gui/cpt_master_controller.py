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
# import zmq


USE_ZMQ = 0


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


data_path = '../data/sample_processed_data.tsv'
stream_fake_data = 1
use_kde = 1 # use kernel density estimation 

# this will hold data to be plotted in the window. will also
# do computations and file IO. no plotting functionality in this class.

class TDCDataHandler( object ) :

    def __init__( self, data_path ) :
        self.data_path = data_path
        self.mcp_positions = [ [], [] ]
        self.tof_data = []
        self.r = []
        self.theta = []
        

        # if USE_ZMQ :
        #     self.zmq_context = zmq.Context()
        #     print( 'reached' )
        #     self.zmq_socket = self.zmq_context.socket( zmq.SUB )
        #     print( 'reached' )
        #     self.zmq_socket.connect( "tcp://localhost:5556" )
        #     self.zmq_socket.setsockopt_string( zmq.SUBSCRIBE, '' )

            
        try:
            self.infile = open( data_path )
            self.filepos = 0 
        except :
            print( 'ERROR: the input file does not exist: %s' % data_path )
            sys.exit(1)

        # self.fifo_fd = open( fifo_path, 'rb' ) 


        
    # check if the infile was emptied. if so we jump back to beginning.
    def infile_was_reset( self ) :
        return 0 

    
    
    def read_data( self ) :
        # tmp = self.fifo_fd.read(5)
        # raw_data = self.zmq_socket.recv()
        # raw_data = self.zmq_socket.recv_multipart()
        
        # # numbers of sets of (x1, x2, y1, y2 )
        # ndata = len( raw_data )
        # for i in range( ndata ) :
        #      x1, x2, y1, y2, t = struct.unpack( 'qqqqq', raw_data[i] )
        #      self.process_data( x1, x2, y1, y2, t )
        with open( self.data_path ) as f :
            f.seek( self.filepos )

            if not stream_fake_data : 
                for line in f :
                    print( line )

            else :
                for i in range( 5 ) :
                    line = f.readline().strip().split( '\t' )
                    # print( line )
                    self.mcp_positions[0].append( float( line[0] ) )
                    self.mcp_positions[1].append( float( line[1] ) )
                    self.tof_data.append( float( line[2] ) )
  
            self.filepos = f.tell() 
        

             
    def process_data( self, x1, x2, y1, y2, t ) :
        absent_data = np.array( [ x2, x2, y1, y2, t ] ) == 0
        if np.sum( absent_data ) > 0 :
            return 

        else :
            x = 0.5 * 1.29 * ( x1 - x2 ) * 0.001
            y = 0.5 * 1.31 * ( y1 - y2 ) * 0.001
            tof = 0.001 * t

            self.mcp_positions.append( [x,y] )
            self.tof_data.append( tof ) 
             

        # if self.infile_was_reset() :
        #     self.reset()
        #     return

        
    def reset( self ) :
        self.current_file_line = 0
        self.mcp_positions = [ [], [] ]
        self.tof_data = []
        self.filepos = 0

        
    def data_file_was_reset( self ) :
        return 0 

    

# class Window(QtGui.QDialog):

#     def __init__(self, parent=None):
#         super(Window, self).__init__(parent)

#         # a figure instance to plot on
#         # self.figure = Figure()

#         f, axarr = plt.subplots( 2, 2 )
#         self.figure = f
#         self.axarr = axarr
        
#         # this is the Canvas Widget that displays the `figure`
#         # it takes the `figure` instance as a parameter to __init__
#         self.canvas = FigureCanvas(self.figure)

#         # this is the Navigation widget
#         # it takes the Canvas widget and a parent
#         self.toolbar = NavigationToolbar(self.canvas, self)

#         # Just some button connected to `plot` method
#         self.button = QtGui.QPushButton('Plot')
#         self.button.clicked.connect(self.plot)

#         # set the layout
#         layout = QtGui.QVBoxLayout()
#         layout.addWidget(self.toolbar)
#         layout.addWidget(self.canvas)
#         layout.addWidget(self.button)
#         self.setLayout(layout)




# # a class providing the complete set of data required to plot
# # and update data 

# class tdc_live_data_plot( object ) :

#     def __init__( self, ax, init, update ) :
#         self.ax = ax
#         self.init = init
#         self.update = update



class TDCPlotter( object ) :

    def __init__( self, tdc_data_handler ) :

        self.tdc_data_handler = tdc_data_handler
        self.mcp_hitmap_plot = None
        self.tof_plot= None
        
    def update_tof_plot( self ) :
        # print( self.tdc_data_handler.tof_data )

        # self.current_tof_plot_data = self.tof_plot.hist( self.tdc_data_handler.tof_data )
        self.tof_plot.clear() 
        self.tof_plot.hist( self.tdc_data_handler.tof_data, bins = 'fd', log = 1  ) 
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
        self.mcp_hitmap_plot.clear()
        # self.mcp_hitmap_fig
        
        if not use_kde :
            image, xedges, yedges = np.histogram2d( self.tdc_data_handler.mcp_positions[0],
                                                    self.tdc_data_handler.mcp_positions[1] )
            # print( image )
            im = self.mcp_hitmap_plot.imshow( image, cmap = mcp_hitmap_cmap ) 

        else :
            kernel = scipy.stats.gaussian_kde( self.tdc_data_handler.mcp_positions )
            x = np.linspace( -10, 10, 100 )
            y = np.linspace( -10, 10, 100 )
            xx, yy = np.meshgrid( x, y )
            positions = np.vstack([xx.ravel(), yy.ravel()])
            f = np.reshape(kernel(positions).T, xx.shape)
            im = self.mcp_hitmap_plot.imshow(  f , cmap = mcp_hitmap_cmap ) 

        
        # divider = make_axes_locatable( self.mcp_hitmap_plot ) 
        # cax = divider.append_axes("right", size="5%", pad=0.05)
        # self.mcp_hitmap_plot.colorbar(im, cax=cax)
        # self.mcp_hitmap_plot.set_xlabel( 'X' )

        title = 'MCP Hitmap'
        if use_kde :
            title += ': KDE'
        else :
            title += ' : binned'
        self.mcp_hitmap_plot.set_title( title )
        self.mcp_hitmap_plot.set_xlabel( 'X' )
        self.mcp_hitmap_plot.set_ylabel( 'Y' ) 
        
        
        
    def init_mcp_hitmap( self, ax ) :
        self.mcp_hitmap_plot = ax

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



    def init_r_histo( self, ax ) :
        self.r_histo = ax 

    def update_r_histo( self ) :
        self.r_histo.set_title( 'r' )
        r = np.linalg.norm( self.tdc_data_handler.mcp_positions - mcp_center_coords,
                            axis = 0 ) 

    
    def init_theta_histo( self, ax ) :
        self.theta_histo = ax 

    def update_theta_histo( self, ax ) :
        self.theta_histo.set_title( r'$\theta$' ) 

    
        
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

        self.tdc_data_handler = TDCDataHandler( data_path )
        self.tdc_plotter = TDCPlotter( self.tdc_data_handler ) 
        
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

        self.tdc_plotter.init_mcp_hitmap( axarr[0][0] )
        self.tdc_plotter.init_tof_plot( axarr[0][1] )
        
        self.tab_updaters[0] = [ self.tdc_plotter.update_mcp_hitmap, self.tdc_plotter.update_tof_plot ]
        
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

        self.tdc_data_handler.read_data()

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
