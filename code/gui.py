import config
import tdc
import tabor
import processing
import plotter


import sys 
import scipy.stats as st
import struct 
import threading
import datetime
import os
import numpy as np
import scipy
import time


# from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, QRadioButton, QTableWidget

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QFont, QPixmap
# from PyQt5 import QtGui
from PyQt5 import QtCore



from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import matplotlib.pyplot as plt


# CONFIG

SUBTITLE_FONT = 'arial'
SUBTITLE_SIZE = 16
SUBTITLE_WEIGHT = 3

DEFAULT_KDE_BW = 0.03


gui_path = sys.path[0] + '/'
# gui_path = gui_path[ : gui_path.rfind( '/' ) ] + '/'



class MetadataWidget( object ) :

    def __init__( self, processor ) :

        self.processor = processor
        
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

        self.time_label_str = 'Time since data reset: '
        self.time_label = QLabel( self.time_label_str )
        # self.time_label_idx = len( time_label_str )

        vbox = QVBoxLayout()
        vbox.addWidget( self.table )
        vbox.addWidget( self.time_label )
        vbox.setAlignment( QtCore.Qt.AlignTop ) 
        self.box.setLayout( vbox ) 

        
    def update( self ) :
        cur_time = time.time()
        diff_time = time.time() - self.processor.session_start_time 

        counts = [ self.processor.num_mcp_hits, self.processor.num_processed_data,
                   self.processor.num_penning_ejects ]

        for i in range( len( counts ) ) :
            self.table.cellWidget( i, 0 ).setText( '%d' % counts[i] )
            self.table.cellWidget( i, 1 ).setText( '%.2f' % ( counts[i] / diff_time ) )

        self.time_label.setText( self.time_label_str + '%d' % int( diff_time ) )
            
        # self.box = QVBoxLayout()

        # total_counts_str = 'Total MCP hits: '
        # self.total_counts_label = QLabel( total_counts_str )
        # self.total_counts_idx = len( total_counts_str )

        # total_penning_eject_str = 'Total Penning Ejects: '
        # self.total_penning_ejects_label = QLabel( total_counts_str )
        # self.total_penning_ejects_idx = 0

        
        
        # self.box.addWidget( self.total_counts_label ) 


        
class gui( QTabWidget ):
    
    def __init__(self, parent = None):
        super( gui, self ).__init__( parent )

        self.date_str = datetime.datetime.now().strftime( '%Y_%m_%d' )
        self.data_dir_path = gui_path + '/data/'
        self.session_dir_path = None
        
        print( self.data_dir_path )
        
        try :
            os.makedirs( self.data_dir_path, exist_ok = 1 )
        except :
            pass

        self.session_dir_path = self.data_dir_path
        
        
        # the 3 custom classes we will be using to manage DAQ, processing, and plots
        self.tdc = tdc.TDC()
        self.tabor = tabor.Tabor() 
        self.processor = processing.Processor( self.tdc ) 
        self.plotter = plotter.Plotter( self.processor )
        
        
        
        self.controls_tab_idx = 0
        self.processed_data_tab_idx = 1
        # self.unprocessed_data_tab_idx = 2
        self.analysis_tab_idx = 2
        self.tools_tab_idx = 3 
        self.help_tab_idx = 4
        
        self.controls_tab = QWidget() 
        self.processed_data_tab = QWidget()
        # self.unprocessed_data_tab = QWidget()
        self.analysis_tab = QWidget()
        self.tools_tab = QWidget() 
        self.help_tab = QWidget()
        
        tabs = [ self.controls_tab, self.processed_data_tab,
                 # self.unprocessed_data_tab,
                 self.analysis_tab,
                 self.tools_tab,
                 self.help_tab ]

        tab_idxs = [ self.controls_tab_idx, self.processed_data_tab_idx,
                     # self.unprocessed_data_tab_idx,
                     self.analysis_tab_idx,
                     self.tools_tab_idx,
                     self.help_tab_idx ]

        tab_names = [ 'DAQ / Tabor / Output', 'Data Stream',
                      # 'Unprocessed Data',
                      'Analysis', 'Tools', 'Help' ]
        
        self.num_tabs = len( tabs ) 
        
        for i in range( self.num_tabs ) :
            self.insertTab( tab_idxs[i], tabs[i], tab_names[i] )
        
        # self.( self., "Processed Data" )
        # self.addTab( self.tab2, "Unprocessed Data" )
        # self.addTab(self.tab3,"Tab 3")
        
        self.tab_updaters = [ None for i in range( self.num_tabs ) ] 
        self.canvases = [ None for i in range( self.num_tabs ) ] 

        self.controls_tab_init()
        self.processed_data_tab_init()
        # self.unprocessed_data_tab_init()
        self.analysis_tab_init()
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
        tabor_layout = QFormLayout()
        tabor_box.setLayout( tabor_layout ) 
        
        # don't expand to take more room than necessary 
        tabor_layout.setFieldGrowthPolicy( 0 ) 
            
        # subtitle = self.make_subtitle( 'Tabor Controls' ) 
        # tabor_layout.addRow( subtitle )
        
        self.load_tabor_button = QPushButton( 'Load Tabor Parameters' )
        self.load_tabor_button.clicked.connect( self.load_tabor_button_clicked ) 
        tabor_layout.addRow( self.load_tabor_button ) 
        
        
        self.num_steps_entry = QLineEdit( '5' )
        tabor_layout.addRow( 'num steps:', self.num_steps_entry ) 

        self.tacc_entry = QLineEdit( '68' )
        tabor_layout.addRow( 'Accumulation Time:', self.tacc_entry ) 

        nrows = 5
        ncols = 3 
        
        self.tabor_table = QTableWidget( nrows, ncols )
        
        # combination of size policy change and resizemode change
        # makes the table not expand more than necessary 
        size_policy = QSizePolicy( QSizePolicy.Maximum,
                                   QSizePolicy.Maximum )
        
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

        tabor_layout.addRow( self.tabor_table )

        self.set_params_from_ion_data_button = QPushButton( 'Set Params From Ion Data' )
        self.set_params_from_ion_data_button.clicked.connect(
            self.set_params_from_ion_data_button_clicked ) 
        tabor_layout.addRow( self.set_params_from_ion_data_button )

        self.z_entry = None
        self.n_entry = None
        self.q_entry = None

        # ion_entry_layout = QFormLayout()
        # ion_entry_layout.addRow( 'Z:', self.z_entry )

        labels = [ 'Z:', 'N:', 'q:' ]
        entries = [ self.z_entry, self.n_entry, self.q_entry ]
        defaults = [ '55', '82', '1' ]

        ion_param_validator = QIntValidator( 0, 1000 ) 

        for i in range( len( labels ) ) :
            entries[i] = QLineEdit( defaults[i] ) 
            entries[i].setValidator( ion_param_validator )
            tabor_layout.addRow( labels[i], entries[i] )
        
        
        
        # tabor_controls_grid = QGridLayout()
        # tabor_layout.addLayout( tabor_controls_grid ) 

        self.toggle_daq_button = QPushButton( 'Pause' )
        self.toggle_daq_button.clicked.connect( self.toggle_daq_button_clicked ) 
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
                
        self.ion_name_entry = QLineEdit()
        daq_layout.addRow( 'Suspected Ion', self.ion_name_entry )
        
        self.session_name_entry = QLineEdit()
        daq_layout.addRow( 'Session Name', self.session_name_entry )

        self.experimenter_entry = QLineEdit()
        daq_layout.addRow( 'Experimenter', self.experimenter_entry ) 

        self.comment_entry = QTextEdit()
        daq_layout.addRow( 'Session Comments', self.comment_entry ) 

        metadata_widget = MetadataWidget( self.processor )
        
        layout = QHBoxLayout()
        layout.addWidget( tabor_box )
        layout.addWidget( daq_box )
        layout.addWidget( metadata_widget.box )
        
        # layout.setContentsMargins(200,100,200,10)
        
        self.controls_tab.setLayout( layout )
        self.tab_updaters[ tab_idx ] = [ metadata_widget.update ]

        


        
    def processed_data_tab_init( self ):

        tab_idx = self.processed_data_tab_idx

        f, axarr = plt.subplots( 2, 2 )
        f.subplots_adjust( hspace = 0.5, wspace = 0.5 )

        self.plotter.init_mcp_hitmap( axarr[0][0], f )
        self.plotter.init_tof_plot( axarr[0][1] )
        self.plotter.init_r_plot( axarr[1][0] )
        self.plotter.init_theta_plot( axarr[1][1] )

        # matplotlib canvas 
        self.canvases[ tab_idx ] = FigureCanvas( f )
        # self.toolbar = NavigationToolbar( self.canvases[ tab_idx ], self )
        
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        

        # self.button = QPushButton('Plot')
        # self.button.clicked.connect( self.update )

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
        self.mcp_kde_bw_entry = QLineEdit( str( DEFAULT_KDE_BW ) )
        self.mcp_kde_bw_entry.setValidator( QDoubleValidator( 0.0, 10000., 10 ) )
        # mcp_hitmap_settings.addWidget( self.mcp_hist_bin_size_entry ) 
        # mcp_hitmap_settings.addWidget( self.mcp_kde_bw_entry ) 

        # mcp hitmap bounds inputs
        self.mcp_hitmap_left_xbound_entry = QLineEdit( str(-5) )
        self.mcp_hitmap_right_xbound_entry = QLineEdit( str(5) )
        self.mcp_hitmap_left_ybound_entry = QLineEdit( str(-5) )
        self.mcp_hitmap_right_ybound_entry = QLineEdit( str(5) )

        mcp_hitmap_bounds_validator = QDoubleValidator( -1000, 1000, 10 )
        self.mcp_hitmap_left_xbound_entry.setValidator( mcp_hitmap_bounds_validator )
        self.mcp_hitmap_right_xbound_entry.setValidator( mcp_hitmap_bounds_validator )
        self.mcp_hitmap_left_ybound_entry.setValidator( mcp_hitmap_bounds_validator ) 
        self.mcp_hitmap_right_ybound_entry.setValidator( mcp_hitmap_bounds_validator ) 

        mcp_hitmap_xbounds_entry = QHBoxLayout()
        mcp_hitmap_ybounds_entry = QHBoxLayout()
        mcp_hitmap_xbounds_entry.addWidget( self.mcp_hitmap_left_xbound_entry ) 
        mcp_hitmap_xbounds_entry.addWidget( self.mcp_hitmap_right_xbound_entry ) 
        mcp_hitmap_ybounds_entry.addWidget( self.mcp_hitmap_left_ybound_entry ) 
        mcp_hitmap_ybounds_entry.addWidget( self.mcp_hitmap_right_ybound_entry ) 

        self.tof_hist_nbins_entry =  QLineEdit( str(0) )
        self.tof_hist_nbins_entry.setValidator( hist_nbins_validator )
        
        self.r_hist_nbins_entry =  QLineEdit( str(0) )
        self.r_hist_nbins_entry.setValidator( hist_nbins_validator )
        
        self.angle_hist_nbins_entry =  QLineEdit( str(0) )
        self.angle_hist_nbins_entry.setValidator( hist_nbins_validator ) 

        
        # tof cut entry 
        tof_bounds = QHBoxLayout()
        
        self.tof_lower_cut_entry = QLineEdit(
            str( self.processor.tof_cut_lower ) )

        self.tof_lower_cut_entry.setValidator(
            QDoubleValidator(0., 10000., 10 ) )

        self.tof_upper_cut_entry = QLineEdit(
            str( self.processor.tof_cut_upper ) )

        self.tof_upper_cut_entry.setValidator(
            QDoubleValidator(0., 10000., 10 ) )

        tof_bounds.addWidget( self.tof_lower_cut_entry ) 
        tof_bounds.addWidget( self.tof_upper_cut_entry )

        r_bounds = QHBoxLayout() 
        
        self.r_lower_cut_entry = QLineEdit( str(0) )
        self.r_lower_cut_entry.setValidator( QDoubleValidator( 0, 10000, 3 ) )
        
        self.r_upper_cut_entry = QLineEdit( str(0) )
        self.r_upper_cut_entry.setValidator( QDoubleValidator( 0, 10000, 3 ) )

        r_bounds.addWidget( self.r_lower_cut_entry )
        r_bounds.addWidget( self.r_upper_cut_entry ) 

        layout = QVBoxLayout() 
        
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
        controls_layout.addRow( 'MCP X Bounds:', mcp_hitmap_xbounds_entry ) 
        controls_layout.addRow( 'MCP Y Bounds:', mcp_hitmap_ybounds_entry ) 
        controls_layout.addRow( 'TOF hist num bins:', self.tof_hist_nbins_entry )
        controls_layout.addRow( 'Radius hist num bins:', self.r_hist_nbins_entry )
        controls_layout.addRow( 'Angle hist num bins:', self.angle_hist_nbins_entry )
        reload_button = QPushButton( 'Reload Parameters' ) 
        reload_button.clicked.connect( self.reload_visualization_params ) 
        controls_layout.addRow( reload_button ) 
        
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
        fits_layout = QVBoxLayout()

        fits_box.setLayout( fits_layout )
        layout.addWidget( fits_box ) 
        

        metadata_widget = MetadataWidget( self.processor )
        layout.addWidget( metadata_widget.box ) 

        # tof fit: button, left bound, right bound, fit results 

        # r fit

        # angle fit
        
        self.tab_updaters[ tab_idx ] = [ self.plotter.update_mcp_hitmap,
                                         self.plotter.update_tof_plot,
                                         self.plotter.update_r_plot,
                                         self.plotter.update_theta_plot,
                                         metadata_widget.update ]
        
        grid_layout = QGridLayout()
        grid_layout.addLayout( layout, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        grid_layout.setColumnStretch( 0, 0.5 ) 
        grid_layout.addWidget( self.canvases[ tab_idx ], 0, 1, 1, 1 )
        grid_layout.setColumnStretch( 1, 1 ) 
        
        self.processed_data_tab.setLayout( grid_layout ) 
        

        
    def unprocessed_data_tab_init( self ):

        tab_idx = self.unprocessed_data_tab_idx 
        
        f, axarr = plt.subplots( 2, 2 )
        self.plotter.init_coords_plots( axarr )
        self.canvases[ tab_idx ] = FigureCanvas( f ) 
        self.tab_updaters[ tab_idx ] = [ self.plotter.update_coords_plots ]
        
        # set the layout
        layout = QVBoxLayout()
        # layout.addWidget(self.toolbar)

        layout.addWidget( self.canvases[ tab_idx ] )
        
        self.unprocessed_data_tab.setLayout( layout )


        
        
    def analysis_tab_init( self ):

        tab_idx = self.analysis_tab_idx 
        
        self.analysis_data_dirs_qlist = QListWidget()
        # self.analysis_data_dirs_qlist.addItem( 'test' )

        analysis_controls_box = QGroupBox( 'Choose Analysis Directories' ) 
        analysis_controls_layout = QVBoxLayout()

        tmp = QHBoxLayout()
        tmp.addWidget( QLabel( 'Display Isolated Dataset' ) )
        self.analysis_display_isolated_dataset = 0
        self.isolated_dataset_checkbox = QCheckBox()
        self.isolated_dataset_checkbox.setCheckState( self.analysis_display_isolated_dataset )
        self.isolated_dataset_checkbox.clicked.connect( self.toggle_isolated_dataset ) 
        tmp.addWidget( self.isolated_dataset_checkbox )
        analysis_controls_layout.addLayout( tmp ) 
        
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
        f, axarr = plt.subplots( 2, 2 )
        f.subplots_adjust( hspace = 0.5 )
        self.canvases[ tab_idx ] = FigureCanvas( f )

        
        
        layout = QGridLayout()
        layout.addWidget( analysis_controls_box, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        layout.setColumnStretch( 0, 0.5 ) 
        layout.addWidget( self.canvases[ tab_idx ], 0, 1, 1, 1 )
        layout.setColumnStretch( 1, 1 ) 
        
        self.analysis_tab.setLayout( layout )

        

    def tools_tab_init( self ) :

        tab_idx = self.tools_tab_idx 

        layout = QHBoxLayout()

        mass_identifier_box = QGroupBox( 'Mass Identifier' )
        # mass_identifier_box.setStyleSheet( '
        tmp = QFormLayout()
        self.tools_freq_entry = QLineEdit() 
        tmp.addRow( 'Cyclotron Frequency', self.tools_freq_entry )
        self.mass_identifier_button = QPushButton( 'Look Up' )
        tmp.addRow( self.mass_identifier_button )
        table_cols = [ 'Freq', 'Name', 'q', 'A', 'Z', 'N', 'T_{1/2}',
                       'Cf yield', 'Rel Natural Abund' ]
        self.mass_identifier_table = QTableWidget( 1, len( table_cols ) )
        self.mass_identifier_table.setHorizontalHeaderLabels( table_cols ) 
        tmp.addRow( self.mass_identifier_table ) 
        mass_identifier_box.setLayout( tmp ) 

        property_lookup_box = QGroupBox( 'Property Lookup' )
        # tmp_layout = QVBoxLayout
        tmp = QFormLayout()
        self.tools_z_entry = QLineEdit( '43' ) 
        self.tools_n_entry = QLineEdit( '36' )
        self.tools_q_entry = QLineEdit( '0' ) 
        self.tools_property_button = QPushButton( 'Look Up' ) 
        tmp.addRow( 'Z', self.tools_z_entry )
        tmp.addRow( 'N', self.tools_n_entry )
        tmp.addRow( 'q', self.tools_q_entry )
        tmp.addRow( self.tools_property_button ) 
        # tmp_layout.addLayout( tmp ) 
        property_lookup_box.setLayout( tmp )

        property_lookup_cols = [ 'Freq', 'T_{1/2}', 'Cf yield', 'Rel Natural Abund' ]
        self.property_lookup_table = QTableWidget( 1, len( property_lookup_cols ) )
        self.property_lookup_table.setHorizontalHeaderLabels( property_lookup_cols ) 
        tmp.addRow( self.property_lookup_table ) 

        layout.addWidget( mass_identifier_box ) 
        layout.addWidget( property_lookup_box ) 
        
        self.tools_tab.setLayout( layout ) 
        



    def help_tab_init( self ) :
        layout = QVBoxLayout()

        subtitles = [ 'Histogram Bin Sizes' ]

        messages = [
            'For all histograms, the default, recommended value of 0 uses the Freedman-Diaconis rule to dynamically select the bin size during each update.'
        ]

        for i in range( len( subtitles ) ) :

            subtitle = QLabel( subtitles[i] )
            subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE, QFont.Bold ) )

            message = QLabel( messages[i] )
            message.setWordWrap( 1 ) 
            
            layout.addWidget( subtitle )
            layout.addWidget( message )

        try : 
            label = QLabel()
            morrison_path = gui_path + '../images/jim-morrison-og.jpg'
            print( morrison_path )
            print( os.path.exists( morrison_path ) ) 
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
        
            tacc = int( self.tacc_entry.text() ) 
            nsteps = int( self.num_steps_entry.text() )
            types = [ float, float, float, int, int ]
            data = [ [ types[i]( self.tabor_table.cellWidget( i, j ).text() ) 
                       for j in range(3) ] 
            for i in range( 5) ]

            print( data )
            freqs, phases, amps, loops, steps = data 

            if config.USE_TABOR :
                self.tabor.load_params( tacc, nsteps, freqs, phases, amps, loops, steps )
            else :
                print( 'INFO: simulating tabor load...' )
                time.sleep( 5 )
                print( 'Done.' )

            self.tdc.resume()
            
            
        
    def set_params_from_ion_data_button_clicked( self ) :
        print( 'INFO: setting tabor params from ion data...' ) 

        
    def toggle_daq_button_clicked( self ) :
        print( 'INFO: toggling DAQ...' ) 

        
    def clear_button_clicked( self ) :
        print( 'INFO: clearing data' ) 
        time.sleep(1)
        self.tdc.clear()
        self.processor.clear()

        
    def save_button_clicked( self ) : 
        print( 'INFO: saving data...' )
        session_name = self.session_name_entry.text()

        if not session_name :
            print( 'ERROR: session name is required' ) 
            return 0 
        
        session_dir_path = self.data_dir_path + session_name + '/'
        print( session_dir_path ) 
        
        if session_dir_path != self.session_dir_path :
            self.session_dir_path = session_dir_path
            os.makedirs( self.session_dir_path, exist_ok = 1 )
            
        np.save( self.session_dir_path + 'test', [1,2,3] )


    def plot_with_cuts_clicked( self ) :
        self.plotter.plot_with_cuts = self.plot_with_cuts_button.checkState() 

    def set_use_kde( self ) :
        self.plotter.use_kde = 1 

    def disable_use_kde( self ) :
        self.plotter.use_kde = 0 

    def reload_visualization_params( self ) :
        self.plotter.mcp_bin_width = float( self.mcp_bin_width_entry.text() )
        self.plotter.mcp_kde_bandwidth = float( self.mcp_kde_bw_entry.text() )
        self.plotter.mcp_x_bounds = [ float( self.mcp_hitmap_left_xbound_entry.text() ),
                                      float( self.mcp_hitmap_right_xbound_entry.text() ) ]
        self.plotter.mcp_y_bounds = [ float( self.mcp_hitmap_left_ybound_entry.text() ),
                                      float( self.mcp_hitmap_right_ybound_entry.text() ) ]
        
        self.plotter.tof_hist_nbins = int( self.tof_hist_nbins_entry.text() ) 
        self.plotter.r_hist_nbins = int( self.r_hist_nbins_entry.text() ) 
        self.plotter.angle_hist_nbins = int( self.angle_hist_nbins_entry.text() )

        self.plotter.rebuild_mcp_plot = 1 



    def add_button_clicked( self ) :
        dir_path = str( QFileDialog.getExistingDirectory( self, "Select Directory") )
        # name = dir_path[ dir_path.rfind( '/' ) + 1 : ] 
        # self.analysis_data_dirs_qlist.addItem( name ) 
        self.analysis_data_dirs_qlist.addItem( dir_path ) 

        
    def delete_button_clicked( self ) :
        row = self.analysis_data_dirs_qlist.currentRow() 
        self.analysis_data_dirs_qlist.takeItem( row ) 
        
    def toggle_isolated_dataset( self ) :
        self.plot_isolated_dataset = self.isolated_dataset_checkbox.checkState() 
        
    # def session_path_button_clicked( self ) :
    #     print( 'INFO: setting session path' )
    #     session_dir = self.session_path_entry.text()

    #     data_name = self.data_name_entry.text() 
        
    #     print( session_dir )
    #     print( data_name )

    #     dir_path = str( QFileDialog.getExistingDirectory( self, "Select Directory") )

    #     print( dir_path ) 
        
        # def analysis_dir_list_clicked( self ) :
        

    
def main():
   app = QApplication(sys.argv)
   app.setStyleSheet( 'QGroupBox { font-weight: bold; }' ) 
   ex = gui()
   ex.show()
   sys.exit( app.exec_() )


   
   
if __name__ == '__main__':  
    main()
