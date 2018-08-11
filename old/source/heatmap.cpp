#include "heatmap.h"
#include <iostream>
#include <wx/dcbuffer.h>



using namespace std;

typedef wxAlphaPixelData PixelData;


    

// Heatmap::Heatmap(wxWindow* parent, wxString file, wxBitmapType format) :
//     wxPanel( parent, wxID_ANY, wxPoint( 0, 0 ), wxSize( 500, 320 ) )
// {
//     // load the file... ideally add a check to see if loading was successful
//     //this->image; // = new wxImage();
//     this->bmp.LoadFile(file, format);
// }



Heatmap::Heatmap( wxWindow *parent, double (* data)[2], int dimx, int dimy,
			    int dimx_scale, int dimy_scale, int bounds[2][2],
			    const char *cmap_name ) :
    wxPanel( parent, wxID_ANY, wxPoint( 0, 0 ), wxSize( 500, 320 ) )
    // cmap( cmap_name )
{
    // user-added data
    this->data = data;
    this->dimx = dimx;
    this->dimy = dimy;
    this->dimx_scale = dimx_scale;
    this->dimy_scale = dimy_scale;
    memcpy( this->histo_bounds, bounds, 4 * sizeof( int ) );
    this->cmap = new ColorMap( cmap_name );
    
    // always the same
    // memset( &(this->histo), 0, dimx * dimy * sizeof( int ) );
    this->histo_dims[0] = dimx;
    this->histo_dims[1] = dimy;
    this->num_data_in_histo = 0;
    this->current_max = 0;
    this->current_min = 0;
    this->current_min_bins[0] = 0;
    this->current_min_bins[1] = 0;

    
    for( int i=0; i<NUM_TICKS; i++ )
    {
	int xcoord = dimx * dimx_scale + COLORBAR_OFFSET + COLORBAR_WIDTH + TICKS_OFFSET;
	int ycoord = dimy * dimy_scale - i * ( dimx * dimx_scale ) / ( NUM_TICKS - 1 );
	
	this->colorbar_ticks[i] = new wxStaticText( parent, wxID_ANY, "", wxPoint( xcoord, ycoord ) );
    }

    histo.resize( dimx, vector<int>( dimy, 0 ) );
}


Heatmap::~Heatmap()
{
    delete this->cmap;
    
}



// Heatmap::Heatmap(wxWindow* parent )  :
//     wxPanel( parent, wxID_ANY, wxPoint( 100, 100 ), wxSize( 320, 320 ) )
// {
//     this->bmp = wxBitmap(); // 320, 320 );
//     this->Update();
//     // this->fetch_new_data( 5 );
    
//     // load the file... ideally add a check to see if loading was successful
//     //this->image; // = new wxImage();
//     //this->bmp.LoadFile(file, format);
// }


// Heatmap::Heatmap( void )
// {
// //    image = new wxImage();
// }

// Heatmap::Heatmap(wxFrame* parent, uint8_t *data, int width, int height ) :
// wxPanel(parent)
// {
//     // load the file... ideally add a check to see if loading was successful
//     wxImage tmp_image( width, height, 3 ) ;
    
//     image = wxBitmap( data );
// }
 
/*
 * Called by the system of by wxWidgets when the panel needs
 * to be redrawn. You can also trigger this call by
 * calling Refresh()/Update().
 */


void Heatmap::refresh( wxSizeEvent & evt )
{
    this->Refresh();
    this->Update();
    evt.Skip();
}


void Heatmap::paintEvent(wxPaintEvent & evt)
{
    // depending on your system you may need to look at double-buffered dcs
    wxBufferedPaintDC dc( this );
    render(dc);
}
 
/*
 * Alternatively, you can use a clientDC to paint on the panel
 * at any time. Using this generally does not free you from
 * catching paint events, since it is possible that e.g. the window
 * manager throws away your drawing when the window comes to the
 * background, and expects you will redraw it when the window comes
 * back (by sending a paint event).
 */
void Heatmap::paintNow()
{
    // depending on your system you may need to look at double-buffered dcs
    wxClientDC dc( this );
    render(dc);
}
 
/*
 * Here we do the actual rendering. I put it in a separate
 * method so that it can work no matter what type of DC
 * (e.g. wxPaintDC or wxClientDC) is used.
 */
void Heatmap::render( wxDC&  dc)
{
    dc.DrawBitmap( this->bmp, 0, 0, false );

    int colorbar_x = COLORBAR_OFFSET + this->dimx_scale * this->dimx;
    dc.DrawBitmap( this->colorbar_bmp, colorbar_x, 0, false );
}



// reconstruct the tmp image from this->data
void Heatmap::update_bmp( )
{           
    uint8_t buffer[ dimx * dimx_scale ][ dimy * dimy_scale ][3];
    
    memset( &buffer, 0, dimx * dimx_scale * dimy * dimy_scale * 3 );


    // update the histogram portion 
    uint8_t tmp_data[3];
    
    for( int x = 0; x < dimx; ++x)
    {
	for( int y = 0; y < dimy; ++y)
	{
	    this->cmap->apply_colormap( tmp_data, this->histo[x][y],
				       this->current_min, this->current_max );

	    for( int i=0; i < dimx_scale; ++i )
	    {
		for( int j=0; j < dimx_scale; ++j )
		{
		    int tmpx = x * dimx_scale + i;
		    int tmpy = y * dimy_scale + j;
		    memcpy( buffer[ tmpy ][ tmpx ], tmp_data, 3 );
		}
	    }
	}
    }

    wxImage tmp_image( dimx * dimx_scale, dimy * dimy_scale, &buffer[0][0][0], 1 );  
    this->bmp = wxBitmap( tmp_image, 3 );
}




// reconstruct the tmp image from this->data
void Heatmap::make_colorbar( )
{
    uint8_t buffer[ dimy * dimy_scale ][ COLORBAR_WIDTH ][3];

    uint8_t tmp_data[3] = {255,255,255};

    int max_y = dimy * dimy_scale;

    for( int y = 0; y < max_y; y++ )
    {
	// val goes through linspace( min, max, resolution ) 
	// double val = this->current_min 
	//     + (double) y * ( this->current_max - this->current_min ) / ( dimy * dimy_scale) ;

	double val = y * 1.0 / ( dimy * dimy_scale );
	
	// apply_colormap( tmp_data, val,
	// 		this->current_min, this->current_max );
	this->cmap->apply_colormap( tmp_data, val, 0, 1 );
	
	for( int x = 0; x < COLORBAR_WIDTH; ++x)
	{
	    memcpy( &( buffer[ max_y - 1 - y ][ x ] ), &tmp_data, 3 * sizeof( uint8_t) );
	}
    }

    wxImage tmp_image( COLORBAR_WIDTH, dimy * dimy_scale, &(buffer[0][0][0]), 1 );  
    this->colorbar_bmp = wxBitmap( tmp_image, 3 );
}




// update the number labels of the colorbar
void Heatmap::update_colorbar_ticks()
{        
    for( int i=0; i<NUM_TICKS; i++ )
    {
	int val = round( this->current_min
			 + i * ( this->current_max
				 - this->current_min ) / ( NUM_TICKS - 1 ) );

	this->colorbar_ticks[i]->SetLabel( to_string( val ) );
    }
}






void Heatmap::update_histo( int num_data )
{    
    int bins[2];
    
    for( int i=0; i<num_data; i++ )
    {
	int data_idx = this->num_data_in_histo + i;

	int add_data = 1;
	
	for( int j=0; j<2; j++ )
	{
	    double current_data = this->data[ data_idx ][j];
	    	    
	    if( current_data < histo_bounds[j][0]
		or current_data > histo_bounds[j][1] )
	    {
		add_data = 0;
		continue;
	    }

	    // otherwise compute bin
	    else
	    {
		bins[j] = ( int ) ( this->histo_dims[j]
				    * ( current_data - histo_bounds[j][0] )
				    / ( histo_bounds[j][1] - histo_bounds[j][0] ) );
	    }
	}

	if( add_data )
	{
	    // check if we just incremented the known smallest entry
	    if( memcmp( &bins, &current_min_bins, 2 * sizeof(int) ) == 0 )
	    {
		//++( this->current_min );
		this->find_new_min();
	    }
	    int newval = ++( this->histo[ bins[0] ][ bins[1] ] );
	    	    
	    if( newval > this->current_max )
		++( this->current_max );
	}
	
    }

    this->num_data_in_histo += num_data;
}



// find new minimum, assuming that A SINGLE DATA POINT
// has been added to the histogram. under that assumption,
// the current implementation of this function works and will
// be fast.
void Heatmap::find_new_min()
{
    int min_found = 0;
    
    for( int i=0; i < this->histo_dims[0]; i++ )
    {
	for( int j=0; j < histo_dims[1]; j++ )
	{
	    if( this->histo[i][j] == this->current_min )
	    {
		this->current_min_bins[0] = i;
		this->current_min_bins[1] = j;
		return;
	    }
	}
    }

    if( ! min_found )
	++( this->current_min );
}



void Heatmap::reset()
{
    for( int i=0; i<dimx; i++ )
    {
	for( int j=0; j<dimy; j++ )
	{
	    histo[i][j] = 0;
	    // memset( &( histo[i][0] ), 0, dimy * sizeof(int) ); 
	}
    }
    num_data_in_histo = 0;
    current_max = 0;
    current_min = 0;
}


void Heatmap::save()
{
    
}

// void compute_max( int *arr_start, size_t size, int *max, int *min )
// {
//     int tmp_max = *arr_start;
//     int tmp_min = *arr_start;

//     for( int i = 0; i < size; i++ )
//     {
// 	if( arr_start[i] > tmp_max )
// 	    tmp_max = arr_start[i];

// 	if( arr_start[i] > tmp_min )
// 	    tmp_min = arr_start[i];
//     }

//     *max = tmp_max;
//     *min = tmp_min;
// }
