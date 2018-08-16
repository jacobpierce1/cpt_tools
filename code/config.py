import os 

IS_WINDOWS = ( os.name == 'nt' ) 

USE_TABOR = 1 
USE_FAKE_DATA = 1
BENCHMARK = 1 

if not IS_WINDOWS :
    USE_TABOR = 0
    USE_FAKE_DATA = 1 
else : 
	print( 'INFO: windows detected' )
	
USE_GUI = 0 
