#include "constants.h"

#if USE_GUI

#ifndef GUI_H
#define GUI_H

#include "heatmap.h"
#include <iostream>
#include <wx/wx.h>
#include <chrono>
#include <wx/timer.h>
#include "tabor.h"





#define FRAME_WIDTH 1200
#define FRAME_HEIGHT 800

#define MAIN_TITLE_FONTSIZE 30
#define MAIN_TITLE_Y_OFFSET 10 

#define TITLE_FONTSIZE 20

// #define DEFAULT_MAX_TEXT_FIELD_CHAR 100
// #define DEFAULT_TEXT_FIELD_LENGTH 30
#define TABOR_TEXT_CTRLS_LABEL_SEP 120
#define TABOR_TEXT_CTRLS_START_YPOS 120
#define TABOR_TEXT_CTRLS_YPOS_DELTA 20
#define TABOR_LABEL_X_OFFSET 60
#define TABOR_TITLE_OFFSET 15


#define MCP_PLOT_TITLE_OFFSET 40
#define MCP_PLOT_Y_OFFSET TABOR_TEXT_CTRLS_START_YPOS
#define MCP_PLOT_X_OFFSET 600
#define MCP_PLOT_SIZE 400

#define CONTROL_BUTTONS_X_START 350 // relative to the histogram
#define CONTROL_BUTTONS_Y_DELTA 30
#define CONTROL_BUTTONS_WIDTH 200
#define CONTROL_BUTTONS_HEIGHT 100
#define BUTTON_FONTSIZE 20



#define TDC_LABELS_Y_OFFSET 500 // below start of tabor settings 
#define TDC_LABELS_Y_DELTA 20
#define NUM_TDC_LABELS 3
#define TDC_TITLE_OFFSET 15

#define OUTPUT_CONTROLS_Y TDC_LABELS_Y_OFFSET 
#define OUTPUT_CONTROLS_X CONTROL_BUTTONS_X_START
#define OUTPUT_CONTROLS_SEP 40

class MainFrame;


class MyApp : public wxApp
{
    bool render_loop_on;
    bool OnInit();
    void onIdle(wxIdleEvent& evt);
    MainFrame *main_frame;
    
    
public:
    // void activateRenderLoop(bool on);

  /* public: */
  /*   wxFrame *frame; */
  /*   virtual bool OnInit(); */
};



class MainFrame: public wxFrame // MainFrame is the class for our window,
{
    // It contains the window and all objects in it
public:
    MainFrame( const wxString &title, const wxPoint &pos, const wxSize &size );
    //wxButton *save_button;
    void OnExit( wxCommandEvent& event );

    void save_button_action( wxCommandEvent &event );
    void save_and_run_next_button_action( wxCommandEvent &event );
    void start_pause_toggle_button_action( wxCommandEvent &event );
    void load_tabor_button_action( wxCommandEvent &event );
    void reset_button_action( wxCommandEvent &event );

    void init_tabor_text_ctrls();
    void init_tdc_labels();
    void init_output_controls();
    
    void update_tdc_labels();
    void update_tdc_state_label();

    wxTextCtrl *tabor_text_ctrls[ NUM_TABOR_SETTINGS ];
    Heatmap *heatmap;

    // tdc information
    wxStaticText *tdc_state_label;
    wxStaticText *tdc_success_counts;
    wxStaticText *tdc_success_rate;
    wxStaticText *tdc_fail_counts;

    // output
    wxDirPickerCtrl *output_dir_picker;
    wxTextCtrl *project_name_text_ctrl;
    wxTextCtrl *description_text_ctrl;
    

    DECLARE_EVENT_TABLE()
};


enum
{
    SAVE_BUTTON_ID = wxID_HIGHEST + 1,
    SAVE_AND_RUN_NEXT_BUTTON_ID,
    START_PAUSE_TOGGLE_BUTTON_ID,
    LOAD_TABOR_BUTTON_ID,
    RESET_BUTTON_ID
};






class RenderTimer : public wxTimer
{
    MainFrame *frame;
public:
    RenderTimer( MainFrame *frame );
    void Notify();
    void start();
};


/* class Button : public wxFrame */
/* { */
/* public: */
/*     Button(const wxString& title); */

/*     void OnQuit(wxCommandEvent & event); */
/* }; */







/* struct TaborCtrls */
/* { */
/*     /\* enum *\/ */
/*     /\* { *\/ */
/*     /\* 	NSTEPS_ID = wxID_MAX + 100, *\/ */
/*     /\* 	WMINUS_ID, *\/ */
/*     /\* 	WPLUS_ID, *\/ */
/*     /\* 	WC_ID, *\/ */
/*     /\* 	WMINUS_PHASE_ID, *\/ */
/*     /\* 	WPLUS_PHASE_ID, *\/ */
/*     /\* 	WC_PHASE_ID, *\/ */
/*     /\* 	WMINUS_AMP_ID, *\/ */
/*     /\* 	WPLUS_AMP_ID, *\/ */
/*     /\* 	WC_AMP_ID, *\/ */
/*     /\* 	WMINUS_LOOPS_ID, *\/ */
/*     /\* 	WPLUS_LOOPS_ID, *\/ */
/*     /\* 	WC_LOOPS_ID, *\/ */
/*     /\* 	WMINUS_LENGTH_ID, *\/ */
/*     /\* 	WPLUS_LENGTH_ID, *\/ */
/*     /\* 	WC_LENGTH_ID, *\/ */
/*     /\* 	TACC_ID *\/ */
/*     /\* }; *\/ */

    
/*     const int num_text_ctrls; */
    
/*     wxTextCtrl *text_ctrls[ num_text_ctrls ]; */

    
/*     char labels[ NUM_TABOR_SETTINGS ][ 64 ]; = */
/* 	{ "num steps", "wminus", "wplus", */
/* 	  "wminus_phase", "wplus_phase", "wc_phase", */
/* 	  "wminus_amp", "wplus_amp", "wc_amp", */
/* 	  "wminus_loops", "wplus_loops", "wc_loops", */
/* 	  "wminus_length", "wplus_length", "wc_length", */
/* 	  "time acc"  */
/* 	}; */
    
/* } tabor_ctrls; */

/* tabor_ctrls.num_text_ctrls = 17; */
/* tabor_ctrls.labels =  */


/* struct TDCDataGui */
/* { */
/*     wxStaticText *tdc_state_label; */
/*     wxStaticText *counts; */
/*     wxStaticText *count_rate; */
/*     wxStaticText *filtered_event_counts; */
/* }; */




struct ControlButtons
{
    wxButton *save_button;
    wxButton *save_and_run_next_button;
    wxButton *start_pause_toggle_button;
    wxButton *reload_caribu_config_button;
    wxButton *reset_button;
    
	
// wxButton *tmp;
};

/* struct MCPPlot */
/* { */
    
/* }; */








/* class Gui */
/* { */
/* public : */
/*     TaborTextCtrls tabor_text_ctrls; */
/*     ControlButtons control_buttons; */
/*     TDCDataGui TDC_data_gui; */

    
/*     // pointers to corresponding array / int in TDC if it exists, */
/*     // otherwise NULL */
/*     double *mcp_positions[2][ TDC_MAX_COUNTS ]; */
/*     int *num_processed_data_ptr; */

/*     void update( void ); */
/*     void main_loop( void ); */
/* }; */










void initControlButtons( wxFrame *frame, ControlButtons control_buttons ) ;

wxStaticText * make_title( wxFrame *frame, const char *label, int x, int y,
			   int fontsize, long style = 0, bool shift = 0 );

template <size_t size_x, size_t size_y>
void func( int (&arr)[size_x][size_y]);


void tdc_thread_main( );

void reset();



#endif // GUI_H 

#endif
