import cpt_tools
from gui_helpers.gui_config import * 
from .ion_entry import IonEntry
import numpy as np


class CalibrationWidget( object ) :

    def __init__( self ) :

        self.box = QGroupBox( 'Calibration' ) 
        self.layout = QFormLayout() 
        self.box.setLayout( self.layout) 

        tmp = QHBoxLayout()

        self.mcp_center_coords_entries = [ QLineEdit(), QLineEdit() ] 

        for i in range(2) :
            tmp.addWidget( self.mcp_center_coords_entries[i] )
            
        button = QPushButton( 'Update MCP Center Coords' ) 
        tmp.addWidget( button ) 

        self.layout.addRow( 'MCP Center Coords', tmp )


        # tmp = QVBoxLayout()

        ion_entry = IonEntry()
        self.layout.addRow( ion_entry.layout )

        self.measured_freq_entry = QLineEdit()
        self.measured_freq_entry.setText( str( cpt_tools.calibrant_omega ) ) 
        self.layout.addRow( 'Measured Frequency', self.measured_freq_entry ) 

        button = QPushButton( 'Update Calibrant' )
        self.layout.addRow( button )
        
        
        # self.layout.addRow(  ) 
