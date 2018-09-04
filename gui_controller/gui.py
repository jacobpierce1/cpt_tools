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

import gui_helpers


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



code_path = os.path.abspath( os.path.dirname( __file__ ) ) + '/'
# code_path = sys.path[0] + '/'
# code_path = code_path[ : code_path.rfind( '/' ) ] + '/'

MU_UNICODE = '\u03bc'

        
        
        
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
          self.isolated_analysis_tab_idx,
          self.combined_analysis_tab_idx,
          self.tools_tab_idx,
          self.help_tab_idx ) = range(6)
        
        self.controls_tab = QWidget() 
        self.processed_data_tab = QWidget()
        # self.unprocessed_data_tab = QWidget()
        self.isolated_analysis_tab = QWidget()
        self.combined_analysis_tab = QWidget()
        self.tools_tab = QWidget() 
        self.help_tab = QWidget()
        
        tabs = [ self.controls_tab, self.processed_data_tab,
                 # self.unprocessed_data_tab,
                 self.isolated_analysis_tab,
                 self.combined_analysis_tab,
                 self.tools_tab,
                 self.help_tab ]

        tab_idxs = [ self.controls_tab_idx, self.processed_data_tab_idx,
                     # self.unprocessed_data_tab_idx,
                     self.isolated_analysis_tab_idx,
                     self.combined_analysis_tab_idx,
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
        self.isolated_analysis_tab_init()
        self.combined_analysis_tab_init() 
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

        tmp = QHBoxLayout()
        tmp.setAlignment( QtCore.Qt.AlignLeft )
        self.tabor_save_checkbox = QCheckBox()
        self.tabor_save_checkbox.setCheckState(2)
        tmp.addWidget( self.tabor_save_checkbox )
        tmp.addWidget( QLabel( 'Automatically save when loading tabor' ) )
        tabor_layout.addLayout( tmp )

        tmp = QHBoxLayout()
        tmp.setAlignment( QtCore.Qt.AlignLeft )
        self.tabor_clear_checkbox = QCheckBox()
        self.tabor_clear_checkbox.setCheckState(2)
        tmp.addWidget( self.tabor_clear_checkbox )
        tmp.addWidget( QLabel( 'Automatically clear when loading tabor' ) )
        tabor_layout.addLayout( tmp ) 
        
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
        
        defaults = [ [ 1600.0, 656252.0, 0.5 ],
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

        set_analysis_ion_data_button = QPushButton( 'Set Analysis Ion Data' )
        set_analysis_ion_data_button.clicked.connect(
            self.set_analysis_ion_data )
        tabor_layout.addWidget( set_analysis_ion_data_button ) 
        
        self.tabor_ion_entry = gui_helpers.IonEntry()
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

        metadata_widget = gui_helpers.MetadataWidget( self.processor )


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
        
        processed_data_plotter_widget = gui_helpers.PlotterWidget( self.plotter )
        
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


        
        
    def isolated_analysis_tab_init( self ):

        self.analyzer = analysis.CPTanalyzer()
        analysis_plotter = plotter.Plotter( CPTdata() ) 
        self.analysis_plotter_widget = gui_helpers.PlotterWidget( analysis_plotter ) 
        
        tab_idx = self.isolated_analysis_tab_idx 
        
        self.analysis_data_dirs_qlist = QListWidget()
        self.analysis_data_dirs_qlist.setMinimumWidth( 200 ) 
        self.analysis_data_dirs_qlist.itemClicked.connect( self.set_analysis_plotter_data ) 
        # self.analysis_data_dirs_qlist.addItem( 'test' )

        analysis_controls_box = QGroupBox( 'Choose Files for Analysis' ) 
        analysis_controls_layout = QVBoxLayout()
        
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
        
        layout = QHBoxLayout()
        layout.addWidget( analysis_controls_box )
        layout.addLayout( self.analysis_plotter_widget.grid_layout ) 
                
        self.isolated_analysis_tab.setLayout( layout )


        
    def combined_analysis_tab_init( self ) :

        self.set_analysis_ion_data()
        self.combined_analysis_widget = gui_helpers.CombinedAnalysisWidget( self.analyzer )
        self.combined_analysis_widget.update()
        
        self.combined_analysis_tab.setLayout( self.combined_analysis_widget.layout )

        

    def tools_tab_init( self ) :

        tab_idx = self.tools_tab_idx 

        layout = QVBoxLayout()

        mass_identifier_box = QGroupBox( 'Mass Identifier' )
        # mass_identifier_box.setStyleSheet( '
        tmp = QFormLayout()
        self.tools_freq_entry = QLineEdit( '675000.3' ) 
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

        self.tools_property_ion_entry = gui_helpers.IonEntry()
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

        self.tdc.pause()

        save = self.tabor_save_checkbox.isChecked()
        clear = self.tabor_clear_checkbox.isChecked() 

        if save :
            print( 'INFO: saving' )
            self.save_button_clicked() 
                
        if clear :
            print( 'INFO: clearing' ) 
            self.processor.clear()
            self.tdc.clear()
                
        thread = threading.Thread( target = self.load_tabor_button_clicked_target )
        thread.start()

        self.tdc.resume()
        

    def load_tabor_button_clicked_target( self ) :
        with self.thread_lock : 
            print( 'INFO: loading tabor...' )

            tabor_params = self.fetch_tabor_params() 
            
            if config.USE_TABOR :
                self.tabor.load_params( tabor_params ) 
            else :
                print( 'INFO: simulating tabor load...' )
                time.sleep( 3 )
                print( 'Done.' )


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
        for i in range( 2 ) :
            self.tabor_table.cellWidget(0,i+1).setText( '%.1f' % frequencies[i] )
        
        self.processor.tabor_params = self.fetch_tabor_params() 
        #self.analyzer.set_ion_params( ion_params )
        

    def set_analysis_ion_data( self )  :
        Z, A, q = self.tabor_ion_entry.fetch()
        self.analyzer.set_ion_params( Z, A, q )
        self.processor.Z = Z
        self.processor.A = A
        
        
            
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

        self.combined_analysis_widget.update()
        
        
    def set_analysis_plotter_data( self, widget ) :
        row = self.analysis_data_dirs_qlist.currentRow()
        self.analysis_plotter_widget.set_cpt_data( self.analyzer.data_list[row] ) 
        self.analysis_plotter_widget.update()
        self.analyzer.active_data_idx = row 
        
        # print( self.analysis_plotter_widget.cpt_data.

        
    def delete_button_clicked( self ) :
        row = self.analysis_data_dirs_qlist.currentRow() 
        self.analysis_data_dirs_qlist.takeItem( row )

        row = self.analysis_data_dirs_qlist.currentRow()
        self.analyzer.active_data_idx = row 
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




        
def main():
   app = QApplication(sys.argv)
   app.setStyleSheet( 'QGroupBox { font-weight: bold; }' ) 
   ex = gui()
   ex.show()
   sys.exit( app.exec_() )


   
   
if __name__ == '__main__':  
    main()
