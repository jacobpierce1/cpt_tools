import numpy as np 


def get_rollover_boundaries( rollovers ) :
    
    tmp = np.roll( rollovers, 1 )
    tmp[0] = rollovers[0]
    
    # print( rollovers ) 
    # print( tmp ) 
    # print( rollovers - tmp ) 
    
    start = np.where( rollovers < tmp )[0]
    end = np.where( rollovers > tmp )[0]

    if not rollovers[0] :
        start = np.insert( start, 0, 0 ) 
    
    if not rollovers[-1] :
        end = np.append( end, len( rollovers ) ) 
        
    # end = np.append( np.where( rollovers > tmp )[0], len( rollovers ) )
    
    # print( 'start: ', start )
    # print( 'end: ', end ) 
    
    return start, end


# x = np.array( [0,0,0,1,1,1,0,0,0,1,1,1] )
# expected = ( (0,6,), (3,9,) )
# print( get_rollover_boundaries( x ) )
# print( expected ) 


# x = np.array( [1,1,1,0,0,0,1,1,1,0,0,0,1,1,1] )
# expected = ( (3,9,), (6,12,) )
# print( get_rollover_boundaries( x ) )
# print( expected ) 



# x = np.array( [1,1,1,0,0,0,1,1,1,0,0,0] )
# expected = ( (3,9,), (6,12,) )
# print( get_rollover_boundaries( x ) )
# print( expected ) 


# x = np.array( [1] )
# expected = ( ( (), ()) )
# print( get_rollover_boundaries( x ) )
# print( expected ) 


# x = np.array( [0] )
# expected = ( ( (0), (1)) )
# print( get_rollover_boundaries( x ) )
# print( expected ) 


# x = np.array( [0,1,0,1,0,1] )
# expected = ( ( (0,2,4), (1,3,5)) )
# print( get_rollover_boundaries( x ) )
# print( expected ) 



# x = np.array( [1,1,1,1,1] )
# expected = ( ( (), ()) )
# print( get_rollover_boundaries( x ) )
# print( expected ) 



x = np.array( [0,0,0,0] )
expected = ( ( (0), (4)) )
print( get_rollover_boundaries( x ) )
print( expected ) 
