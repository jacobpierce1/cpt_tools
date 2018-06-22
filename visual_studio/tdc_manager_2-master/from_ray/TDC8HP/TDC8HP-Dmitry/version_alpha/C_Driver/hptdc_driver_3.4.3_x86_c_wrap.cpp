// hptdc_driver_3.4.3_x86_c_wrap.cpp : 
// Defines the exported functions for the DLL application.
//
#include "stdafx.h"

#include "hptdc_driver_3.4.3_x86/tdcmanager_3.4.3.h"

#define TDC_C_WRAP_EXPORTS
#include "hptdc_driver_3.4.3_x86_c_wrap.h"

#ifdef __cplusplus
extern "C"  {
#endif
//	TDC_WRAP_API const static int STATE_UNINITIALIZED = 0;
//	TDC_WRAP_API const static int STATE_NOT_CONFIGURED = 1;

	TDC_C_WRAP_API C_TDC* TDCManager_New(){
		TDCManager* tdc = new TDCManager();
		return (C_TDC *)tdc;
	};

	TDC_C_WRAP_API int TDCManager_Delete(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->CleanUp();
		delete tdc;
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_Init(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->Init();
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_InitDev(C_TDC* c_tdc, int startDevice, int deviceCount){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->Init(startDevice, deviceCount);
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_Start(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->Start();
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_Stop(C_TDC* c_tdc){
		TDCManager*tdc = (TDCManager*)c_tdc;
		tdc->Stop();	
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_Pause(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->Pause();
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_Continue(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->Continue();
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_Reconfigure(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->Reconfigure();
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_CleanUp(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->CleanUp();
		return 0;
	};

	TDC_C_WRAP_API int TDCManager_ClearBuffer(C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		tdc->ClearBuffer();
		return 0;
	};

/*=========================================*/
	TDC_C_WRAP_API int TDCManager_GetDriverVersion(const C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		int driverVersion = tdc->GetDriverVersion();
		return driverVersion;
	};

	TDC_C_WRAP_API int TDCManager_GetTDCCount(const C_TDC* c_tdc){
		TDCManager* tdc = (TDCManager*)c_tdc;
		int tdcCount = tdc->GetTDCCount();
		return tdcCount;
	};

	TDC_C_WRAP_API int TDCManager_GetState(const C_TDC* c_tdc){
		TDCManager*  tdc = (TDCManager*)c_tdc;
		int state = tdc->GetState();
		return state;
	};

/*	TDC_C_WRAP_API TDCInfo TDCManager_GetTDCInfo(const C_TDC* c_tdc, int index){
		TDCManager *tdc = (TDCManager *)c_tdc;
		int driverVersion = tdc->GetDriverVersion();
		return driverVersion;
	};
*/

	TDC_C_WRAP_API const char * TDCManager_GetParameter(C_TDC* c_tdc, const char *parameter){
		TDCManager* tdc = (TDCManager*)c_tdc;
		const char* parValue = tdc->GetParameter(parameter); 
		return parValue;
	};


//=[Set section]========================================================================
	TDC_C_WRAP_API bool TDCManager_SetParameter(C_TDC* c_tdc, const char* config){
		TDCManager *tdc = (TDCManager*)c_tdc;
		bool result = tdc->SetParameter(config);
		return result;
	};

//=[Read section]=========================================================================
	TDC_C_WRAP_API int TDCManager_Read(C_TDC* c_tdc, HIT* out, int size){
		TDCManager* tdc = (TDCManager*)c_tdc;
		int result = tdc->Read(out, size);
		return result;
	};

	TDC_C_WRAP_API int TDCManager_ReadTDCHit(C_TDC* c_tdc, TDCHit* buffer, int length){
		TDCManager* tdc = (TDCManager*)c_tdc;
		int result = tdc->ReadTDCHit(buffer, length);
		return result;
	};




#ifdef __cplusplus
}
#endif
