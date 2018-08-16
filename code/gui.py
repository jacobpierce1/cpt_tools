import config
import tdc
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
        self.tdc_mgr = tdc.TDC()
        self.tdc_data_processor = processing.Processor( self.tdc_mgr ) 
        self.plotter = plotter.Plotter( self.tdc_data_processor )

        self.controls_tab_idx = 0
        self.processed_data_tab_idx = 1
        # self.unprocessed_data_tab_idx = 2
        self.analysis_tab_idx = 2
        self.help_tab_idx = 3
        
        self.controls_tab = QWidget() 
        self.processed_data_tab = QWidget()
        # self.unprocessed_data_tab = QWidget()
        self.analysis_tab = QWidget()
        self.help_tab = QWidget()
        
        tabs = [ self.controls_tab, self.processed_data_tab,
                 # self.unprocessed_data_tab,
                 self.analysis_tab,
                 self.help_tab ]

        tab_idxs = [ self.controls_tab_idx, self.processed_data_tab_idx,
                     # self.unprocessed_data_tab_idx,
                     self.analysis_tab_idx,
                     self.help_tab_idx ]

        tab_names = [ 'Tabor / DAQ / Output', 'Processed Data',
                      # 'Unprocessed Data',
                      'Analysis', 'Help' ]
        
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
        self.help_tab_init() 
        
        self.setWindowTitle("Phase Imaging DAQ and Real-Time Analysis")
        self.resize( 1300, 900 )
                
        self.kill_update_thread = 0
        self.update_thread = threading.Thread( target = self.update_loop )
        self.update_thread.start()

        

    # this automatically is called when the window is closed.
    def closeEvent( self, event ): 
        # this is checked by the thread which then terminates within 1 second
        self.kill_update_thread = 1 # self.destroy()

        
        
    def controls_tab_init( self ) :

        tabor_layout = QFormLayout()

        # don't expand to take more room than necessary 
        tabor_layout.setFieldGrowthPolicy( 0 ) 
            
        # subtitle = QLabel( 'Tabor Controls' )
        # subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE,
        #                                Qtgui.QFont.Bold ) )

        subtitle = self.make_subtitle( 'Tabor Controls' ) 
        tabor_layout.addRow( subtitle )
        
        self.load_tabor_button = QPushButton( 'Load Tabor Parameters' )
        self.load_tabor_button.clicked.connect( self.load_tabor_button_clicked ) 
        tabor_layout.addRow( self.load_tabor_button ) 
        
        
        self.num_steps_entry = QLineEdit( '5' )
        tabor_layout.addRow( 'num steps:', self.num_steps_entry ) 

        self.tacc_entry = QLineEdit( '68' )
        tabor_layout.addRow( 'Accumulation Time:', self.tacc_entry ) 

        nrows = 5
        ncols = 3 
        
        tabor_table = QTableWidget( nrows, ncols )
        
        # combination of size policy change and resizemode change
        # makes the table not expand more than necessary 
        size_policy = QSizePolicy( QSizePolicy.Maximum,
                                   QSizePolicy.Maximum )
        
        tabor_table.setSizePolicy( size_policy )
        self.load_tabor_button.setSizePolicy( size_policy ) 
        
        tabor_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        tabor_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        
        tabor_table.setHorizontalHeaderLabels( [ 'w_-', 'w_+', 'w_c' ] )
        tabor_table.setVerticalHeaderLabels( [ 'omega', 'phase', 'amp',
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
                tabor_table.setCellWidget( i,j, tmp )

        print( tabor_table.cellWidget( 0, 0 ).text() )

        tabor_layout.addRow( tabor_table )

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
        self.toggle_daq_button.setSizePolicy( size_policy )
        
        self.clear_button = QPushButton( 'Clear' )
        self.clear_button.clicked.connect( self.clear_button_clicked ) 
        self.clear_button.setSizePolicy( size_policy )
        
        daq_layout = QFormLayout()
        daq_layout.addRow( self.make_subtitle( 'DAQ Controls' ) )
        daq_layout.addRow( self.toggle_daq_button )
        daq_layout.addRow( self.clear_button )

        daq_layout.addRow( self.make_subtitle( 'Output Controls' ) ) 

        self.save_button = QPushButton( 'Save' )
        self.save_button.clicked.connect( self.save_button_clicked ) 
        self.save_button.setSizePolicy( size_policy )
        daq_layout.addRow( self.save_button ) 

        self.session_name_entry = QLineEdit()
        daq_layout.addRow( 'Session Name', self.session_name_entry )

        self.experimenter_entry = QLineEdit()
        daq_layout.addRow( 'Experimenter', self.experimenter_entry ) 

        self.comment_entry = QTextEdit()
        daq_layout.addRow( 'Session Comments', self.comment_entry ) 
        
        # dirpicker = QHBoxLayout() 
        # self.session_path_button = QPushButton( 'Choose Session Path' )
        # self.session_path_button.clicked.connect( self.session_path_button_clicked ) 
        # self.session_path_entry = QLineEdit()
        # dirpicker.addWidget( self.session_path_button )
        # dirpicker.addWidget( self.session_path_entry ) 
        # daq_layout.addRow( dirpicker )

        
        
        # self.data_name = QPushButton( 'Current Data Name' )

        # daq_layout.addRow( 
        
        # grid_layout = QGridLayout()
        # grid_layout.addLayout( tabor_layout, 0, 0, 0, 0 )
        # grid_layout.addLayout( daq_layout, 0, 0, 0, 1 ) 

        # daq_layout.setAlignment( QtCore.Qt.AlignLeft )
        # tabor_layout.setAlignment( QtCore.Qt.AlignRight ) 
        # tabor_layout.setFieldGrowthPolicy( QFormLayout.FieldsStayAtSizeHint )
        # tabor_layout.setAlignment( QtCore.Qt.AlignRight )

        
        layout = QHBoxLayout()
        # layout.setSpacing(0)
        layout.addLayout( tabor_layout )
        layout.addLayout( daq_layout )

        
        # layout.setAlignment( QtCore.Qt.AlignHCenter ) 

        # layout.setStretch( 0, 0 ) 
        # layout.setStretch( 1, 0 )

        # layout.setSpacing(30)
        layout.setContentsMargins(200,100,200,10)

        # layout.setSizePolicy( size_policy ) 
        
        self.controls_tab.setLayout( layout )

        
      
    def processed_data_tab_init( self ):
        # layout = QFormLayout()
        # layout.addRow("Name", QLineEdit() )
        # layout.addRow("Address", QLineEdit() )
        # self.setTabText(0,"Contact Details")
        # self.tab1.setLayout(layout)

        f, axarr = plt.subplots( 2, 2 )

        f.subplots_adjust( hspace = 0.5, wspace = 0.5 )

        self.plotter.init_mcp_hitmap( axarr[0][0], f )
        self.plotter.init_tof_plot( axarr[0][1] )
        self.plotter.init_r_plot( axarr[1][0] )
        self.plotter.init_theta_plot( axarr[1][1] )

        tab_idx = self.processed_data_tab_idx
        
        self.tab_updaters[ tab_idx ] = [ self.plotter.update_mcp_hitmap,
                                         self.plotter.update_tof_plot,
                                         self.plotter.update_r_plot,
                                         self.plotter.update_theta_plot ]

        # matplotlib canvas 
        self.canvases[ tab_idx ] = FigureCanvas( f )

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        # self.toolbar = NavigationToolbar(self.canvas, self)

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
        self.mcp_hist_button.clicked.connect( self.disable_use_kde ) 
        mcp_hitmap_buttons.addWidget( self.mcp_kde_button ) 
        mcp_hitmap_buttons.addWidget( self.mcp_hist_button )
        
        # mcp hitmap histo bin size and kde bandwidth
        # mcp_hitmap_settings = QHBoxLayout()
        hist_nbins_validator =  QIntValidator( 0, 10000 ) 
        self.mcp_hist_nbins_entry = QLineEdit( str(0) )
        self.mcp_hist_nbins_entry.setValidator( hist_nbins_validator ) 
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

        self.tof_histo_nbins_entry =  QLineEdit( str(0) )
        self.tof_histo_nbins_entry.setValidator( hist_nbins_validator )
        
        self.r_histo_nbins_entry =  QLineEdit( str(0) )
        self.r_histo_nbins_entry.setValidator( hist_nbins_validator )
        
        self.angle_histo_nbins_entry =  QLineEdit( str(0) )
        self.angle_histo_nbins_entry.setValidator( hist_nbins_validator ) 

        
        # tof cut entry 
        tof_bounds = QHBoxLayout()
        
        self.tof_lower_cut_entry = QLineEdit(
            str( self.tdc_data_processor.tof_cut_lower ) )

        self.tof_lower_cut_entry.setValidator(
            QDoubleValidator(0., 10000., 10 ) )

        self.tof_upper_cut_entry = QLineEdit(
            str( self.tdc_data_processor.tof_cut_upper ) )

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
        
        controls_layout = QFormLayout()
        subtitle = QLabel( 'Visualization Controls' )
        subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE,
                                       QFont.Bold ) )

        controls_layout.addRow( subtitle )
        controls_layout.addRow( 'Plot with Cuts', self.plot_with_cuts_button ) 
        controls_layout.addRow( 'Hitmap Type:', mcp_hitmap_buttons )
        # controls_layout.addRow( mcp_hitmap_settings )
        controls_layout.addRow( 'MCP hist num bins:', self.mcp_hist_nbins_entry )
        controls_layout.addRow( 'MCP KDE bandwidth:', self.mcp_kde_bw_entry )
        controls_layout.addRow( 'MCP X Bounds:', mcp_hitmap_xbounds_entry ) 
        controls_layout.addRow( 'MCP Y Bounds:', mcp_hitmap_ybounds_entry ) 
        controls_layout.addRow( 'TOF histo num bins:', self.tof_histo_nbins_entry )
        controls_layout.addRow( 'Radius histo num bins:', self.r_histo_nbins_entry )
        controls_layout.addRow( 'Angle histo num bins:', self.angle_histo_nbins_entry )
        
        subtitle = QLabel( 'Data Cuts' )
        subtitle.setFont( QFont( SUBTITLE_FONT, SUBTITLE_SIZE, QFont.Bold ) )
        controls_layout.addRow( subtitle )
        controls_layout.addRow( 'TOF lower / upper bounds:', tof_bounds ) 
        controls_layout.addRow( 'Radius Cut:', r_bounds ) 

        controls_layout.addRow( self.make_subtitle( 'Gaussian Fitting' ) )

        # tof fit: button, left bound, right bound, fit results 

        # r fit

        # angle fit 
        
        grid_layout = QGridLayout()
        grid_layout.addLayout( controls_layout, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
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
        # layout.addWidget(self.button)

        
        
        self.unprocessed_data_tab.setLayout( layout )
        
        # layout = QFormLayout()
        # sex = QHBoxLayout()
        # sex.addWidget( QRadioButton("Male"))
        # sex.addWidget( QRadioButton("Female"))
        # layout.addRow( QLabel("Sex"),sex)
        # layout.addRow("Date of Birth", QLineEdit() )
        # self.setTabText(1,"Personal Details")
        # self.tab2.setLayout(layout)

        
        
    def analysis_tab_init( self ):

        tab_idx = self.analysis_tab_idx 
        
        # layout.addWidget( QLabel("subjects") ) 
        # layout.addWidget( QCheckBox("Physics"))
        # layout.addWidget( QCheckBox("Maths"))
        # # self.setTabText( 2, "Education Details" )

        
        # self.canvases[ tab_idx ].draw() 

        # box = QGroupBox( 'Data for Analysis' )

        
        self.analysis_data_dirs_qlist = QListWidget()
        self.analysis_data_dirs_qlist.addItem( 'test' )
        
        analysis_controls_layout = QVBoxLayout()
        analysis_controls_layout.addWidget(
            self.make_subtitle( 'Choose Analysis Directories' ) )
        analysis_controls_layout.addWidget( self.analysis_data_dirs_qlist ) 
        
        # layout.addWidget( self.analysis_data_dirs_qlist )
        # layout.addWidget( self.canvases[ tab_idx ] )
        # self.analysis_tab.setLayout( layout )

        # plotting 
        f, axarr = plt.subplots( 2, 2 )
        f.subplots_adjust( hspace = 0.5 )
        self.canvases[ tab_idx ] = FigureCanvas( f )

        
        layout = QGridLayout()
        layout.addLayout( analysis_controls_layout, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        layout.setColumnStretch( 0, 0.5 ) 
        layout.addWidget( self.canvases[ tab_idx ], 0, 1, 1, 1 )
        layout.setColumnStretch( 1, 1 ) 
        
        self.analysis_tab.setLayout( layout )
        


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

        # self.tdc_data_handler.read_data()
        self.tdc_mgr.read()
        self.tdc_data_processor.extract_candidates()
    
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
        print( 'INFO: loading tabor...' )

        
    def set_params_from_ion_data_button_clicked( self ) :
        print( 'INFO: setting tabor params from ion data...' ) 

        
    def toggle_daq_button_clicked( self ) :
        print( 'INFO: toggling DAQ...' ) 

        
    def clear_button_clicked( self ) :
        print( 'INFO: clearing data' ) 
        time.sleep(1)
        self.tdc_mgr.reset()
        self.tdc_data_processor.reset()

        
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
    
    # def session_path_button_clicked( self ) :
    #     print( 'INFO: setting session path' )
    #     session_dir = self.session_path_entry.text()

    #     data_name = self.data_name_entry.text() 
        
    #     print( session_dir )
    #     print( data_name )

    #     dir_path = str( QFileDialog.getExistingDirectory( self, "Select Directory") )

    #     print( dir_path ) 
        
    #     # def analysis_dir_list_clicked( self ) :
        

    
def main():
   app = QApplication(sys.argv)
   ex = gui()
   ex.show()
   sys.exit( app.exec_() )


   
   
if __name__ == '__main__':  
    main()
