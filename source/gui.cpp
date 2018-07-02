#if USE_GUI

#ifdef _WIN32
#include "stdafx.h"
#endif


#include <iostream>
#include <stdlib.h> 
#include <thread> 
#include <math.h>
#include <limits.h>
#include <ctime>

#include <wx/valnum.h>
#include <wx/wx.h>
#include <wx/filepicker.h>
#include <wx/bannerwindow.h>
#include <wx/window.h>
#include <wx/tooltip.h>



#include "global.h" 
#include "gui.h"
#include "tabor.h"
#include "tdc.h"
#include "mathplot.h"
#include "heatmap.h" 



using namespace std;



#define SLEEP_TIME_MS 1000




BEGIN_EVENT_TABLE(Heatmap, wxPanel)
EVT_PAINT(Heatmap::paintEvent)
// EVT_BUTTON ( START_PAUSE_TOGGLE_BUTTON_ID_, MainFrame::OnExit )
// EVT_BUTTON ( LOAD_TABOR_ID, MainFrame::OnExit ) 
END_EVENT_TABLE()




// int histo[ HISTO_DIMX ][ HISTO_DIMY ];
thread *tdc_thread;
TDC_controller *tdc;



RenderTimer::RenderTimer( MainFrame *frame ) : wxTimer()
{
    this->frame = frame;
}


void RenderTimer::Notify()
{
    int num_data_to_add = tdc->num_processed_data - frame->heatmap->num_data_in_histo;
    bool needs_update = this->frame->heatmap->needs_update;
    needs_update |= ( num_data_to_add > 0 );
    
    if( needs_update )
    {
	frame->heatmap->update_histo( num_data_to_add );
	frame->heatmap->update_colorbar_ticks();
	frame->heatmap->update_bmp();
	frame->heatmap->Refresh();
	frame->update_tdc_labels();
    }
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
    delete this->heatmap;
    delete tdc_thread;    
    Close(TRUE); // Tells the OS to quit running this process
}






bool MyApp::OnInit()
{
    render_loop_on = false;

    wxInitAllImageHandlers();
	         
    MainFrame *frame = new MainFrame( "CPT Master Controller",
				      wxDefaultPosition,
				      wxSize( FRAME_WIDTH, FRAME_HEIGHT  ) );

// Create and initialize the banner.
    wxBannerWindow* banner = new wxBannerWindow( frame, wxUP);
    banner->SetText( "Phase Imaging Master Controller", "" );
    // And position it along the left edge of the window.
    wxSizer* sizer = new wxBoxSizer(wxVERTICAL);
    sizer->Add(banner, wxSizerFlags().Expand());
    frame->SetSizer(sizer);
    
    frame->heatmap_panel = new wxPanel( frame, wxID_ANY, 
					wxPoint( MCP_PLOT_X_OFFSET,
						 MCP_PLOT_Y_OFFSET + TITLE_OFFSET ),
					wxSize( 1000, 1000 ) );
    // wxSize( MCP_PLOT_SIZE*2 + COLORBAR_WIDTH
    // 	+ COLORBAR_OFFSET,
    // 	MCP_PLOT_SIZE   ) );
    frame->heatmap_panel->Show();
    
    const int dimx = 64;
    const int dimy = 64;
    int dimx_scale = 5;
    int dimy_scale = 5;
        
    // func( histo );

    tdc = new TDC_controller();

    int histo_bounds[2][2] = { {-10,10}, {-10,10} };
    
    Heatmap *heatmap = new Heatmap( frame->heatmap_panel, tdc->mcp_positions,
				    dimx, dimy,
				    dimx_scale, dimy_scale,
				    histo_bounds, "linear_bmy_10_95_c71" ); 

    
    frame->heatmap = heatmap;
    heatmap->update_bmp();
    heatmap->make_colorbar();
        
    // make_title( frame, "CPT Master Controller",
    // 		FRAME_WIDTH / 2,
    // 		MAIN_TITLE_Y_OFFSET,
    // 		MAIN_TITLE_FONTSIZE );

 
    frame->Show();


    RenderTimer *timer = new RenderTimer( frame );
    timer->start();

    // dispatch tdc data acquisition thread
    tdc_thread = new thread( tdc_thread_main );


    // TaborTextCtrls tabor_text_ctrls;
    frame->init_tabor_text_ctrls() ;
    frame->init_tdc_labels() ;
    frame->init_output_controls();
    

    ControlButtons control_buttons;
    initControlButtons( frame, control_buttons );
        
    make_title( frame, "MCP Hits",
    		MCP_PLOT_X_OFFSET + MCP_PLOT_SIZE / 2 - 75,
    		MCP_PLOT_Y_OFFSET - TITLE_OFFSET,
    		TITLE_FONTSIZE, 0 );
    
    return true;
}



// // test data: gaussian spot 

// template <size_t size_x, size_t size_y>
// void func(int (&arr)[size_x][size_y])
// {
//     cout << "generating data " << endl;
//     int x_center = rand() % 32;
    
//     for( int i=0; i < size_x; i++ )
//     {
// 	for( int j=0; j < size_y; j++ )
// 	{
// 	    arr[i][j] = (int) 200 * exp( 0 - pow( x_center - i, 2 ) / 10
// 					 - pow( 10 - j, 2 ) / 10 );
// 	}
//     }
// }





wxStaticText * make_title( wxFrame *frame, const char *label, int x, int y,
			   int fontsize, long style, bool shift )
{
    wxPoint title_coords = wxPoint( x,y ) ;
    
    wxStaticText *title = new wxStaticText( frame, 0, label, title_coords,
					    wxDefaultSize, style );
    
    wxFont title_font( fontsize, wxDEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD);
    title->SetFont( title_font );

    // if( shift )
    // {
    // 	int tmpx;
    // 	int tmpy;
    // 	title->GetBestSize( &tmpx, &tmpy );
    // 	wxPoint shift = wxPoint( tmpx / 2, 0 );
    // 	title->Move( title->GetPosition() - shift );
    // }
    
    return title;
}







void MainFrame::init_tabor_text_ctrls()
{

    make_title( this, "Tabor Settings", TABOR_LABEL_X_OFFSET,
		TABOR_TEXT_CTRLS_START_YPOS - TABOR_TITLE_OFFSET, 20 );

    // wxPoint textctrl_positions[ NUM_TABOR_SETTINGS ];

    const char *labels[ NUM_TABOR_SETTINGS + 1 ] =
	{ "num steps",
	  "wminus", "wplus", "wc",
	  "wminus_phase", "wplus_phase", "wc_phase",
	  "wminus_amp", "wplus_amp", "wc_amp",
	  "wminus_loops", "wplus_loops", "wc_loops",
	  "wminus_length", "wplus_length", "wc_length",
	  "time acc" 
	};

    const char *default_vals[ NUM_TABOR_SETTINGS + 1 ] =
	{
	    "1",
	    "2", "3", "4",
	    "5", "6", "7",
	    "8", "9", "10",
	    "11", "12", "13",
	    "14", "15", "16",
	    "17"
	};

    // 0->int, 1->double
    const int validator_types[ NUM_TABOR_SETTINGS + 1 ] =
	{
	    0,
	    1, 1, 1,
	    1, 1, 1,
	    1, 1, 1,
	    0, 0, 0,
	    1, 1, 1,
	    1
	};

    const double upper_bounds[ NUM_TABOR_SETTINGS + 1 ] =
	{
	    100,
	    1e8, 1e8, 1e8,
	    360, 360, 360,
	    100, 100, 100,
	    100, 100, 100,
	    100, 100, 100,
	    100
	};
    
    for( int i = 0; i < NUM_TABOR_SETTINGS; i++ )
    {
	wxPoint text_ctrl_position = wxPoint( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP,
					      TABOR_TEXT_CTRLS_START_YPOS
					      + (i+1) * TABOR_TEXT_CTRLS_YPOS_DELTA ) ;
	
	wxPoint label_position = wxPoint( TABOR_LABEL_X_OFFSET,
					  TABOR_TEXT_CTRLS_START_YPOS
					  + (i+1) * TABOR_TEXT_CTRLS_YPOS_DELTA ) ;
	
	new wxStaticText( this, 0, labels[i], label_position ) ;

	if( validator_types[i] == 0 )
	{	    
	    wxIntegerValidator<signed char> int_validator;
	    int_validator.SetRange( 0, upper_bounds[i] );
	    this->tabor_text_ctrls[i] = new wxTextCtrl( this, 0, default_vals[i], text_ctrl_position,
							wxDefaultSize, 0, int_validator );

	}
	else
	{
	    wxFloatingPointValidator<signed char> int_validator;
	    int_validator.SetRange( 0, upper_bounds[i] );
	    this->tabor_text_ctrls[i] = new wxTextCtrl( this, 0, default_vals[i], text_ctrl_position,
							wxDefaultSize, 0, int_validator );
	}
    }
    
}





void MainFrame::init_tdc_labels()
{
    // int xcoord = (int) ( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP ) / 2;

    int xcoord = TABOR_LABEL_X_OFFSET;
    int ycoord = TDC_LABELS_Y_OFFSET + TABOR_TITLE_OFFSET ;
    
    make_title( this,  "TDC Info", xcoord, ycoord - TDC_TITLE_OFFSET, TITLE_FONTSIZE );

    const int x_label = TABOR_LABEL_X_OFFSET;
    const int x_data = TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP;
    
    int y = TDC_LABELS_Y_OFFSET + 2 * TABOR_TITLE_OFFSET;
    
    this->tdc_state_label = new wxStaticText( this, 0, "", wxPoint( x_label, y ) );
    this->update_tdc_state_label();
    y += TDC_LABELS_Y_DELTA;
    
    wxStaticText **static_texts[ NUM_TDC_LABELS + 1 ] =
	{
	    &( this->tdc_success_counts ),
	    &( this->tdc_success_rate ),
	    &( this->tdc_fail_counts )
	};

    const char *labels[ NUM_TDC_LABELS + 1 ] =
	{
	    "Counts",
	    "Count Rate (Hz)",
	    "Invalid Counts"
	};
    
    for( int i=0; i < NUM_TDC_LABELS; i++ )
    {	
	new wxStaticText( this, 0, labels[i], wxPoint( x_label, y ) );
	*(static_texts[i]) = new wxStaticText( this, 0, "", wxPoint( x_data, y ) );
	y += TDC_LABELS_Y_DELTA;
    }
}




void MainFrame::init_output_controls()
{
    
    const int x = OUTPUT_CONTROLS_X ; 
    int y = OUTPUT_CONTROLS_Y;
    
    make_title( this, "Output", x, y, 20 );
    y += OUTPUT_CONTROLS_SEP;

    char abs_path[ PATH_MAX + 1 ];
    get_abs_path( "../output/", abs_path );
    //cout << abs_path << endl;
    
    this->output_dir_picker = new wxDirPickerCtrl( this, wxID_ANY, wxString( abs_path ) + "/",
						   "Choose Directory for Data Output",
						   wxPoint( x, y ),
						   wxDefaultSize );
    wxToolTip *tooltip = new wxToolTip( "output directory" );
    output_dir_picker->SetToolTip( tooltip );
    y += OUTPUT_CONTROLS_SEP;

    this->session_name_text_ctrl = new wxTextCtrl( this, wxID_ANY, "133Cs",
						   wxPoint( x, y ), wxSize( 100, 20 ) );
    
    tooltip = new wxToolTip( "Session Name" );
    session_name_text_ctrl->SetToolTip( tooltip );
    y += OUTPUT_CONTROLS_SEP;

    this->data_description_text_ctrl = new wxTextCtrl( this, wxID_ANY, "",
						       wxPoint( x, y ), wxSize( 100, 20 ) );
    
    tooltip = new wxToolTip( "Data Description" );
    data_description_text_ctrl->SetToolTip( tooltip );
    y += OUTPUT_CONTROLS_SEP;

    this->time_in_trap_text_ctrl = new wxTextCtrl( this, wxID_ANY, "260ms",
						       wxPoint( x, y ), wxSize( 100, 20 ) );
    
    tooltip = new wxToolTip( "Time in Trap" );
    time_in_trap_text_ctrl->SetToolTip( tooltip );
    y += OUTPUT_CONTROLS_SEP;
    
    this->description_text_ctrl = new wxTextCtrl( this, wxID_ANY,
						  "Name: \nDate: \nIsobar: \nNotes: ",
						  wxPoint( x, y ), wxSize( 300, 140 ),
						  wxTE_MULTILINE );
}



void tdc_thread_main()
{
    // tdc.start();
    while(1)
    {
	mySleep( SLEEP_TIME_MS );
	tdc->read();
	tdc->process_hit_buffer();
    }
}






void initControlButtons( wxFrame *frame, ControlButtons control_buttons )
{

    const int num_buttons = 5;

    char button_labels[ num_buttons ][ 64 ] =
	{
	    "Save",
	    "Save and Run Next",
	    "Pause",
	    "Load Tabor",
	    "Reset"
	};
    
    int button_ids[ num_buttons ] =
	{
	    SAVE_BUTTON_ID,
	    SAVE_AND_RUN_NEXT_BUTTON_ID,
	    START_PAUSE_TOGGLE_BUTTON_ID,
	    LOAD_TABOR_BUTTON_ID,
	    RESET_BUTTON_ID
	};
    
    const int x_offset = CONTROL_BUTTONS_X_START ;
    const wxSize size( CONTROL_BUTTONS_WIDTH, CONTROL_BUTTONS_HEIGHT );
    const wxFont font( wxFontInfo( BUTTON_FONTSIZE ) );

    int y_offset = TABOR_TEXT_CTRLS_START_YPOS;

    
    make_title( frame,  "Actions", x_offset, y_offset - TITLE_OFFSET, TITLE_FONTSIZE );
    
    y_offset += CONTROL_BUTTONS_Y_DELTA;
    
    //wxBoxSizer *sizer = new wxBoxSizer( wxVERTICAL );
    
    for( int i=0; i<num_buttons; i++ )
    {
	wxPoint pos( x_offset, y_offset );
    
	wxButton *button = new wxButton( frame, button_ids[i], button_labels[i], pos ); //, size );
	//button->SetFont( font );

	// sizer->Add( button );

	y_offset += CONTROL_BUTTONS_Y_DELTA;
	 
	// //const wxSize size = button->GetBestSize ();
// 	// button->SetSize( size );
// 	wxSizer* sizer = new wxBoxSizer( wxHORIZONTAL );
// 	sizer->Add( button, 1, wxEXPAND, 0 );
// //	sizer->SetAutoLayout(true);
// 	frame->SetSizer(sizer);
    }
}








void MainFrame::save_button_action( wxCommandEvent &event )
{
    TaborSettings tabor_settings = this->read_tabor_settings();
    
    string dir_path = this->output_dir_picker->GetPath().ToStdString();
    string session_name = this->session_name_text_ctrl->GetValue().ToStdString();
    string data_description = this->data_description_text_ctrl->GetValue().ToStdString();
    string description = this->description_text_ctrl->GetValue().ToStdString();
    string time_in_trap = this->time_in_trap_text_ctrl->GetValue().ToStdString();
    
    string tacc;
    if( tabor_settings.tacc == 0 )
	tacc = string( "ref" );
    else
	tacc = to_string( tabor_settings.tacc );

    time_t current_time = time(0);
    char timebuf[128];
    strftime( timebuf, 128, "%Y-%m-%d", localtime( & current_time ) );
    string date_str = string( timebuf );
        
    string session_key = session_name + "_" + tacc + "mswc_" + date_str
	+ "_" + time_in_trap;

    if( ! data_description.empty() )
	session_key += "_" + data_description;
    
    ofstream description_file;
    description_file.open( dir_path + "/description.txt", ios::out );
    description_file << description;
    description_file.close();
    
    tdc->write_data( dir_path, session_key );
        
    string plot_path = dir_path + "/" + session_key + "_plot.jpg" ;    
    this->save_screenshot( plot_path );
}



void MainFrame::save_and_run_next_button_action( wxCommandEvent &event )
{
    cout << "test" << endl;
}




void MainFrame::start_pause_toggle_button_action( wxCommandEvent &event )
{
    if( tdc->collecting_data )
    {
	tdc->pause();
	// wxFont title_font( fontsize, wxDEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD);
	//title->SetFont( title_font );
	//this->tdc_state_label->SetFont( 
    }
    else
	tdc->resume();

    this->update_tdc_state_label();
}





void MainFrame::update_tdc_labels()
{
    tdc_success_counts->SetLabel( to_string( tdc->num_processed_data ) );
    //tdc_success_rate.SetLabel( 
}





void MainFrame::update_tdc_state_label()
{
    if( tdc->collecting_data )
    {
	this->tdc_state_label->SetLabel( "Collecting Data" );
	this->tdc_state_label->SetForegroundColour( wxColour( 0, 200,0 ));
    }
    else
    {
	this->tdc_state_label->SetLabel( "Data Collection Paused" );
	this->tdc_state_label->SetForegroundColour( wxColour( 255, 0,0 ));
    }
}




void MainFrame::load_tabor_button_action( wxCommandEvent &event )
{
    cout << "test" << endl;
    //load_tabor();
}






void MainFrame::reset_button_action( wxCommandEvent &event )
{
    cout << "INFO: clearing plots." << endl;
    this->heatmap->reset();
    tdc->reset();
    cout << "current_max:  " << heatmap->current_max << endl;
    this->heatmap->needs_update = 1;
    this->heatmap->paintNow();
}





void get_abs_path( const char *rel_path, char buf[] )
{
    // char buf[ PATH_MAX + 1 ];
#ifdef _WIN32
    GetFullPathName( rel_path, MAX_PATH, buf, NULL );
#else
    realpath( rel_path, buf );
#endif
}




void MainFrame::save_screenshot( string path )
{    
    wxWindowDC dcScreen( this->heatmap_panel );

    wxCoord screenWidth, screenHeight;
    this->heatmap_panel->GetSize( &screenWidth, &screenHeight );

    wxBitmap screenshot(screenWidth, screenHeight,-1);

    wxMemoryDC memDC;
    memDC.SelectObject(screenshot);
    memDC.Blit( 0, //Copy to this X coordinate
		0, //Copy to this Y coordinate
		screenWidth, //Copy this width
		screenHeight, //Copy this height
		&dcScreen, //From where do we copy?
		0, //What's the X offset in the original DC?
		0  //What's the Y offset in the original DC?
	);

    memDC.SelectObject( wxNullBitmap );
    screenshot.SaveFile( path, wxBITMAP_TYPE_JPEG );
}




TaborSettings MainFrame::read_tabor_settings()
{
    TaborSettings settings;

    settings.nsteps = atoi( this->tabor_text_ctrls[ NSTEPS_IDX ]->GetValue() );

    settings.wminus = atoi( this->tabor_text_ctrls[ WMINUS_IDX ]->GetValue() );
    settings.wplus = atoi( this->tabor_text_ctrls[ WPLUS_IDX ]->GetValue() );
    settings.wc = atoi( this->tabor_text_ctrls[ WC_IDX ]->GetValue() );

    settings.wminus_phase = atoi( this->tabor_text_ctrls[ WMINUS_PHASE_IDX ]->GetValue() );
    settings.wplus_phase = atoi( this->tabor_text_ctrls[ WPLUS_PHASE_IDX ]->GetValue() );
    settings.wc_phase = atoi( this->tabor_text_ctrls[ WC_PHASE_IDX ]->GetValue() );

    settings.wminus_amp = atoi( this->tabor_text_ctrls[ WMINUS_AMP_IDX ]->GetValue() );
    settings.wplus_amp = atoi( this->tabor_text_ctrls[ WPLUS_AMP_IDX ]->GetValue() );
    settings.wc_amp = atoi( this->tabor_text_ctrls[ WC_AMP_IDX ]->GetValue() );

    settings.wminus_loops = atoi( this->tabor_text_ctrls[ WMINUS_LOOPS_IDX ]->GetValue() );
    settings.wplus_loops = atoi( this->tabor_text_ctrls[ WPLUS_LOOPS_IDX ]->GetValue() );
    settings.wc_loops = atoi( this->tabor_text_ctrls[ WC_LOOPS_IDX ]->GetValue() );

    settings.wminus_length = atoi( this->tabor_text_ctrls[ WMINUS_LENGTH_IDX ]->GetValue() );
    settings.wplus_length = atoi( this->tabor_text_ctrls[ WPLUS_LENGTH_IDX ]->GetValue() );
    settings.wc_length = atoi( this->tabor_text_ctrls[ WC_LENGTH_IDX ]->GetValue() );

    settings.tacc = atoi( this->tabor_text_ctrls[ TACC_IDX ]->GetValue() );
    
    return settings;
}

IMPLEMENT_APP( MyApp )




#endif 
