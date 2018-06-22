#include "windows.h"
#include "stdio.h"
#include "..\TDC8HP_wrapper.h"

typedef int(*my_Proc2)(TDCHit *buffer, int length);
typedef bool(*my_Proc3)(const char * config);
typedef void(*my_Proc5)();


int main(int argc, char* argv[])
{
	// load the DLL:
	HMODULE DLL_handle = LoadLibrary("TDC8HP_wrapper_x64.dll");

	// get handles of the functions
	my_Proc2 my_TDC8HP_ReadTDCHit = (my_Proc2)GetProcAddress(DLL_handle, "TDC8HP_ReadTDCHit");
	my_Proc3 my_TDC8HP_SetParameter = (my_Proc3)GetProcAddress(DLL_handle, "TDC8HP_SetParameter");
	my_Proc5 my_TDC8HP_Reconfigure = (my_Proc5)GetProcAddress(DLL_handle, "TDC8HP_Reconfigure");
	my_Proc5 my_TDC8HP_Start = (my_Proc5)GetProcAddress(DLL_handle, "TDC8HP_Start");
	my_Proc5 my_TDC8HP_Stop = (my_Proc5)GetProcAddress(DLL_handle, "TDC8HP_Stop");

	if (!my_TDC8HP_Read) {
		printf("the DLL could not be loaded\n");
		exit(1);
	}

	// set TDC parameters
	my_TDC8HP_SetParameter("MMXEnable true");
	my_TDC8HP_SetParameter("SSEEnable false");
	my_TDC8HP_SetParameter("DMAEnable true");
	my_TDC8HP_SetParameter("TriggerEdge falling");
	my_TDC8HP_SetParameter("AllowOverlap false");
	my_TDC8HP_SetParameter("OutputLevel false");
	my_TDC8HP_SetParameter("RisingEnable none");
	my_TDC8HP_SetParameter("GroupingEnable false");
	my_TDC8HP_SetParameter("FallingEnable 0-7");
	my_TDC8HP_SetParameter("VHR true");
	my_TDC8HP_SetParameter("UseFineINL true");
	my_TDC8HP_SetParameter("GroupRangeStart -1ns");
	my_TDC8HP_SetParameter("GroupRangeEnd 1ns");
	my_TDC8HP_SetParameter("TriggerDeadTime 1ns");

	// initialize the TDC:
	my_TDC8HP_Reconfigure();

	// start the data acquisition:
	my_TDC8HP_Start();

	double resolution = my_TDC8HP_Get_TDC_binsize_in_ns();
	printf("bin size = %lf ns\n",resolution);

	TDCHit buffer[10000];

	for (int i=0;i<100;i++) {

		// get up to 10000 new signals:
		int count = my_TDC8HP_ReadTDCHit(buffer, 10000);
		if (!count) {i--; continue;}
		for (int k=0;k<count;k++) {
			printf("ch %i, t=%I64i\n",buffer[k].channel,buffer[k].time);
		}
	}

	// start the data acquisition:
	my_TDC8HP_Stop();

	
	return 0;
}

