import config
import tdc
import tabor
# import processing
from cpt_tools.cpt_data_structures import CPTdata, LiveCPTdata
import plotter
import analysis
import cpt_tools

import sys 
import scipy.stats as st
import struct 
import threading
import datetime
import os
import numpy as np
import scipy
import time
from functools import partial


# from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QRadioButton, QTableWidget

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QPixmap
# from PyQt5 import QtGui
from PyQt5 import QtCore



from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


# CONFIG

SUBTITLE_FONT = 'arial'
SUBTITLE_SIZE = 16
SUBTITLE_WEIGHT = 3

DEFAULT_KDE_BW = 0.03

PLOTTER_WIDGET_QLINEEDIT_WIDTH = 70
MAX_SIZE_POLICY = size_policy = QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Maximum )


code_path = os.path.abspath( os.path.dirname( __file__ ) ) + '/'
# code_path = sys.path[0] + '/'
# code_path = code_path[ : code_path.rfind( '/' ) ] + '/'

MU_UNICODE = '\u03bc'


class IonEntry( object ) :

    def __init__( self ) :

        self.layout = QFormLayout()
        
        labels = [ 'Z', 'A', 'q' ]
                    
        entries = [ None, None, None ]
        defaults = [ '55', '137', '1' ]

        ion_param_validator = QIntValidator( 0, 1000 ) 

        for i in range( len( labels ) ) :
            entries[i] = QLineEdit( defaults[i] ) 
            entries[i].setValidator( ion_param_validator )
            self.layout.addRow( labels[i], entries[i] )

        self.z_entry, self.a_entry, self.q_entry = entries 
        

    def fetch( self ) :
        z = self.z_entry.text() 
        a = int( self.a_entry.text() )
        q = int( self.q_entry.text() )

        try :
            z = int( z )
        except ValueError : 
            z = cpt_tools.element_to_z

        return [ z, a, q ] 

        
        

class MetadataWidget( object ) :

    def __init__( self, cpt_data ) :

        self.cpt_data = cpt_data
        
        self.box = QGroupBox( 'Metadata' )
        
        h_labels = [ 'Counts', 'Rate (Hz)' ]
        v_labels = [ 'MCP Hits', 'Valid data', 'Penning Eject' ]
        
        self.table = QTableWidget( len( v_labels ), len( h_labels ) )
        
        size_policy = QSizePolicy( QSizePolicy.Maximum,
                                   QSizePolicy.Maximum )
        
        self.table.setSizePolicy( size_policy )
                
        self.table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        self.table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        
        self.table.setHorizontalHeaderLabels( h_labels )
        self.table.setVerticalHeaderLabels( v_labels )

        for i in range( len( v_labels ) ) :
            for j in range( len( h_labels ) ) :
                self.table.setCellWidget( i, j, QLabel( '0' ) )

        self.time_label_str = 'Active time since data reset: '
        self.time_label = QLabel( self.time_label_str )
        # self.time_label_idx = len( time_label_str )

        vbox = QVBoxLayout()
        vbox.addWidget( self.table )
        vbox.addWidget( self.time_label )
        vbox.setAlignment( QtCore.Qt.AlignTop ) 
        self.box.setLayout( vbox ) 

        
    def update( self ) :
                
        counts = [ self.cpt_data.num_mcp_hits, self.cpt_data.num_events,
                   self.cpt_data.num_penning_ejects ]

        for i in range( len( counts ) ) :
            self.table.cellWidget( i, 0 ).setText( '%d' % counts[i] )

            if self.cpt_data.duration > 0 : 
                rate = counts[i] / self.cpt_data.duration
            else :
                rate = np.nan
                
            self.table.cellWidget( i, 1 ).setText( '%.2f' % rate ) 

        self.time_label.setText( self.time_label_str + '%d'
                                 % int( self.cpt_data.duration ) )
            
        
        


class PlotterWidget( object ) :

    def __init__( self, plotter = None ) :

        if not plotter :
            plotter = plotting.Plotter()
            
        self.plotter = plotter

        self.canvas = FigureCanvas( self.plotter.f )
        self.canvas.mpl_connect( 'motion_notify_event', self.mouse_moved )        

        # mcp hitmap type
        self.plot_with_cuts_button = QCheckBox()
        self.plot_with_cuts = 0
        self.plot_with_cuts_button.setCheckState( self.plot_with_cuts ) 
        self.plot_with_cuts_button.clicked.connect( self.plot_with_cuts_clicked ) 
        
        mcp_hitmap_buttons = QHBoxLayout()
        self.mcp_kde_button = QRadioButton( 'KDE' )
        self.mcp_hist_button = QRadioButton( 'Hist' )
        self.mcp_kde_button.clicked.connect( self.set_use_kde )
        self.mcp_hist_button.click()
        self.mcp_hist_button.clicked.connect( self.disable_use_kde ) 
        mcp_hitmap_buttons.addWidget( self.mcp_kde_button ) 
        mcp_hitmap_buttons.addWidget( self.mcp_hist_button )
        
        # mcp hitmap histo bin size and kde bandwidth
        # mcp_hitmap_settings = QHBoxLayout()
        hist_nbins_validator =  QIntValidator( 0, 10000 ) 
        self.mcp_bin_width_entry = QLineEdit( str( self.plotter.mcp_bin_width ) )
        self.mcp_bin_width_entry.setValidator( QDoubleValidator(0., 10000., 10 ) )
        self.mcp_bin_width_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        self.mcp_kde_bw_entry = QLineEdit( str( DEFAULT_KDE_BW ) )
        self.mcp_kde_bw_entry.setValidator( QDoubleValidator( 0.0, 10000., 10 ) )
        self.mcp_kde_bw_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        # mcp_hitmap_settings.addWidget( self.mcp_hist_bin_size_entry ) 
        # mcp_hitmap_settings.addWidget( self.mcp_kde_bw_entry ) 

        # mcp hitmap bounds inputs

        self.mcp_bounds_entries = np.zeros( (2,2), dtype = object )
        mcp_bounds_layouts = np.zeros(2, dtype = object ) 
        defaults = np.array( [[-5,5], [-5,5]] )
        mcp_hitmap_bounds_validator = QDoubleValidator( -1000, 1000, 10 )
        
        for i in range(2) :
            mcp_bounds_layouts[i] = QHBoxLayout()
            for j in range(2) :
                self.mcp_bounds_entries[i,j] = QLineEdit( str( defaults[i,j] ) )
                self.mcp_bounds_entries[i,j].setValidator( mcp_hitmap_bounds_validator )
                self.mcp_bounds_entries[i,j].setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH )
                mcp_bounds_layouts[i].addWidget( self.mcp_bounds_entries[i,j] )
            
                
        self.tof_hist_nbins_entry =  QLineEdit( str(0) )
        self.tof_hist_nbins_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        self.tof_hist_nbins_entry.setValidator( hist_nbins_validator )
        
        self.r_hist_nbins_entry =  QLineEdit( str(0) )
        self.r_hist_nbins_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        self.r_hist_nbins_entry.setValidator( hist_nbins_validator )
        
        self.angle_hist_nbins_entry =  QLineEdit( str(0) )
        self.angle_hist_nbins_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        self.angle_hist_nbins_entry.setValidator( hist_nbins_validator ) 

        
        # tof cut entry 
        tof_bounds = QHBoxLayout()
        
        self.tof_lower_cut_entry = QLineEdit( str( self.plotter.cpt_data.tof_cut_lower ) )
        self.tof_lower_cut_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH )
        self.tof_lower_cut_entry.setValidator( QDoubleValidator(0., 10000., 10 ) )

        self.tof_upper_cut_entry = QLineEdit( str( self.plotter.cpt_data.tof_cut_upper ) )
        self.tof_upper_cut_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        self.tof_upper_cut_entry.setValidator( QDoubleValidator(0., 10000., 10 ) )

        tof_bounds.addWidget( self.tof_lower_cut_entry ) 
        tof_bounds.addWidget( self.tof_upper_cut_entry )

        r_bounds = QHBoxLayout() 
        
        self.r_lower_cut_entry = QLineEdit( str(0) )
        self.r_lower_cut_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH )
        self.r_lower_cut_entry.setValidator( QDoubleValidator( 0, 10000, 3 ) )
        
        self.r_upper_cut_entry = QLineEdit( str(0) )
        self.r_upper_cut_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH )
        self.r_upper_cut_entry.setValidator( QDoubleValidator( 0, 10000, 3 ) )

        r_bounds.addWidget( self.r_lower_cut_entry )
        r_bounds.addWidget( self.r_upper_cut_entry ) 

        layout = QVBoxLayout()

        reload_button = QPushButton( 'Reload Parameters' ) 
        reload_button.clicked.connect( self.reload_visualization_params )         
        layout.addWidget( reload_button ) 
        
        controls_box = QGroupBox( 'Visualization Controls' )
        controls_layout = QFormLayout()
        # subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE,
        #                                QFont.Bold ) )

        # controls_layout.addRow( subtitle )
        controls_layout.addRow( 'Plot with Cuts', self.plot_with_cuts_button ) 
        controls_layout.addRow( 'Hitmap Type:', mcp_hitmap_buttons )
        # controls_layout.addRow( mcp_hitmap_settings )
        controls_layout.addRow( 'MCP bin width (mm):', self.mcp_bin_width_entry )
        controls_layout.addRow( 'MCP KDE bandwidth:', self.mcp_kde_bw_entry )
        controls_layout.addRow( 'MCP X Bounds:', mcp_bounds_layouts[0] ) 
        controls_layout.addRow( 'MCP Y Bounds:', mcp_bounds_layouts[1] ) 
        controls_layout.addRow( 'TOF hist num bins:', self.tof_hist_nbins_entry )
        controls_layout.addRow( 'Radius hist num bins:', self.r_hist_nbins_entry )
        controls_layout.addRow( 'Angle hist num bins:', self.angle_hist_nbins_entry )

        zoom_buttons = QHBoxLayout()

        zoom_in_button = QPushButton( 'Zoom In' )
        zoom_in_button.clicked.connect( self.zoom_in )
        zoom_buttons.addWidget( zoom_in_button ) 

        zoom_out_button = QPushButton( 'Zoom Out' )
        zoom_out_button.clicked.connect( self.zoom_out )
        zoom_buttons.addWidget( zoom_out_button )
        
        controls_layout.addRow( zoom_buttons ) 
        
        controls_box.setLayout( controls_layout )
        layout.addWidget( controls_box ) 
        
        # subtitle = QLabel( 'Data Cuts' )
        # subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE, QFont.Bold ) )
        # controls_layout.addRow( subtitle )

        cuts_box = QGroupBox( 'Data Cuts' ) 
        cuts_layout = QFormLayout() 
        cuts_layout.addRow( 'TOF lower / upper bounds:', tof_bounds ) 
        cuts_layout.addRow( 'Radius Cut:', r_bounds ) 
        cuts_box.setLayout( cuts_layout )
        layout.addWidget( cuts_box ) 

        fits_box = QGroupBox( 'Gaussian Fitting' )
        # fits_layout = QVBoxLayout()
        # fits_layout.setSpacing(0)
        
        self.fit_widget = FitWidget( self.plotter.all_hists ) 

               # self.tof_fit_widget = FitWidget( 'TOF', self.plotter.tof_hist )
               # self.angle_fit_widget = FitWidget( 'Angle', self.plotter.angle_hist )
               # self.radius_fit_widget = FitWidget( 'Radius', self.plotter.radius_hist )

        # fits_layout.addLayout( self.tof_fit_widget.layout ) 
        # fits_layout.addLayout( self.angle_fit_widget.layout ) 
        # fits_layout.addLayout( self.radius_fit_widget.layout ) 
        
        fits_box.setLayout( self.fit_widget.layout )
        layout.addWidget( fits_box ) 

        self.metadata_widget = MetadataWidget( self.plotter.cpt_data )
        layout.addWidget( self.metadata_widget.box )

        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget( self.canvas )

        self.coords_label = QLabel() 
        
        canvas_layout.addWidget( self.coords_label )

        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout( layout, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        self.grid_layout.setColumnStretch( 0, 0.5 ) 
        self.grid_layout.addLayout( canvas_layout, 0, 1, 1, 1 )
        self.grid_layout.setColumnStretch( 1, 1 ) 

        
    def update( self, update_first = 0 ) :
        if not update_first : 
            self.canvas.draw()
            
        self.plotter.update_all()
        self.metadata_widget.update()

        if update_first :
            self.canvas.draw()

            
    # deallocate plotter 
    def release( self ) :
        plotter.release()
        
    def plot_with_cuts_clicked( self ) :
        plot_with_cuts = self.plot_with_cuts_button.checkState() 
        self.plotter.set_plot_with_cuts( plot_with_cuts ) 
        
    def set_use_kde( self ) :
        self.plotter.use_kde = 1 

    def disable_use_kde( self ) :
        self.plotter.use_kde = 0 

    def reload_visualization_params( self ) :
        self.plotter.mcp_bin_width = float( self.mcp_bin_width_entry.text() )
        self.plotter.mcp_kde_bandwidth = float( self.mcp_kde_bw_entry.text() )

        self.plotter.mcp_x_bounds = np.array( [ float( self.mcp_bounds_entries[0,j].text() )
                                                for j in range(2) ] )

        self.plotter.mcp_y_bounds = np.array( [ float( self.mcp_bounds_entries[1,j].text() )
                                                for j in range(2) ] )
                
        self.plotter.tof_hist_nbins = int( self.tof_hist_nbins_entry.text() ) 
        self.plotter.r_hist_nbins = int( self.r_hist_nbins_entry.text() ) 
        self.plotter.angle_hist_nbins = int( self.angle_hist_nbins_entry.text() )

        self.plotter.cpt_data.tof_cut_lower = float( self.tof_lower_cut_entry.text() )
        self.plotter.cpt_data.tof_cut_upper = float( self.tof_upper_cut_entry.text() )

        self.plotter.tof_hist.n_bins = float( self.tof_hist_nbins_entry.text() )
        self.plotter.radius_hist.n_bins = float( self.r_hist_nbins_entry.text() )
        self.plotter.angle_hist.n_bins = float( self.angle_hist_nbins_entry.text() )
        
        
        # self.plotter.clear()
        if self.plotter.cpt_data.is_live : 
            self.plotter.cpt_data.reset_cuts()
        # self.plotter.cpt_data.apply_cuts()
        
        self.plotter.rebuild_mcp_plot = 1

        self.update()


    def zoom_in( self ) :

        bounds = [ self.plotter.mcp_x_bounds, self.plotter.mcp_y_bounds ]
        new_bounds = [ None, None ]
        for i in range(2) :
            new_bounds[i] = bounds[i] + np.array( [ 2.5, -2.5 ] )
            print( new_bounds[i] )
            if new_bounds[i][1] <= new_bounds[i][0] :
                print( 'WARNING: unable to zoom in' ) 
                return 

        for i in range(2) :
            for j in range(2) : 
                self.mcp_bounds_entries[i,j].setText( str( new_bounds[i][j] ) )

        self.reload_visualization_params() 
        self.update()
        
        
    def zoom_out( self ) :
        
        bounds = [ self.plotter.mcp_x_bounds, self.plotter.mcp_y_bounds ]
        new_bounds = [ None, None ]
        for i in range(2) :
            new_bounds[i] = bounds[i] + np.array( [ -2.5, 2.5 ] )
            print( new_bounds[i] ) 
            if new_bounds[i][1] <= new_bounds[i][0] :
                print( 'WARNING: unable to zoom in' ) 
                return 

        for i in range(2) :
            for j in range(2) : 
                self.mcp_bounds_entries[i,j].setText( str( new_bounds[i][j] ) )

        self.reload_visualization_params() 
        self.update()

        
        
    def set_cpt_data( self, cpt_data ) :
        self.plotter.set_cpt_data( cpt_data ) 
        self.metadata_widget.cpt_data = cpt_data
        

    def mouse_moved( self, mouse_event ) :
        if mouse_event.inaxes:
            x, y = mouse_event.xdata, mouse_event.ydata
            self.coords_label.setText( '(%.2f, %.2f)' % (x ,y ) )



            
                                       
class FitWidget( object ) :

    def __init__( self, plotter_hist_list ) :

        self.layout = QVBoxLayout()

        self.hists = plotter_hist_list 

        params_labels = [ 'A', '\u03c3', '\u03bc', '\u03c72' ]
        self.num_params = len( params_labels ) 

        h_labels = [ '', '', 'Left', 'Right' ]
        h_labels.extend( params_labels ) 
        v_labels = [ x.title for x in plotter_hist_list ] 
        
        nrows = len( v_labels )
        ncols = len( h_labels ) 

        self.table = QTableWidget( nrows, ncols ) 
        self.table.setMinimumWidth( 400 ) 

        # size_policy = QSizePolicy( QSizePolicy.Maximum,
        #                            QSizePolicy.Maximum )
        
        # self.table.setSizePolicy( size_policy )
                
        self.table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        self.table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        # header = self.table.horizontalHeader() 
        # header.setSectionResizeMode( 0, QHeaderView.Stretch )
        # for j in range( 1, len( h_labels ) ) : 
        #     header.setSectionResizeMode( j, QHeaderView.ResizeToContents )
        
        self.table.setHorizontalHeaderLabels( h_labels )
        self.table.setVerticalHeaderLabels( v_labels )

        self.bounds_entries = [] 
        self.params_labels = []
        fit_buttons = []
        delete_buttons = [] 
        
        for i in range( len( plotter_hist_list ) ) :
            
            self.bounds_entries.append( [ QLineEdit(), QLineEdit() ] )
            self.params_labels.append( [ QLabel() for i in range( self.num_params ) ] )

            fit_buttons.append( QPushButton( 'Fit' ) )
            delete_buttons.append( QPushButton( 'Delete' ) )
 
            fit_buttons[i].clicked.connect( lambda state, a=i : self.fit_button_clicked( a ) )
            delete_buttons[i].clicked.connect( lambda state, a=i : self.delete_button_clicked( a ) )
            # fit_buttons[i].clicked.emit() 

            self.table.setCellWidget( i, 0, fit_buttons[i] )
            self.table.setCellWidget( i, 1, delete_buttons[i] ) 

            self.table.setCellWidget( i, 2, self.bounds_entries[i][0] )
            self.table.setCellWidget( i, 3, self.bounds_entries[i][1] )

            for j in range( self.num_params ) :
                self.table.setCellWidget( i, 4 + j, self.params_labels[i][j] )

            # self.left_x_bound_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
            # self.right_x_bound_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        
        # self.layout.setSpacing(0)
        # self.layout.addLayout( label_layout ) 

        self.layout.addWidget( self.table )
        

        
    def fit_button_clicked( self, i ) :
                
        try : 
            left_x_bound = float( self.bounds_entries[i][0].text() )
            right_x_bound = float( self.bounds_entries[i][1].text() )
        except :
            print( 'WARNING: please specify bounds for fit' )
            return

        bounds = [ left_x_bound, right_x_bound ]    
        fit = self.hists[i].apply_fit( bounds ) 
        if fit is None :
            return
        
        params, params_errors, redchisqr = fit
        
        if params_errors is not None : 
            labels = [ '%.2f\u00b1%.2f' % ( params[j], params_errors[j] ) for j in range( len(params) ) ]
        else :
            labels = [ '%.2f' % params[j] for j in range( len(params) ) ]
            
        labels.append( '%.2f' % redchisqr )
        for j in range( len(params) + 1 ) : 
            self.params_labels[i][j].setText( labels[j] ) 
            
        # ret = analysis.gaussian_fit( self.cpt_data ) 
        

    def delete_button_clicked( self, i ) :
        self.hists[i].remove_fit() 
    




class CombinedAnalysisWidget( object ) :

    def __init__( self ) :
                
        data_box = QGroupBox( 'Processed Data' ) 
        data_layout = QVBoxLayout()
        data_box.setLayout( data_layout ) 

        self.mass_label_str = 'Current Mass Estimate: '
        self.mass_estimate_label = QLabel( self.mass_label_str + '?' ) 
        
        data_cols = [ 'Accumulation \nTime (ms)', 'Measured \u0394\u03B8 (deg)' ]
        self.data_table = QTableWidget( 1, len( data_cols ) )
        self.data_table.setHorizontalHeaderLabels( data_cols )
        self.data_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        # self.data_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )


        data_layout.addWidget( self.mass_estimate_label ) 
        data_layout.addWidget( self.data_table )

        for i in range( len( data_cols ) ) :
            self.data_table.setColumnWidth( i, 100 ) 
        # self.data_table.setSizePolicy( MAX_SIZE_POLICY )

        
        self.data_table.setMinimumWidth( 250 ) 
        # self.data_table.resizeColumnsToContents()
        
        # self.data_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch)

        # self.data_table.setSizeAdjustPolicy( QAbstractScrollArea.AdjustToContents )
        # self.data_table.resizeColumnsToContents()
        # self.data_table.resizeColumnsToContents()

        
        # setTableWidth( self.data_table ) 
        
        predictions_box = QGroupBox( 'Predictions' ) 
        predictions_layout = QVBoxLayout()
        predictions_box.setLayout( predictions_layout )
                
        predictions_cols = [ 'Accumulation \nTime (ms)',
                             'Corrected \u0394\u03B8 \nPrediction (deg)',
                             'AME \u0394\u03B8 \nPrediction (deg)' ]
        self.predictions_table = QTableWidget( 1, len( predictions_cols ) )
        self.predictions_table.setHorizontalHeaderLabels( predictions_cols )
        self.predictions_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        # self.predictions_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        self.predictions_table.setMinimumWidth( 400 )
        predictions_layout.addWidget( self.predictions_table ) 
        # self.predictions_table.setSizePolicy( MAX_SIZE_POLICY )


        canvas_box = QGroupBox( 'Visualization' ) 
        canvas_layout = QVBoxLayout() 
        self.analyzer = analysis.CPTanalyzer()
        self.canvas = FigureCanvas( self.analyzer.f )
        canvas_layout.addWidget( self.canvas )
        canvas_box.setLayout( canvas_layout ) 

        
        self.layout = QHBoxLayout() 
        self.layout.addWidget( data_box )
        self.layout.addWidget( predictions_box ) 
        self.layout.addWidget( canvas_box )        

        # self.layout = QGridLayout()
        # # self.layout.addWidget( data_box, 0, 0, 0, 0, QtCore.Qt.AlignLeft )
        # self.layout.addWidget( data_box, 0, 0 )
        # # self.layout.setColumnStretch( 0, 1 ) 
        # self.layout.addWidget( predictions_box, 0, 1 )
        # # self.layout.setColumnStretch( 1, 0.25 ) 
        # #self.layout.addWidget( canvas_box, 0, 2 ) 
        # # self.layout.setColumnStretch( 2, 0 ) 
        

    # def update( self ) :
    #     self.analyzer.update()
    #     self.canvas.draw() 
        


        
        
        
class gui( QTabWidget ):
    
    def __init__(self, parent = None):
        super( gui, self ).__init__( parent )

        self.date_str = datetime.datetime.now().strftime( '%Y_%m_%d' )
        self.data_dir_path = code_path + '../data/'
        self.session_dir_path = None
                
        try :
            os.makedirs( self.data_dir_path, exist_ok = 1 )
        except :
            pass

        self.session_dir_path = self.data_dir_path
        
        
        # the 3 custom classes we will be using to manage DAQ, processing, and plots
        self.tdc = tdc.TDC()
        self.tabor = tabor.Tabor() 
        self.processor = LiveCPTdata( self.tdc ) 
        self.plotter = plotter.Plotter( self.processor )
                
        ( self.controls_tab_idx,
          self.processed_data_tab_idx,
          self.analysis_1_tab_idx,
          self.analysis_2_tab_idx,
          self.tools_tab_idx,
          self.help_tab_idx ) = range(6)
        
        self.controls_tab = QWidget() 
        self.processed_data_tab = QWidget()
        # self.unprocessed_data_tab = QWidget()
        self.analysis_1_tab = QWidget()
        self.analysis_2_tab = QWidget()
        self.tools_tab = QWidget() 
        self.help_tab = QWidget()
        
        tabs = [ self.controls_tab, self.processed_data_tab,
                 # self.unprocessed_data_tab,
                 self.analysis_1_tab,
                 self.analysis_2_tab,
                 self.tools_tab,
                 self.help_tab ]

        tab_idxs = [ self.controls_tab_idx, self.processed_data_tab_idx,
                     # self.unprocessed_data_tab_idx,
                     self.analysis_1_tab_idx,
                     self.analysis_2_tab_idx,
                     self.tools_tab_idx,
                     self.help_tab_idx ]

        tab_names = [ 'DAQ / Tabor / Output', 'Data Stream',
                      # 'Unprocessed Data',
                      'Isolated Analysis', 'Combined Analysis', 'Tools', 'Help' ]
        
        self.num_tabs = len( tabs ) 
        
        for i in range( self.num_tabs ) :
            self.insertTab( tab_idxs[i], tabs[i], tab_names[i] )
        
        self.tab_updaters = [ None for i in range( self.num_tabs ) ] 
        self.canvases = [ None for i in range( self.num_tabs ) ] 

        self.controls_tab_init()
        self.processed_data_tab_init()
        # self.unprocessed_data_tab_init()
        self.analysis_1_tab_init()
        self.analysis_2_tab_init() 
        self.tools_tab_init() 
        self.help_tab_init() 
        
        self.setWindowTitle("Phase Imaging DAQ and Real-Time Analysis")
        self.resize( 1300, 900 )
                
        self.kill_update_thread = 0
        self.thread_lock = threading.Lock() 
        self.update_thread = threading.Thread( target = self.update_loop )
        self.update_thread.start()

        

    # this automatically is called when the window is closed.
    def closeEvent( self, event ): 
        # this is checked by the thread which then terminates within 1 second
        self.kill_update_thread = 1 # self.destroy()

        
        
    def controls_tab_init( self ) :

        tab_idx = self.controls_tab_idx
        
        tabor_box = QGroupBox( 'Tabor Controls' ) 
        tabor_layout = QVBoxLayout()
        tabor_box.setLayout( tabor_layout ) 
        
        # don't expand to take more room than necessary 
        # tabor_layout.setFieldGrowthPolicy( 0 ) 
            
        # subtitle = self.make_subtitle( 'Tabor Controls' ) 
        # tabor_layout.addRow( subtitle )
        
        self.load_tabor_button = QPushButton( 'Load Tabor Parameters' )
        self.load_tabor_button.clicked.connect( self.load_tabor_button_clicked ) 
        tabor_layout.addWidget( self.load_tabor_button ) 

        tmp = QFormLayout()
        
        self.num_steps_entry = QLineEdit( '5' )
        tmp.addRow( 'Num Steps:', self.num_steps_entry ) 

        self.tacc_entry = QLineEdit( '68' )
        tmp.addRow( 'Accumulation Time (%ss):' % MU_UNICODE, self.tacc_entry ) 

        tabor_layout.addLayout( tmp ) 
        
        nrows = 5
        ncols = 3 
        
        self.tabor_table = QTableWidget( nrows, ncols )
        
        # combination of size policy change and resizemode change
        # makes the table not expand more than necessary 
        size_policy = QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Maximum )
        
        # self.tabor_table.setSizePolicy( size_policy )
        # self.load_tabor_button.setSizePolicy( size_policy ) 
        
        self.tabor_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        self.tabor_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        
        self.tabor_table.setHorizontalHeaderLabels( [ 'w_-', 'w_+', 'w_c' ] )
        self.tabor_table.setVerticalHeaderLabels( [ 'omega', 'phase', 'amp',
                                               'loops', 'length' ] )
        
        defaults = [ [ 1600.0, 656252.0, 657844.5 ],
                     [ -140.0, 0.0, 0.0 ],
                     [ 0.0005, 0.2, 0.5 ],
                     [ 1, 100, 208 ],
                     [ 3, 1, 1 ]
        ]
                
        omega_validator = QDoubleValidator( 0, 1e8, 4 ) 
        phase_validator = QDoubleValidator( -180.0, 180.0, 4 ) 
        amp_validator = QDoubleValidator( 0, 1.0, 4 ) 
        int_validator = QIntValidator( 0, 300 ) 
        
        validators = [
            [ omega_validator ] * 3,
            [ phase_validator ] * 3,
            [ amp_validator ] * 3,
            [ int_validator ] * 3,
            [ int_validator ] * 3
        ]
        
        for i in range( nrows ) :
            for j in range( ncols ) :
                tmp = QLineEdit( str( defaults[i][j] ) )
                tmp.setValidator( validators[i][j] )
                self.tabor_table.setCellWidget( i,j, tmp )

        tabor_layout.addWidget( self.tabor_table )

        self.set_params_from_ion_data_button = QPushButton( 'Set Params From Ion Data' )
        self.set_params_from_ion_data_button.clicked.connect(
            self.set_params_from_ion_data_button_clicked ) 
        tabor_layout.addWidget( self.set_params_from_ion_data_button )

        self.tabor_ion_entry = IonEntry()
        tabor_layout.addLayout( self.tabor_ion_entry.layout ) 

        self.set_params_from_ion_data_button_clicked()
        
        # tabor_controls_grid = QGridLayout()
        # tabor_layout.addLayout( tabor_controls_grid ) 

        self.toggle_daq_button = QPushButton() 
        tmp = lambda state : self.toggle_daq_button_clicked( 1 ) 
        self.toggle_daq_button.clicked.connect( tmp ) 
        self.toggle_daq_button_clicked( toggle = 0 ) 
        
        # self.toggle_daq_button.setSizePolicy( size_policy )
        
        self.clear_button = QPushButton( 'Clear' )
        self.clear_button.clicked.connect( self.clear_button_clicked ) 
        # self.clear_button.setSizePolicy( size_policy )
        
        self.save_button = QPushButton( 'Save' )
        self.save_button.clicked.connect( self.save_button_clicked )
        # self.save_button.setSizePolicy( size_policy )
        
        daq_box = QGroupBox( 'DAQ / Output Controls' ) 
        daq_layout = QFormLayout()
        daq_box.setLayout( daq_layout )
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget( self.toggle_daq_button )
        buttons_layout.addWidget( self.clear_button )
        buttons_layout.addWidget( self.save_button ) 
        daq_layout.addRow( buttons_layout ) 
                
        self.alternate_name_entry = QLineEdit()
        daq_layout.addRow( 'Alternate Name', self.alternate_name_entry )
        
        # self.session_name_entry = QLineEdit()
        # daq_layout.addRow( 'Session Name', self.session_name_entry )

        self.experimenter_entry = QLineEdit()
        daq_layout.addRow( 'Experimenter', self.experimenter_entry ) 

        self.comment_entry = QTextEdit()
        daq_layout.addRow( 'Session Comments', self.comment_entry ) 

        metadata_widget = MetadataWidget( self.processor )


        batch_box = QGroupBox( 'Batch Instructions' )
        batch_layout = QHBoxLayout() 
        batch_box.setLayout( batch_layout )

        self.batch_button = QPushButton( 'Start Batch' ) 

        rows = [ 'Accumulation\nTime (\u03BCs)' ]
        ncols = 20 
        self.batch_table = QTableWidget( len( rows ), ncols )
        self.batch_table.setVerticalHeaderLabels( rows )
        # self.batch_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        self.batch_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        self.batch_table.setMinimumWidth( 1000 ) 
        for i in range( ncols ) :
            tmp = QLineEdit()
            tmp.setValidator( QIntValidator( 1, int(1e7) ) ) 
            self.batch_table.setCellWidget( 0, i, tmp )
        
        batch_input_layout = QFormLayout()
        batch_start_button = QPushButton( 'Start Batch' ) 
        batch_input_layout.addRow( batch_start_button ) 
        self.batch_stop_time_entry = QLineEdit()
        batch_input_layout.addRow( 'Stop Time (s)', self.batch_stop_time_entry )
        self.batch_stop_counts_entry = QLineEdit()
        batch_input_layout.addRow( 'Stop Counts', self.batch_stop_counts_entry )
        generate_linspace_button = QPushButton( 'Generate Linspace' )
        generate_linspace_button.clicked.connect( self.batch_generate_linspace ) 
        batch_input_layout.addRow( generate_linspace_button )
        self.linspace_start_entry = QLineEdit( '0' ) 
        batch_input_layout.addRow( 'Linspace Start', self.linspace_start_entry )
        self.linspace_stop_entry = QLineEdit( '1000' ) 
        batch_input_layout.addRow( 'Linspace Stop (ms)', self.linspace_stop_entry )
        self.linspace_num_data_entry = QLineEdit( '11' ) 
        batch_input_layout.addRow( 'Linspace Num Data', self.linspace_num_data_entry )
        
        batch_layout.addLayout( batch_input_layout ) 
        batch_layout.addWidget( self.batch_table ) 
        
        top_layout = QHBoxLayout()
        top_layout.addWidget( tabor_box )
        top_layout.addWidget( daq_box )
        top_layout.addWidget( metadata_widget.box )

        # bottom_layout = QHBoxLayout()
        # bottom_layout.addWidget( batch_box )
        
        layout = QVBoxLayout()
        layout.addLayout( top_layout ) 
        layout.addWidget( batch_box ) 
        
        # layout.setContentsMargins(200,100,200,10)
        
        self.controls_tab.setLayout( layout )
        self.tab_updaters[ tab_idx ] = [ metadata_widget.update ]

        


        
    def processed_data_tab_init( self ):

        tab_idx = self.processed_data_tab_idx
        
        processed_data_plotter_widget = PlotterWidget( self.plotter )
        
        # matplotlib canvas 
        self.canvases[ tab_idx ] = processed_data_plotter_widget.canvas

        
        # self.toolbar = NavigationToolbar( self.canvases[ tab_idx ], self )

        self.tab_updaters[ tab_idx ] = [ processed_data_plotter_widget.update ]
        
        self.processed_data_tab.setLayout( processed_data_plotter_widget.grid_layout ) 
        

        
    # def unprocessed_data_tab_init( self ):

    #     tab_idx = self.unprocessed_data_tab_idx 
        
    #     f, axarr = plt.subplots( 2, 2 )
    #     self.plotter.init_coords_plots( axarr )
    #     self.canvases[ tab_idx ] = FigureCanvas( f ) 
    #     self.tab_updaters[ tab_idx ] = [ self.plotter.update_coords_plots ]
        
    #     # set the layout
    #     layout = QVBoxLayout()
    #     # layout.addWidget(self.toolbar)

    #     layout.addWidget( self.canvases[ tab_idx ] )
        
    #     self.unprocessed_data_tab.setLayout( layout )


        
        
    def analysis_1_tab_init( self ):

        self.analyzer = analysis.CPTanalyzer()
        analysis_plotter = plotter.Plotter( CPTdata() ) 
        self.analysis_plotter_widget = PlotterWidget( analysis_plotter ) 
        
        tab_idx = self.analysis_1_tab_idx 
        
        self.analysis_data_dirs_qlist = QListWidget()
        self.analysis_data_dirs_qlist.itemClicked.connect( self.set_analysis_plotter_data ) 
        # self.analysis_data_dirs_qlist.addItem( 'test' )

        analysis_controls_box = QGroupBox( 'Choose Files for Analysis' ) 
        analysis_controls_layout = QVBoxLayout()

        # tmp = QHBoxLayout()
        # tmp.addWidget( QLabel( 'Display Isolated Dataset' ) )
        # self.analysis_display_isolated_dataset = 0
        # self.isolated_dataset_checkbox = QCheckBox()
        # self.isolated_dataset_checkbox.setCheckState( self.analysis_display_isolated_dataset )
        # self.isolated_dataset_checkbox.clicked.connect( self.toggle_isolated_dataset ) 
        # tmp.addWidget( self.isolated_dataset_checkbox )
        # analysis_controls_layout.addLayout( tmp ) 
        
        analysis_controls_layout.addWidget( self.analysis_data_dirs_qlist )
        
        
        buttons = QHBoxLayout()
        add_button = QPushButton( 'Add' )
        add_button.clicked.connect( self.add_button_clicked ) 
        delete_button = QPushButton( 'Delete' )
        delete_button.clicked.connect( self.delete_button_clicked ) 
        buttons.addWidget( add_button )
        buttons.addWidget( delete_button )
        analysis_controls_layout.addLayout( buttons ) 

        analysis_controls_box.setLayout( analysis_controls_layout ) 
        
        # layout.addWidget( self.analysis_data_dirs_qlist )
        # layout.addWidget( self.canvases[ tab_idx ] )
        # self.analysis_tab.setLayout( layout )

        # plotting 
        # f, axarr = plt.subplots( 2, 2 )
        # f.subplots_adjust( hspace = 0.5 )
        # self.canvases[ tab_idx ] = FigureCanvas( self.analysis_plotter.f )

        # self.tab_updaters[ tab_idx ] = [ self.analysis_plotter_widget.update ]

        layout = QHBoxLayout()
        layout.addWidget( analysis_controls_box )
        layout.addLayout( self.analysis_plotter_widget.grid_layout ) 
        
        # layout = QGridLayout()
        # layout.addWidget( analysis_controls_box, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        # layout.setColumnStretch( 0, 0.5 ) 
        # layout.addWidget( self.canvases[ tab_idx ], 0, 1, 1, 1 )
        # layout.setColumnStretch( 1, 1 ) 
        
        self.analysis_1_tab.setLayout( layout )


        
    def analysis_2_tab_init( self ) :

        tmp = CombinedAnalysisWidget() 
        
        self.analysis_2_tab.setLayout( tmp.layout )

        

    def tools_tab_init( self ) :

        tab_idx = self.tools_tab_idx 

        layout = QVBoxLayout()

        mass_identifier_box = QGroupBox( 'Mass Identifier' )
        # mass_identifier_box.setStyleSheet( '
        tmp = QFormLayout()
        self.tools_freq_entry = QLineEdit( '616024' ) 
        tmp.addRow( 'Cyclotron Frequency', self.tools_freq_entry )
        self.tools_freq_delta_entry = QLineEdit( '0.5' ) 
        tmp.addRow( 'Cyclotron Frequency Uncertainty', self.tools_freq_delta_entry )

        mass_identifier_button = QPushButton( 'Look Up' )
        mass_identifier_button.clicked.connect( self.mass_identifier_button_clicked ) 
        tmp.addRow( mass_identifier_button )
        table_cols = [ 'Freq', 'Name', 'q', 'A', 'Z', 'N', 'T_{1/2}',
                       'Cf yield', 'Rel Natural Abund' ]
        self.mass_identifier_table = QTableWidget( 1, len( table_cols ) )
        self.mass_identifier_table.setHorizontalHeaderLabels( table_cols )
        
        self.mass_identifier_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        self.mass_identifier_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        
        tmp.addRow( self.mass_identifier_table ) 
        mass_identifier_box.setLayout( tmp ) 

        property_lookup_box = QGroupBox( 'Nuclide Property Lookup' )
        # tmp_layout = QVBoxLayout
        tmp = QVBoxLayout()

        self.tools_property_ion_entry = IonEntry()
        tmp.addLayout( self.tools_property_ion_entry.layout )
        
        self.tools_property_button = QPushButton( 'Look Up' ) 
        self.tools_property_button.clicked.connect( self.property_lookup_button_clicked ) 
        
        tmp.addWidget( self.tools_property_button ) 
        # tmp_layout.addLayout( tmp ) 
        property_lookup_box.setLayout( tmp )

        property_lookup_cols = [ 'Freq', 'Mass', 'T_{1/2}', 'Cf yield', 'Rel Natural Abund' ]
        self.property_lookup_table = QTableWidget( 1, len( property_lookup_cols ) )
        self.property_lookup_table.setHorizontalHeaderLabels( property_lookup_cols )

        self.property_lookup_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        self.property_lookup_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )

        for i in range( len( property_lookup_cols ) ) :
            self.property_lookup_table.setCellWidget( 0, i, QLabel( '' ) )
                                
        tmp.addWidget( self.property_lookup_table ) 

        layout.addWidget( mass_identifier_box ) 
        layout.addWidget( property_lookup_box ) 
        
        self.tools_tab.setLayout( layout ) 
        



    def help_tab_init( self ) :
        layout = QVBoxLayout()

        # subtitles = [ 'Histogram Bin Sizes' ]

        # messages = [
        #     'For all histograms, the default, recommended value of 0 uses the Freedman-Diaconis rule to dynamically select the bin size during each update.'
        # ]

        # for i in range( len( subtitles ) ) :

        #     subtitle = QLabel( subtitles[i] )
        #     subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE, QFont.Bold ) )

        #     message = QLabel( messages[i] )
        #     message.setWordWrap( 1 ) 
            
        #     layout.addWidget( subtitle )
        #     layout.addWidget( message )

        try : 
            label = QLabel()
            morrison_path = code_path + '../images/jim-morrison-og.jpg'
            # print( morrison_path )
            # print( os.path.exists( morrison_path ) ) 
            pixmap = QPixmap( morrison_path ) 
            label.setPixmap( pixmap )        
            layout.addWidget( label )
            
        except :
            print( 'ERROR: please put a picture of Jim Morisson in ../images/jim-morrison-og.jpg' )
            # sys.exit(0)
            
        
        self.help_tab.setLayout( layout ) 
        

        
    def update( self ) :

        # get the current index and update that tab 
        current_tab = self.currentIndex()

        # prevent tdc read 
        with self.thread_lock : 
            self.tdc.read()
            self.processor.extract_candidates()
    
        updaters = self.tab_updaters[ current_tab ]
        if updaters is not None :
            for updater in updaters : 
                updater() 

        # draw canvas if it exists 
        mpl_canvas = self.canvases[ current_tab ]
        if mpl_canvas is not None :
            mpl_canvas.draw() 

            
        
    def update_loop( self ) :
        # time.sleep(1)
        while( not self.kill_update_thread ) :
            time.sleep(1)
            self.update()

        else :
            print( 'INFO: successfully killed update thread.' ) 


            
    def make_subtitle( self, s ) :
        subtitle = QLabel( s )
        subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE,
                                       QFont.Bold ) )
        return subtitle



    def load_tabor_button_clicked( self ) :
        thread = threading.Thread( target = self.load_tabor_button_clicked_target )
        thread.start()
        

    def load_tabor_button_clicked_target( self ) :
        with self.thread_lock : 
            print( 'INFO: loading tabor...' )

            self.tdc.pause()
            self.tdc.clear()
            self.processor.clear() 
        
            tabor_params = self.fetch_tabor_params() 
            
            if config.USE_TABOR :
                self.tabor.load_params( tabor_params ) 
            else :
                print( 'INFO: simulating tabor load...' )
                time.sleep( 5 )
                print( 'Done.' )

            self.tdc.resume()


    def fetch_tabor_params( self ) :
        tacc = int( self.tacc_entry.text() ) 
        nsteps = int( self.num_steps_entry.text() )
        types = [ float, float, float, int, int ]
        data = [ [ types[i]( self.tabor_table.cellWidget( i, j ).text() ) 
                   for j in range(3) ] 
                 for i in range( 5) ]
        
        print( data )
        freqs, phases, amps, loops, steps = data 
            
        tabor_params = tabor.TaborParams( tacc, nsteps, freqs, phases,
                                          amps, loops, steps )

        return tabor_params 
        
        
    def set_params_from_ion_data_button_clicked( self ) :
        print( 'INFO: setting tabor params from ion data...' ) 
        Z, A, q = self.tabor_ion_entry.fetch()
        N = A - Z 

        self.processor.Z = Z
        self.processor.A = A
        # self.processor.q = q 
        
        mass = cpt_tools.nuclear_data.masses[Z,N]
        omega_c = cpt_tools.mass_to_omega( mass, q, atomic_mass = 1 ) 
        omega_minus = float( self.tabor_table.cellWidget( 0, 0 ).text() )
        omega_plus = omega_c - omega_minus

        print( omega_minus )
        print( omega_c )
        print( omega_plus ) 
        
        frequencies = [ omega_plus, omega_c ]
        for i in range( 1, len( frequencies ) ) :
            self.tabor_table.cellWidget(0,i).setText( '%.1f' % frequencies[i] )
        
        self.processor.tabor_params = self.fetch_tabor_params() 
        
            
    def toggle_daq_button_clicked( self, toggle = 1 ) :
        print( 'INFO: toggling DAQ...' ) 
        
        if toggle : 
            state = self.tdc.toggle()
        else :
            state = self.tdc.collecting_data

        if state :
            self.toggle_daq_button.setStyleSheet("background-color:#89E552;")
            self.toggle_daq_button.setText( 'Running' )
        else : 
            self.toggle_daq_button.setStyleSheet("background-color: #E55959")
            self.toggle_daq_button.setText( 'Paused' ) 

            
        
    def clear_button_clicked( self ) :
        print( 'INFO: clearing data' ) 
        time.sleep(1)
        self.tdc.clear()
        self.processor.clear()

        
    def save_button_clicked( self ) : 
  
        alternate_name = self.alternate_name_entry.text()
        if alternate_name : 
            prefix = alternate_name
        else :
            prefix = None
            
        self.processor.save( prefix = prefix )

        comment = self.comment_entry.toPlainText()
        experimenter = self.experimenter_entry.text() 

        if len( comment ) > 0 : 
            cpt_tools.write_log( comment, experimenter ) 

        self.comment_entry.setPlainText( '' )
        
        

    def batch_generate_linspace( self ) :

        start = int( self.linspace_start_entry.text() )
        stop =  int( self.linspace_stop_entry.text() )
        num_data = int( self.linspace_num_data_entry.text() )

        data = np.linspace( start, stop, num_data, dtype = int )

        for i in range( len( data ) ) :
            self.batch_table.cellWidget( 0, i ).setText( str( data[i] ) )
        

    def add_button_clicked( self ) :
        path = QFileDialog.getOpenFileName( self, 'Select File' )[0]

        if not path :
            return 
        
        print( 'path: ', path )
        # name = dir_path[ dir_path.rfind( '/' ) + 1 : ] 
        # self.analysis_data_dirs_qlist.addItem( name ) 
        self.analysis_data_dirs_qlist.addItem( path )
        new_cpt_data = CPTdata.load( path )
        # print( new_cpt_data.tofs ) 
        self.analysis_plotter_widget.set_cpt_data( new_cpt_data ) 
        # self.analysis_plotter_widget.plotter.cpt_data = new_cpt_data
        # self.anal
        # print( 'initial set' ) 
        # print( self.analysis_plotter_widget.cpt_data ) 
        # self.analyzer.data_list.append( new_cpt_data )
         # = new_cpt_data

        self.analyzer.append( new_cpt_data ) 
         
        self.analysis_plotter_widget.update( update_first = 1 )

        
    def set_analysis_plotter_data( self, widget ) :
        row = self.analysis_data_dirs_qlist.currentRow()
        self.analysis_plotter_widget.set_cpt_data( self.analyzer.data_list[row] ) 
        self.analysis_plotter_widget.update()
        
        # print( self.analysis_plotter_widget.cpt_data.

        
    def delete_button_clicked( self ) :
        row = self.analysis_data_dirs_qlist.currentRow() 
        self.analysis_data_dirs_qlist.takeItem( row ) 
        # del self.analysis_data_list[ row ]
        
        
    def toggle_isolated_dataset( self ) :
        self.plot_isolated_dataset = self.isolated_dataset_checkbox.checkState()



    def mass_identifier_button_clicked( self ) :
        omega = float( self.tools_freq_entry.text() )
        d_omega = float( self.tools_freq_delta_entry.text() )
        
        thread = threading.Thread( target = cpt_tools.mass_identifier,
                                   args = ( 1, omega, d_omega ) ) 
        thread.start()
        

        
    def property_lookup_button_clicked( self ) :

        Z, A, q = self.tools_property_ion_entry.fetch() 

        N = A - Z 
        
        # freq = cpt_tools.nuclear_data.

        # print( cpt_tools.nuclear_data.half_lives )

        mass = cpt_tools.nuclear_data.masses[ Z, N ]
        half_life = cpt_tools.nuclear_data.half_lives[Z,N]
        cf_yield =  cpt_tools.nuclear_data.cf_yields[Z,N]
        abund = cpt_tools.nuclear_data.rel_abundances[Z,N]
        

        if q > 0 : 
            omega = cpt_tools.mass_to_omega( mass, q, 1 )
        else :
            omega = np.nan
            
        self.property_lookup_table.cellWidget( 0, 0 ).setText( '%.2f' % omega )
        self.property_lookup_table.cellWidget( 0, 1 ).setText( '%.2f' % mass )
        self.property_lookup_table.cellWidget( 0, 2 ).setText( '%.2e' % half_life )
        self.property_lookup_table.cellWidget( 0, 3 ).setText( '%.2e' % cf_yield )
        self.property_lookup_table.cellWidget( 0, 4 ).setText( '%.2e' % abund )
        
    # def session_path_button_clicked( self ) :
    #     print( 'INFO: setting session path' )
    #     session_dir = self.session_path_entry.text()

    #     data_name = self.data_name_entry.text() 
        
    #     print( session_dir )
    #     print( data_name )

    #     dir_path = str( QFileDialog.getExistingDirectory( self, "Select Directory") )

    #     print( dir_path ) 
        
        # def analysis_dir_list_clicked( self ) :
        



def setTableWidth( table ):

    table.setVisible(False)
    table.verticalScrollBar().setValue(0)
    table.resizeColumnsToContents()
    table.setVisible(True)
        
    width = table.verticalHeader().width()
    width += table.horizontalHeader().length()

    if table.verticalScrollBar().isVisible():
        width += table.verticalScrollBar().width()
        width += table.frameWidth() * 2
        table.setFixedWidth(width)


        
def main():
   app = QApplication(sys.argv)
   app.setStyleSheet( 'QGroupBox { font-weight: bold; }' ) 
   ex = gui()
   ex.show()
   sys.exit( app.exec_() )


   
   
if __name__ == '__main__':  
    main()
