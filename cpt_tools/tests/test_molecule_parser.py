# from ... import moleculer_parser


import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

# print( sys.path ) 

import molecule_parser 



tests = [  'Ba(BrO3)2·2H2O', 'D3O2+', 'D3O 2+', 'Ba(BrO3)2·2H2O' ] 

for s in tests :

    print( '\nTesting %s...' %s ) 
    print( molecule_parser.atom_counter( s ) )
    # print( 'Should be Ba:1, Br:2, O:8, H:4' ) 
