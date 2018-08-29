import re
import collections



def parse(s):
#     atomCount = collections.defaultdict(lambda: 0)
    atomCount = collections.Counter()

    tmp = re.findall("(?:([A-Z][a-z]?)(\d+)?|\(([^\)]*)\)(\d+))", s )

    # print( tmp ) 

    for m in tmp : 
        if m[0]:
            atomCount[m[0]] += int(m[1] or 1)
        else:
            for atom, count in parse(m[2]).items():
                atomCount[atom] += count*int(m[3])
    return atomCount




def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])




# return a tuple containing 2 lists: one with the groups, and the other containing
# the number of copies of that group 

def get_groups( s ) :

    groupnum = 0

    groups = [ '' ]
    counts = [ ]
    
    i = 0
    while i < len( s ) :

        # handle all non-parenthases text

        # if s[i] == '·' :
        #     if groups[ groupnum ] : 
        #         groupnum += 1
        #         groups.append( '' )
        #         counts.append( 1 )

            
        if s[i] != '(' :

            groups[ groupnum ] += s[i]
            i += 1

            # # there is probably a more efficient way to do this but whatever.
            # if len( groups ) > len( counts ) :
            # counts.append( 0 )
            
        # handle all text in parenth
        else :

            # check for empty list 
            if groups[ groupnum ] : 
                groupnum += 1
                groups.append( '' )
                counts.append( 1 ) 

            parenth_count = 1

            # this makes the parenth not be appended to the list 
            i += 1 
            
            while i < len( s ) :

                # check for a starting parenth
                if s[i] == '(' :
                    parenth_count += 1
                    groups[ groupnum ] += s[i]

                elif s[i] == ')' :
                    parenth_count -= 1

                    # check if we are done: find the number and add to counts, break and increment
                    if parenth_count == 0 : 
                        i += 1
                        groupnum += 1

                        group_count = re.match( '\d+', s[ i: ] )
                        if group_count :
                            group_count = group_count.group()
                            i += len( group_count )
                            group_count = int( group_count ) 

                        else :
                            group_count = 1 
                            
                        # print( 'group_count: ' + str( group_count ))
                        counts.append( group_count )

                        if i != len( s ) :
                            groups.append( '' )

                        break

                    else :
                        groups[ groupnum ] += s[i]
                    
                else :
                    groups[ groupnum ] += s[i]    
                        
                i += 1

            else :
                print( 'ERROR: invalid formula, there was no closing ) or ].' )
                return None

    # in this case we ended with a non-parenth group following a parenth-group
    if len( groups ) > len( counts ) :
        counts.append( 1 ) 

    return ( groups, counts ) 






def atom_counter( s, debug = 0 ) :        

    counter = collections.Counter()

    if '·' in s :
        return None 
    
    s = s.replace( '[', '(' ).replace( ']', ')' )

    if s[-1] in '-+' :
        j = len(s) - 2
        while j > 0  :
            # print( s[j] ) 
            if s[j].isdigit() :
                j -= 1
            else :
                if s[j].isspace() :
                    break
                else :
                    print( 'ERROR: ion state of $s is ambiguous. + or - at end'
                           + 'of string must be preceded by a space' )
                    return None 
            
    if debug :
        print( s ) 
    
    # print( s )

    if s.count( '(' ) < 2 :
        return parse( s )

    else :
        groups, counts = get_groups( s )

        if( debug ) :
            print( (groups, counts ) )
        
        # print( ( groups, counts ) )
        
        for i in range( len( groups ) ) :

            # recursively process each group until we get something with less than 1 pair of parenth
            # then it will return a collections.Counter

            sub_counter = atom_counter( groups[i] )
            
            for key, val in sub_counter.items() :

                counter[ key ] += val * counts[i]

    # only return if we are done or if we reached a group with 1 set of parenths
    return counter










# # print( parse( 'PbCl(NH3(H2O)4)2' ) ) 
# # print( parse( 'PbCl(NH3)2(COOH)2' )  )
# # print( parse2( 'PbCl(NH3)2[COOH]2' )  )
# #print( parse2(  'PbCl(NH3)2(COOH)2' )  )


# # s = 'NaClBrI'
# # print( s )
# # print( parse( s )  )


# s =  '(CH4)(NH4)2[Pt(SCN)6]2'
# s2 = '(CH4)2CN2'

# print( atom_count( s ) ) 
# # print( parse( s2 ) )



# print( atom_counter( '[Cu(H2O)4]SO4', 1 ) )
