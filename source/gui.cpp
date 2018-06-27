#if USE_GUI

#ifdef _WIN32
#include "stdafx.h"
#endif

#include "global.h" 

#include <iostream>
#include "gui.h"
#include <wx/valnum.h>
#include "tabor.h"
#include "mathplot.h"
#include "histo_image.h" 
#include <wx/wx.h>
#include <math.h>
#include <stdlib.h> 
#include <thread> 

using namespace std;





void initTaborTextCtrls( wxFrame *frame, TaborTextCtrls *tabor_text_ctrls );

void initTDCLabels( wxFrame *frame, TDCDataGui *tdc_data_gui );
//void mpFXYVector::AddData(float x, float y, std::vector<double> &xs, std::vector<double> &ys);


void initControlButtons( wxFrame *frame, ControlButtons control_buttons ) ;

wxStaticText * make_title( wxFrame *frame, const char *label, int x, int y,
			   int fontsize, long style = 0 );


// void gen_test_data( int dimy, int (*data)[dimy]);

// void gen_test_data(int **data, int nrows, int ncols );

template <size_t size_x, size_t size_y>
void func( int (&arr)[size_x][size_y]);


void tdc_thread_main( );

    
// void test_image( wxFrame *frame, uint8_t a );




BEGIN_EVENT_TABLE(wxImagePanel, wxPanel)
EVT_PAINT(wxImagePanel::paintEvent)
EVT_SIZE( wxImagePanel::refresh )
END_EVENT_TABLE()


// void refresh( )
// {
//     wxWindow.Refresh() ;
// }


int data[ HISTO_DIMX ][ HISTO_DIMY ];



bool MyApp::OnInit()
{

    wxInitAllImageHandlers();
	         
    wxFrame *frame = new wxFrame(NULL, wxID_ANY, "CPT Master Controller",
    				 wxDefaultPosition,
    				 wxSize( FRAME_WIDTH, FRAME_HEIGHT  ) );


    wxPanel *bmp_panel = new wxPanel( frame, wxID_ANY, 
    				      wxPoint( 100, 100 ), wxSize( 400, 400   ) );

    bmp_panel->Show();

	
    // bmp_frame->Show();
    
    // then simply create like this
// #define dimx 32
// #define dimy 32
    
    const int dimx = 32;
    const int dimy = 32;
    int dimx_scale = 10;
    int dimy_scale = 10;
    

    // gui->data = data;
    
    func( data );

    // gen_test_data( &data, dimx, dimy );
    
    wxImagePanel *drawPane = new wxImagePanel( bmp_panel, data, dimx, dimy,
					       dimx_scale, dimy_scale ); 

    
    drawPane->update_bmp(  ) ;
    //drawPane->Refresh();
    
    // cout << drawPane->bmp.IsOk() << endl;
    
    make_title( frame, "CPT Master Controller",
    		FRAME_WIDTH / 2,
    		MAIN_TITLE_Y_OFFSET,
    		MAIN_TITLE_FONTSIZE, wxALIGN_RIGHT );

 
    frame->Show();
    
    thread tdc_thread( tdc_thread_main );

    
    while(1)
    {
	mySleep(1000);
    }
    
    // frame->Refresh();
    return true;


    // TaborTextCtrls tabor_text_ctrls;
    // initTaborTextCtrls( frame, &tabor_text_ctrls ) ;
    
    // TDCDataGui tdc_data_gui;
    // initTDCLabels( frame, &tdc_data_gui ) ;

    // ControlButtons control_buttons;
    // initControlButtons( frame, control_buttons );

    // // test_image( frame, 5 ) ;
    
    // make_title( frame, "MCP Hits",
    // 		MCP_PLOT_X_OFFSET + MCP_PLOT_SIZE / 2,
    // 		MCP_PLOT_Y_OFFSET - MCP_PLOT_TITLE_OFFSET,
    // 		TITLE_FONTSIZE, wxALIGN_RIGHT );

    
    // // wxImagePanel *drawPane = new wxImagePanel( frame, "test.jpg", wxBITMAP_TYPE_JPEG );
    // wxImagePanel *drawPane = new wxImagePanel( frame, "../gui_images/test.jpg",
    // 					       wxBITMAP_TYPE_JPEG );
    
    // drawPane->fetch_new_data( 100 ) ;
	    
    // frame->Show();
	        
    // return true;
}



// test data: gaussian spot 

// void gen_test_data( const int dimy, int (*data)[dimy])

// void gen_test_data(int **data, int nrows, int ncols )

template <size_t size_x, size_t size_y>
void func(int (&arr)[size_x][size_y])
{

    int x_center = rand() % 32;
    
    for( int i=0; i < size_x; i++ )
    {
	for( int j=0; j < size_y; j++ )
	{
	    arr[i][j] = (int) 200 * exp( 0 - pow( x_center - i, 2 ) / 10 - pow( 10 - j, 2 ) / 10 );
	}
    }
}





wxStaticText * make_title( wxFrame *frame, const char *label, int x, int y,
			   int fontsize, long style )
{
    wxPoint title_coords = wxPoint( x,y ) ;
    
    wxStaticText *title = new wxStaticText( frame, 0, label, title_coords,
					    wxDefaultSize, style );
    
    wxFont title_font( fontsize, wxDEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD);
    title->SetFont( title_font );


    int tmpx;
    int tmpy;
    title->GetSize( &tmpx, &tmpy );

    wxPoint shift = wxPoint( tmpx / 2, 0 );
    
    title->Move( title->GetPosition() - shift );

    return title;
}





void initTaborTextCtrls( wxFrame *frame, TaborTextCtrls *tabor_text_ctrls )
{

    make_title( frame, "Tabor Settings",
		( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP ) / 2,
		TABOR_TEXT_CTRLS_START_YPOS - TABOR_TITLE_OFFSET,
		20 );

    // add the labels 

    wxPoint textctrl_positions[ NUM_TABOR_SETTINGS ];

    char labels[ NUM_TABOR_SETTINGS ][ 64 ] =
	{ "num steps", "wminus", "wplus",
	  "wminus_phase", "wplus_phase", "wc_phase",
	  "wminus_amp", "wplus_amp", "wc_amp",
	  "wminus_loops", "wplus_loops", "wc_loops",
	  "wminus_length", "wplus_length", "wc_length",
	  "time acc" 
	};
    
    for( int i = 0; i < NUM_TABOR_SETTINGS; i++ )
    {
	textctrl_positions[i] = wxPoint( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP,
					 TABOR_TEXT_CTRLS_START_YPOS
					 + i * TABOR_TEXT_CTRLS_YPOS_DELTA ) ;

	wxPoint label_position = wxPoint( TABOR_LABEL_X_OFFSET,
					  TABOR_TEXT_CTRLS_START_YPOS
					  + i * TABOR_TEXT_CTRLS_YPOS_DELTA ) ;
	
	new wxStaticText( frame, 0, labels[i], label_position ) ;

    }


    // now add all text controls 

    TaborSettings default_tabor_settings;

    wxIntegerValidator<signed char> nsteps_validator;
    nsteps_validator.SetRange(1, 10);

    string default_nsteps = to_string( default_tabor_settings.nsteps );
    tabor_text_ctrls->nsteps = new wxTextCtrl(  frame, 0,
						default_nsteps.c_str(), 
						textctrl_positions[0],
						wxDefaultSize, 0,
						nsteps_validator ) ;

    string default_wminus = to_string( default_tabor_settings.wminus );
    tabor_text_ctrls->wminus = new wxTextCtrl(  frame, 0, default_wminus.c_str(),
						textctrl_positions[1],
						wxDefaultSize, 0,
						nsteps_validator ) ;


    tabor_text_ctrls->nsteps = new wxTextCtrl(  frame, 0, wxT("5"), textctrl_positions[2],
						wxDefaultSize, 0,
						nsteps_validator ) ;


    tabor_text_ctrls->nsteps = new wxTextCtrl(  frame, 0, wxT("5"), textctrl_positions[3],
						wxDefaultSize, 0,
						nsteps_validator ) ;


    tabor_text_ctrls->nsteps = new wxTextCtrl(  frame, 0, wxT("5"), textctrl_positions[4],
						wxDefaultSize, 0,
						nsteps_validator ) ;


    tabor_text_ctrls->nsteps = new wxTextCtrl(  frame, 0, wxT("5"), textctrl_positions[5],
						wxDefaultSize, 0,
						nsteps_validator ) ;


    tabor_text_ctrls->nsteps = new wxTextCtrl(  frame, 0, wxT("5"), textctrl_positions[6],
						wxDefaultSize, 0,
						nsteps_validator ) ;


    tabor_text_ctrls->nsteps = new wxTextCtrl(  frame, 0, wxT("5"), textctrl_positions[7],
						wxDefaultSize, 0,
						nsteps_validator ) ;
    
}





void initTDCLabels( wxFrame *frame, TDCDataGui *tdc_data_gui )
{
    // int xcoord = (int) ( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP ) / 2;

    wxPoint title_coords = wxPoint( ( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP ) / 2,
				    TDC_LABELS_Y_OFFSET + TABOR_TITLE_OFFSET ) ;
    wxSize title_size = wxSize( 100, 40 ) ;
    wxStaticText *title = new wxStaticText( frame, 0, "TDC Data", title_coords, title_size );
    wxFont title_font( 20, wxDEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD);
    title->SetFont( title_font );

    int x1 = TABOR_LABEL_X_OFFSET;
    int x2 = TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP;
    int y1 = TDC_LABELS_Y_OFFSET + 2 * TABOR_TITLE_OFFSET;
    int y2 = TDC_LABELS_Y_OFFSET + 2 * TABOR_TITLE_OFFSET
	+ TABOR_TEXT_CTRLS_YPOS_DELTA;

    new wxStaticText( frame, 0, "Counts", wxPoint( x1, y1 ) );
    new wxStaticText( frame, 0, "Count Rate", wxPoint( x1, y2 ) );
    
    tdc_data_gui->counts = new wxStaticText( frame, 0, "0", wxPoint( x2, y1 ) );
    tdc_data_gui->count_rate = new wxStaticText( frame, 0, "0", wxPoint( x2, y2 ) );

}




void tdc_thread_main(  )
{
    
        cout << "reached 5" << endl;
#if USE_TDC
    while(1)
    {
	mySleep( 1000 );
	tdc->r
    }
#else
    while(1)
    {
	mySleep( 1000 );
	func( data );
	// gen_sample_data( data );
    }
#endif
}


// Button::Button(const wxString& title)
//     : wxFrame(NULL, wxID_ANY, title, wxDefaultPosition, wxSize(270, 150))
// {
//     wxPanel *panel = new wxPanel(this, wxID_ANY);
    
//     wxButton *button = new wxButton(panel, wxID_EXIT, wxT("Quit"), 
// 				    wxPoint(20, 20));
//     Connect(wxID_EXIT, wxEVT_COMMAND_BUTTON_CLICKED, 
// 	    wxCommandEventHandler(Button::OnQuit));
//     button->SetFocus();

//     wxTextCtrl *text_ctrl = new wxTextCtrl( panel, wxID_EXIT, wxT("123") ) ;
  
//     Centre();
// }



// void Button::OnQuit(wxCommandEvent & WXUNUSED(event))
// {
//     Close(true);
// }



// void mpFXYVector::AddData(float x, float y, std::vector<double> &xs, std::vector<double> &ys)
// {
//     // Check if the data vectora are of the same size
//     if (xs.size() != ys.size()) {
// 	wxLogError(_("wxMathPlot error: X and Y vector are not of the same length!"));
// 	return;
//     }

//     //Delete first point if you need a filo buffer (i dont need it)
//     //xs.erase(xs.begin());
//     //xy.erase(xy.begin());

//     //Add new Data points at the end
//     xs.push_back(x);
//     ys.push_back(y);


//     // Copy the data:
//     m_xs = xs;
//     m_ys = ys;

//     // Update internal variables for the bounding box.
//     if (xs.size()>0)
//     {
// 	m_minX  = xs[0];
// 	m_maxX  = xs[0];
// 	m_minY  = ys[0];
// 	m_maxY  = ys[0];

// 	std::vector<double>::const_iterator  it;

// 	for (it=xs.begin();it!=xs.end();it++)
// 	{
// 	    if (*it<m_minX) m_minX=*it;
// 	    if (*it>m_maxX) m_maxX=*it;
// 	}
// 	for (it=ys.begin();it!=ys.end();it++)
// 	{
// 	    if (*it<m_minY) m_minY=*it;
// 	    if (*it>m_maxY) m_maxY=*it;
// 	}
// 	m_minX-=0.5f;
// 	m_minY-=0.5f;
// 	m_maxX+=0.5f;
// 	m_maxY+=0.5f;
//     }
//     else
//     {
// 	m_minX  = -1;
// 	m_maxX  = 1;
// 	m_minY  = -1;
// 	m_maxY  = 1;
//     }
// }





// THE INBETWEENERS 

void initControlButtons( wxFrame *frame, ControlButtons control_buttons )
{

    const int num_buttons = 4;

    wxButton *buttons[4] = { control_buttons.save_button,
			     control_buttons.save_and_run_next_button,
			     control_buttons.start_pause_toggle_button,
			     control_buttons.reload_caribu_config_button };
    
    char button_labels[ num_buttons ][ 64 ] = {
	"save", "Save and Run Next", "Pause", "Reload Caribu Config" };

    // functions = {}

    const int xoffset = CONTROL_BUTTONS_X_START ;
    
    for( int i=0; i<num_buttons; i++ )
    {
	wxPoint position = wxPoint( xoffset,
				    TABOR_TEXT_CTRLS_START_YPOS + i * CONTROL_BUTTONS_Y_DELTA ) ;

	buttons[i] = new wxButton(  frame, 0, button_labels[i], position );
	buttons[i]->SetFocus();
	buttons[i]->Show();
    }
	    

    // Connect(wxID_EXIT, wxEVT_COMMAND_BUTTON_CLICKED, 
    // 	    wxCommandEventHandler(Button::OnQuit));
    // button->SetFocus();
    // button->Show();
}







IMPLEMENT_APP(MyApp)




#endif 
