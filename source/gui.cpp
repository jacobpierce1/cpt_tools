#include <iostream>
#include "gui.h"
#include <wx/valnum.h>
#include "tabor.h"
#include "mathplot.h"


using namespace std;

void initTaborTextCtrls( wxFrame *frame, TaborTextCtrls *tabor_text_ctrls );

void initTDCLabels( TDCDataGui *tdc_data_gui, wxFrame *frame );

    
IMPLEMENT_APP(MyApp)






// class MyFrame : public wxFrame
// {
// public:
//     MyFrame();
// private:
//     void OnHello(wxCommandEvent& event);
//     void OnExit(wxCommandEvent& event);
//     void OnAbout(wxCommandEvent& event);
// };
// enum
// {
//     ID_Hello = 1
// };



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
				 wxDefaultPosition, wxSize( 1200, 800 ) );
    frame->Show(true);

    
    // Button *btnapp = new Button(wxT("Button"));
    // btnapp->Show(true);

    // wxPanel *panel = new wxPanel( frame, wxID_ANY);
    
    wxButton *button = new wxButton(  frame, wxID_EXIT, wxT("Quit"), 
				    wxPoint(20, 20));
    Connect(wxID_EXIT, wxEVT_COMMAND_BUTTON_CLICKED, 
	    wxCommandEventHandler(Button::OnQuit));
    button->SetFocus();
    button->Show();

    TaborTextCtrls tabor_text_ctrls;
    initTaborTextCtrls( frame, &tabor_text_ctrls ) ;

    TDCDataGui tdc_data_gui;
    initTDCLabels( &tdc_data_gui, frame ) ;
        
    return true;
}



void initTaborTextCtrls( wxFrame *frame, TaborTextCtrls *tabor_text_ctrls )
{

    // create title for this section 
    wxPoint title_coords = wxPoint( ( TABOR_LABEL_X_OFFSET + TABOR_TEXT_CTRLS_LABEL_SEP ) / 2,
				    TABOR_TEXT_CTRLS_START_YPOS - TABOR_TITLE_OFFSET ) ;
    wxSize title_size = wxSize( 100, 40 ) ;
    wxStaticText *title = new wxStaticText( frame, 0, "Tabor Settings", title_coords, title_size );
    wxFont title_font( 20, wxDEFAULT, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD);
    title->SetFont( title_font );


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





void initTDCLabels( TDCDataGui *tdc_data_gui, wxFrame *frame )
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



void Button::OnQuit(wxCommandEvent & WXUNUSED(event))
{
    Close(true);
}





// void MyFrame::OnExit(wxCommandEvent& event)
// {
//     Close(true);
// }


// void MyFrame::OnAbout(wxCommandEvent& event)
// {
//     wxMessageBox("This is a wxWidgets Hello World example",
//                  "About Hello World", wxOK | wxICON_INFORMATION);
// }


// void MyFrame::OnHello(wxCommandEvent& event)
// {
//     wxLogMessage("Hello world from wxWidgets!");
// } 






// void Text :: OnEnter( wxCommandEvent & WXUNUSED( event ) )
// {
//     printf( "enter pressed" ) ;
// }




// #include <QApplication>
// #include <QWidget>

// #define RUN_INSTRUMENTS defined( _WIN_32 ) 


// int main(int argc, char *argv[]) {
//     QApplication app(argc, argv);

//     QWidget window;

//     window.resize(250, 150);
//     window.setWindowTitle("Simple example");
//     window.show();

//     return app.exec();
// }








// Gui::init( void )
// {
   
// }




// // tabor part of GUI






// // text field:

// // modifiable

// int nsteps = 5; //  1 or 2 = wminus only, 3 or 4 = wminus + wplus, 5 = everything

// double wminus = 1600.0;
	
// double wplus = 656252.0; // 130In //646445.9 135Te// 150Ce 1164702.5; // 1118649.8;// // //133Cs = 656250.0 //142Cs = 614447.6
// double wc = 657844.5; //130I648038.4 135Te // 150Ce 1166293.3; // 1120240.8;//1797579.0;// 1181999.3;// 1121410.2;// 130In = 672935.5; // 616040.4; // 657844.5;// 133Cs = 657844.5; //// 142Cs = 616040.4

// double wminus_phase = -140.0;// -110.0;// 30.0;
// double wplus_phase = 0.0;
// double wc_phase = 0.0;

// double wminus_amp = 0.0005;// 0.0035;// 0.003;//0.0045;// 0.0075
// double wplus_amp = 0.2;//0.22;  //0.11
// double wc_amp = 0.5;

// int wminus_loops = 1; // don't change
// int wplus_loops = 100;// 133Cs = 100;
// int wc_loops = 208;// 212;// 133Cs = 210
	 
// int wminus_length = 3;// 3 ; // 2
// int wplus_length = 1;
// int wc_length = 1; // don't change

// int tacc = 68;// 220040;// 234075; // 240023;// 250063; // 190318;// 148010;// 60008 18500; // time in us
// //int tacc 55.21	// Load three arbitrary waveforms consecutively on all channels

// // modifiable<
