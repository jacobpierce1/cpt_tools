import cpt_tools
from gui_helpers.gui_config import * 


            
                                       
class FitWidget( object ) :

    def __init__( self, plotter_widget, analyzer = None ) :

        self.plotter_widget = plotter_widget        
        self.plotter = plotter_widget.plotter
        self.hists = self.plotter.all_hists
        
        self.layout = QVBoxLayout()

        params_labels = [ 'A', '\u03c3', '\u03c72', '\u03bc' ]
        self.num_params = len( params_labels ) 

        h_labels = [ '', '', 'Left', 'Right' ]
        h_labels.extend( params_labels ) 
        v_labels = [ x.title for x in self.hists ] 
        
        nrows = len( v_labels )
        ncols = len( h_labels ) 

        self.table = QTableWidget( nrows, ncols ) 
        self.table.setMinimumWidth( 400 ) 
        self.table.setMinimumHeight(100)
        # self.table.setMaximumHeight(200)
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
        
        for i in range( len( self.hists ) ) :
            
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
            print( 'ERROR: fit failed' ) 
            return
        
        params, params_errors, redchisqr = fit
        
        if params_errors is not None : 
            labels = [ '%.2f\u00b1%.2f' % ( params[j], params_errors[j] ) for j in range( len(params) ) ]
        else :
            labels = [ '%.2f' % params[j] for j in range( len(params) ) ]
            
        labels.append( '%.2f' % redchisqr )
        for j in range( len(params) + 1 ) : 
            self.params_labels[i][j].setText( labels[j] )

        self.plotter.update_all()
        self.plotter_widget.reload_visualization_params()

        # if self.analyzer is not None :
        #     if i == 1 :
        #         self.analyzer.set_active_radius( 

            # self.analyzer.set_active_fit_params( fit ) 
            
        # ret = analysis.gaussian_fit( self.cpt_data ) 


    # def 
        

    def delete_button_clicked( self, i ) :
        self.hists[i].remove_fit() 
