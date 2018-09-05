# functions for reading and writing cpt files, logs, etc

import os 
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
from datetime import datetime 

from cpt_tools import DEFAULT_STORAGE_DIRECTORY




def write_log( message, author = None ) :

    print( 'ABOUT TO WRITE LOG' ) 
    
    time_str = datetime.now().strftime( '%Y-%m-%d %H:%M' ) 

    if author is None or author == '' :
        author = 'Experimenter unknown' 
    
    log_message = '%s\n%s\n%s\n\n' % ( time_str, author, message ) 

    log_path = DEFAULT_STORAGE_DIRECTORY + 'log.txt'

    if os.path.exists( log_path ) :
        unlock_file( log_path )

    with open( log_path, 'a+' ) as f:
        f.write( log_message ) 
        
    lock_file( log_path )

    print( 'WROTE LOG' ) 



# lock a file as read only
def lock_file( file_path ) :
    os.chmod( file_path, S_IREAD | S_IRGRP | S_IROTH )



def unlock_file( file_path ) :
    os.chmod( file_path, S_IWUSR | S_IREAD )
