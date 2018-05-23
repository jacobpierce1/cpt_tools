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
wikipedia_molecule_data_path = './data/molecules/wikipedia_molecule_data.txt'
carbon_molecule_data_dir = './data/molecules/carbon_molecules/'
carbon_file_name = 'C'
wallet_card_path = './data/nuclear-wallet-cards.txt'
fission_yield_data_path = './data/fissionyields.txt' 
abundances_path = './data/abundances.txt'




# B is obtained using this calibration data

electron_mass = 548.579909
neutron_mass = 1.008665e6
proton_mass = 1.007276e6 

cesium_133_mass = 132905451.961
cesium_133_omega =  657844.45

line_break =  '--------------------------------------------' * 2 

max_Z = 119
max_N = 200
max_A = 500 

max_mass = 500

min_half_life = 0.05  # seconds. modifiable as command line arg 


# used for debug 
proton_mass = 1.007276e6 

# the maximum charge of an ion or molecule in the trap
# only used during the query 
max_charge = 2

# maximum number of atoms constituting a  molecule
# small_molecule_size = 7
small_molecule_size = 8

# large_molecule_min_abund = 0.02
large_molecule_max_uncommon = 3
large_molecule_common_abund = 0.1
large_molecule_common_half_life = 1.0
large_molecule_common_cf_yield_fraction = 1e-4


# probability of nuclide production for unstable nuclides must be at least this much
# to be considered in calculations 
min_cf_yield_fraction = 1e-8




# these are the min and max carbon numbers that we have a list of molecules for
min_carbon_number = 1 
max_carbon_number = 24





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

    if len( sys.argv ) < 4 :
        print( '\nERROR: less than 3 args supplied' )
        print_help_info() 
        return

    print( '\n' ) 
    
    # atomic number of singly ionized ions in the trap
    mode = int( sys.argv[1] )
    omega = float( sys.argv[2] )
    d_omega = float( sys.argv[3] )

    # specified in seconds
    if len( sys.argv ) > 4  :
        parse_extra_args( sys.argv[4:] ) 


    print( 'Using params for query: \n\tsmall_molecule_size = %d \n\tmin_half_life = %.1f s\n\tmin_cf_yield_fraction = %.1f \n\tmax_charge = %d \n'
               % ( small_molecule_size, min_half_life,
                   min_cf_yield_fraction, max_charge ) )


    atom_masses = get_atom_masses()
    
    filtered_atom_masses, filtered_atom_labels = get_filtered_atom_masses_and_labels( atom_masses )
    
    if mode == 0 :

        print( line_break ) 
        check_ions( atom_masses, omega, d_omega,
                    half_lives, cf_yields, abundances )
        
        print( line_break ) 

    elif mode == 1 :
        
        molecule_db = get_molecule_db( filtered_atom_masses, filtered_atom_labels )
        print( '' ) 

        print( line_break ) 

        check_ions( atom_masses, omega, d_omega,
                    half_lives, cf_yields, abundances )

        print( line_break )
        print( '\n' * 4 )
        print( line_break ) 

        check_molecule_combinations( molecule_db,  omega, d_omega,
                                     half_lives, cf_yields, abundances ) 

        print( line_break ) 
        
    # elif mode == 2 :

    #     print( line_break ) 
    #     check_all_ion_combinations( atom_masses, atom_labels ) 
    #     print( line_break ) 
        
    else :
        print( 'ERROR: mode not implemented\n' )
        return -1

    return 0



def parse_extra_args( a ) :

    global small_molecule_size
    global min_half_life
    global min_cf_yield_fraction
    global max_charge 
    
    for i in range( 0, len( a ), 2 ) :

        mode = a[ i ]
       
        if mode == 'min_half_life' :
            min_half_life = float( a[ i + 1 ] )
        
        elif mode == 'min_cf_yield' :
            min_cf_yield_fraction = float( a[ i + 1 ] )

        elif mode == 'small_molecule_size' :
            small_molecule_size = int( a[ i+1 ] )

        elif mode == 'max_charge' :
            max_charge = int( a[ i+1 ] )

        else :
            print( '\nERROR: argument %s not recognized' % mode )
            print_help_info()
    


def print_help_info() :

    print( ( '\n\nsyntax: ipython mass_identifier.py  mode  omega  d_omega  [optional query args] \n'
             + '\n\tmode: \t0 for all ions \n\t\t1 for all ions and known molecules'
             + '\n\n'
             + '\toptional query args: \n\t\tmin_half_life FLOAT \n\t\tmin_cf_yield FLOAT '
             + '\n\t\tsmall_molecule_size INT \n\t\tmax_charge INT'
             + '\n\n'
             + '\texample: to check all molecules in DB with max charge of 1 and defaults for other params: \n\t\tipython mass_identifier.py 1 616024 0.5 max_charge 1  '
             # + '<--- check all molecules in database with max charge of 1, defaults for rest of params'
             + '\n\n'
    ) )

    sys.exit(0)
    
    return 




def check_ions( atom_masses, omega, d_omega,
                half_lives, cf_yields, abundances ) :

    print( 'ION MATCHES' )
    print( 'OMEGA\t NAME\t q\t A\t Z\t N\t T_1/2\t CF_YIELD \tNATURAL_ABUND\n' )

    none_found_flag = 1 
    
    for q in range( 1, max_charge + 1 ) :
        
        # total_A = q * A1
        
        # print( '\n\nINFO: Checking q = %d,  A = %d' % ( q, total_A)  )

        
        for Z in range( 1, max_Z ) :
            for N in range( 0, max_N ) : 

                # we have a candidate, add mass and all labels
                mass = atom_masses[Z][N]

                # default value: mass was not found in ame16
                if mass == -1 :
                    continue

                mass -= q * electron_mass 
                current_omega = mass_to_omega( mass, q )


                if np.abs( current_omega - omega ) <= d_omega : 

                    half_life = half_lives[ Z, N ]

                    element_name = get_element_name( Z ).title()

                    print( '%.1f\t%s \t%d\t%d\t%d\t%d\t%.2f\t%.2f\t%.2f'
                           % ( current_omega, element_name, q, Z+N, Z, N,
                               half_life, cf_yields[Z,N],
                               abundances[Z,N] ) )

                    none_found_flag = 0

    if none_found_flag :

        print( 'NONE FOUND' ) 
                    
            
    







# # check every possible combination of ions, regardless of
# # whethere it is a molecule in the wikipedia page

# def check_all_ion_combinations( masses, labels ) :
    
#     candidate_masses = []
#     candidate_indices = [] 
#     candidate_labels = []

#     # time_estimator = TimeEstimator(  

#     for q in range( 1, max_charge + 1 ) :

#         print( 'checking q=%d...' % q  )

#         # the A of each constituent needs to sum to this
#         total_A = q * A1


#         # print( possible_A_values ) 
            
#         # loop through lists of A values that add to total_A 
#         A_indices = get_partitions( total_A, total_A, max_molecule_size ) 

#         # total_A, max_len = max_molecule_size ) 

#         # print( list( A_indices ) ) 
        
#         print( 'Found %d isobar candidates...' % len( list( A_indices ) ) ) 

#         time_estimator = TimeEstimator( len( A_indices ), 20 )

#         for A_index in A_indices : 


#             # print( 'A_list: ' + str( A_list ) )
#             # print( masses[ A_list[0] ] )
#             # print( [ len( masses[ A_list[x] ] ) for x in range( len( A_list) ) ] )
            
#             num_indices = len( A_index )
            
#             nuclide_indices = itertools.product( * [ range( len( masses[ A_index[x] ] ) )
#                                                for x in range( num_indices ) ]  ) 


#             for nuclide_index in nuclide_indices :

#                 # print( A_indices ) 
#                 # print( nuclide_index ) 
#                 mass = np.sum( [ masses[ A_index[ x ] ][ nuclide_index[ x ] ]
#                                  for x in range( num_indices ) ] )

#                 mass -= q * electron_mass 

#                 # print( mass ) 
#                 # print( mass / proton_mass ) 

#                 # we have a candidate, add mass and all labels 
#                 if np.abs( mass_to_omega( mass, q ) - omega ) <= d_omega : 

#                     candidate_masses.append( mass )
#                     candidate_indices.append( [ A_index, nuclide_index ] )
                    
#                     nuclide_labels = [ labels[ A_index[ x ] ][ nuclide_index[ x ] ]
#                                               for x in range( num_indices ) ]

#                     print( nuclide_labels ) 

                    
#                     candidate_labels.append( [ nuclide_labels ] )

                    
                    
        
            
    
         



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





def check_molecule_combinations( molecule_db, omega, d_omega,
                                 half_lives, cf_yields, abundances ) :

    candidate_masses = []
    candidate_indices = [] 
    candidate_labels = []

    none_found_flag = 1 
    
    print( 'MOLECULE MATCHES' )
    print( 'KEY:' )
    print( 'MOLECULE NAME' )
    print( '\tQ' )
    print( '\tA' ) 
    print( '\tOMEGA  (Hz)' ) 
    print( '\tZ' )
    print( '\tN' )
    print( '\tHalf lives (inf = stable)  (seconds)' )
    print( '\tCf yield' )
    print( '\tRelative natural Abundance' )
    print( '' ) 

    
    for q in range( 1, max_charge + 1 ) :

        print( '\n\nINFO: checking q = %d' % q ) # , expected A = %d' % ( q, total_A)  )

        mass_low = omega_to_mass( omega + d_omega, q ) + q * electron_mass 
        mass_high = omega_to_mass( omega - d_omega, q ) + q * electron_mass

        # print( [ mass_low, mass_high ] ) 

        isobar_molecules = molecule_db.search_mass( mass_low, mass_high )

        if len( isobar_molecules ) > 0 : 

            print( 'INFO: Found %d candidates:\n' % len( isobar_molecules ) )

            for data in isobar_molecules : 

                mass = data[ 'mass' ] 

                mass -= q * electron_mass

                current_omega = mass_to_omega( mass, q )

                # A = data['A'] 
                Z = pickle.loads( data[ 'Z' ] ) 
                N = pickle.loads( data[ 'N' ] )
                isomer_labels = pickle.loads( data[ 'isomer_labels' ] )
                molecule_name = data[ 'molecule_name' ]

                A = np.sum( Z ) + np.sum( N ) 
                
                # molecule_name, Z, N = pickle.loads( data[ 'label' ] )

                half_life = []
                for i in range( len( Z ) ) :
                    tmp = half_lives[ Z[i], N[i] ]

                    half_life.append( tmp  )

                if np.any( ( np.array( half_life ) < min_half_life ) ) :
                    continue

                # store cf yield if unstable or relative natural abundance if stable 
                cf_yields_arr = []
                for i in range( len( Z ) ) :

                    cf_yields_arr.append( cf_yields[ Z[i], N[i] ] )

                abunds_arr = [ abundances[ Z[i], N[i] ]
                               for i in range( len( Z ) ) ]

                half_life_str = [ '%.2e' % x for x in half_life ] 
                cf_yields_str = [ '%.2e' % x for x in cf_yields_arr ]
                abunds_str = [ '%.2e' % x for x in abunds_arr ]

                print( '%s' % molecule_name )
                print( '\t%d' % q ) 
                print( '\t%d' % A ) 
                print( '\t%.1f' % current_omega ) 
                print( '\t%s' % str( Z ) )
                print( '\t%s' % str( N ) )
                print( '\t%s' % str( half_life_str ) )
                print( '\t%s' % str( cf_yields_str ) )
                print( '\t%s' % str( abunds_str ) ) 
                print( '\n' )


                # candidate_labels.append( [ nuclide_labels ] )

        else : 
            print( 'NONE FOUND' ) 

                    
    

    



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







def get_filtered_atom_masses_and_labels( atom_masses ) :

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
                
                filtered_atom_labels[Z].append( N )  

    return filtered_atom_masses, filtered_atom_labels 
    





def get_molecule_db( atom_masses, atom_labels ) :

    transaction_block_size = 10000
    
    molecule_db = molecule_db_manager()

    if molecule_db.exists :
        return molecule_db        
    
    iteration = 0

    molecule_db.begin_transaction()

    molecule_files = [ wikipedia_molecule_data_path ]

    for i in range( min_carbon_number, max_carbon_number ) :
        molecule_files.append( carbon_molecule_data_dir + carbon_file_name + str(i) )
    
    num_lines = np.sum( [ file_len( molecule_files[i] )
                                    for i in range( len( molecule_files) ) ] ) 

    time_estimator = TimeEstimator( num_lines, 100 ) 


    for molecule_file in molecule_files : 
    
        with open( molecule_file ) as f :

            for line in f.readlines() :

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

                Z_list_unique = [ periodic_table_dict.get( x.lower() )
                                  for x in molecule_counts.keys() ]

                # make sure it's a valid molecule
                if None in Z_list_unique :
                    continue

                Z_num_occurrences = list( molecule_counts.values() )  

                Z_list_repeats = [ Z_list_unique[i]  for i in range( len( Z_list_unique ) )
                                   for j in range( Z_num_occurrences[i] ) ]
                
                # now we have a list with (repeated) values of Z. if
                # molecule is small: find all unique permutations of the
                # corresponding neutron number for nuclies which are
                # produced in the Cf fission above our probability
                # threshold and have a half life above the threshold (
                # these filteres were already applied in generation of the
                # atomic mass table array )

                if len( Z_list_repeats ) <= small_molecule_size : 

                    tmp = [ itertools.combinations_with_replacement(
                        range( len( atom_masses[ Z_list_unique[i] ] ) ),
                        Z_num_occurrences[i] )
                            for i in range( len( Z_list_unique ) ) ]

                    N_indices_gen = itertools.product( * tmp )


                # if molecule is large, check a reduced set of combinations.
                # most of the combinations are extremely unlikely and there are
                # too many to add to the DB.

                else :
                    # continue
                    N_indices_gen = get_large_molecule_N_indices(
                        atom_labels, Z_list_unique, Z_num_occurrences ) 

                    
                for N_indices in N_indices_gen :

                    # print( N_indices ) 

                    mass = 0
                    N = [] 
                    
                    for i in range( len( Z_list_unique ) ) :

                        tmp = atom_labels[ Z_list_unique[i] ]

                        for j in range( Z_num_occurrences[i] ) :
                            mass += atom_masses[ Z_list_unique[i] ][ N_indices[i][j] ]
                            N.append( tmp[ N_indices[i][j] ] )

                    if mass > max_mass :
                        continue

                    if iteration % transaction_block_size == 0 :
                        molecule_db.end_transaction() 
                        molecule_db.begin_transaction()

                        
                    molecule_db.insert_molecule_data( mass, Z_list_repeats, N,
                                                      None, molecule_string )

                    iteration += 1 

    molecule_db.end_transaction()
    molecule_db.update_db_complete_metadata()

    return molecule_db 








# modifiable function to return the allowed N index combinations for a
# large molecule. mass = scalar, Z = Z repeats, N = 

# large_molecule_max_unstable = 3
# large_molecule_common_abund = 0.1
# large_molecule_common_half_life = 1.0
# large_molecule_common_cf_yield_fraction = 1e-4


def get_large_molecule_N_indices( atom_labels, Z_list_unique, Z_num_occurrences ) :
    
    # partition the indices into two categories: common and uncommon.
    # all common combinations will be checked, and only at most
    # large_molecule_max_uncommon uncommon atoms will occur

    # print( half_lives[1] )
    # print( half_lives[2] )

    all_combinations = [] 

    Z_num_occurrences = np.asarray( Z_num_occurrences ) 

    common_indices = []
    uncommon_indices = []

    num_unique_atoms = len( Z_list_unique )
    
    for i in range( num_unique_atoms ) :

        common_indices.append( [] )
        uncommon_indices.append( [] )

        N = atom_labels[ Z_list_unique[i] ]

        # print( '\nZ: ' + str( Z_list_unique[i] ) ) 
        # print( 'N: ' + str( N ) )
        # print( 'half_lives: ' + str( half_lives[ Z_list_unique[i] ][ N ] ) )
        # print( 'abundances: ' + str( abundances[ Z_list_unique[i] ][ N ] ) )
        # print( 'cf_yields: ' + str( cf_yields[ Z_list_unique[i] ][ N ] )  )
        
        for j in range( len( N ) ) :

            if ( ( ( half_lives[ Z_list_unique[i] ][ N[j] ] == np.inf )
                   and ( abundances[ Z_list_unique[i] ][ N[j] ] >
                         large_molecule_common_abund ) )
                 or ( ( cf_yields[ Z_list_unique[i] ][ N[j] ] >
                        large_molecule_common_cf_yield_fraction )
                      and ( half_lives[ Z_list_unique[i] ][ N[j] ] >
                            large_molecule_common_half_life ) ) ) : 
                
                common_indices[i].append( j )

            else : 
                uncommon_indices[i].append( j )

    # print( 'Z ', Z_list_unique )
    # print( 'Z_num_occurrences ', Z_num_occurrences ) 
    # print( 'common indices ', common_indices )
    # print( 'uncommon indices ', uncommon_indices )

    num_uncommon_nuclides_per_atom = np.array( [ len( uncommon_indices[i] )
                                                 for i in range( num_unique_atoms ) ] )

    # print( num_uncommon_nuclides_per_atom ) 
    
    # combinations = []

    # for unstable_atom_indices in itertools.combinations_with_replacement( range( num_unique_atoms ),
    #                                                                      large_molecule_max_unstable ) :

    for i in range( 0, large_molecule_max_uncommon + 1 ) :

        partitions = get_partitions( i, i, num_unique_atoms )

        for partition in partitions :

            while len( partition ) < num_unique_atoms :
                partition.append( 0 )
                
            permutations = perm_unique( partition )

            # print( partition ) 
            # print( list( permutations ) )

            # print( len( list( permutations ) ) )

            # x = list( permutations ) 
            # print( x  ) 

            for p in permutations :

                # print( p ) 

                # print( 'reached' ) 

                # check p
                # print(  'test', np.array( p ) <= Z_num_occurrences) 
                if not np.all( np.array( p ) <= Z_num_occurrences ) : 
                    continue 
                    
                # common_combinations = []
                # uncommon_combinations = []

                final_combinations_per_atom = []
                
                for j in range( num_unique_atoms ) :
                    
                    common_combinations = list( itertools.combinations_with_replacement(
                        common_indices[j], Z_num_occurrences[j] - p[j] ) )

                    # tmp_common = list( common_combinations )
                    # print( j, 'tmp_common ', tmp_common )
                    # print( len( tmp_common ) ) 
                    
                    uncommon_combinations = list( itertools.combinations_with_replacement(
                        uncommon_indices[j], p[j] ) ) 

                    # prod = itertools.product( common_combinations, uncommon_combinations )

                    # print( list( common_combinations ) ) 
                    # print( [ (*x) for x in common_combinations ] )

                    
                    # prod = [ ( *x, *y) for x in common_combinations
                    #          for y in uncommon_combinations ]

                    prod = []

                    # print( 'common ', common_combinations )
                    # print( 'uncommon ' , uncommon_combinations ) 

                    if p[j] == 0 :
                        prod.extend( common_combinations )

                    elif p[j] == Z_num_occurrences[j] :
                        prod.extend( uncommon_combinations )

                    
                    
                    # if ( not common_combinations ) or ( not common_combinations[0] ) : 
                    #     prod.append( uncommon_combinations )

                    # elif ( not uncommon_combinations ) or ( not uncommon_combinations[0] ) :
                    #     prod.append( common_combinations )

                    else :                         
                        for x in common_combinations :
                            for y in uncommon_combinations :
                                # print( 'x ', x )
                                # print( 'y ', y ) 
                                prod.append( ( *x, *y ) )

                    # print( j, 'prod ', prod )
                    
                    final_combinations_per_atom.append( prod ) 

                tmp = itertools.product( * final_combinations_per_atom )
                    
                all_combinations.append( tmp ) 

                
    # for num_unstable_per_element in get_partitions( num_unique_atoms, num_unique_atoms, num_unique_atoms )
    ret = itertools.chain.from_iterable( all_combinations )

    # for x in ret :
    #     print( x )

    # sys.exit( 0 ) 
    return ret 



    
# https://stackoverflow.com/questions/6284396/permutations-with-unique-values

class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences

def perm_unique(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    u=len(elements)
    return perm_unique_helper(listunique,[0]*u,u-1)

def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in  perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1









def get_abundances_data() :

    abundances = np.zeros( ( 126, 250 ) )

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



def str_is_int( s ) :
    try: 
        int(s)
        return True
    except ValueError:
        return False


    

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
            N = A - Z 
                        
            fission_yield = float( line[-2] ) / 200
            cf_yields[ Z, N ] = fission_yield
            
    return cf_yields 








def get_half_life_data() :

    half_lives = np.zeros( ( 126, 200 ) )

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





def string_to_numstring( s ) :
     return ''.join( [ c for c in s if c.isdigit() ] )

 
def has_digit( s ) :
    for c in s :
        if c.isdigit() :
            return 1
    return 0 
                   
                   
                   
    
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

            print( '\tTime taken to generate (mins) : %.1f ' % self.generation_time )
            print( '\tmin_half_life = %.2f s' % self.min_half_life )
            print( '\tmin_cf_yield_fractionfraction (per 1 decay): %.1e' % self.min_cf_yield_fraction )
            print( '\tsmall_molecule_size = %d' % self.small_molecule_size ) 
            
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
                                      small_molecule_size, 0,
                                      -1, str( self.start_time ) ) )

        self.conn.commit() 

        return 1
    

    def update_db_complete_metadata( self ) :

        stop_time = datetime.datetime.now()
        tmp = stop_time - self.start_time
        generation_time = tmp.days * 1440 + tmp.seconds / 60 # report in minutes

        # print( generation_time )
        # print( type( generation_time ) ) 
    
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
        self.small_molecule_size = metadata[ 'small_molecule_size' ]
        self.database_complete = metadata[ 'database_complete' ]
        self.generation_time = metadata[ 'generation_time' ]
        self.timestamp = metadata[ 'timestamp' ]

        return 1



    # note: does not handle updating, only inserting the data once.
    
    def insert_molecule_data( self, mass, Z, N, isomer_labels, molecule_name ) :

        if self.conn is None:
            raise ValueError( 'Cannot insert data, sqlite3 connection is not open. Call db.connect().' )

        query = 'INSERT INTO molecule_masses VALUES ( ?, ?, ?, ?, ? )'
        
        self.cursor.execute( query, ( mass, pickle.dumps( Z ), pickle.dumps( N ),
                                      pickle.dumps( isomer_labels), molecule_name ) )
        # self.conn.commit() 
        
        return None


    # # read all molecules from the DB that have total atomic number A 
    
    # def read_isobar( self, A ) :

    #     if self.conn is None:
    #         raise ValueError( 'Cannot read db, sqlite3 connection is not open. Call db.connect().' )

    #     query = 'SELECT * FROM molecule_masses WHERE A=?'

    #     # cursor = self.conn.cursor()
    #     self.cursor.execute( query, (A,) )

    #     return self.cursor.fetchall()



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
        


half_lives = get_half_life_data() 
cf_yields = get_cf_yield_data()
abundances = get_abundances_data() 
        
  
main() 



