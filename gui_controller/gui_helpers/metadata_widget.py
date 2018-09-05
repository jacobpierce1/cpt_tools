import cpt_tools
from gui_helpers.gui_config import * 
import numpy as np

        

class MetadataWidget( object ) :

    def __init__( self, cpt_data ) :

        self.cpt_data = cpt_data
        
        self.box = QGroupBox( 'Metadata' )
        
        h_labels = [ 'Counts', 'Rate (Hz)' ]
        v_labels = [ 'MCP Hits', 'Valid data', 'Cut Data', 'Penning Eject' ]
        
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
                   self.cpt_data.num_cut_data, self.cpt_data.num_penning_ejects ]

        for i in range( len( counts ) ) :
            self.table.cellWidget( i, 0 ).setText( '%d' % counts[i] )

            if self.cpt_data.duration > 0 : 
                rate = counts[i] / self.cpt_data.duration
            else :
                rate = np.nan
                
            self.table.cellWidget( i, 1 ).setText( '%.2f' % rate ) 

        self.time_label.setText( self.time_label_str + '%d'
                                 % int( self.cpt_data.duration ) )
            
        
        
