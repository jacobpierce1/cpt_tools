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
#include "heatmap.h" 
#include <wx/wx.h>
#include <math.h>
#include <stdlib.h> 
#include <thread> 
#include "tdc.h"
#include <wx/filepicker.h>




using namespace std;



#define SLEEP_TIME_MS 1000


void test( wxCommandEvent &event );


BEGIN_EVENT_TABLE(Heatmap, wxPanel)
EVT_PAINT(Heatmap::paintEvent)
// EVT_BUTTON ( START_PAUSE_TOGGLE_BUTTON_ID_, MainFrame::OnExit )
// EVT_BUTTON ( LOAD_TABOR_ID, MainFrame::OnExit ) 
END_EVENT_TABLE()




// int histo[ HISTO_DIMX ][ HISTO_DIMY ];
thread *tdc_thread;
TDC_controller *tdc;



RenderTimer::RenderTimer( Heatmap *heatmap ) : wxTimer()
{
    RenderTimer::heatmap = heatmap;
}
 
void RenderTimer::Notify()
{
    int num_data_to_add = tdc->num_processed_data - heatmap->num_data_in_histo;
    heatmap->update_histo( num_data_to_add );
    heatmap->update_colorbar_ticks();
    heatmap->update_bmp();
    heatmap->Refresh();
}


void RenderTimer::start()
{
    wxTimer::Start( SLEEP_TIME_MS );
}





 
BEGIN_EVENT_TABLE ( MainFrame, wxFrame )
EVT_BUTTON ( SAVE_BUTTON_ID, MainFrame::save_button_action )
EVT_BUTTON( SAVE_AND_RUN_NEXT_BUTTON_ID, MainFrame::save_and_run_next_button_action )
EVT_BUTTON( START_PAUSE_TOGGLE_BUTTON_ID, MainFrame::start_pause_toggle_button_action )
EVT_BUTTON( LOAD_TABOR_BUTTON_ID, MainFrame::load_tabor_button_action )
EVT_BUTTON( RESET_BUTTON_ID, MainFrame::reset_button_action )
END_EVENT_TABLE() 




MainFrame::MainFrame(const wxString &title, const wxPoint &pos, const wxSize
		     &size) :
wxFrame((wxFrame*)NULL,  -1, title, pos, size)
{
    
}



void MainFrame::OnExit( wxCommandEvent& event )
{
    delete tdc;
    Close(TRUE); // Tells the OS to quit running this process
}






bool MyApp::OnInit()
{
    render_loop_on = false;

    wxInitAllImageHandlers();
	         
    MainFrame *frame = new MainFrame( "CPT Master Controller",
				    wxDefaultPosition,
				    wxSize( FRAME_WIDTH, FRAME_HEIGHT  ) );

    wxPanel *bmp_panel = new wxPanel( frame, wxID_ANY, 
    				      wxPoint( MCP_PLOT_X_OFFSET, MCP_PLOT_Y_OFFSET ),
				      wxSize( MCP_PLOT_SIZE + COLORBAR_WIDTH + COLORBAR_OFFSET,
					      MCP_PLOT_SIZE   ) );
       
    bmp_panel->Show();
    
    const int dimx = 64;
    const int dimy = 64;
    int dimx_scale = 5;
    int dimy_scale = 5;
        
    // func( histo );

    tdc = new TDC_controller();

    int histo_bounds[2][2] = { {-10,10}, {-10,10} };

    cout << "allocating heatmap" << endl;
    
    Heatmap *heatmap = new Heatmap( bmp_panel, tdc->mcp_positions,
				    dimx, dimy,
				    dimx_scale, dimy_scale,
				    histo_bounds, "linear_bmw_5_95_c86" ); 

    frame->heatmap = heatmap;
    heatmap->update_bmp();
    heatmap->make_colorbar();
    cout << "reached" << endl;
        
    make_title( frame, "CPT Master Controller",
    		FRAME_WIDTH / 2,
    		MAIN_TITLE_Y_OFFSET,
    		MAIN_TITLE_FONTSIZE );

 
    frame->Show();


    RenderTimer *timer = new RenderTimer(heatmap);
    timer->start();

    // dispatch tdc data acquisition thread
    tdc_thread = new thread( tdc_thread_main );


    TaborTextCtrls tabor_text_ctrls;
    initTaborTextCtrls( frame, &tabor_text_ctrls ) ;
    
    TDCDataGui tdc_data_gui;
    initTDCLabels( frame, &tdc_data_gui ) ;

    ControlButtons control_buttons;
    initControlButtons( frame, control_buttons );
        
    make_title( frame, "MCP Hits",
    		MCP_PLOT_X_OFFSET + MCP_PLOT_SIZE / 2,
    		MCP_PLOT_Y_OFFSET - MCP_PLOT_TITLE_OFFSET,
    		TITLE_FONTSIZE );

    wxDirPickerCtrl *dir_picker = new wxDirPickerCtrl( frame, wxID_ANY );

    
    return true;
}



// test data: gaussian spot 

template <size_t size_x, size_t size_y>
void func(int (&arr)[size_x][size_y])
{
    cout << "generating data " << endl;
    int x_center = rand() % 32;
    
    for( int i=0; i < size_x; i++ )
    {
	for( int j=0; j < size_y; j++ )
	{
	    arr[i][j] = (int) 200 * exp( 0 - pow( x_center - i, 2 ) / 10
					 - pow( 10 - j, 2 ) / 10 );
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

    int xcoord = ( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP ) / 2;
    int ycoord = TDC_LABELS_Y_OFFSET + TABOR_TITLE_OFFSET ;
    
    make_title( frame,  "TDC Info", xcoord, ycoord, TITLE_FONTSIZE );
    
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




void tdc_thread_main()
{
    // tdc.start();
    while(1)
    {
	cout << "reading tdc data" << endl;	
	mySleep( SLEEP_TIME_MS );
	tdc->read();
	tdc->process_hit_buffer();
    }
}






void initControlButtons( wxFrame *frame, ControlButtons control_buttons )
{

    const int num_buttons = 5;

    char button_labels[ num_buttons ][ 64 ] = {
	"Save", "Save and Run Next", "Pause", "Load Tabor", "Reset" };

    int button_ids[ num_buttons ] = { SAVE_BUTTON_ID,
				      SAVE_AND_RUN_NEXT_BUTTON_ID,
				      START_PAUSE_TOGGLE_BUTTON_ID,
				      LOAD_TABOR_BUTTON_ID,
				      RESET_BUTTON_ID };
        
    const int xoffset = CONTROL_BUTTONS_X_START ;

    const wxSize size( CONTROL_BUTTONS_WIDTH, CONTROL_BUTTONS_HEIGHT );

    for( int i=0; i<num_buttons; i++ )
    {
	const int yoffset = TABOR_TEXT_CTRLS_START_YPOS +
	    i * CONTROL_BUTTONS_Y_DELTA;

	wxPoint pos( xoffset, yoffset );
    
	new wxButton( frame, button_ids[i], button_labels[i], pos, size );
    		  
    }
}








void MainFrame::save_button_action( wxCommandEvent &event )
{
    cout << "test" << endl;
}


void MainFrame::save_and_run_next_button_action( wxCommandEvent &event )
{
    cout << "test" << endl;
}


void MainFrame::start_pause_toggle_button_action( wxCommandEvent &event )
{
    cout << "test" << endl;
}


void MainFrame::load_tabor_button_action( wxCommandEvent &event )
{
    cout << "test" << endl;
}


void MainFrame::reset_button_action( wxCommandEvent &event )
{
    cout << "INFO: clearing plots." << endl;
    this->heatmap->reset();
    cout << "current_max:  " << heatmap->current_max << endl;
    this->heatmap->paintNow();
}





IMPLEMENT_APP( MyApp )




#endif 
