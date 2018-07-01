#include "colormap.h"
#include "colormap_arrays.h"

#include <cstdlib>
#include <cstdio>
#include <string>
#include <iostream>
#include <math.h>

using namespace std;


ColorMap::ColorMap( const char *type )
{
    if( strcmp( type, "fire" ) == 0 )
    {
	memcpy( values, fire_cmap, 3 * 256 * sizeof( double ) );
	this->size = 256;
    }
    else if( strcmp( type, "linear_bmw_5_95_c86" ) == 0 )
    {
	memcpy( values, linear_bmw_5_95_c86, 3 * 256 * sizeof( double ) );
	this->size = 256;
    }
    else
    {
	cout << "ERROR: unrecognized colormap name " << endl;
	exit(0);
// throw( this->CmapNotFoundError();
    }
}



void ColorMap::apply_colormap( uint8_t buf[3], double v, double vmin, double vmax )
{
    double dv;

    if( vmax == vmin )
    {
	buf[0] = 0;
	buf[1] = 0;
	buf[2] = 0;
	return;
    }

    // clip data 
   if (v < vmin)
      v = vmin;
   if (v > vmax)
      v = vmax;
   
   dv = vmax - vmin;

   int bin = (int) ( 255 * ( v - vmin ) / dv );

   
   
   
   // cout <<   this->size * ( v - vmin ) / dv  << endl;
	
   buf[0] =  255 * this->values[bin][0] ;
   buf[1] =  255 * this->values[bin][1] ;
   buf[2] = 255 * this->values[bin][2] ;

   // cout << v << " " << bin << " " << this->values[bin][0] << " " << (int) buf[0] << endl;
}



// void ColorMap::copy_values( double (*cmap_array)[3] )
// {
// }



// ColorMap::CmapNotFoundError()
// {

// }

