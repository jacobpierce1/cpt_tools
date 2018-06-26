#if USE_GUI

#ifdef _WIN32
#include "stdafx.h"
#endif

#include <iostream>
#include "gui.h"
#include <wx/valnum.h>
#include "tabor.h"
#include "mathplot.h"


using namespace std;

void initTaborTextCtrls( wxFrame *frame, TaborTextCtrls *tabor_text_ctrls );

void initTDCLabels( wxFrame *frame, TDCDataGui *tdc_data_gui );
//void mpFXYVector::AddData(float x, float y, std::vector<double> &xs, std::vector<double> &ys);


void initControlButtons( wxFrame *frame, ControlButtons control_buttons ) ;

wxStaticText * make_title( wxFrame *frame, const char *label, int x, int y,
			   int fontsize, long style = 0 );
    
IMPLEMENT_APP(MyApp)




class MyLissajoux : public mpFXY
{
    double m_rad;
    int    m_idx;
public:
    MyLissajoux(double rad) : mpFXY( wxT("Lissajoux")) { m_rad=rad; m_idx=0; m_drawOutsideMargins = false;}
    virtual bool GetNextXY( double & x, double & y )
	{
	    if (m_idx < 360)
	    {
		x = m_rad * cos(m_idx / 6.283185*360);
		y = m_rad * sin(m_idx / 6.283185*360*3);
		m_idx++;
		return TRUE;
	    }
	    else
	    {
		return FALSE;
	    }
	}
    virtual void Rewind() { m_idx=0; }
    virtual double GetMinX() { return -m_rad; }
    virtual double GetMaxX() { return  m_rad; }
    virtual double GetMinY() { return -m_rad; }
    virtual double GetMaxY() { return  m_rad; }
};



// MyFrame::MyFrame()
//     : wxFrame(NULL, wxID_ANY, "CPT Master Controller")
// {
//     // wxMenu *menuFile = new wxMenu;
//     // menuFile->Append(ID_Hello, "&Hello...\tCtrl-H",
//     //                  "Help string shown in status bar for this menu item");
//     // menuFile->AppendSeparator();
//     // menuFile->Append(wxID_EXIT);
//     // wxMenu *menuHelp = new wxMenu;
//     // menuHelp->Append(wxID_ABOUT);
//     // wxMenuBar *menuBar = new wxMenuBar;
//     // menuBar->Append(menuFile, "&File");
//     // menuBar->Append(menuHelp, "&Help");
//     // SetMenuBar( menuBar );
//     // CreateStatusBar();
//     // SetStatusText("Welcome to wxWidgets!");
//     // Bind(wxEVT_MENU, &MyFrame::OnHello, this, ID_Hello);
//     // Bind(wxEVT_MENU, &MyFrame::OnAbout, this, wxID_ABOUT);
//     // Bind(wxEVT_MENU, &MyFrame::OnExit, this, wxID_EXIT);
// }



bool MyApp::OnInit()
{
    wxFrame *frame = new wxFrame(NULL, wxID_ANY, "CPT Master Controller",
				 wxDefaultPosition,
				 wxSize( FRAME_WIDTH, FRAME_HEIGHT  ) );
    frame->Show(true);

    make_title( frame, "CPT Master Controller",
		FRAME_WIDTH / 2,
		MAIN_TITLE_Y_OFFSET,
		MAIN_TITLE_FONTSIZE, wxALIGN_RIGHT );
	

    TaborTextCtrls tabor_text_ctrls;
    initTaborTextCtrls( frame, &tabor_text_ctrls ) ;

    TDCDataGui tdc_data_gui;
    initTDCLabels( frame, &tdc_data_gui ) ;

    ControlButtons control_buttons;
    initControlButtons( frame, control_buttons );


    
    make_title( frame, "MCP Hits",
		MCP_PLOT_X_OFFSET + MCP_PLOT_SIZE / 2,
		MCP_PLOT_Y_OFFSET - MCP_PLOT_TITLE_OFFSET,
		TITLE_FONTSIZE, wxALIGN_RIGHT );
    
    // MCPPlot mcp_plot;
    // initMCPPlot( frame, &mcp_plot );


    // mpFXYVector *m_Vector = new mpFXYVector();
    // mpWindow *m_plot = new mpWindow( frame, 0, wxPoint( 400, 100 ),
    // 				    wxSize( 400, 400 ) );
    // // mpLayer *layer = &mpFXY
    // m_Vector->SetVisible( true ) ;
    
    // vector<double> vectorX;
    // vector<double> vectorY;
    // double xpos = 1.0;
    // double ypos = 2.0;
    
    // m_Vector->AddData( xpos, ypos, vectorX, vectorY);

    // m_plot->AddLayer( m_Vector );
    
    // m_plot->Fit();

    mpInfoCoords *nfo; // mpInfoLayer* nfo;
    
    mpLayer* l;

    // Create a mpFXYVector layer
    mpFXYVector* vectorLayer = new mpFXYVector(_("Vector"));
    // Create two vectors for x,y and fill them with data
    std::vector<double> vectorx, vectory;
    double xcoord;
    for (unsigned int p = 0; p < 100; p++) {
	xcoord = ((double)p-50.0)*5.0;
	vectorx.push_back(xcoord);
	vectory.push_back(0.0001*pow(xcoord, 3));
    }
    vectorLayer->SetData(vectorx, vectory);
    vectorLayer->SetContinuity(true);
    wxPen vectorpen(*wxBLUE, 2, wxSOLID);
    vectorLayer->SetPen(vectorpen);
    vectorLayer->SetDrawOutsideMargins(false);


    wxFont graphFont(11, wxFONTFAMILY_DEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_NORMAL);
    mpWindow *m_plot = new mpWindow( frame, -1,
				     wxPoint( MCP_PLOT_X_OFFSET, MCP_PLOT_Y_OFFSET ),
				     wxSize( MCP_PLOT_SIZE, MCP_PLOT_SIZE ),
				     wxSUNKEN_BORDER );
	
    mpScaleX* xaxis = new mpScaleX(wxT("X"), mpALIGN_BOTTOM, true, mpX_NORMAL);
    mpScaleY* yaxis = new mpScaleY(wxT("Y"), mpALIGN_LEFT, true);
    xaxis->SetFont(graphFont);
    yaxis->SetFont(graphFont);
    xaxis->SetDrawOutsideMargins(false);
    yaxis->SetDrawOutsideMargins(false);
    // Fake axes formatting to test arbitrary format string
    // xaxis->SetLabelFormat(wxT("%.2f €"));
    // yaxis->SetLabelFormat(wxT("%p"));
    m_plot->SetMargins(30, 30, 50, 100);
//     m_plot->SetMargins(50, 50, 200, 150);
    m_plot->AddLayer(     xaxis );
    m_plot->AddLayer(     yaxis );
    // m_plot->AddLayer(     new MySIN( 10.0, 220.0 ) );
    // m_plot->AddLayer(     new MyCOSinverse( 10.0, 100.0 ) );
    m_plot->AddLayer( l = new MyLissajoux( 125.0 ) );
    m_plot->AddLayer(     vectorLayer );
    m_plot->AddLayer(     new mpText(wxT("mpText sample"), 10, 10) );
    wxBrush hatch(wxColour(200,200,200), wxSOLID);
    //m_plot->AddLayer( nfo = new mpInfoLayer(wxRect(80,20,40,40), &hatch));
    m_plot->AddLayer( nfo = new mpInfoCoords(wxRect(80,20,10,10), wxTRANSPARENT_BRUSH)); //&hatch));
    nfo->SetVisible(false);
    wxBrush hatch2(wxColour(163,208,212), wxSOLID);
    mpInfoLegend* leg;
    m_plot->AddLayer( leg = new mpInfoLegend(wxRect(200,20,40,40), wxTRANSPARENT_BRUSH)); //&hatch2));
    leg->SetVisible(true);
    
    // m_plot->EnableCoordTooltip(true);
    // set a nice pen for the lissajoux
    wxPen mypen(*wxRED, 5, wxSOLID);
    l->SetPen( mypen);

    // m_log = new wxTextCtrl( this, -1, wxT("This is the log window.\n"), wxPoint(0,0), wxSize(100,100), wxTE_MULTILINE );
    // wxLog *old_log = wxLog::SetActiveTarget( new wxLogTextCtrl( m_log ) );
    // delete old_log;
    
    wxBoxSizer *topsizer = new wxBoxSizer( wxVERTICAL );

    // topsizer->Add( m_plot, 1, wxEXPAND );
    // // topsizer->Add( m_log, 0, wxEXPAND );

    // SetAutoLayout( TRUE );
    // SetSizer( topsizer );
    // axesPos[0] = 0;
    // axesPos[1] = 0;
    // ticks = true;

    m_plot->EnableDoubleBuffer(true);
    m_plot->SetMPScrollbars(false);
    m_plot->Fit();
    
    return true;
}



wxStaticText * make_title( wxFrame *frame, const char *label, int x, int y,
			   int fontsize, long style )
{
    wxPoint title_coords = wxPoint( x,y ) ;
    
    wxStaticText *title = new wxStaticText( frame, 0, label, title_coords,
					    wxDefaultSize, style );
    
    wxFont title_font( fontsize, wxDEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD);
    title->SetFont( title_font );

    wxSize size = title->GetSize();

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



void mpFXYVector::AddData(float x, float y, std::vector<double> &xs, std::vector<double> &ys)
{
    // Check if the data vectora are of the same size
    if (xs.size() != ys.size()) {
	wxLogError(_("wxMathPlot error: X and Y vector are not of the same length!"));
	return;
    }

    //Delete first point if you need a filo buffer (i dont need it)
    //xs.erase(xs.begin());
    //xy.erase(xy.begin());

    //Add new Data points at the end
    xs.push_back(x);
    ys.push_back(y);


    // Copy the data:
    m_xs = xs;
    m_ys = ys;

    // Update internal variables for the bounding box.
    if (xs.size()>0)
    {
	m_minX  = xs[0];
	m_maxX  = xs[0];
	m_minY  = ys[0];
	m_maxY  = ys[0];

	std::vector<double>::const_iterator  it;

	for (it=xs.begin();it!=xs.end();it++)
	{
	    if (*it<m_minX) m_minX=*it;
	    if (*it>m_maxX) m_maxX=*it;
	}
	for (it=ys.begin();it!=ys.end();it++)
	{
	    if (*it<m_minY) m_minY=*it;
	    if (*it>m_maxY) m_maxY=*it;
	}
	m_minX-=0.5f;
	m_minY-=0.5f;
	m_maxX+=0.5f;
	m_maxY+=0.5f;
    }
    else
    {
	m_minX  = -1;
	m_maxX  = 1;
	m_minY  = -1;
	m_maxY  = 1;
    }
}


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

// void Gui::main_loop( void )
// {

// }

// void Gui::update( void )
// {
    

// }




// Gui::Gui( void )
// {
   
// }




// // tabor part of GUI






#endif 
