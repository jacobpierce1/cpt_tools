#include "stdafx.h"

#include "constants.h"
#include <iostream> 
#include <cstdlib>
#include <chrono>
//#include <mutex>
//#include <thread>

using namespace std;



// TDC only availble if using windows 


// these are all protected: compilation / inclusion only occur if
// USE_TDC, USE_GUI, or USE_CARIBU is set 
#include "gui.h"
#include "tdc.h"
#include "caribu.h" 

void TDC_thread( void );



void allocate_globals( void );
void delete_globals( void );


#if USE_TDC    
TDC_controller *tdc;
#endif

#if USE_GUI
Gui *gui;
#endif

#if USE_CARIBU
Caribu_controller *caribu;
#endif


#ifdef _WIN32
int _tmain( int argc, char **argp )
#else
    int main(  int argc, char **argp )
#endif
{

    allocate_globals();

    // register delete_globals to be called at termination of program 
    atexit( delete_globals );    

    // int count = TDCManager_GetTDCCount( tdc->tdcmgr);
    // int driver_version = TDCManager_GetDriverVersion( tdc->tdcmgr );
    // int state = TDCManager_GetState(tdc->tdcmgr );

    // // const char * buf_size_bits_str = TDCManager_GetParameter( tdc->tdcmgr, "BufferSize");
    // // unsigned long buf_size; 
    // // sscanf( buf_size_bits_str, "%ul", &buf_size );


    // // cout << buf_size << endl;

    // cout << "count: " << count << endl;
    // cout << "driver version: " << driver_version << endl;
    // cout << "state: " << state << endl;

    // Sleep(1000);
    // TDCManager_Start( tdc->tdcmgr );

    // Sleep(1000);

    // state = TDCManager_GetState( tdc->tdcmgr );
    // cout << "state: " << state << endl;


    // Sleep(1000);


	cout << "HELLO CPT" << endl;

	//TDC_controller *tdc = new TDC_controller();

	Sleep(1000);


	/*int count = TDCManager_GetTDCCount( tdc->tdcmgr);
	int driver_version = TDCManager_GetDriverVersion( tdc->tdcmgr );
	int state = TDCManager_GetState(tdc->tdcmgr );
*/
	const char * buf_size_bits_str = TDCManager_GetParameter( tdc->tdcmgr, "BufferSize");

	//unsigned long buf_size; 
	//sscanf( buf_size_bits_str, "%ul", &buf_size );


	// cout << buf_size << endl;

	/*cout << "count: " << count << endl;
	cout << "driver version: " << driver_version << endl;
	cout << "state: " << state << endl;*/

	// Sleep(1000);

	Sleep(1000);

	// state = TDCManager_GetState( tdc->tdcmgr );
	// cout << "state: " << state << endl;


	// Sleep(1000);



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

	for (int i = 0; i < 2; i++)
	{
		int num_words = tdc->read();
		cout << "num words: " << num_words << endl;
		tdc->process_hit_buffer();
		Sleep(10);
	}

	// test_batch_read(tdcmgr);

	Sleep(1000);
	//delete tdc;

	// delete_globals();

	return 0;
}



void allocate_globals( void )
{
 
#if USE_TDC    
    tdc = new TDC_controller();
#endif

#if USE_GUI
    gui = new Gui();
#endif

#if USE_CARIBU
    caribu = new Caribu_controller();
#endif
}



void delete_globals( void )
{
    cout << "deleting globals" << endl;
 
#if USE_TDC    
    delete tdc;
#endif

#if USE_GUI
    delete gui;
#endif

#if USE_CARIBU
    delete caribu;
#endif

}



void TDC_thread( void ) 
{
	return;
}
