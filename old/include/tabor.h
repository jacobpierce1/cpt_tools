#ifndef TABOR_H
#define TABOR_H


#define NUM_TABOR_SETTINGS 17

struct TaborSettings
{
TaborSettings() : nsteps(5),
	wminus( 1600.0 ), wplus( 656252.0 ), wc( 656252.0 ),
	wminus_phase( 140.0 ), wplus_phase(0.0), wc_phase(0.0),
	wminus_amp(0.0005), wplus_amp(0.2), wc_amp(0.5),
	wminus_loops(1), wplus_loops(100), wc_loops(208),
	wminus_length(3), wplus_length(1), wc_length(1),
	tacc( 68 ) {}
		
    int nsteps; //  1 or 2 = wminus only, 3 or 4 = wminus + wplus, 5 = everything

    double wminus;
    double wplus; 
    double wc;
        
    double wminus_phase;// -110.0;// 30.0;
    double wplus_phase;
    double wc_phase;

    double wminus_amp;// 0.0035;// 0.003;//0.0045;// 0.0075
    double wplus_amp;//0.22;  //0.11
    double wc_amp;
    
    int wminus_loops; // don't change
    int wplus_loops;// 133Cs = 100;
    int wc_loops;// 212;// 133Cs = 210
    
    int wminus_length;// 3 ; // 2
    int wplus_length;
    int wc_length; // don't change
    
    int tacc;// 220040;// 234075; // 240023;// 250063; // 190318;// 148010;// 60008 18500; // time in us
//int tacc 55.21	// Load three arbitrary waveforms consecutively on all channels
};



int load_tabor( TaborSettings settings );


#endif
