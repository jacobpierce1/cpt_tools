#include "stdafx.h"

#include "constants.h"



#include "tdc.h"
#include <cstdlib>
#include <iostream>
#include <bitset> 
#include <string>


using namespace std;


#if USE_TDC 
void print_all_params(C_TDC* c_tdc);
void print_TDCInfo(C_TDC* c_tdc);
void test_read(C_TDC *c_tdc);
void test_batch_read(C_TDC *c_tdc);
void test_batch_ReadTDCHit(C_TDC *c_tdc);
void test_batch_Read(C_TDC *c_tdc);
#endif




#if !( USE_TDC )
#define TDC_SAMPLE_DATA_FILE "../data/sample_tdc_times.txt"
#endif 


const HIT TRANSITION_TIME_MASK = bitset<32>( "00000000111111111111111111111111" ).to_ulong();
//
//const HIT ERROR_COUNT_MASK =     bitset<32>( "00000000000000001111111111111111" ).to_ulong();





#define CHANNEL_SHIFT 24
#define ERROR_MESSAGE_SHIFT 16




TDC_controller::TDC_controller() 
{
#if USE_TDC
    this->tdcmgr = TDCManager_New();

    mySleep(1000);

    TDCManager_Init( this->tdcmgr );
    TDCManager_ClearBuffer( this->tdcmgr );

    this->num_data_in_hit_buffer = 0;
    this->num_processed_data = 0;

    mySleep(1000);
	
    // this->hit_buffer = new 
    //TDCManager_Start( this->tdcmgr );
#else
    this->infile.open( TDC_SAMPLE_DATA_FILE );
#endif
    start();
}




TDC_controller::~TDC_controller()
{
#if USE_TDC
    TDCManager_CleanUp( this->tdcmgr );
    TDCManager_Delete( this->tdcmgr );
#else
    this->infile.close();
#endif
}



int TDC_controller::read()
{
#if USE_TDC
    if( collecting_data )
    {
	this->num_data_in_hit_buffer = TDCManager_Read( this->tdcmgr, this->hit_buffer,
							TDC_HIT_BUFFER_SIZE );
	return this->num_data_in_hit_buffer;
    }
#endif
    return 0;
}




void TDC_controller::start()
{
#if USE_TDC
    TDCManager_Start( this->tdcmgr );
#endif
    this->collecting_data = 1;
}



void TDC_controller::stop()
{
#if USE_TDC
    TDCManager_Stop( this->tdcmgr );
#endif
    this->collecting_data = 0;
}



void TDC_controller::pause()
{
#if USE_TDC
    TDCManager_Pause( this->tdcmgr );
#endif
    this->collecting_data = 0;
}



void TDC_controller::resume()
{
#if USE_TDC
    TDCManager_Continue( this->tdcmgr );
#endif
    this->collecting_data = 1;
}



double TDC_controller::process_hit( HIT hit, int *channel, long long *time )
{
    // cout << sizeof( RISING_MASK ) << endl; 
#if USE_TDC
    int edge = -1;
    int error = 0;

    bitset<32> bits = bitset<32>( hit );
	
    // cout << bits << endl;
	
    if( bits[31] && bits[30] )
    {
	// cout << "rising" << endl;
	// edge = 0;
    }
    else if( bits[31] && ! bits[30] )
    {
	// cout << "falling" << endl;
	// edge = 1;
    }
    else if( (! bits[31] ) && bits[30] )
    {
	cout << "error" << endl;
	error = 1;
    }
    else if ( ! ( bits[31] | bits[30] | bits[29] | bits[28] ) )
    {
	cout << "group" << endl;
    }
    else if( ! ( bits[31] | bits[30] | bits[29] ) & bits[28] )
    {
	cout << "rollover" << endl;
    }
    else
    {
	cout << "?" << endl;
    }

    unsigned long tmp = 63;
    bitset<32> mask( tmp );

    *channel = (( bits >> 24 ) & mask).to_ulong();

    *time = TRANSITION_TIME_MASK & hit; 

    cout << "tmpchannel: " << tmpchannel << endl << endl;
    return 0;
#else
    return 0;
#endif
}





// return number of valid data added
int TDC_controller::process_hit_buffer()
{
    if( ! collecting_data )
	return 0;
    
    
    long long times[ TDC_HIT_BUFFER_SIZE ];

    long long valid_times[6];
    int valid_channel_indices_set[6];

    // int first_pass = 1;
    
#if USE_TDC
    int channels[ TDC_HIT_BUFFER_SIZE ];

    // unpack all the data 
    for( int i=0; i < this->num_data_in_hit_buffer; i++ )
    {
	process_hit( hit_buffer[i], &( channels[i] ), &( times[i] ) );
    }
#else
    this->num_data_in_hit_buffer = 6;
    int tmp_channels[ TDC_HIT_BUFFER_SIZE ] = { 7, 0, 1, 2, 3, 6 };
    int channels[ TDC_HIT_BUFFER_SIZE ];
    memset( &channels, -1, TDC_HIT_BUFFER_SIZE * sizeof(int) );

    for( int i=0; i<6; i++ )
    {
	string tmp_str;

	if( this->infile.eof() )
	    break;
	
	getline( this->infile, tmp_str );
	times[i] = stoll( tmp_str );
	channels[i] = tmp_channels[i];
	// cout << times[i] << endl;
    }
#endif

    
    // look for candidate channels for x1, x2, y1, y2
    // int hit_idx = 0;
    int num_data_added = 0;
    int channel_map[9] = { 0, 1, 2, 3, -1, -1, 4, 5, -1 };
    
    // cout << "entering processing loop" << endl;
    
    for( int hit_idx = 0; hit_idx < this->num_data_in_hit_buffer; )
    {	
	// cout << "hit_idx: " << hit_idx << endl;
    
	memset( &valid_channel_indices_set, 0, 6 * sizeof(int) );
	
	// find next trigger channel
	while( hit_idx < this->num_data_in_hit_buffer )
	{
	    // cout << "searching for trigger_channel... " << channels[ hit_idx ] << endl;
	    if( channels[ hit_idx ] == TRIGGER_CHANNEL )
	    {
		// intentionally don't increment hit_idx before breaking
		// so that the trigger channel is processed in the next loop
		// cout << "found trigger on idx " << hit_idx << endl;
		break; 
	    }
	    hit_idx++;
	}

	
	// keep processing while there is data left and data is still valid
	// ideally, this will only be 5 more data points if there are
	// no rollovers or extra hits on the same channel
	
	int valid_data = 1;

	while( hit_idx < this->num_data_in_hit_buffer && valid_data )
	{
	    // cout << "found trigger. hit_idx: " << hit_idx << endl; 
	    int channel = channels[ hit_idx ];
	    int idx = channel_map[ channel ];

	    // cout << "channel / idx: " << channel << " "  << idx << endl;

	    if( valid_channel_indices_set[ idx ] )
	    {
		cout << "duplicate hit detected" << endl;
		valid_data = 0;
	    }
	    else
	    {
		valid_channel_indices_set[ idx ] = 1;
		valid_times[ idx ] = times[ hit_idx ];
	    }
	    hit_idx++;
	}
	
	// verify that all channels were detected
	for( int i = 0; i<6; i++ )
	{
	    // cout << "valid_channel_indices_set[i]" << i << " " << valid_channel_indices_set[ i ] << endl;
	    valid_data &= valid_channel_indices_set[ i ];
	}

	if( ! valid_data )
	{
	    cout << "not all channels were set" << endl;
	}
	else{
	    int data_idx = this->num_processed_data;

	    long long x1 = valid_times[0];
	    long long x2 = valid_times[1];
	    long long y1 = valid_times[2];
	    long long y2 = valid_times[3];
	    long long t = valid_times[4];
	    
	    compute_tof_and_mcp_pos( this->mcp_positions[ data_idx ],
				     &( this->tof[ data_idx ] ),
				     x1, x2, y1, y2, t );

	    ++( this->num_processed_data );
	}
		
    }
    
    this->num_data_in_hit_buffer = 0;
    return num_data_added;
}



void TDC_controller::reset_buffers()
{
    this->num_data_in_hit_buffer = 0;
    this->num_processed_data = 0;
}




int TDC_controller::write_data( string dir_path, string session_key )
{
    ofstream channel_file;
    channel_file.open( dir_path + "/" + session_key + "_channels.bin",
		       ios::out | ios::binary );
    channel_file.write( (char *) channels, sizeof(uint8_t) * num_processed_data );
    channel_file.close();

    ofstream times_file;
    times_file.open( dir_path + "/" + session_key + "_times.bin",
		     ios::out | ios::binary );
    times_file.write( (char *) channel_times, sizeof(long long) * 6 * num_processed_data );
    times_file.close();

    ofstream tof_file;
    tof_file.open( dir_path + "/" + session_key + "_tof.txt", ios::out );
    // tof_file.write( (char *) tof, sizeof(double) * num_processed_data );
    for( int i=0; i < num_processed_data; i++ )
    {
	tof_file << tof[i] << endl;
    }
    tof_file.close();
    
    ofstream mcp_positions_file;
    mcp_positions_file.open( dir_path + "/" + session_key + "_mcp_positions.txt", ios::out );
    // mcp_positions_file.write( (char *) mcp_positions,
    // 			      sizeof(double) * 2 * num_processed_data );
    for( int i=0; i < num_processed_data; i++ )
    {
	mcp_positions_file << mcp_positions[i][0] << " " << mcp_positions[i][1] << endl;
    }
    mcp_positions_file.close();

    return num_processed_data;
}


						


int TDC_controller::compute_tof_and_mcp_pos( double mcp_pos[2], double *tofptr,
					     long long x1, long long x2,
					     long long y1, long long y2,
					     long long t )
{
    double kx = 1.29;
    double ky = 1.31;

    // double center_x = -1.6;
    // double center_y = 3.0;
    
    mcp_pos[0] = 0.5 * kx * ( x1 - x2 ) * 0.001;
    mcp_pos[1] = 0.5 * ky * ( y1 - y2 ) * 0.001;
    *tofptr = t * 0.001;

    // timeStamp = eventTimeStamp * (1.0e-12);
	
    return 0 ;
}




// reset the buffers. they don't actually have to be cleared,
// we just tell the tdc that no data has been added so that
// old data gets overwritten.
void TDC_controller::reset()
{
    this->num_data_in_hit_buffer = 0;
    this->num_processed_data = 0;
}







#if USE_TDC
void print_all_params(C_TDC* c_tdc)
{
    const int num_params = 23;
    char *all_params[num_params] =
	{ "RisingEnable", "FallingEnable", "TriggerEdge",
	  "TriggerChannel", "OutputLevel", "GroupingEnable",
	  "AllowOverlap", "TriggerDeadTime",
	  "GroupRangeStart", "GroupRangeEnd", "ExternalClock",
	  "OutputRollovers", "VHR", "UseFineINL",
	  "GroupTimeout", "BufferSize", "DllTapAdjust:0",
	  "DelayTap:0", "INL:0", "UseClock80",
	  "MMXEnable", "DMAEnable", "SSEEnable"
	};
    
    char buf[256];

    for (int i = 0; i < num_params; i++)
    {
	strcpy(buf, TDCManager_GetParameter( c_tdc, all_params[i]));
	cout << all_params[i] << " = " << buf << endl;
    }

    return;
}
#endif 



// void test_read(C_TDC *c_tdc)
// {
// 	cout << "TESTING READ" << endl;
// 	TDCHit test_hit;
// 	int num_words = TDCManager_ReadTDCHit( c_tdc, &test_hit, 1);
// 	cout << "rising: " << test_hit.RISING << endl;
// 	cout << "falling: " << test_hit.FALLING << endl;
// 	cout << "tdc_error: " << test_hit.TDC_ERROR << endl;
// 	printf("time: %lld \n", test_hit.time);
// 	printf("time (s): %.4f \n", test_hit.time * 25.0e-12);
// 	printf("channel: %u \n", test_hit.channel );
// 	printf("type: %u \n", test_hit.type );
// 	cout << "words read: " << num_words << endl << endl;
// }



// void test_batch_ReadTDCHit(C_TDC *c_tdc)
// {
// 	const int num_reads = 100;
// 	TDCHit test_hit[num_reads];

// 	cout << "\n\nTESTING BATCH ReadTDCHit" << endl;
// 	int num_words = TDCManager_ReadTDCHit(c_tdc, test_hit, num_reads);
// 	/*cout << "rising: " << test_hit.RISING << endl;
// 	cout << "falling: " << test_hit.FALLING << endl;
// 	cout << "tdc_error: " << test_hit.TDC_ERROR << endl;
// 	printf("time: %lld \n", test_hit.time);
// 	printf("time (s): %.4f \n", test_hit.time * 25.0e-12);
// 	printf("channel: %u \n", test_hit.channel);
// 	printf("type: %u \n", test_hit.type);*/
	
// 	cout << "hits read: " << num_words << endl << endl;

// 	long long first_time = test_hit[0].time;

// 	for (int i = 0; i < num_words; i++)
// 	{
// 		cout << "rising: " << test_hit[i].RISING << endl;
// 		printf("channel: %u \n", test_hit[i].channel);
// 		printf("type: %u \n", test_hit[i].type);
// 		printf("time: %e\n", (test_hit[i].time - first_time)*1.0e-12);
// 		cout << endl; 
// 	}

// }





// void test_batch_Read(C_TDC *c_tdc)
// {
// 	// ofstream outfile("test_batch_read.bin", ofstream::binary );
// 	const int num_reads = 1000;
// 	HIT test_hit[num_reads];

// 	cout << "\n\nTESTING BATCH REead" << endl;
// 	int num_words = TDCManager_Read(c_tdc, test_hit, num_reads);
// 	/*cout << "rising: " << test_hit.RISING << endl;
// 	cout << "falling: " << test_hit.FALLING << endl;
// 	cout << "tdc_error: " << test_hit.TDC_ERROR << endl;
// 	printf("time: %lld \n", test_hit.time);
// 	printf("time (s): %.4f \n", test_hit.time * 25.0e-12);
// 	printf("channel: %u \n", test_hit.channel);
// 	printf("type: %u \n", test_hit.type);*/
	
// 	cout << "hits read: " << num_words << endl << endl;
// 	// outfile.write( (char *) test_hit, num_words * sizeof( HIT ) );
// 	// outfile.close();
// }








// #endif 
