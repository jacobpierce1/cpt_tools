import os.path


calibrant_Z = 55
calibrant_A = 133 # atomic mass 
# calibrant_mass = 132905451.961
calibrant_omega =  675000.3
# calibrant_omega =  657844.45



# IS_WINDOWS = ( os.name == 'nt' )

code_path = os.path.abspath( os.path.dirname( __file__ ) ) + '/'

DEFAULT_STORAGE_DIRECTORY = code_path + '../debug/test_storage/'

# if not IS_WINDOWS : 
#     DEFAULT_STORAGE_DIRECTORY = ( os.path.expanduser('~')
#                                   + '/savard_group/cpt/cpt_tools/debug/test_storage/' )
# else :
#     DEFAULT_STORAGE_DIRECTORY = 

# default_storage_directory = '~/savard_group/cpt/data/'

