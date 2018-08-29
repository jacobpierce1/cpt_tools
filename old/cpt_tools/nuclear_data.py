import numpy as np 
import os
import sys
import re



# available constants





print( os.path.dirname( os.path.abspath( __file__ ) ) ) 
data_path = os.path.join( os.path.dirname( os.path.abspath( __file__ ) ),  'data' )

# data_path = '../data/'
# print( type( data_path ) ) 

ame16_data_path = os.path.join( data_path, 'ame16_all_masses_accurate.txt' )
nubase2016_data_path = os.path.join( data_path, 'nubase2016_raw.txt' ) 
wallet_card_path = os.path.join( data_path, 'nuclear-wallet-cards.txt' ) 
fission_yield_data_path = os.path.join( data_path, 'fissionyields.txt' )
abundances_path = os.path.join( data_path, 'abundances.txt' )


max_Z = 119
max_N = 200




def _get_periodic_table_dict() :

    periodic_table_string = '''h he
    li be b c n o f ne
    na mg al si p s cl ar
    k ca sc ti v cr mn fe co ni cu zn ga ge as se br kr
    rb sr y zr nb mo tc ru rh pd ag cd in sn sb te i xe
    cs ba la ce pr nd pm sm eu gd tb dy ho er tm yb lu hf ta w re os ir pt au hg tl pb bi  po at rn
    fr ra ac th pa u np pu am cm bk cf es fm md no lr rf db sg bh hs mt ds rg cn nh fl mc lv ts og'''

    keys = periodic_table_string.split() 
    
    tmp = dict( zip( keys, range( 1, 119 ) )  )

    tmp[ 'd' ] = 1 

    return tmp 


_periodic_table_dict = _get_periodic_table_dict()
_reverse_periodic_table_dict = {v: k for k, v in _periodic_table_dict.items()}



def element_to_z( elem ) :
    return _periodic_table_dict[ elem.lower() ] 

def z_to_element( z ) :
    return _reverse_periodic_table_dict[ z ] 


class _NuclearData( object ) :

    def __init__( self ) :

        self._masses = _load_masses()
        self._half_lives = _load_half_lives() 
        self._rel_abundances = _load_rel_abundances()
        self._cf_yields = _load_cf_yields()

        self.electron_mass = 548.579909
        self.neutron_mass = 1.008665e6
        self.proton_mass = 1.007276e6 


    @property
    def masses( self ) :
        return self._masses 

    @property
    def half_lives( self ) :
        return self._half_lives

    @property
    def rel_abundances( self ) :
        return self._rel_abundances
    
    @property
    def cf_yields( self ) :
        return self._cf_yields


def _load_masses() :

    atom_masses = np.zeros( ( max_Z, max_N ) )

    # default value 
    atom_masses[:] = -1 
    
    # parse the ame16 data. this only has ground state masses. 
    
    with open( ame16_data_path ) as f :

        # skip first line 
        f.readline()

        for line in f.readlines() :

            data = line.split( '\t' )
            Z = int(data[1])
            N = int(data[0])

            name = data[3] 
            mass = float( data[4] )

            atom_masses[Z,N] = mass

    return atom_masses 




    
    
def _load_half_lives() :
    
    half_lives = np.zeros( ( max_Z, max_N ) )
    half_lives[:] = np.nan

    with open( wallet_card_path ) as f :

        for full_line in f.readlines()  :

            line = full_line.split()

            if 'STABLE' in full_line :
                half_life = np.inf

            else :
                try : 
                    half_life = float( line[-1] )
                except:
                    continue

            if has_digit( line[0] ) :
                A_idx = 0

            else :
                A_idx = 1

            # can't currently handle excited states. 
            if not line[ A_idx ].isdigit() :
                continue

            else : 
                A = int( line[ A_idx ] ) 

            Z = int( line[ A_idx + 1 ] ) 
            
            # this denotes a metastable state
            # A = string_to_numstring( line[0] )
            # if A == '' :
            #     A = int( string_to_numstring( line[ 1 ] ) ) 
            #     Z = int( line[ 2 ] )

            # else :
            #     A = int( A )
            #     Z = int( line[1] ) 

            N = A - Z

            
            # if Z == 9 :
            #     print( full_line )
            #     print( N ) 
            #     print( half_life ) 

            half_lives[ Z, N ] = half_life

                    
    return half_lives




def _load_rel_abundances() :
    
    abundances = np.zeros( ( max_Z, 250 ) )
    abundances[:] = np.nan
    
    current_Z = 0

    skiplines = 0 
    
    with open( abundances_path ) as f :
        
        for line in f.readlines() :

            if skiplines < 3 :
                skiplines += 1
                continue

            line = line.split()

            # print( line ) 

            # if( not line or len( line ) < 4 or not( line[0].isdigit() ) ) :
            #     continue
            
            if line[0].isdigit() and line[1].isalpha() :
                Z_idx = 0 
                Z = int( line[0] )
                current_Z = Z
                min_len = 5

            else :
                Z_idx = -2 
                Z = current_Z
                min_len = 3 

            if len( line ) < min_len :
                continue

            A = int( line[ 2 + Z_idx ] )
            abund = line[ 4 + Z_idx ]

            if '[' in abund :
                continue
            
            parenth_idx = abund.find( '(' )
            if parenth_idx != -1 :
                abund = float( abund[ : parenth_idx ] )

            # print( abund ) 

            N = A - Z

            # print( line )
            # print( Z, N )
            # print( abund ) 
                        
            abundances[Z,N] = abund
    
    return abundances




def _load_cf_yields() :
    
    cf_yields = np.zeros( ( max_Z, max_N ) )
    cf_yields[:] = np.nan

    with open( fission_yield_data_path ) as f :

        for line in f.readlines() :

            line = line.split()

            if( not line ) :
                continue

            element_string = line[0]
            A, element_name  = re.findall( r'(\d*)([A-Z][a-z]*)', element_string )[0]
            A = int( A )
            Z = element_to_z( element_name )
            N = A - Z 
                        
            fission_yield = float( line[-2] ) / 200
            cf_yields[ Z, N ] = fission_yield
            
    return cf_yields 




def string_to_numstring( s ) :
     return ''.join( [ c for c in s if c.isdigit() ] )

 
def has_digit( s ) :
    for c in s :
        if c.isdigit() :
            return 1
    return 0




print( 'INFO: loading nuclear data (this should only be printed once)' ) 
nuclear_data = _NuclearData() 


# masses = _load_masses()
# half_lives = _load_half_lives()
# cf_yields = _load_cf_yields()
# rel_abundances = _load_rel_abundances()
