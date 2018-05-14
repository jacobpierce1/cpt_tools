# TITLE: CPT contaminant identifier
# AUTHOR: jacob pierce, Argonne National lab
# DATE: 4.27.18
#
# DESCRIPTION: given the cyclotron frequency of something measured in
# the CPT (or elsewhere), CPT, determine all possible nuclides or
# molecules that could produce that cyclotron frequency.

# all masses are given in 10^6 AMU. all frequencies are measured in
# Hz.  charges are measured in units of electron charge


import numpy as np
import sys
import pandas as pd
import os
import pickle
import itertools
import time
import re
import datetime
import sqlite3
from molecule_parser import atom_counter


# define this for database debug
DEBUG_DB = 0



# from periodic_table_dict import get_periodic_table_dict

molecule_db_dir = './storage/'
molecule_db_schema_path = './molecule_db_schema.sql'


ame16_data_path = './data/ame16_all_masses_accurate.txt'
nubase2016_data_path = './data/nubase2016_raw.txt'
wikipedia_molecule_data_path = './data/wikipedia_molecule_data.txt'
wallet_card_path = './data/nuclear-wallet-cards.txt'
fission_yield_data_path = './data/fissionyields.txt' 
stable_isotopes_path = './data/stable_masses.txt'




# B is obtained using this calibration data

electron_mass = 548.579909
neutron_mass = 1.008665e6
proton_mass = 1.007276e6 

cesium_133_mass = 132905451.961
cesium_133_omega =  657844.45

line_break =  '----------------------------------------------------------' * 2 

max_Z = 119
max_N = 200
max_A = 500 


min_half_life = 0.05  # seconds. modifiable as command line arg 


# used for debug 
proton_mass = 1.007276e6 

# the maximum charge of an ion or molecule in the trap 
max_charge = 2

# maximum number of atoms constituting a  molecule
max_atoms_per_molecule = 7

# probability of nuclide production must be at least this much
# to be considered in calculations 
min_cf_yield_fraction = 1e-8




def get_periodic_table_dict() :

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



periodic_table_dict = get_periodic_table_dict()



def main() :

    if len( sys.argv ) <= 4 :

        print( ( '\nERROR: 4 arguments were not supplied'
                 + '\n\tsyntax: contaminant_identifier  [mode]  [A]  [omega]  [d_omega]  <min_lifetime>\n'
                 + '\n\t mode: 0 for known molecules, 1 for all combinations '
                 + '(computationally intensive)\n'
        ) )

        return

    print( '\n' ) 
    
    # atomic number of singly ionized ions in the trap
    mode = int( sys.argv[1] )
    A1 = int( sys.argv[2] ) 
    omega = float( sys.argv[3] )
    d_omega = float( sys.argv[4] )

    # specified in seconds
    if len( sys.argv ) > 5  :
        min_lifetime = float( sys.argv[5] )
        

    # A for the q = 1 isobar 
    # print( omega_to_mass( omega, 1 ) / proton_mass ) 
    # A1 = 
    
    half_lives = get_half_life_data() 
    cf_yields = get_cf_yield_data()
    stable_abundances = get_stable_abundances_data() 

    atom_masses = get_atom_masses()
    
    filtered_atom_masses, filtered_atom_labels = get_filtered_atom_masses_and_labels(
        atom_masses, half_lives, cf_yields, stable_abundances )
    
    if mode == 0 :

        print( line_break ) 
        check_ions( atom_masses, A1, omega, d_omega,
                    half_lives, cf_yields, stable_abundances )
        
        print( line_break ) 

    elif mode == 1 :
        
        molecule_db = get_molecule_db( filtered_atom_masses, filtered_atom_labels )
        print( '' ) 

        print( line_break ) 

        check_ions( atom_masses, A1, omega, d_omega,
                    half_lives, cf_yields, stable_abundances )

        print( line_break )
        print( '\n' * 4 )
        print( line_break ) 

        check_molecule_combinations( molecule_db, A1, omega, d_omega,
                                     half_lives, cf_yields, stable_abundances ) 

        print( line_break ) 
        
    elif mode == 2 :

        print( line_break ) 
        check_all_ion_combinations( atom_masses, atom_labels, A1 ) 
        print( line_break ) 
        
    else :
        print( 'ERROR: mode not implemented\n' )
        return -1

    return 0








def check_ions( atom_masses, A1, omega, d_omega,
                half_lives, cf_yields, stable_abundances ) :

    print( 'ION MATCHES' )
    print( 'OMEGA\t NAME\t Z\t N\t T_1/2\t CF_YIELD_OR_NATURAL_ABUND\n' )

    none_found_flag = 1 
    
    for q in range( 1, max_charge + 1 ) :
        
        total_A = q * A1
        
        # print( '\n\nINFO: Checking q = %d,  A = %d' % ( q, total_A)  )

        
        for Z in range( 1, max_Z ) :
            
            N = total_A - Z 

            if N >= max_N :
                continue

            
            # we have a candidate, add mass and all labels
            mass = atom_masses[Z][N]

            # default value: mass was not found in ame16
            if mass == -1 :
                continue
            
            mass -= q * electron_mass 
            current_omega = mass_to_omega( mass, q )
            
            
            if np.abs( current_omega - omega ) <= d_omega : 

                half_life = half_lives[ Z, N ]
                
                if half_life == np.inf :
                    tmp = stable_abundances[ Z, N ]
                    
                else :
                    tmp = cf_yields[ Z, N ]

                cf_yield_or_abund = tmp

                # half_life_str = '%.2e' % half_life 
                # cf_yield_or_abund_str = '%.2e' % cf_yield_or_abund
                
                element_name = get_element_name( Z ).title()
                
                print( '%.1f\t%s %d\t%d\t%d\t%.2f\t%.2f' % ( current_omega, element_name,
                                                             total_A, Z, N,
                                                             half_life, cf_yield_or_abund ) )
                
                none_found_flag = 0

    if none_found_flag :

        print( 'NONE FOUND' ) 
                    
            
    







# check every possible combination of ions, regardless of
# whethere it is a molecule in the wikipedia page

def check_all_ion_combinations( masses, labels ) :
    
    candidate_masses = []
    candidate_indices = [] 
    candidate_labels = []

    # time_estimator = TimeEstimator(  

    for q in range( 1, max_charge + 1 ) :

        print( 'checking q=%d...' % q  )

        # the A of each constituent needs to sum to this
        total_A = q * A1

        # # construct A indices that are possible
        # possible_A_values = []
        # for i in range( 1, total_A + 1 ) :
        #     possible_A_values.extend( [i] * min( max_molecule_size,
        #                                          total_A // i ) )

        # print( possible_A_values ) 
            
        # loop through lists of A values that add to total_A 
        A_indices = get_partitions( total_A, total_A, max_molecule_size ) 

        # total_A, max_len = max_molecule_size ) 

        # print( list( A_indices ) ) 
        
        print( 'Found %d isobar candidates...' % len( list( A_indices ) ) ) 

        time_estimator = TimeEstimator( len( A_indices ), 20 )

        for A_index in A_indices : 


            # print( 'A_list: ' + str( A_list ) )
            # print( masses[ A_list[0] ] )
            # print( [ len( masses[ A_list[x] ] ) for x in range( len( A_list) ) ] )
            
            num_indices = len( A_index )
            
            nuclide_indices = itertools.product( * [ range( len( masses[ A_index[x] ] ) )
                                               for x in range( num_indices ) ]  ) 


            for nuclide_index in nuclide_indices :

                # print( A_indices ) 
                # print( nuclide_index ) 
                mass = np.sum( [ masses[ A_index[ x ] ][ nuclide_index[ x ] ]
                                 for x in range( num_indices ) ] )

                mass -= q * electron_mass 

                # print( mass ) 
                # print( mass / proton_mass ) 

                # we have a candidate, add mass and all labels 
                if np.abs( mass_to_omega( mass, q ) - omega ) <= d_omega : 

                    candidate_masses.append( mass )
                    candidate_indices.append( [ A_index, nuclide_index ] )
                    
                    nuclide_labels = [ labels[ A_index[ x ] ][ nuclide_index[ x ] ]
                                              for x in range( num_indices ) ]

                    print( nuclide_labels ) 

                    
                    candidate_labels.append( [ nuclide_labels ] )

                    
                    
        
            
    
         



# modified from 
# https://stackoverflow.com/questions/17720072/print-all-unique-integer-partitions-given-an-integer-as-input

def get_partitions( target, maxvalue, max_len ) :

    ret = []
    get_partitions_recurs( target, maxvalue, ret, [], max_len  )
    return ret 




def get_partitions_recurs( target, maxvalue, ret, partial, max_len ) : 
    
    if target == 0 :
        ret.append( partial )

    else :
        if maxvalue > 1 :
            get_partitions_recurs( target, maxvalue - 1, ret, partial, max_len )

        if maxvalue <= target :

            if len( partial ) >= max_len :
                return
            
            get_partitions_recurs( target - maxvalue, maxvalue,
                                   ret, partial + [ maxvalue ], max_len  )





def check_molecule_combinations( molecule_db, A0, omega, d_omega,
                                 half_lives, cf_yields, stable_abundances ) :

    candidate_masses = []
    candidate_indices = [] 
    candidate_labels = []

    none_found_flag = 1 
    
    print( 'MOLECULE MATCHES' )
    print( 'KEY:' )
    print( 'MOLECULE NAME' )
    print( '\tOMEGA  (Hz)' ) 
    print( '\tZ' )
    print( '\tN' )
    print( '\tHalf lives (inf = stable)  (seconds)' )
    print( '\tCf yield if unstable, else natural abundance\n' )

    
    for q in range( 1, max_charge + 1 ) :


        # the A of each constituent needs to sum to this
        total_A = q * A0

        print( '\n\nINFO: checking q = %d,  A = %d' % ( q, total_A)  )

        Avals = [ total_A ] 
        
        # num_molecules_to_test = np.sum( [ len( molecule_masses[A] ) for A in Avals ] )

        # print( 'testing %d molecules...' % num_molecules_to_test )
        
        for A in Avals :

            # todo
            # isobar_molecules = molecule_db.read_isobar( A )
            mass_low = omega_to_mass( omega + d_omega, q ) + q * electron_mass 
            mass_high = omega_to_mass( omega - d_omega, q ) + q * electron_mass

            print( [ mass_low, mass_high ] ) 
            
            isobar_molecules = molecule_db.search_mass( mass_low, mass_high ) 
            
            print( 'INFO: checking %d molecules...\n' % len( isobar_molecules ) )
            # print( 'OMEGA\tMASS\tID\tZ\tN\tT_1/2\tCF_YIELDS_OR_ABUND' ) 
            
            for data in isobar_molecules : 
            
                # print( data[ 'A' ] )
                # print( pickle.loads( data[ 'label' ] ) )
                mass = data[ 'mass' ] 
                    
                # time_estimator = TimeEstimator( len( A_indices ), 20 )

                mass -= q * electron_mass

                current_omega = mass_to_omega( mass, q )

                # print( '%f\t%d\t%s' % ( current_omega, int( mass ),
                #                                      pickle.loads( data[ 'label' ] ) ) )
                
                # we have a candidate, add mass and all labels 
                # if np.abs( current_omega - omega ) <= d_omega : 
                    
                    
                    # candidate_masses.append( mass )
                    # candidate_indices.append( [ A_index, nuclide_index ] )
                    
                    # nuclide_labels = [ labels[ A_index[ x ] ][ nuclide_index[ x ] ]
                    #                   for x in range( num_indices ) ]

                A = data['A'] 
                molecule_name, Z, N = pickle.loads( data[ 'label' ] )

                half_life = []
                for i in range( len( Z ) ) :
                    tmp = half_lives[ Z[i], N[i] ]

                        # if tmp == np.inf :
                        #     tmp = 'stable'
                            
                    half_life.append( tmp  )


                # store cf yield if unstable or relative natural abundance if stable 
                cf_yields_or_abund = []
                cf_yields_or_abund_str = [] 
                for i in range( len( Z ) ) :

                    if half_lives[ Z[i], N[i] ] == np.inf :
                        tmp = stable_abundances[ Z[i], N[i] ]

                    else :
                        tmp = cf_yields[ Z[i], N[i] ]

                    cf_yields_or_abund.append( tmp )


                half_life_str = [ '%.2e' % x for x in half_life ] 
                cf_yields_or_abund_str = [ '%.2e' % x for x in cf_yields_or_abund ]

                # print( '%.1f\t%s\t%s\t%s\t%s\t%s' % ( current_omega, id, str(Z), str(N),
                #                                           half_life_str, cf_yields_or_abund_str ) )

                # print( '%s' % id )
                # print( '\t%.1f \t\t Omega' % current_omega ) 
                # print( '\t%s \t\t Z' % str( Z ) )
                # print( '\t%s \t\t N' % str( N ) )
                # print( '\t%s \t\t t_1/2 ' % str( half_life_str ) )
                # print( '\t%s \t\t Cf yields or natural abund' % str( cf_yields_or_abund_str ) )
                # print( '\n' )

                print( '%s' % molecule_name )
                print( '\t%d' % A ) 
                print( '\t%.1f' % current_omega ) 
                print( '\t%s' % str( Z ) )
                print( '\t%s' % str( N ) )
                print( '\t%s' % str( half_life_str ) )
                print( '\t%s' % str( cf_yields_or_abund_str ) )
                print( '\n' )

                none_found_flag = 0 
                    
                    # candidate_labels.append( [ nuclide_labels ] )

    if none_found_flag :

        print( 'NONE FOUND' ) 

                    
    

    

# num_entries = 10000


def get_atom_masses() :

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
            # return ( atom_masses, atom_labels )






def get_filtered_atom_masses_and_labels( atom_masses, half_lives, cf_yields, stable_abundances ) :

    mask = ( ( ( cf_yields >= min_cf_yield_fraction )
               & ( half_lives >= min_half_life ) )
             | ( half_lives == np.inf ) )

    
    filtered_atom_masses = [ [] for z in range( max_Z ) ]
    filtered_atom_labels = [ [] for z in range( max_Z ) ]

    numZ, numN = atom_masses.shape

    for Z in range( numZ ) :

        for N in range( numN ) : 
    
            if mask[Z,N] :
                
                filtered_atom_masses[Z].append( atom_masses[Z][N] )
                
                # todo : add excited state info here
                # excited_state_number = 0 
                
                filtered_atom_labels[Z].append( N )  

    return filtered_atom_masses, filtered_atom_labels 
    





def get_molecule_db( atom_masses, atom_labels ) :

    transaction_block_size = 10000
    
    molecule_db = molecule_db_manager()

    if molecule_db.exists :
        return molecule_db        
    

    num_lines = file_len( wikipedia_molecule_data_path ) 

    time_estimator = TimeEstimator( 2600, 100 ) 

    iteration = 0

    molecule_db.begin_transaction()
    
    with open( wikipedia_molecule_data_path ) as f :

        for line in f.readlines() :

            # print( line ) 
            
            time_estimator.update() 
            
            line = line.split( '\t' )

            if line[0] == 'Chemical formula' :
                continue

            elif len( line ) == 0 :
                continue

            # check that first character is capital
            elif not line[0][0].isupper() :
                continue

            
            # otherwise parse
            # https://stackoverflow.com/questions/13923325/parsing-chemical-formula
            molecule_string = line[0]

            print( molecule_string ) 
            
            molecule_counts = atom_counter( molecule_string )

            # print( molecule_counts ) 
            
            if sum( molecule_counts.values() ) > max_atoms_per_molecule :
                continue
            
            Z_list_unique = [ periodic_table_dict.get( x.lower() ) for x in molecule_counts.keys() ]

            # make sure it's a valid molecule
            if None in Z_list_unique :
                continue

            num_elements = len( Z_list_unique ) 

            Z_num_occurrences = list( molecule_counts.values() )  

            Z_list_repeats = [ Z_list_unique[i]  for i in range( len( Z_list_unique ) )
                               for j in range( Z_num_occurrences[i] ) ]

            total_Z = np.sum( Z_list_repeats ) 

            # now we have a list with (repeated) values of Z. find all unique
            # permutations of the corresponding neutron number for nuclies
            # which are produced in the Cf fission above our probability threshold
            # and have a half life above the threshold ( these filteres were already
            # applied in generation of the atomic mass table array )


            # tmp = [ [ list(tup) for tup in
            #         itertools.combinations_with_replacement( range(
            #             len( atom_masses[ Z_list_unique[i] ] ) ),
            #             Z_num_occurrences[i] ) ]
            #         for i in range( len( Z_list_unique ) ) ]

            tmp = [ itertools.combinations_with_replacement(
                range( len( atom_masses[ Z_list_unique[i] ] ) ),
                Z_num_occurrences[i] )
                    for i in range( len( Z_list_unique ) ) ]

            
            for N_indices in itertools.product( * tmp ) :
      
                A = total_Z
                mass = 0
                label = [ molecule_string, Z_list_repeats, [] ]
                
                for i in range( num_elements ) :

                    tmp = atom_labels[ Z_list_unique[i] ]
                    
                    for j in range( Z_num_occurrences[i] ) :

                        A += tmp[ N_indices[i][j] ]
                        mass += atom_masses[ Z_list_unique[i] ][ N_indices[i][j] ]
                        label[2].append( tmp[ N_indices[i][j] ] )
                        
      
                if iteration % transaction_block_size == 0 :
                    molecule_db.end_transaction() 
                    molecule_db.begin_transaction()
                
                molecule_db.insert_molecule_data( A, mass, label )

                iteration += 1 

                # print( 'Inserted data: %d %f %s' % ( A, mass, str(label) ) )


    molecule_db.end_transaction()
    molecule_db.update_db_complete_metadata()

    return molecule_db 






def get_stable_abundances_data() :

    stable_abundances = np.zeros( ( 126, 200 ) )

    with open( stable_isotopes_path ) as f :
        
        for line in f.readlines() :

            line = line.split()

            # print( line ) 
            if( not line ) :
                continue

            A = int( line[0] )
            symbol = line[1]
            abund = line[2]
            
            Z = periodic_table_dict[ symbol.lower() ]
            N = A - Z
            
            stable_abundances[Z,N] = abund
    
    return stable_abundances




def get_cf_yield_data() :

    cf_yields = np.zeros( ( 126, 200 ) )

    with open( fission_yield_data_path ) as f :

        for line in f.readlines() :

            line = line.split()

            if( not line ) :
                continue

            element_string = line[0]
            A, element_name  = re.findall( r'(\d*)([A-Z][a-z]*)', element_string )[0]
            A = int( A )
            Z = periodic_table_dict[ element_name.lower() ]
            # print( element_name )
            # print( Z )  
            N = A - Z 
                        
            fission_yield = float( line[-2] ) / 200
            cf_yields[ Z, N ] = fission_yield
            
            # if fission_yield > min_cf_yield_fraction :

            #     cf_yield_bools[Z][N] = 1
    
    return cf_yields 








def get_half_life_data() :

    half_lives = np.zeros( ( 126, 200 ) )

    # print( 'INFO: using min half life %f seconds' % min_half_life ) 

    with open( wallet_card_path ) as f :

        for line in f.readlines()  :

            line = line.split()

            # this denotes a metastable state
            A = string_to_numstring( line[0] )
            if A == '' :
                A = int( string_to_numstring( line[ 1 ] ) ) 
                Z = int( line[ 2 ] )

            else :
                A = int( A )
                Z = int( line[1] ) 

            N = A - Z

            try : 
                half_life = float( line[-1] )

            except:
                continue

            # notation for a stable nuclide 
            if( half_life == 0.0 ) :
                half_life = np.inf

            half_lives[ Z, N ] = half_life
            
            # # this is the files notation for saying that its stable
            # if half_life == 0.0 or half_life >= min_half_life : 
            #     half_life_bools[Z,N] = 1 
                
    return half_lives





def string_to_numstring( s ) :
     return ''.join( [ c for c in s if c.isdigit() ] )
                                
                     
                   
                   
                   
    
# the cyclotron frequency is qB/m
    
def mass_to_omega( mass, q ) :
    omega = q * cesium_133_omega * ( cesium_133_mass - electron_mass ) / mass 
    return omega
    

def omega_to_mass( omega, q ) :
    return q * cesium_133_omega * ( cesium_133_mass - electron_mass ) / omega 



def file_len( fname ):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1




def get_element_name( Z ) :

    try :
        return next( key for key, value in periodic_table_dict.items() if value == Z )

    except :
        print( 'ERROR: no element name for Z = %s' % str( Z ) )
        sys.exit( 0 )
    

        


class TimeEstimator( object ) :

    def __init__( self, num_iterations, num_updates ) :
        self.iteration = 0 
        self.counter = 1
        self.num_updates = num_updates 
        self.num_iterations = num_iterations
        self.start_time = time.time()

        
    def update( self ) :
        self.iteration += 1

        if( 1. * self.iteration / self.num_iterations 
            >= 1. * self.counter / self.num_updates ): 

            current_time = time.time()
            self.counter += 1
            print( "%d/%d complete, %f mins remaining" \
                   % ( self.counter, self.num_updates,
                       (current_time - self.start_time) / 60.0
                       * ( self.num_updates - self.counter )
                       / self.counter ) )

            
    def reset( self, num_updates = None ) :
        self.iteration = 0 
        self.counter = 1
        self.start_time = time.time()
        if num_updates is not None :
            self.num_updates = num_updates 
        

            



# class for reading, writing, creating, and resetting a db
# to store all the 

class molecule_db_manager( object ) :

    def __init__( self ) :

        self.conn = None

        os.makedirs( molecule_db_dir, exist_ok = 1 )

        self.db_path = molecule_db_dir + 'molecule_db.sql'

        if DEBUG_DB : 
            self.delete() # remove 

        self.exists = os.path.exists( self.db_path )
        
        self.connect()

        if not self.exists :
            print( 'INFO: molecule database not found, creating new one... ' )
            self.create()
            self.read_metadata() 
            
        else : 
            print( 'INFO: successfully found molecule database.' )
            self.read_metadata()

            print( '\tGenerated on: %s' % str( self.timestamp ) )

            if self.database_complete : 
                print( '\tDatabase was generated successfully' )
            else : 
                print( '\tWARNING: database was not completely generated. there may have been a keyboard interrupt during generation.' )  

            print( '\tTime taken to generate (mins) : %d ' % int( self.generation_time ) )
            print( '\tMin half life (s): %f s' % self.min_half_life )
            print( '\tMin Cf yield fraction (per 1 decay): %.2e' % self.min_cf_yield_fraction )
            print( '\tMax atoms per molecule: %d' % self.max_atoms_per_molecule ) 
            
        return 

    

    def connect( self )  :
        
        self.conn = sqlite3.connect( self.db_path )

        self.conn.isolation_level = None 

        # this is set to allow you to read into an sqlite3.Row,
        # which is a dict-like object. 
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor() 

        return 1 

    
    
    def disconnect( self ):

        if self.conn is None:
            return 0 
        
        self.conn.close()
        self.conn = None
        
        return 1



        
    def create( self ):

        if self.conn is None:
            print( 'ERROR in create(): db connection does not exist.' )
            return 0

        if self.exists :
            print( 'ERROR in create(): db already exists.' )
            return 0

        with open( molecule_db_schema_path, 'rt' ) as f:
            schema = f.read() 
            self.conn.executescript( schema )   

        self.start_time = datetime.datetime.now() # start time of this session 

        self.write_metadata()

        self.database_complete = 0
        self.generation_time = -1 

        return 1        

    

    # used primarily for debugging 
    def delete( self ) :

        if os.path.exists( self.db_path ) : 
            os.remove( self.db_path )

        return 1 


    
    def write_metadata( self ) :
        
        if self.conn is None:
            print( 'ERROR in write_metadata() : db connection not open' )
            return 0
        
        self.conn.cursor().execute( 'INSERT INTO metadata VALUES ( ?, ?, ?, ?, ?, ? ) ',
                                    ( min_cf_yield_fraction, min_half_life,
                                      max_atoms_per_molecule, 0,
                                      -1, str( self.start_time ) ) )

        self.conn.commit() 

        return 1
    

    def update_db_complete_metadata( self ) :

        stop_time = datetime.datetime.now()
        tmp = stop_time - self.start_time
        generation_time = tmp.days * 1440 + tmp.seconds / 60 # report in minutes

        print( generation_time )
        print( type( generation_time ) ) 
    
        query = 'UPDATE metadata SET generation_time=?, database_complete=1'

        self.conn.cursor().execute( query, ( generation_time, ) )
        self.conn.commit()
        
        return 1
        
        
    
    
    def read_metadata( self ) :

        cursor = self.conn.cursor()
        cursor.execute( 'SELECT * FROM metadata' )
        metadata  = dict( cursor.fetchone() )

        self.min_cf_yield_fraction = metadata[ 'min_cf_yield_fraction' ]
        self.min_half_life = metadata[ 'min_half_life' ]
        self.max_atoms_per_molecule = metadata[ 'max_atoms_per_molecule' ]
        self.database_complete = metadata[ 'database_complete' ]
        self.generation_time = metadata[ 'generation_time' ]
        self.timestamp = metadata[ 'timestamp' ]

        return 1



    # note: does not handle updating, only inserting the data once.
    
    def insert_molecule_data( self, A, mass, label ) :

        if self.conn is None:
            raise ValueError( 'Cannot insert data, sqlite3 connection is not open. Call db.connect().' )

        query = 'INSERT INTO molecule_masses VALUES ( ?, ?, ? )'
        
        self.cursor.execute( query, ( int(A), int(mass), pickle.dumps( label ) ) )
        # self.conn.commit() 
        
        return None


    # read all molecules from the DB that have total atomic number A 
    
    def read_isobar( self, A ) :

        if self.conn is None:
            raise ValueError( 'Cannot read db, sqlite3 connection is not open. Call db.connect().' )

        query = 'SELECT * FROM molecule_masses WHERE A=?'

        # cursor = self.conn.cursor()
        self.cursor.execute( query, (A,) )

        return self.cursor.fetchall()



    def search_mass( self, mass_low, mass_high ) :
        
        if self.conn is None:
            raise ValueError( 'Cannot read db, sqlite3 connection is not open. Call db.connect().' )

        query = 'SELECT * FROM molecule_masses WHERE mass>=? AND mass <=?'

        self.cursor.execute( query, ( mass_low, mass_high ) )

        return self.cursor.fetchall() 

                             
        
    

    def begin_transaction( self ) :

        self.cursor.execute( 'BEGIN' )

        
    def end_transaction( self ) :

        self.cursor.execute( 'COMMIT' ) 

        
  
main() 




# print(get_count(20))
# print( omega_to_mass( 616024, 1 ) ) 





# print( mass_to_omega( 121.916113434e6, 1 ) ) 
