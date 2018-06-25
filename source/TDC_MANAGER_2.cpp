#if USE_TDC 

// here is a relatively harmless implementation of the masks required to 
// unpack data from the TDC.
// const HIT RISING_MASK = 23;


const HIT RISING_MASK =          bitset<32>( "11000000000000000000000000000000" ).to_ulong();
const HIT FALLING_MASK =         bitset<32>( "10000000000000000000000000000000" ).to_ulong();
const HIT CHANNEL_MASK =         bitset<32>(  "00111111000000000000000000000000" ).to_ulong();
const HIT TRANSITION_TIME_MASK = bitset<32>( "00000000111111111111111111111111" ).to_ulong();

const HIT ERROR_HEADER_MASK =    bitset<32>( "01000000000000000000000000000000" ).to_ulong();
const HIT ERROR_MESSAGE_MASK =   bitset<32>( "00000000111111110000000000000000" ).to_ulong();
const HIT ERROR_COUNT_MASK =     bitset<32>( "00000000000000001111111111111111" ).to_ulong();


#define CHANNEL_SHIFT 24
#define ERROR_MESSAGE_SHIFT 16




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





double TDC::hit_to_time( HIT hit, int *channel, double *time )
{
	cout << sizeof( RISING_MASK ) << endl; 

	int edge;
	
	if( hit & RISING_MASK ) 
	{
	    edge = 0;
		cout << "rising" << endl;
	}
	else if( hit & FALLING_MASK ) 
	{
		cout << "falling" << endl;
	}

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






#endif 
