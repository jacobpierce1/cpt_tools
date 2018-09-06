import cpt_tools
from gui_helpers.gui_config import * 
import gui_helpers


import numpy as np
import io


class PlotterWidget( object ) :

    def __init__( self, plotter = None ) :

        if not plotter :
            plotter = plotting.Plotter()
            
        self.plotter = plotter

        self.canvas = FigureCanvas( self.plotter.f )
        self.canvas.mpl_connect( 'motion_notify_event', self.mouse_moved )        
        self.canvas.mpl_connect( 'button_press_event', self.clipboard_handler )
        
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
        self.mcp_kde_bw_entry = QLineEdit( str( self.plotter.kde_bandwidth ) )
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
        
        self.r_upper_cut_entry = QLineEdit( str(10) )
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

        cuts_box = QGroupBox( 'Data Cuts' ) 
        cuts_layout = QFormLayout() 
        cuts_layout.addRow( 'TOF lower / upper bounds:', tof_bounds ) 
        cuts_layout.addRow( 'Radius Cut:', r_bounds ) 
        cuts_box.setLayout( cuts_layout )
        layout.addWidget( cuts_box ) 

        fits_box = QGroupBox( 'Gaussian Fitting' )
        # fits_layout = QVBoxLayout()
        # fits_layout.setSpacing(0)
        
        self.fit_widget = gui_helpers.FitWidget( self ) 
        
        fits_box.setLayout( self.fit_widget.layout )
        # self.fit_widget.layout.setMinimumHeight( 150 )
        # layout.addWidget( fits_box ) 

        self.metadata_widget = gui_helpers.MetadataWidget( self.plotter.cpt_data )
        layout.addWidget( self.metadata_widget.box )

        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget( self.canvas )
        canvas_layout.addWidget( fits_box ) 

        self.coords_label = QLabel() 
        
        canvas_layout.addWidget( self.coords_label )

        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout( layout, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        self.grid_layout.setColumnStretch( 0, 0.5 ) 
        self.grid_layout.addLayout( canvas_layout, 0, 1, 1, 1 )
        self.grid_layout.setColumnStretch( 1, 1 ) 

        # self.grid_layout = QHBoxLayout()
        # self.grid_layout.addLayout( layout )
        # self.grid_layout.addLayout( 

        
    def update( self, update_first = 0 ) :
        if not update_first : 
            self.canvas.draw()
            
        self.plotter.update_all()
        self.metadata_widget.update()

        if update_first or not self.plotter.cpt_data.is_live :
            self.canvas.draw()

            
    # deallocate plotter 
    def release( self ) :
        plotter.release()
        
    def plot_with_cuts_clicked( self ) :
        plot_with_cuts = self.plot_with_cuts_button.checkState() 
        self.plotter.set_plot_with_cuts( plot_with_cuts )
        # self.plotter.cpt_data.apply_cuts() 
        self.reload_visualization_params() 
        
    def set_use_kde( self ) :
        self.plotter.use_kde = 1
        self.reload_visualization_params()
        
    def disable_use_kde( self ) :
        self.plotter.use_kde = 0 
        self.reload_visualization_params() 
        
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

        self.plotter.tof_hist.n_bins = int( self.tof_hist_nbins_entry.text() )
        self.plotter.radius_hist.n_bins = int( self.r_hist_nbins_entry.text() )
        self.plotter.angle_hist.n_bins = int( self.angle_hist_nbins_entry.text() )
        
        self.plotter.cpt_data.tof_cut_lower = float( self.tof_lower_cut_entry.text() )
        self.plotter.cpt_data.tof_cut_upper = float( self.tof_upper_cut_entry.text() )
        self.plotter.cpt_data.r_cut_lower = float( self.r_lower_cut_entry.text() )
        self.plotter.cpt_data.r_cut_upper = float( self.r_upper_cut_entry.text() )
        
        
        if self.plotter.cpt_data.is_live : 
            self.plotter.cpt_data.reset_cuts()
        self.plotter.cpt_data.apply_cuts()
        
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


            
    # store the image in a buffer using savefig(), this has the
    # advantage of applying all the default savefig parameters
    # such as background color; those would be ignored if you simply
    # grab the canvas using Qt
    def clipboard_handler( self, event ):
        # print( 'reached clipboard handler' ) 
        if event.dblclick :
            # print( 'copying...' ) 
            # if event.key == 'ctrl+c':
            buf = io.BytesIO()
            self.plotter.f.savefig(buf)
            QApplication.clipboard().setImage(QImage.fromData(buf.getvalue()))
            buf.close()
