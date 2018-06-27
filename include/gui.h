#include "constants.h"

#if USE_GUI

#ifndef GUI_H
#define GUI_H


#include "constants.h" 
#include <iostream>
#include <wx/wx.h>
#include <chrono>

#define FRAME_WIDTH 1200
#define FRAME_HEIGHT 800

#define MAIN_TITLE_FONTSIZE 30
#define MAIN_TITLE_Y_OFFSET 10 

#define TITLE_FONTSIZE 20

// #define DEFAULT_MAX_TEXT_FIELD_CHAR 100
// #define DEFAULT_TEXT_FIELD_LENGTH 30
#define TABOR_TEXT_CTRLS_LABEL_SEP 120
#define TABOR_TEXT_CTRLS_START_YPOS 100
#define TABOR_TEXT_CTRLS_YPOS_DELTA 20
#define TABOR_LABEL_X_OFFSET 60
#define TABOR_TITLE_OFFSET 40


#define TDC_LABELS_Y_OFFSET 420 // below start of tabor settings 

#define MCP_PLOT_TITLE_OFFSET 40
#define MCP_PLOT_Y_OFFSET 100 
#define MCP_PLOT_X_OFFSET 400
#define MCP_PLOT_SIZE 400

#define CONTROL_BUTTONS_X_START 1000 // relative to the histogram
#define CONTROL_BUTTONS_Y_DELTA 40




class MyApp : public wxApp
{
  public:
    wxFrame *frame;
    virtual bool OnInit();
};




/* class Button : public wxFrame */
/* { */
/* public: */
/*     Button(const wxString& title); */

/*     void OnQuit(wxCommandEvent & event); */
/* }; */



struct TaborTextCtrls
{
    wxTextCtrl *nsteps; //  1 or 2 = wminus only, 3 or 4 = wminus + wplus, 5 = everything

    wxTextCtrl *wminus;
    double wplus; // 130In //646445.9 135Te// 150Ce 1164702.5; // 1118649.8;// // //133Cs = 656250.0 //142Cs = 614447.6
// double wc = 657844.5; //130I648038.4 135Te // 150Ce 1166293.3; // 1120240.8;//1797579.0;// 1181999.3;// 1121410.2;// 130In = 672935.5; // 616040.4; // 657844.5;// 133Cs = 657844.5; //// 142Cs = 616040.4

    wxTextCtrl *wminus_phase;// -110.0;// 30.0;
    wxTextCtrl *wplus_phase;
    wxTextCtrl *wc_phase;

    wxTextCtrl *wminus_amp;// 0.0035;// 0.003;//0.0045;// 0.0075
    wxTextCtrl *wplus_amp;//0.22;  //0.11
    wxTextCtrl *wc_amp;
    
    wxTextCtrl *wminus_loops; // don't change
    wxTextCtrl *wplus_loops;// 133Cs = 100;
    wxTextCtrl *wc_loops;// 212;// 133Cs = 210
    
    wxTextCtrl * wminus_length;// 3 ; // 2
    wxTextCtrl *wplus_length;
    wxTextCtrl *wc_length; // don't change
    
    wxTextCtrl *tacc;// 220040;// 234075; // 60008 18500; // time in us
};



struct TDCDataGui
{
    wxStaticText *counts;
    wxStaticText *count_rate;
    wxStaticText *filtered_event_counts;
};




struct ControlButtons
{
    wxButton *save_button;
    wxButton *save_and_run_next_button;
    wxButton *start_pause_toggle_button;
    wxButton *reload_caribu_config_button;
    // wxButton *tmp;
};

/* struct MCPPlot */
/* { */
    
/* }; */








class Gui
{
public :
    TaborTextCtrls tabor_text_ctrls;
    ControlButtons control_buttons;
    TDCDataGui TDC_data_gui;

    
    // pointers to corresponding array / int in TDC if it exists,
    // otherwise NULL
    double *mcp_positions[2][ TDC_MAX_COUNTS ];
    int *num_processed_data_ptr;

    void update( void );
    void main_loop( void );
};





#endif // GUI_H 

#endif
