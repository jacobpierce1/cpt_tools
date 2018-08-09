import os 

IS_WINDOWS = ( os.name == 'nt' ) 


USE_FAKE_DATA = 1

if not IS_WINDOWS :
    USE_FAKE_DATA = 1 


USE_GUI = 0 
