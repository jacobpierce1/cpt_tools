import os 

IS_WINDOWS = ( os.name == 'nt' ) 

USE_TABOR = 1 
USE_FAKE_DATA = 1
BENCHMARK = 1
SAVEDIR = None

code_path = os.path.abspath( os.path.dirname( __file__ ) )

if not IS_WINDOWS :
    USE_TABOR = 0
    USE_FAKE_DATA = 1
    SAVEDIR = code_path + '../data/'
else : 
    print( 'INFO: windows detected' )
	
USE_GUI = 0 

