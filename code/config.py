import os 

IS_WINDOWS = ( os.name == 'nt' ) 

USE_TABOR = 1 
USE_FAKE_DATA = 0
BENCHMARK = 0
SAVEDIR = None
PRINT_TDC_DATA = 0

code_path = os.path.abspath( os.path.dirname( __file__ ) )

if not IS_WINDOWS :
    print( 'INFO: non-windows detected')
    USE_TABOR = 0
    USE_FAKE_DATA = 1
    SAVEDIR = code_path + '../data/'
else : 
    print( 'INFO: windows detected' )
	
USE_GUI = 0 

