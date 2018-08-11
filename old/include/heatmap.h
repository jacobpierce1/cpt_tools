#ifndef HEATMAP_H
#define HEATMAP_H

#include <wx/wx.h>
#include <wx/sizer.h>
#include <wx/rawbmp.h>
#include <wx/bitmap.h>
#include "constants.h" 
#include "colormap.h"
#include <vector>

typedef struct {
    double r,g,b;
} COLOUR;


#define COLORBAR_OFFSET 20
#define COLORBAR_WIDTH 20
#define COLORBAR_RESOLUTION 256
#define NUM_TICKS 5
#define TICKS_OFFSET 5



class Heatmap : public wxPanel
{
    void find_new_min();

public :

    Heatmap( wxWindow *parent, wxString file, wxBitmapType format);

    Heatmap( wxWindow *parent, double (*data)[2],
		  int dimx, int dimy,
		  int dimx_scale, int dimy_scale, int bounds[2][2],
		  const char *cmap = "fire" );

    ~Heatmap();

    bool needs_update;
    
    int dimx;
    int dimy;
    // int **histo;
    std::vector< std::vector<int> > histo;
    double (* data)[2];
    
    int dimx_scale;
    int dimy_scale;

    int current_max;
    int current_min;
    int current_min_bins[2];
    
    int num_data_in_histo;

    int histo_bounds[2][2];
    int histo_dims[2];

    ColorMap *cmap;
    
    // wxWidgets stuff
    wxBitmap bmp;
    wxBitmap colorbar_bmp;
    wxStaticText *colorbar_ticks[ NUM_TICKS ];

    int background_color[3];
		
    // Heatmap( wxWindow *frame );

    void refresh( wxSizeEvent & evt );
    void paintEvent(wxPaintEvent & evt);
    void paintNow();
    void render(wxDC& dc);

    void update_bmp();
    void apply_colormap( uint8_t buf[3], double v, double vmin, double vmax );
    void update_histo( int num_data );
    void make_colorbar();
    void update_colorbar_ticks();

    void reset();

    void save();
    
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
