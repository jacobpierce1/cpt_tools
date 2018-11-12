import cpt_tools
from gui_helpers.gui_config import * 
import gui_helpers


import numpy as np
import io


class CutWidget( object ) :

    def __init__( self, name, default_low, default_high ) :

        self.layout = QHBoxLayout()

        self.checkbox = QCheckBox()
        self.checkbox.setCheckState(2)
        
        self.lower_entry = QLineEdit( str( default_low ) )
        self.lower_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH )
        self.lower_entry.setValidator( QDoubleValidator(0., 10000., 10 ) )

        self.upper_entry = QLineEdit( str( default_high ) )
        self.upper_entry.setMaximumWidth( PLOTTER_WIDGET_QLINEEDIT_WIDTH ) 
        self.upper_entry.setValidator( QDoubleValidator(0., 10000., 10 ) )

        self.layout.addWidget( self.checkbox ) 
        self.layout.addWidget( self.lower_entry ) 
        self.layout.addWidget( self.upper_entry )

        self.name = name


    def read( self ) :

        if not self.checkbox.checkState() :
            return None 
        
        lower = self.lower_entry.text() 
        upper = self.upper_entry.text()

        if not ( lower or upper ) :
            return None

        if not lower :
            lower = - np.inf
        else :
            lower = float( lower )

        if not upper :
            upper = np.inf
        else :
            upper = float( upper ) 

        return [ lower, upper ] 



class FixedAspectFigureCanvas( FigureCanvas ) :

    def __init__( self, figure ) :
        super( FixedAspectFigureCanvas, self ).__init__( figure )
        # sizePolicy = QSizePolicy( QSizePolicy.Preferred, QSizePolicy.Preferred )
        sizePolicy = QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Maximum )
        sizePolicy.setHeightForWidth( True )
        self.setSizePolicy(sizePolicy)

    def heightForWidth( self, width ) :
        print( 'computing width' )
        return width 

    def sizeHint( self ) :
        return QtCore.QSize( 700, 700 ) 
    
    
class PlotterWidget( object ) :

    def __init__( self, plotter = None ) :

        if not plotter :
            plotter = plotting.Plotter()

        plot_selector_layout = QHBoxLayout()
        button_names = plotter.plot_titles 
        for i in range( len( button_names ) ) :
            button = QPushButton( button_names[i] )
            plot_selector_layout.addWidget( button ) 
            button.clicked.connect( lambda state, a=i : self.set_active_fig( a ) )
            
        self.plotter = plotter

        # self.canvas = FigureCanvas( self.plotter.f )
        self.canvas = FixedAspectFigureCanvas( self.plotter.f ) 
        self.canvas.mpl_connect( 'motion_notify_event', self.mouse_moved )        
        self.canvas.mpl_connect( 'button_press_event', self.clipboard_handler )

        # self.canvas.setFixedWidth( 700 )
        # self.canvas.setFixedHeight( 700 )
        
        
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
        defaults = np.array( [ self.plotter.mcp_x_bounds, self.plotter.mcp_y_bounds ] )
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

        
        self.tof_cut_widget = CutWidget( 'TOF Cut', DEFAULT_TOF_CUT_LOWER, DEFAULT_TOF_CUT_UPPER )

        self.radius_cut_widget = CutWidget( 'Radius Cut', DEFAULT_RADIUS_CUT_LOWER,
                                            DEFAULT_RADIUS_CUT_UPPER )

        self.sum_x_cut_widget = CutWidget( 'Sum X', DEFAULT_SUM_X_CUT_LOWER,
                                           DEFAULT_SUM_X_CUT_UPPER )

        self.sum_y_cut_widget = CutWidget( 'Sum Y', DEFAULT_SUM_Y_CUT_LOWER,
                                           DEFAULT_SUM_Y_CUT_UPPER )
        
        self.diff_xy_cut_widget = CutWidget( 'X - Y', DEFAULT_DIFF_XY_CUT_LOWER,
                                             DEFAULT_DIFF_XY_CUT_UPPER )
        
        layout = QVBoxLayout()

        
        
        controls_box = QGroupBox( 'Visualization Controls' )
        controls_layout = QFormLayout()

        
        reload_button = QPushButton( 'Reload Parameters' ) 
        reload_button.clicked.connect( self.reload_visualization_params )         
        controls_layout.addWidget( reload_button ) 

        controls_layout.addRow( 'Plot with Cuts', self.plot_with_cuts_button ) 
        controls_layout.addRow( 'Hitmap Type:', mcp_hitmap_buttons )
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
        cuts_layout.addRow( self.tof_cut_widget.name, self.tof_cut_widget.layout ) 
        cuts_layout.addRow( self.radius_cut_widget.name, self.radius_cut_widget.layout  ) 
        cuts_layout.addRow( self.sum_x_cut_widget.name, self.sum_x_cut_widget.layout  ) 
        cuts_layout.addRow( self.sum_y_cut_widget.name, self.sum_y_cut_widget.layout  ) 
        cuts_layout.addRow( self.diff_xy_cut_widget.name, self.diff_xy_cut_widget.layout  )
        
        cuts_box.setLayout( cuts_layout )
        layout.addWidget( cuts_box ) 

        fits_box = QGroupBox( 'Gaussian Fitting' )
        
        self.fit_widget = gui_helpers.FitWidget( self ) 
        
        fits_box.setLayout( self.fit_widget.layout )

        self.metadata_widget = gui_helpers.MetadataWidget( self.plotter.cpt_data )
        layout.addWidget( self.metadata_widget.box )

        canvas_layout = QVBoxLayout()
        canvas_layout.addLayout( plot_selector_layout )
        canvas_layout.addWidget( self.canvas )
        canvas_layout.addWidget( fits_box ) 

        self.coords_label = QLabel() 
        
        canvas_layout.addWidget( self.coords_label )

        self.grid_layout = QGridLayout()
        self.grid_layout.addLayout( layout, 0, 0, 0, 1, QtCore.Qt.AlignLeft )
        self.grid_layout.setColumnStretch( 0, 0.5 ) 
        self.grid_layout.addLayout( canvas_layout, 0, 1, 1, 1 )
        self.grid_layout.setColumnStretch( 1, 1 )

        # self.reload_visualization_params() 

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

            
    # # deallocate plotter 
    # def release( self ) :
    #     plotter.release()
        
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
        self.plotter.rectangular_hitmap.bin_width = float( self.mcp_bin_width_entry.text() )
        self.plotter.rectangular_hitmap.kde_bandwidth = float( self.mcp_kde_bw_entry.text() )

        self.plotter.rectangular_hitmap.bounds[0] = np.array(
            [ float( self.mcp_bounds_entries[0,j].text() ) for j in range(2) ] )

        self.plotter.rectangular_hitmap.bounds[1] = np.array(
            [ float( self.mcp_bounds_entries[1,j].text() ) for j in range(2) ] )
                

        self.plotter.tof_hist.n_bins = int( self.tof_hist_nbins_entry.text() )
        self.plotter.radius_hist.n_bins = int( self.r_hist_nbins_entry.text() )
        self.plotter.angle_hist.n_bins = int( self.angle_hist_nbins_entry.text() )
        
        tof_cut = self.tof_cut_widget.read()
        radius_cut = self.radius_cut_widget.read()
        sum_x_cut = self.sum_x_cut_widget.read()
        sum_y_cut = self.sum_y_cut_widget.read()
        diff_xy_cut = self.diff_xy_cut_widget.read()

        self.plotter.cpt_data.set_cuts( tof_cut = tof_cut, radius_cut = radius_cut,
                                        sum_x_cut = sum_x_cut, sum_y_cut = sum_y_cut,
                                        diff_xy_cut = diff_xy_cut ) 
                
        if self.plotter.cpt_data.is_live : 
            self.plotter.cpt_data.reset_cuts()
        self.plotter.cpt_data.apply_cuts()
        
        self.plotter.rectangular_hitmap.rebuild = 1
        self.plotter.polar_hitmap.rebuild = 1
        
        self.update()


    def zoom_in( self ) :

        bounds = [ self.plotter.mcp_x_bounds, self.plotter.mcp_y_bounds ]
        new_bounds = [ None, None ]
        for i in range(2) :
            new_bounds[i] = bounds[i] + np.array( [ 2.5, -2.5 ] )
            # print( new_bounds[i] )
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
            # print( new_bounds[i] ) 
            # if new_bounds[i][1] <= new_bounds[i][0] :
            #     print( 'WARNING: unable to zoom out' ) 
            #     return 

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

    def set_active_fig( self, i )  :
        self.plotter.clear() 
        self.plotter.active_fig = i
        self.plotter.update_all() 
        self.canvas.draw() 
        
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
