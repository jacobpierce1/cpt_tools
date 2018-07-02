#include "histo_image.h" 

// #include <wx/wx.h>
// #include <wx/sizer.h>
// #include <wx/rawbmp.h>


typedef wxAlphaPixelData PixelData;

// void RGBAtoBitmap( bitmap, unsigned char *rgba, int w, int h);


// class wxImagePanel : public wxPanel
//     {
//         wxBitmap image;
 
//     public:
//         wxImagePanel(wxFrame* parent, wxString file, wxBitmapType format);
// 	wxImagePanel(wxFrame* parent, uint8_t *data, int width, int height );
 
//         void paintEvent(wxPaintEvent & evt);
//         void paintNow();
 
//         void render(wxDC& dc);
// 	void fetch_new_data( uint8_t a );
 
//         // some useful events
//         /*
//          void mouseMoved(wxMouseEvent& event);
//          void mouseDown(wxMouseEvent& event);
//          void mouseWheelMoved(wxMouseEvent& event);
//          void mouseReleased(wxMouseEvent& event);
//          void rightClick(wxMouseEvent& event);
//          void mouseLeftWindow(wxMouseEvent& event);
//          void keyPressed(wxKeyEvent& event);
//          void keyReleased(wxKeyEvent& event);
//          */
 
//         DECLARE_EVENT_TABLE()
//     };
 
 
BEGIN_EVENT_TABLE(wxImagePanel, wxPanel)
// some useful events
/*
 EVT_MOTION(wxImagePanel::mouseMoved)
 EVT_LEFT_DOWN(wxImagePanel::mouseDown)
 EVT_LEFT_UP(wxImagePanel::mouseReleased)
 EVT_RIGHT_DOWN(wxImagePanel::rightClick)
 EVT_LEAVE_WINDOW(wxImagePanel::mouseLeftWindow)
 EVT_KEY_DOWN(wxImagePanel::keyPressed)
 EVT_KEY_UP(wxImagePanel::keyReleased)
 EVT_MOUSEWHEEL(wxImagePanel::mouseWheelMoved)
 */
 
// catch paint events
EVT_PAINT(wxImagePanel::paintEvent)
 
END_EVENT_TABLE()
 
 
// some useful events
/*
 void wxImagePanel::mouseMoved(wxMouseEvent& event) {}
 void wxImagePanel::mouseDown(wxMouseEvent& event) {}
 void wxImagePanel::mouseWheelMoved(wxMouseEvent& event) {}
 void wxImagePanel::mouseReleased(wxMouseEvent& event) {}
 void wxImagePanel::rightClick(wxMouseEvent& event) {}
 void wxImagePanel::mouseLeftWindow(wxMouseEvent& event) {}
 void wxImagePanel::keyPressed(wxKeyEvent& event) {}
 void wxImagePanel::keyReleased(wxKeyEvent& event) {}
 */
 
wxImagePanel::wxImagePanel(wxFrame* parent, wxString file, wxBitmapType format) :
wxPanel(parent)
{
    // load the file... ideally add a check to see if loading was successful
    image.LoadFile(file, format);
}


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
 
void wxImagePanel::paintEvent(wxPaintEvent & evt)
{
    // depending on your system you may need to look at double-buffered dcs
    wxPaintDC dc(this);
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
void wxImagePanel::paintNow()
{
    // depending on your system you may need to look at double-buffered dcs
    wxClientDC dc(this);
    render(dc);
}
 
/*
 * Here we do the actual rendering. I put it in a separate
 * method so that it can work no matter what type of DC
 * (e.g. wxPaintDC or wxClientDC) is used.
 */
void wxImagePanel::render(wxDC&  dc)
{
    dc.DrawBitmap( image, 0, 0, false );
}



void wxImagePanel::fetch_new_data( uint8_t a )
{
    // unsigner char data[32][32][4]; 
    // unsigned char *rgba = &(data[0][0]);
    // wxBitmap *RGBAtoBitmap( this->image, rgba, int w, int h);

    wxImage tmp_image( 32, 32 );
    uint8_t buffer[32][32];
    memset( buffer, a, 32 * 32 ) ;

//    uint8_t *start = buffer;
    for(uint16_t y = 0; y < 32; ++y)
    {
	for(uint16_t x = 0; x < 32; ++x)
	{
	    uint8_t intensity = buffer[y][x];
	    tmp_image.SetRGB(x, y, x*8, y*8, 0 );
	}
    }
    tmp_image.Rescale( 400, 400 ) ;
    this->image = wxBitmap( tmp_image );
}



 
// ----------------------------------------
// how-to-use example
 
class MyApp: public wxApp
    {
 
        wxFrame *frame;
        wxImagePanel * drawPane;
    public:
        bool OnInit()
        {
            wxInitAllImageHandlers();
	    
            frame = new wxFrame(NULL, wxID_ANY, wxT("Hello wxDC"), wxPoint(50,50),
				wxSize(800,600));
 
            // then simply create like this
	    drawPane = new wxImagePanel( frame, "test.jpg", wxBITMAP_TYPE_JPEG);

	    drawPane->fetch_new_data( 100 ) ;
 
            frame->Show();
            return true;
        } 
 
    };

 
IMPLEMENT_APP(MyApp)





// void RGBAtoBitmap( bitmap, unsigned char *rgba, int w, int h)
// {
// //   wxBitmap *bitmap=new wxBitmap(w, h, 32);
//    if(!bitmap->Ok()) {
//       delete bitmap;
//       return NULL;
//    }

//    PixelData bmdata(*bitmap);
//    if(bmdata==NULL) {
//        //wxLogDebug(wxT("getBitmap() failed"));
//       delete bitmap;
//       return NULL;
//    }

//    bmdata.UseAlpha();
//    PixelData::Iterator dst(bmdata);

//    for(int y=0; y<h; y++) {
//       dst.MoveTo(bmdata, 0, y);
//       for(int x=0; x<w; x++) {
//          // wxBitmap contains rgb values pre-multiplied with alpha
//          unsigned char a=rgba[3];
//          dst.Red()=rgba[0]*a/255;
//          dst.Green()=rgba[1]*a/255;
//          dst.Blue()=rgba[2]*a/255;
//          dst.Alpha()=a;
//          dst++;
//          rgba+=4;
//       }
//    }
//    return bitmap;
// }


// IMPLEMENT_APP(MyApp)




// bool MyApp::OnInit()
// {
//     wxFrame *frame = new wxFrame(NULL, wxID_ANY, "CPT Master Controller",
// 				 wxDefaultPosition,
// 				 wxSize( FRAME_WIDTH, FRAME_HEIGHT  ) );
//     frame->Show(true);

//     make_title( frame, "CPT Master Controller",
// 		FRAME_WIDTH / 2,
// 		MAIN_TITLE_Y_OFFSET,
// 		MAIN_TITLE_FONTSIZE, wxALIGN_RIGHT );
// }
