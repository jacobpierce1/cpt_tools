# this class connects to a tdc_daq_mgr and processes the data in real time 

import config 

import numpy as np
import sys
import time
from numba import jit, jitclass
import numba

# start = time.time() 



# spec = [ 
# ( 'first_pass', numba.int32 )
# ]
# @jitclass( spec ) 
