import cpt_tools
from gui_helpers.gui_config import * 


class IonEntry( object ) :

    def __init__( self ) :

        self.layout = QFormLayout()
        
        labels = [ 'Z', 'A', 'q' ]
                    
        entries = [ None, None, None ]
        defaults = [ '55', '133', '1' ]

        ion_param_validator = QIntValidator( 0, 1000 ) 

        for i in range( len( labels ) ) :
            entries[i] = QLineEdit( defaults[i] ) 
            entries[i].setValidator( ion_param_validator )
            self.layout.addRow( labels[i], entries[i] )

        self.z_entry, self.a_entry, self.q_entry = entries 
        

    def fetch( self ) :
        z = self.z_entry.text() 
        a = int( self.a_entry.text() )
        q = int( self.q_entry.text() )

        try :
            z = int( z )
        except ValueError : 
            z = cpt_tools.element_to_z

        return [ z, a, q ] 



# class IonEntry( object ) :

#     def __init__( self ) :
#         pass
