// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the TDC_C_WRAP_B_EXPORTS
// symbol defined on the command line. This symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// TDC_C_WRAP_B_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.

#include "tdcmanager_3.5.2.h"

#ifdef TDC_C_WRAP_EXPORTS
#define TDC_C_WRAP_API __declspec(dllexport)
#else
#define TDC_C_WRAP_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif

	typedef struct C_TDC C_TDC;

/*	typedef unsigned long HIT;

	struct TDCHit{
		public:
			const static int RISING = 1;
			const static int FALLING = 0;
			const static int TDC_ERROR = 2;

			long long time;
			unsigned char channel;
			unsigned char type;
			unsigned short bin;
	};
*/ 

	TDC_C_WRAP_API C_TDC* TDCManager_New();
	TDC_C_WRAP_API int TDCManager_Delete(C_TDC* c_tdc);

	TDC_C_WRAP_API int TDCManager_Init(C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_InitDev(C_TDC* c_tdc, int startDevice, int deviceCount);
	TDC_C_WRAP_API int TDCManager_Start(C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_Stop(C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_Pause(C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_Continue(C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_Reconfigure(C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_CleanUp(C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_ClearBuffer(C_TDC* c_tdc);

	TDC_C_WRAP_API int TDCManager_GetDriverVersion(const C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_GetTDCCount(const C_TDC* c_tdc);
	TDC_C_WRAP_API int TDCManager_GetState(const C_TDC* c_tdc);
	// TDC_C_WRAP_API TDCInfo TDCManager_GetTDCInfo(const C_TDC* c_tdc, int index);

	// Sets a parameter like in the config file 
	TDC_C_WRAP_API bool TDCManager_SetParameter(C_TDC* c_tdc, const char* config);

//	// sets a single parameter with key value
//	TDC_C_WRAP_API bool TDCManager_SetParameter(C_TDC* c_tdc, const char* property, const char* value);

//	// reads config, returns false, if the file could not be found
//	bool ReadConfigFile(const char * filename);

//	// Reads the input of a string (may contain multiple parameters)
//	bool ReadConfigString(const char *parameter);

//	// The value of the parameter (result must not be freed)
	TDC_C_WRAP_API const char * TDCManager_GetParameter(C_TDC* c_tdc, const char *parameter);

//	// Returns all parameter names count contains the number of elements in array
//	//  the result must be freed with "delete[] params"
//	const char ** GetParameterNames(int &count);

	// reads data from the TDCs 
	TDC_C_WRAP_API int TDCManager_Read(C_TDC* c_tdc, HIT* out, int size);

	// Reads a hit as a struct (1ps resolution)
	TDC_C_WRAP_API int TDCManager_ReadTDCHit(C_TDC* c_tdc, TDCHit* buffer, int length);

/*	// Reads a hit as a struct (1ps resolution)
	int ReadTDCHitSince(TDCHit *buffer, int length, long long since);

		// reads data from the TDCs 
	int TDCManager::ReadNextFrame(HIT *out, int size);

	// converts a hit to text representation
	static string PrettyPrint(HIT hit);

	// prints into a buffer (no size check, min length > 200 bytes)
	static void PrettyPrint(HIT hit, char *buffer);
	
	// Returns information about the TDC
	TDCInfo getTDCInfo(int index);  //DEPRECATED
	TDCInfo GetTDCInfo(int index) {
		return getTDCInfo(index);
	}
	// Clears all remaining data which is not yet read/
	void ClearBuffer();

	// Returns number of TDCs/
	int getTDCCount() { //DEPRECATED
		assertNotInState(STATE_UNINITIALIZED, "Must call Init before requesting TDC count");
		return tdcCount;
	}
	int GetTDCCount() {
		assertNotInState(STATE_UNINITIALIZED, "Must call Init before requesting TDC count");
		return tdcCount;
	}
	// Get the state of the Manager see STATE_* constants
	int GetState() {
		return state; 
	}
	long long GetTDCStatusRegister(int index);  

	//===========================================================
	// Internal methods 
	//===========================================================
	void TDCManager::EmergencyCleanUp();
	bool updateThrottle(bool value, int freeBuffer);
	void  PokeD(int index, int offset, DWORD value);
	DWORD PeekD(int index, int offset);
	// Internal Method write the flash 
	void WriteConfigFlash();
    
	// Internal Method, sets the serial number
	void SetTDCSerialNumber(int index, DWORD serialNumber);

	void SetMaxDevices(int deviceCount);
	TDCManager_ReadHit();
	deleteTDCManager();
*/
#ifdef __cplusplus
}
#endif




