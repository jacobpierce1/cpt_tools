#include "constants.h"
// #include <time.h>

#if USE_TDC 

#ifndef TDC_H
#define TDC_H

#include <iostream> 

#include <Windows.h>
//#include <WinBase.h> 
//#include <stdio> 
#include <fstream>

// #include <numeric_limits>

#include <bitset> 



#include "hptdc_driver_3.4.3_x86_c_wrap.h"

using namespace std;


void print_all_params(C_TDC* c_tdc);
void print_TDCInfo(C_TDC* c_tdc);
void test_read(C_TDC *c_tdc);
void test_batch_read(C_TDC *c_tdc);
void test_batch_ReadTDCHit(C_TDC *c_tdc);
void test_batch_Read(C_TDC *c_tdc);




struct TDC_Data
{
    unsigned int counts;
    // clock_t start_time;
    unsigned int filtered_data_counts;
    
};



class TDC_controller
{
public :
	TDC_controller( void );
	~TDC_controller( void );

	C_TDC *tdcmgr;
	
	unsigned int num_data_in_hit_buffer;
	unsigned int num_processed_data;
	
	HIT hit_buffer[ TDC_HIT_BUFFER_SIZE ]; 
	double channel_times[6][ TDC_MAX_COUNTS ];
	double mcp_positions[2][ TDC_MAX_COUNTS ];
	
	int read(void);

	// bool TDC::check_rollover( HIT hit );
	// double TDC::check_hit_edge( Hit hit );
	double hit_to_time(HIT hit, int *channel, double *time);
	void process_hit_buffer();
	int reset_channel_times( void );
	int compute_mcp_position( double x1, double x2, double y1, double y2 );

};


#endif 

#endif 