import cpt_tools
from gui_helpers.gui_config import * 
import numpy as np

MAX_NUM_SPOTS = 10
MAX_CHARGE = 2
MAX_NUM_MEASUREMENTS = 20
MAX_NUM_PREDICTIONS = 20

class TrackingWidget( object ) :

    def __init__( self ) :

        self.layout = QVBoxLayout()

        cols = [ str(i+1) for i in range( MAX_NUM_SPOTS ) ]
        tmp_cols = [ 'Accumulation Time (%ss)' % MU_UNICODE ] + cols 
        
        measurements_box = QGroupBox( 'Measurements: Accumulation Time vs. Absolute Angle' )
        self.measurements_table = QTableWidget( MAX_NUM_MEASUREMENTS, len( tmp_cols ) )
        self.measurements_table.setHorizontalHeaderLabels( tmp_cols )
        # self.measurements_table.setVerticalHeaderLabels( rows )
        self.measurements_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch )
        self.measurements_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )         
        layout = QVBoxLayout()
        layout.addWidget( self.measurements_table ) 
        measurements_box.setLayout( layout )

        for i in range( MAX_NUM_MEASUREMENTS ) :
            for j in range( MAX_NUM_SPOTS + 1 ) : 
                self.measurements_table.setCellWidget( i, j, QLineEdit() )

        
        rows = [ 'Frequency', 'Mass' ] + [ 'Candidates (Q=%d)' % (i+1) for i in range( MAX_CHARGE ) ]
        
        estimates_box = QGroupBox( 'Estimates' )
        make_estimates_button = QPushButton( 'Make Estimates' ) 
        self.estimates_table = QTableWidget( len( rows ), len( cols ) )
        self.estimates_table.setHorizontalHeaderLabels( cols )
        self.estimates_table.setVerticalHeaderLabels( rows )
        self.estimates_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch )
        self.estimates_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )         
        layout = QVBoxLayout()
        layout.addWidget( make_estimates_button ) 
        layout.addWidget( self.estimates_table ) 
        estimates_box.setLayout( layout )

        for i in range( MAX_NUM_SPOTS ) :
            self.estimates_table.setCellWidget( 0, i, QLineEdit() )
        
        
        predictions_box = QGroupBox( 'Predictions: Accumulation Time vs. Phase Difference' )
        generate_predictions_button = QPushButton( 'Generate Predictions' ) 
        self.predictions_table = QTableWidget( MAX_NUM_MEASUREMENTS, len( tmp_cols ) )
        self.predictions_table.setHorizontalHeaderLabels( tmp_cols )
        self.predictions_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch )         
        layout = QVBoxLayout()
        layout.addWidget( generate_predictions_button ) 
        layout.addWidget( self.predictions_table ) 
        predictions_box.setLayout( layout )

        for i in range( MAX_NUM_PREDICTIONS ) :
            self.predictions_table.setCellWidget( i, 0, QLineEdit( str( int( 100 * i ) ) ) )

        
        # rows = 

        # predictions_box = QGroupBox( 'Predictions' )
        # self.predictions_table = QTableWidget( 1, len( cols ) )
        # self.predictions_table.setHorizontalHeaderLabels( cols )
        # self.predictions_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch )         
        # layout = QVBoxLayout()
        # layout.addWidget( self.predictions_table ) 
        # predictions_box.setLayout( layout )  
        
        
        self.layout.addWidget( measurements_box ) 
        self.layout.addWidget( estimates_box ) 
        self.layout.addWidget( predictions_box ) 
        
