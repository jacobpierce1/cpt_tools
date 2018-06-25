// TDC_MANAGER_2.cpp : Defines the entry point for the console application.
//
#define _CRT_SECURE_NO_WARNINGS 1



#include "stdafx.h"
#include <iostream> 

#include <Windows.h>
#include <WinBase.h> 
#include <stdio.h> 
#include <fstream>

// #include <numeric_limits>

#include <bitset> 

// SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);


#include "hptdc_driver_3.4.3_x86_c_wrap.h"

using namespace std; 


void print_all_params(C_TDC* c_tdc);
void print_TDCInfo(C_TDC* c_tdc);
void test_read(C_TDC *c_tdc);
void test_batch_read(C_TDC *c_tdc);
void test_batch_ReadTDCHit(C_TDC *c_tdc);
void test_batch_Read(C_TDC *c_tdc);


#define TDC_HIT_BUFFER_SIZE 1000
const unsigned int TDC_MAX_COUNTS = 100000;








// here is a relatively harmless implementation of the masks required to 
// unpack data from the TDC.
// const HIT RISING_MASK = 23;


const HIT RISING_MASK = bitset<32>(          "10000000000000000000000000000000" ).to_ulong();
//#define FALLING_MASK         0b01000000000000000000000000000000
//#define CHANNEL_MASK         0b00111111000000000000000000000000
//#define TRANSITION_TIME_MASK 0b00000000111111111111111111111111
//
//#define ERROR_HEADER_MASK    0b01000000000000000000000000000000
//#define ERROR_MESSAGE_MASK   0b00000000111111110000000000000000
//#define ERROR_COUNT_MASK     0b00000000000000001111111111111111
////
//#define 0b00000000000000000000000000000000
//#define 0b00000000000000000000000000000000
//#define 0b00000000000000000000000000000000
//#define 0b00000000000000000000000000000000
//#define 0b00000000000000000000000000000000
//

// #define CHANNEL_SHIFT 16
// #define ERROR_MESSAGE_SHIFT 16

// #define HIT_EDGE_MASK = ( 0b11 << 31 );
//struct transition_bitfield
//{
//	unsigned char edge : 2;
//	unsigned char channel : 6;
//	unsigned int transition_time : 24;
//};
//
//struct error_bitfield
//{
//	unsigned char header : 2;
//	unsigned char channel : 6;
//	unsigned char error : 8;
//	unsigned int count : 16;
//};
//
//struct group_bitfield
//{
//	unsigned char header : 4;
//	unsigned char id : 4;
//	unsigned int trigger_time : 24;
//};
//
//struct rollover_bitfield
//{
//	unsigned char header : 8;
//	unsigned int timestamp : 24;
//};
//
//struct level_information_bitfield
//{
//	unsigned char header : 5;
//	unsigned char n : 6;
//	unsigned int level : 21;
//};
//
//struct resolution_bitfield
//{
//	unsigned char header : 8;
//	unsigned int bin_size : 24;  // in fs 
//};



class TDC
{
public :
	TDC( void );
	~TDC( void );

	C_TDC *tdcmgr;
	
	unsigned int num_data_in_hit_buffer;
	unsigned int num_data_in_channel_times;

	HIT hit_buffer[ TDC_HIT_BUFFER_SIZE ]; 
	double channel_times[6][ TDC_MAX_COUNTS ];

	int read(void);

	bool TDC::check_rollover( HIT hit );
	// double TDC::check_hit_edge( Hit hit );
	double TDC::hit_to_time(HIT hit, int *channel, double *time);
	void process_hit_buffer();
	int reset_channel_times( void );
	int compute_mcp_position( double x1, double x2, double y1, double y2 );

};


TDC::TDC() 
{
	this->tdcmgr = TDCManager_New();
	TDCManager_Init( this->tdcmgr );

	this->num_data_in_hit_buffer = 0;
	this->num_data_in_channel_times = 0;
	// this->hit_buffer = new 
}


TDC::~TDC()
{
	TDCManager_CleanUp( this->tdcmgr );
	TDCManager_Delete( this->tdcmgr );
}


int TDC::read()
{
	this->num_data_in_hit_buffer = TDCManager_Read( this->tdcmgr, this->hit_buffer, TDC_HIT_BUFFER_SIZE );
	return this->num_data_in_hit_buffer;
}

//// when a rollover occurs, it is encoded as a hit 
//// return true if rollover detecter 
//bool TDC::check_rollover( HIT hit )
//{
//
//}


//double TDC::check_hit_edge( Hit hit ) 
//{
//
//}


double TDC::hit_to_time( HIT hit, int *channel, double *time )
{
	cout << sizeof( RISING_MASK ) << endl; 

	if( hit & RISING_MASK ) 
	{
		cout << "rising" << endl;
	}
	else if( hit & FALLING_MASK ) 
	{
		cout << "falling" << endl;
	}

	// transition_bitfield x;

//	unsigned int time = 
	// first check for rising / falling transition or an error 
	return 0;
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
//int TDC::compute_mcp_position(double x1, double x2, double y1, double y2)
//{
//}
//

int _tmain(int argc, _TCHAR* argv[])
{
	cout << "HELLO CPT" << endl;

	TDC *tdc = new TDC();

	Sleep(1000);


	int count = TDCManager_GetTDCCount( tdc->tdcmgr);
	int driver_version = TDCManager_GetDriverVersion( tdc->tdcmgr );
	int state = TDCManager_GetState(tdc->tdcmgr );

	const char * buf_size_bits_str = TDCManager_GetParameter( tdc->tdcmgr, "BufferSize");

	//unsigned long buf_size; 
	//sscanf( buf_size_bits_str, "%ul", &buf_size );


	// cout << buf_size << endl;

	cout << "count: " << count << endl;
	cout << "driver version: " << driver_version << endl;
	cout << "state: " << state << endl;

	Sleep(1000);
	TDCManager_Start( tdc->tdcmgr );

	Sleep(1000);

	state = TDCManager_GetState( tdc->tdcmgr );
	cout << "state: " << state << endl;


	Sleep(1000);



/*
	TDCManager_Pause( tdc->tdcmgr );

	Sleep(1000);

	state = TDCManager_GetState( tdc->tdcmgr );
	cout << "state: " << state << endl;

	Sleep(1000);

	TDCManager_Continue( tdc->tdcmgr );

	Sleep(1000);


	state = TDCManager_GetState( tdc->tdcmgr );
	cout << "state: " << state << endl;
*/

	for (int i = 0; i < 10; i++)
	{
		int num_words = tdc->read();
		cout << "num words: " << num_words << endl;
		tdc->hit_to_time( tdc->hit_buffer[0], NULL, NULL );
		Sleep(10);
	}

	// test_batch_read(tdcmgr);

	Sleep(1000);
	delete tdc;

	return 0;
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


//void print_TDCInfo(C_TDC* c_tdc)
//{
//
//	TDCInfo info = TDCManager_GetTDCInfo(c_tdc, 0);
//	cout << info.index << endl;
//	return;
//}


	// TDCManager x; 


	////// TDCHit x;
	////// cout << "RISING: SHOULD BE 1 " << x.RISING << endl;

	// TDCManager test; 


	//// https://msdn.microsoft.com/en-us/library/windows/desktop/ms686944(v=vs.85).aspx
	//HINSTANCE hinstLib = LoadLibrary( TEXT( "hptdc_driver_3.4.3_x86.dll") );

	//if( hinstLib ) 
	//{
	//	cout << "INFO: loaded library" << endl; 

	//	MYPROC procAdd = (MYPROC)GetProcAddress(hinstLib, "TDCManager_New");

	//	if (procAdd)
	//	{
	//		cout << " added init\n"; 

	//	}
	//	else
	//	{

	//		cout << "failed to add init\n";
	//	}

	//	FreeLibrary(hinstLib);
	//}
	//else
	//{

	//	cout << "ERROR: unable to load library" << endl;
	//}

	// return 0;






