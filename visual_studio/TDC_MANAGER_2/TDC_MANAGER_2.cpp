// TDC_MANAGER_2.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <iostream> 

#include <Windows.h>
#include <stdio.h> 
#include <fstream>

#define _CRT_SECURE_NO_WARNINGS 1


#include "hptdc_driver_3.4.3_x86_c_wrap.h"

using namespace std; 



void print_all_params(C_TDC* c_tdc);
void print_TDCInfo(C_TDC* c_tdc);
void test_read(C_TDC *c_tdc);
void test_batch_read(C_TDC *c_tdc);
void test_batch_ReadTDCHit(C_TDC *c_tdc);
void test_batch_Read(C_TDC *c_tdc);




int _tmain(int argc, _TCHAR* argv[])
{
	cout << "HELLO CPT" << endl;

	C_TDC *tdcmgr = TDCManager_New();

	TDCManager_Init(tdcmgr);

	Sleep(1000);


	int count = TDCManager_GetTDCCount(tdcmgr);
	int driver_version = TDCManager_GetDriverVersion(tdcmgr);
	int state = TDCManager_GetState(tdcmgr);

	cout << "count: " << count << endl;
	cout << "driver version: " << driver_version << endl;
	cout << "state: " << state << endl;

	Sleep(1000);

	TDCManager_Start(tdcmgr);

	Sleep(1000);

	state = TDCManager_GetState(tdcmgr);
	cout << "state: " << state << endl;


	Sleep(1000);




	TDCManager_Pause(tdcmgr);

	Sleep(1000);

	state = TDCManager_GetState(tdcmgr);
	cout << "state: " << state << endl;

	Sleep(1000);

	TDCManager_Continue(tdcmgr);

	Sleep(1000);


	state = TDCManager_GetState(tdcmgr);
	cout << "state: " << state << endl;

	// print_all_params(tdcmgr);
	// print_TDCInfo(tdcmgr);

	//// HIT *test_hit;
	//char buf[128];
	//strcpy( buf, TDCManager_GetParameter(tdcmgr, "GroupRangeStart") );
	//cout << buf << endl;
	
	//strcpy(buf, TDCManager_GetParameter(tdcmgr, "GroupRangeStart"));
	//cout << buf << endl;
	
	
	/*for (int i = 0; i < 5; i++)
	{
		Sleep(1000);
		test_read(tdcmgr);
	}
*/

	for (int i = 0; i < 10; i++)
	{
		test_batch_ReadTDCHit(tdcmgr);
		Sleep(1);
		test_batch_Read(tdcmgr);
		Sleep( 1 );

	}

	// test_batch_read(tdcmgr);

	Sleep(1000);

	TDCManager_CleanUp(tdcmgr);
	TDCManager_Delete(tdcmgr);

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

	const int num_reads = 100;
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


