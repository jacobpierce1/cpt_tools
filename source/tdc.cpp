#include "stdafx.h"

#include "constants.h"


//#if USE_TDC 


#include "tdc.h"
#include <cstdlib>
#include <iostream>
#include <bitset> 
#include <string>

using namespace std;



// here is a relatively harmless implementation of the masks required to 
// unpack data from the TDC.
// const HIT RISING_MASK = 23;


// const HIT RISING_MASK =          std::bitset<32>( "11000000000000000000000000000000" ).to_ulong();
// const HIT FALLING_MASK =         bitset<32>( "10000000000000000000000000000000" ).to_ulong();
//const HIT CHANNEL_MASK =         bitset<32>(  "00111111000000000000000000000000" ).to_ulong();
const HIT TRANSITION_TIME_MASK = bitset<32>( "00000000111111111111111111111111" ).to_ulong();
//
//const HIT ERROR_HEADER_MASK =    bitset<32>( "01000000000000000000000000000000" ).to_ulong();
//const HIT ERROR_MESSAGE_MASK =   bitset<32>( "00000000111111110000000000000000" ).to_ulong();
//const HIT ERROR_COUNT_MASK =     bitset<32>( "00000000000000001111111111111111" ).to_ulong();


// std::bitset<32> TRANSITION_TIME_MASK( "00000000111111111111111111111111" );



#define CHANNEL_SHIFT 24
#define ERROR_MESSAGE_SHIFT 16




TDC_controller::TDC_controller() 
{
	this->tdcmgr = TDCManager_New();

	Sleep(1000);

	TDCManager_Init( this->tdcmgr );
	TDCManager_ClearBuffer( this->tdcmgr );

	this->num_data_in_hit_buffer = 0;
	this->num_processed_data = 0;

	Sleep(1000);
	
	// this->hit_buffer = new 
	TDCManager_Start( this->tdcmgr );
}


TDC_controller::~TDC_controller()
{
	TDCManager_CleanUp( this->tdcmgr );
	TDCManager_Delete( this->tdcmgr );
}


int TDC_controller::read()
{
	this->num_data_in_hit_buffer = TDCManager_Read( this->tdcmgr, this->hit_buffer, TDC_HIT_BUFFER_SIZE );
	return this->num_data_in_hit_buffer;
}





double TDC_controller::process_hit( HIT hit, int *channel, double *time )
{
	// cout << sizeof( RISING_MASK ) << endl; 

	int edge = -1;
	int error = 0;

	bitset<32> bits = bitset<32>( hit );
	
	cout << bits << endl;
	
	if( bits[31] && bits[30] )
	{
		cout << "rising" << endl;
		edge = 0;
	}
	else if( bits[31] && ! bits[30] )
	{
		cout << "falling" << endl;
		edge = 1;
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
	// cout << "mask: " << mask << endl;

	unsigned short tmpchannel = (( bits >> 24 ) & mask).to_ulong();

	// bitset<32> tmpchannel = 
	// unsigned long channel_int = tmpchannel.to_ulong();
	unsigned long tmptime = TRANSITION_TIME_MASK & hit; 


	//cout << "tmpchannel ulong " << tmpchannel.to_ulong() << endl;

	//cout << "channel: " << channel << endl ;

	cout << "tmpchannel: " << tmpchannel << endl << endl;

	//if( hit & RISING_MASK ) 
	//{
	//    edge = 0;
	//	cout << "rising" << endl;
	//}
	//else if( hit & FALLING_MASK ) 
	//{
	//	cout << "falling" << endl;
	//}

	// first check for rising / falling transition or an error 
	return 0;
}


void TDC_controller::process_hit_buffer( )
{
	for( int i=0; i<this->num_data_in_hit_buffer; i++ )
	{
		process_hit( hit_buffer[i], NULL, NULL );
	}

	this->num_data_in_hit_buffer = 0;
}




//
//void TDC::process_hit_buffer()
//{
//}
//
//int TDC::reset_channel_times(void)
//{
//}
//
int TDC_controller::compute_mcp_position(double x1, double x2, double y1, double y2)
{
	double pTPCalX = 1.29;
	double pTPCalY = 1.31;

	double center_x = -1.6;
	double center_y = 3.0;
	return 0 ;

}







void print_all_params(C_TDC* c_tdc)
{
	const int num_params = 23;
	char *all_params[num_params] = { "RisingEnable", "FallingEnable", "TriggerEdge",
		"TriggerChannel", "OutputLevel", "GroupingEnable", "AllowOverlap", "TriggerDeadTime",
		"GroupRangeStart", "GroupRangeEnd", "ExternalClock", "OutputRollovers", "VHR", "UseFineINL",
		"GroupTimeout", "BufferSize", "DllTapAdjust:0", "DelayTap:0", "INL:0", "UseClock80",
		"MMXEnable", "DMAEnable", "SSEEnable" };

	char buf[256];

	for (int i = 0; i < num_params; i++)
	{
		strcpy(buf, TDCManager_GetParameter( c_tdc, all_params[i]));
		cout << all_params[i] << " = " << buf << endl;
	}

	return;
}




void test_read(C_TDC *c_tdc)
{
	cout << "TESTING READ" << endl;
	TDCHit test_hit;
	int num_words = TDCManager_ReadTDCHit( c_tdc, &test_hit, 1);
	cout << "rising: " << test_hit.RISING << endl;
	cout << "falling: " << test_hit.FALLING << endl;
	cout << "tdc_error: " << test_hit.TDC_ERROR << endl;
	printf("time: %lld \n", test_hit.time);
	printf("time (s): %.4f \n", test_hit.time * 25.0e-12);
	printf("channel: %u \n", test_hit.channel );
	printf("type: %u \n", test_hit.type );
	cout << "words read: " << num_words << endl << endl;
}



void test_batch_ReadTDCHit(C_TDC *c_tdc)
{
	const int num_reads = 100;
	TDCHit test_hit[num_reads];

	cout << "\n\nTESTING BATCH ReadTDCHit" << endl;
	int num_words = TDCManager_ReadTDCHit(c_tdc, test_hit, num_reads);
	/*cout << "rising: " << test_hit.RISING << endl;
	cout << "falling: " << test_hit.FALLING << endl;
	cout << "tdc_error: " << test_hit.TDC_ERROR << endl;
	printf("time: %lld \n", test_hit.time);
	printf("time (s): %.4f \n", test_hit.time * 25.0e-12);
	printf("channel: %u \n", test_hit.channel);
	printf("type: %u \n", test_hit.type);*/
	
	cout << "hits read: " << num_words << endl << endl;

	long long first_time = test_hit[0].time;

	for (int i = 0; i < num_words; i++)
	{
		cout << "rising: " << test_hit[i].RISING << endl;
		printf("channel: %u \n", test_hit[i].channel);
		printf("type: %u \n", test_hit[i].type);
		printf("time: %e\n", (test_hit[i].time - first_time)*1.0e-12);
		cout << endl; 
	}

}





void test_batch_Read(C_TDC *c_tdc)
{
	// ofstream outfile("test_batch_read.bin", ofstream::binary );
	const int num_reads = 1000;
	HIT test_hit[num_reads];

	cout << "\n\nTESTING BATCH REead" << endl;
	int num_words = TDCManager_Read(c_tdc, test_hit, num_reads);
	/*cout << "rising: " << test_hit.RISING << endl;
	cout << "falling: " << test_hit.FALLING << endl;
	cout << "tdc_error: " << test_hit.TDC_ERROR << endl;
	printf("time: %lld \n", test_hit.time);
	printf("time (s): %.4f \n", test_hit.time * 25.0e-12);
	printf("channel: %u \n", test_hit.channel);
	printf("type: %u \n", test_hit.type);*/
	
	cout << "hits read: " << num_words << endl << endl;
	// outfile.write( (char *) test_hit, num_words * sizeof( HIT ) );
	// outfile.close();
}








// #endif 
