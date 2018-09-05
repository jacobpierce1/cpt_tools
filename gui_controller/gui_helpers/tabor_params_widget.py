import cpt_tools
from gui_helpers.gui_config import *

import numpy as np

from cpt_tools import TaborParams


MU_UNICODE = '\u03bc'



class TaborParamsWidget( object ) :

    # editable = 1 -> user can edit the fields
    # use_defaults: load the data with defaults from gui config 
    def __init__( self, editable, use_defaults, tooltips = 0 ) :

        if editable :
            Qtype = QLineEdit
        else :
            Qtype = QLabel

        self.layout = QVBoxLayout() 
            
        tmp = QFormLayout()

        if use_defaults :
            default_tacc = DEFAULT_TACC
            default_num_steps = DEFAULT_NUM_STEPS 
            default_table = DEFAULT_TABOR_SETTINGS
        else :
            default_tacc = ''
            default_num_steps = ''
            default_table = [ [ '' for i in range(3) ]
                              for i in range(5) ] 
        
        self.num_steps_entry = Qtype( str( default_num_steps ) )
        tmp.addRow( 'Num Steps:', self.num_steps_entry ) 

        self.tacc_entry = Qtype( str( default_tacc ) )
        tmp.addRow( 'Accumulation Time (%ss):' % MU_UNICODE, self.tacc_entry ) 

        self.layout.addLayout( tmp ) 
        
        nrows = 5
        ncols = 3 
        
        self.table = QTableWidget( nrows, ncols )
        self.table.setMinimumHeight( 150 ) 
        
        # combination of size policy change and resizemode change
        # makes the table not expand more than necessary 
        # size_policy = QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Maximum )
        
        # self.table.setSizePolicy( size_policy )
        # self.load_tabor_button.setSizePolicy( size_policy ) 
        
        self.table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        self.table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        
        self.table.setHorizontalHeaderLabels( [ 'w_-', 'w_+', 'w_c' ] )
        self.table.setVerticalHeaderLabels( [ 'omega', 'phase', 'amp',
                                               'loops', 'length' ] )
                
        omega_validator = QDoubleValidator( 0, 1e8, 4 ) 
        phase_validator = QDoubleValidator( -180.0, 180.0, 4 ) 
        amp_validator = QDoubleValidator( 0, 1.0, 4 ) 
        int_validator = QIntValidator( 0, 300 ) 

        if editable : 
            validators = [
                [ omega_validator ] * 3,
                [ phase_validator ] * 3,
                [ amp_validator ] * 3,
                [ int_validator ] * 3,
                [ int_validator ] * 3
            ]
        
        for i in range( nrows ) :
            for j in range( ncols ) :
                tmp = Qtype( str( default_table[i][j] ) )
                if editable : 
                    tmp.setValidator( validators[i][j] )
                self.table.setCellWidget( i,j, tmp )

        self.layout.addWidget( self.table ) 
        
        
    def fetch( self ) :
        tacc = int( self.tacc_entry.text() ) 
        nsteps = int( self.num_steps_entry.text() )
        types = [ float, float, float, int, int ]
        data = [ [ types[i]( self.table.cellWidget( i, j ).text() ) 
                   for j in range(3) ] 
                 for i in range( 5) ]
        
        print( data )
        freqs, phases, amps, loops, steps = data 
            
        tabor_params = cpt_tools.TaborParams( tacc, nsteps, freqs, phases,
                                              amps, loops, steps )

        return tabor_params 


    
    def set( self, tabor_params ) :
        return 
