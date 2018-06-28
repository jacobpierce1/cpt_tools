#include "constants.h"
// #include <time.h>


#ifndef TDC_H
#define TDC_H

#include "global.h"
#include <iostream> 
#include <fstream>
#include <bitset> 


#define X1_CHANNEL 0
#define X2_CHANNEL 1
#define Y1_CHANNEL 2
#define Y2_CHANNEL 3
#define TRIGGER_CHANNEL 8

// these are not real channels, but are used to encode info
#define ERROR_CHANNEL -1
#define ROLLOVER_CHANNEL -2
#define EMPTY_CHANNEL -3


#if USE_TDC
#include "hptdc_driver_3.4.3_x86_c_wrap.h"

void print_all_params(C_TDC* c_tdc);
void print_TDCInfo(C_TDC* c_tdc);
void test_read(C_TDC *c_tdc);
void test_batch_read(C_TDC *c_tdc);
void test_batch_ReadTDCHit(C_TDC *c_tdc);
void test_batch_Read(C_TDC *c_tdc);

#endif

typedef unsigned long HIT;

using namespace std;



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

#if USE_TDC
	C_TDC *tdcmgr;
#endif
	
	unsigned int num_data_in_hit_buffer;
	unsigned int num_processed_data;
	// unsigned int num_data_in_
	
	HIT hit_buffer[ TDC_HIT_BUFFER_SIZE ]; 
	long long channel_times[ TDC_MAX_COUNTS ][6];
	double tof[ TDC_MAX_COUNTS ]; 
	double mcp_positions[ TDC_MAX_COUNTS ][2];
	
	int read(void);
	double process_hit(HIT hit, int *channel, long long *time );
	void process_hit_buffer();

	void start();
	void stop();
	void resume();

	void reset_buffers();

	int reset_channel_times( void );
	int compute_tof_and_mcp_pos( double mcp_pos[2], double *tof_ptr,
				     long long x1, long long x2,
				     long long y1, long long y2,
				     long long t );
	
	int write_data( const char *path );
};


#endif 

