#include <iostream>
#include "gui.h"



Gui::init( void )
{
   
}




// tabor part of GUI






// text field:

// modifiable

int nsteps = 5; //  1 or 2 = wminus only, 3 or 4 = wminus + wplus, 5 = everything

double wminus = 1600.0;
	
double wplus = 656252.0; // 130In //646445.9 135Te// 150Ce 1164702.5; // 1118649.8;// // //133Cs = 656250.0 //142Cs = 614447.6
double wc = 657844.5; //130I648038.4 135Te // 150Ce 1166293.3; // 1120240.8;//1797579.0;// 1181999.3;// 1121410.2;// 130In = 672935.5; // 616040.4; // 657844.5;// 133Cs = 657844.5; //// 142Cs = 616040.4

double wminus_phase = -140.0;// -110.0;// 30.0;
double wplus_phase = 0.0;
double wc_phase = 0.0;

double wminus_amp = 0.0005;// 0.0035;// 0.003;//0.0045;// 0.0075
double wplus_amp = 0.2;//0.22;  //0.11
double wc_amp = 0.5;

int wminus_loops = 1; // don't change
int wplus_loops = 100;// 133Cs = 100;
int wc_loops = 208;// 212;// 133Cs = 210
	 
int wminus_length = 3;// 3 ; // 2
int wplus_length = 1;
int wc_length = 1; // don't change

int tacc = 68;// 220040;// 234075; // 240023;// 250063; // 190318;// 148010;// 60008 18500; // time in us
//int tacc 55.21	// Load three arbitrary waveforms consecutively on all channels

// modifiable<
