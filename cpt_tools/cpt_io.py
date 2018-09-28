# functions for reading and writing cpt files, logs, etc

import os 
from stat import S_IREAD, S_IRGRP, S_IROTH, S_IWUSR
from datetime import datetime 
import numpy as np 

from cpt_tools import DEFAULT_STORAGE_DIRECTORY


cpt_header_key = np.array( [ 3, 16, 20 ], dtype = float )


def write_log( message, author = None ) :
    
    time_str = datetime.now().strftime( '%Y-%m-%d %H:%M' ) 

    if author is None or author == '' :
        author = 'Experimenter unknown' 
    
    log_message = '%s\n%s\n%s\n\n' % ( time_str, author, message ) 

    log_path = DEFAULT_STORAGE_DIRECTORY + 'user_log.txt'

    if os.path.exists( log_path ) :
        unlock_file( log_path )

    with open( log_path, 'a+' ) as f:
        f.write( log_message ) 
        
    lock_file( log_path )



# lock a file as read only
def lock_file( file_path ) :
    os.chmod( file_path, S_IREAD | S_IRGRP | S_IROTH )



def unlock_file( file_path ) :
    os.chmod( file_path, S_IWUSR | S_IREAD )
