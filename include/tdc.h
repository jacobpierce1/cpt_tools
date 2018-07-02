#include "constants.h"
// #include <time.h>


#ifndef TDC_H
#define TDC_H

#include "global.h"
#include <iostream> 
#include <fstream>
#include <bitset> 

#define TDC_HIT_BUFFER_SIZE  10000
#define TDC_MAX_COUNTS  100000

#define X1_CHANNEL 0
#define X2_CHANNEL 1
#define Y1_CHANNEL 2
#define Y2_CHANNEL 3
#define TRIGGER_CHANNEL 7

// these are not real channels, but are used to encode info
#define ERROR_CHANNEL -1
#define ROLLOVER_CHANNEL -2
#define EMPTY_CHANNEL -3




#if USE_TDC
#include "hptdc_driver_3.4.3_x86_c_wrap.h"


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

	
// use either actual TDC or a file stream for the data 
#if USE_TDC
	C_TDC *tdcmgr;
#else
	ifstream infile;
#endif
	
	unsigned int num_data_in_hit_buffer;
	unsigned int num_processed_data;

	bool collecting_data;
	
	HIT hit_buffer[ TDC_HIT_BUFFER_SIZE ];
	uint8_t channels[ TDC_MAX_COUNTS ];
	long long channel_times[ TDC_MAX_COUNTS ][6];
	double tof[ TDC_MAX_COUNTS ]; 
	double mcp_positions[ TDC_MAX_COUNTS ][2];
	
	int read(void);
	double process_hit(HIT hit, int *channel, long long *time );
	int process_hit_buffer();

	void start();
	void stop();
	void pause();
	void resume();
	
	void reset_buffers();

	int reset_channel_times( void );
	int compute_tof_and_mcp_pos( double mcp_pos[2], double *tof_ptr,
				     long long x1, long long x2,
				     long long y1, long long y2,
				     long long t );
	
	int write_data( string dir_path, string session_key );

	void reset();
};


#endif 

