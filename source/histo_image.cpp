#include "histo_image.h"
#include <iostream>
#include <wx/dcbuffer.h>



using namespace std;

typedef wxAlphaPixelData PixelData;

// void RGBAtoBitmap( bitmap, unsigned char *rgba, int w, int h);




wxImagePanel::wxImagePanel(wxWindow* parent, wxString file, wxBitmapType format) :
    wxPanel( parent, wxID_ANY, wxPoint( 100, 100 ), wxSize( 320, 320 ) )
{
    // load the file... ideally add a check to see if loading was successful
    //this->image; // = new wxImage();
    this->bmp.LoadFile(file, format);
}



wxImagePanel::wxImagePanel( wxWindow *parent, int (*data)[ HISTO_DIMY], int dimx, int dimy,
	      int dimx_scale, int dimy_scale ) :
        wxPanel( parent, wxID_ANY, wxPoint( 100, 100 ), wxSize( 320, 320 ) )
{
    this->data = data;
    this->dimx = dimx;
    this->dimy = dimy;
    this->dimx_scale = dimx_scale;
    this->dimy_scale = dimy_scale;
}



// wxImagePanel::wxImagePanel(wxWindow* parent )  :
//     wxPanel( parent, wxID_ANY, wxPoint( 100, 100 ), wxSize( 320, 320 ) )
// {
//     this->bmp = wxBitmap(); // 320, 320 );
//     this->Update();
//     // this->fetch_new_data( 5 );
    
//     // load the file... ideally add a check to see if loading was successful
//     //this->image; // = new wxImage();
//     //this->bmp.LoadFile(file, format);
// }


// wxImagePanel::wxImagePanel( void )
// {
// //    image = new wxImage();
// }

// wxImagePanel::wxImagePanel(wxFrame* parent, uint8_t *data, int width, int height ) :
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


void wxImagePanel::refresh( wxSizeEvent & evt )
{
    cout << "refresh called" << endl;
    this->Refresh();
    this->Update();
    evt.Skip();
}


void wxImagePanel::paintEvent(wxPaintEvent & evt)
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
// void wxImagePanel::paintNow()
// {
//     // depending on your system you may need to look at double-buffered dcs
//     wxBufferedPaintDC dc( this );
//     render(dc);
// }
 
/*
 * Here we do the actual rendering. I put it in a separate
 * method so that it can work no matter what type of DC
 * (e.g. wxPaintDC or wxClientDC) is used.
 */
void wxImagePanel::render( wxDC&  dc)
{
    dc.DrawBitmap( this->bmp, 0, 0, false );
}



void wxImagePanel::update_bmp( )
{
    uint8_t buffer[ dimx * dimx_scale ][ dimy * dimy_scale ][3];
    memset( buffer, 0, dimx * dimx_scale * dimy * dimy_scale * 3 );
    // uint8_t tmp = 
    
    // memset( buffer, a, 32 * 32 ) ;

    for( int x = 0; x < dimx; ++x)
    {
	for( int y = 0; y < dimy; ++y)
	{
	    uint8_t tmp_data = this->data[x][y];
	    for( int i=0; i < dimx_scale; ++i )
	    {
		for( int j=0; j < dimx_scale; ++j )
		{
		    int tmpx = x * dimx_scale + i;
		    int tmpy = y * dimy_scale + j;
		    buffer[ tmpx ][ tmpy ][1] = tmp_data;
		}
	    }
	}
    }

    wxImage tmp_image( dimx * dimx_scale, dimy * dimy_scale, &buffer[0][0][0], 1 );
    
    
    //tmp_image.Rescale( 320, 320, wxIMAGE_QUALITY_HIGH );
        
    this->bmp = wxBitmap( tmp_image, 3 );
    // cout << this->bmp.GetScaleMode( ) << endl;

    
    // cout << "red: " << this->bmp.ConvertToImage().GetRed( 20, 10 ) << endl;
    // cout << bmp.GetWidth() << endl;
    
    // this->Refresh();
    // this->Update();
    // this->paintNow();
    //cout << bmp.GetHeight() << endl;
}


