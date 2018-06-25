#include <iostream> 
#include <cstdlib>
#include <chrono>
#include <mutex>
#include <thread>

using namespace std

#define USE_TDC  1 
#define USE_GUI  1
#define USE_CARIBU 1

// TDC only availble if using windows 
#ifndef _WIN32
#define USE_TDC  0
#endif


// these are all protected: compilation / inclusion only occur if
// USE_TDC, USE_GUI, or USE_CARIBU is set 
#include "gui.h"
#include "tdc.h"
#include "caribu.h" 




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
    
    Sleep(1000);


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


    return 1;
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
