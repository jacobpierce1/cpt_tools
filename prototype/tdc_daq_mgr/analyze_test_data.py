import numpy as np

data = np.load( 'test_data_tabor_on.npy' )

print( data ) 

falling_transition_mask = 2**31 
rising_transition_mask = 2**31 + 2**30 
rollover_mask = 2**28
channel_mask = np.sum( 2 ** np.arange( 24, 30, dtype = 'int' ) )
time_mask = np.sum( 2 ** np.arange( 0, 24, dtype = 'int' ) )

def print_bin( x ) :
    print( format( x, '#034b' ) )

def get_channel( x  ) :
    return ( x & channel_mask ) >> 24

def get_time( x ) :
    return x & time_mask

# print_bin( rising_transition_mask ) 
# print_bin( falling_transition_mask )
# print_bin( channel_mask )
# print_bin( time_mask ) 

for i in range( 10000 ) :
    # print( bin( data[i] ) )
    # print( format( data[i], '#034b' ) )

    if ( data[i] & rising_transition_mask ) == rising_transition_mask :
        continue
        print( 'rising' )
        print( get_channel( data[i] ) ) 
        
    elif ( data[i] & falling_transition_mask ) == falling_transition_mask :
        # print( 'falling' )
        channel =  get_channel( data[i] )
        if channel == 7 or channel == 6 :
            print()
            
        print( channel, end = ' ' )
        

    elif ( data[i] & rollover_mask ) == rollover_mask :
        continue
        print( 'rollover' ) 
    
    # print() 
