import cpt_tools
from gui_helpers.gui_config import *

import numpy as np 

PREDICTION_TACC_START = 15
PREDICTION_TACC_END = 200000
NUM_PREDICTIONS = 20


class CombinedAnalysisWidget( object ) :

    def __init__( self, analyzer ) :

        self.analyzer = analyzer 

        current_estimates_box = QGroupBox( 'Current Estimates' )
        current_estimates_layout = QVBoxLayout()
        current_estimates_box.setLayout( current_estimates_layout ) 
        
        self.mass_label_str = 'Current Mass Estimate: '
        self.mass_estimate_label = QLabel( self.mass_label_str + '?' ) 

        self.freq_label_str = 'Current Frequency Estimate: '
        self.freq_estimate_label = QLabel( self.freq_label_str + '?' ) 

        self.ame_mass_label_str = 'AME Mass Estimate: '
        self.ame_mass_estimate_label = QLabel( self.ame_mass_label_str + '?' ) 

        self.ame_freq_label_str = 'AME Frequency Estimate: '
        self.ame_freq_estimate_label = QLabel( self.ame_freq_label_str + '?' ) 

        current_estimates_layout.addWidget( self.mass_estimate_label )
        current_estimates_layout.addWidget( self.freq_estimate_label ) 
        current_estimates_layout.addWidget( self.ame_mass_estimate_label ) 
        current_estimates_layout.addWidget( self.ame_freq_estimate_label ) 

    
        data_box = QGroupBox( 'Processed Data' ) 
        data_layout = QVBoxLayout()
        data_box.setLayout( data_layout ) 
        
        data_cols = [ 'Accumulation \nTime (\u03bcs)', 'Measured \u0394\u03B8 (deg)' ]
        self.data_table = QTableWidget( 1, len( data_cols ) )
        self.data_table.setHorizontalHeaderLabels( data_cols )
        self.data_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        # self.data_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )


        data_layout.addWidget( self.data_table )

        # for i in range( len( data_cols ) ) :
        #     self.data_table.setColumnWidth( i, 100 ) 
        # self.data_table.setSizePolicy( MAX_SIZE_POLICY )

        
        self.data_table.setMinimumWidth( 250 ) 

                
        predictions_box = QGroupBox( 'Predictions' ) 
        predictions_layout = QVBoxLayout()
        predictions_box.setLayout( predictions_layout )

        # self.predictions_status_label = QLabel( 'Waiting for reference...' )
        # self.predictions_status_label.setStyleSheet( 'color: #E55959' ) 
        # predictions_layout.addWidget( self.predictions_status_label )
        
        predictions_cols = [ 'Accumulation \nTime (\u03bcs)',
                             'Corrected \u0394\u03B8 \nPrediction (deg)',
                             'AME \u0394\u03B8 \nPrediction (deg)' ]
        self.predictions_table = QTableWidget( NUM_PREDICTIONS, len( predictions_cols ) )
        self.predictions_table.setHorizontalHeaderLabels( predictions_cols )
        self.predictions_table.horizontalHeader().setSectionResizeMode( QHeaderView.Stretch ) 
        # self.predictions_table.verticalHeader().setSectionResizeMode( QHeaderView.Stretch )
        self.predictions_table.setMinimumWidth( 320 )
        predictions_layout.addWidget( self.predictions_table ) 
        

        canvas_box = QGroupBox( 'Visualization' ) 
        canvas_layout = QVBoxLayout() 
        # self.analyzer = analysis.CPTanalyzer()
        self.canvas = FigureCanvas( self.analyzer.f )
        canvas_layout.addWidget( self.canvas )
        canvas_box.setLayout( canvas_layout ) 

        
        self.layout = QHBoxLayout()
        tmp = QVBoxLayout()
        tmp.addWidget( current_estimates_box )
        tmp.addWidget( data_box ) 
        self.layout.addLayout( tmp )
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
        

    def update( self ) :

        self.analyzer.update()
        
        if len( self.analyzer.data_list ) > 0 : 
            self.mass_estimate_label.setText( self.mass_label_str +
                                              str( self.analyzer.current_mass_estimate ) )
            self.freq_estimate_label.setText( self.freq_label_str +
                                              str( self.analyzer.current_freq_estimate ) )
        else :
            self.mass_estimate_label.setText( self.mass_label_str + '?' ) 
            self.freq_estimate_label.setText( self.freq_label_str + '?' )

        self.ame_mass_estimate_label.setText( self.ame_mass_label_str +
                                              '%.1f' % self.analyzer.ame_mass )
        self.ame_freq_estimate_label.setText( self.ame_freq_label_str +
                                              '%.1f' % self.analyzer.ame_freq )

        self.populate_predictions() 
        
        self.canvas.draw() 
        


    def populate_predictions( self ) :

        taccs = np.linspace( PREDICTION_TACC_START, PREDICTION_TACC_END, NUM_PREDICTIONS, dtype = int )

        # need at least one reference to generate predictions 
        # if self.analyzer.reference_indices :
        #     self.predictions_status_label.setText( '' )
            
        for i in range( NUM_PREDICTIONS ) :
            tacc = taccs[i]

            ame_prediction = 50
            while( np.abs( ame_prediction - 5 ) > 5 ) :
                tacc += 1 
                ame_prediction = cpt_tools.mass_to_phase( self.analyzer.ame_mass, self.analyzer.q,
                                                          tacc, atomic_mass = 1 )
                
            self.predictions_table.setCellWidget( i, 0, QLabel( str( tacc ) ) )
            
            self.predictions_table.setCellWidget( i, 1, QLabel( '%.1f' % ame_prediction ) )
            # else : 
        #     self.predictions_status_label.setText( 'Waiting for reference...' )

        #     for i in range( NUM_PREDICTIONS ) :
        #         for j in range( 3 ) :
        #             self.predictions_table.setCellWidget( i, j, QLabel( '' ) ) 
