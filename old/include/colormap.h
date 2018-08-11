#ifndef COLORMAP_H
#define COLORMAP_H

#include <stdint.h>


class ColorMap
{
private :
    int size;
    double values[256][3] ;
//    void copy_values( double (*cmap_array)[3] );
    
public :
    ColorMap( const char *type );
    
    void apply_colormap( uint8_t buf[3], double v, double vmin, double vmax );
};


#endif
