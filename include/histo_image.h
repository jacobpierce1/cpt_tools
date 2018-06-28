#ifndef HISTO_IMAGE_H
#define HISTO_IMAGE_H


typedef struct {
    double r,g,b;
} COLOUR;



#include <wx/wx.h>
#include <wx/sizer.h>
#include <wx/rawbmp.h>
#include <wx/bitmap.h>
#include "constants.h" 
    
class wxImagePanel : public wxPanel
{
    int dimx;
    int dimy;
    int (*data)[ HISTO_DIMY];
    
    int dimx_scale;
    int dimy_scale;
	
    // wxFrame *frame;
    wxBitmap bmp;

    /* wxImage image; */
    /* wxBitmap resized; */
    /* int w, h; */

public :

    wxImagePanel( wxWindow *parent, wxString file, wxBitmapType format);

    wxImagePanel( wxWindow *parent, int (*data)[HISTO_DIMY], int dimx, int dimy,
		  int dimx_scale, int dimy_scale );
	
	
    // wxImagePanel( wxWindow *frame );

    void refresh( wxSizeEvent & evt );
    void paintEvent(wxPaintEvent & evt);
    void paintNow();
    void render(wxDC& dc);

    void update_bmp();
    COLOUR apply_colormap( int v, int vmin, int vmax);
    
    // some useful events
    /*
      void mouseMoved(wxMouseEvent& event);
      void mouseDown(wxMouseEvent& event);
      void mouseWheelMoved(wxMouseEvent& event);
      void mouseReleased(wxMouseEvent& event);
      void rightClick(wxMouseEvent& event);
      void mouseLeftWindow(wxMouseEvent& event);
      void keyPressed(wxKeyEvent& event);
      void keyReleased(wxKeyEvent& event);
    */

	
    DECLARE_EVENT_TABLE();
	
};
 
 


#endif
