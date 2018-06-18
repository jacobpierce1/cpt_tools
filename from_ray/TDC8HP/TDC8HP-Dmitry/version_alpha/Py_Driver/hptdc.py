import ctypes

#Load c-driver into drv handler 
drv = ctypes.cdll.LoadLibrary("/Users/ray/Desktop/TDC8HP/version_alpha/C_Driver/hptdc_driver_3.4.3_x86_c_wrap.dll")

#########################################################
#Ctypes signaturas for C-functions
#########################################################

#Structure TDCManager
#It is an effective structure, to handle a pointer to the TDCManager object 
class TDC_Structure(ctypes.Structure):
	pass
	
#C_TDC* TDCManager_New()
TDC_New = drv.TDCManager_New
TDC_New.restype = ctypes.POINTER(TDC_Structure)

#int TDCManager_Delete(C_TDC* c_tdc);
TDC_Delete = drv.TDCManager_Delete
TDC_Delete.argtype = ctypes.POINTER(TDC_Structure)
TDC_Delete.restype = ctypes.c_int

#int TDCManager_Init(C_TDC* c_tdc);
TDC_Init = drv.TDCManager_Init
TDC_Init.argtype = ctypes.POINTER(TDC_Structure)
TDC_Init.restype = ctypes.c_int

#int TDCManager_InitDev(C_TDC* c_tdc, int startDevice, int deviceCount);
TDC_InitDev = drv.TDCManager_InitDev
TDC_InitDev.argtypes = (ctypes.POINTER(TDC_Structure), ctypes.c_int, ctypes.c_int)
TDC_InitDev.restype  = ctypes.c_int

#int TDCManager_Start(C_TDC* c_tdc);
TDC_Start= drv.TDCManager_Start
TDC_Start.argtype = ctypes.POINTER(TDC_Structure)
TDC_Start.restype = ctypes.c_int

#int TDCManager_Stop(C_TDC* c_tdc);
TDC_Stop = drv.TDCManager_Stop
TDC_Stop.argtype = ctypes.POINTER(TDC_Structure)
TDC_Stop.restype = ctypes.c_int

#int TDCManager_Pause(C_TDC* c_tdc);
TDC_Pause = drv.TDCManager_Pause
TDC_Pause.argtype = ctypes.POINTER(TDC_Structure)
TDC_Pause.restype = ctypes.c_int

#int TDCManager_Continue(C_TDC* c_tdc);
TDC_Continue = drv.TDCManager_Continue
TDC_Continue.argtype = ctypes.POINTER(TDC_Structure)
TDC_Continue.restype = ctypes.c_int

#int TDCManager_Reconfigure(C_TDC* c_tdc);
TDC_Reconfigure = drv.TDCManager_Reconfigure
TDC_Reconfigure.argtype = ctypes.POINTER(TDC_Structure)
TDC_Reconfigure.restype = ctypes.c_int

#int TDCManager_CleanUp(C_TDC* c_tdc);
TDC_CleanUp = drv.TDCManager_CleanUp
TDC_CleanUp.argtype = ctypes.POINTER(TDC_Structure)
TDC_CleanUp.restype = ctypes.c_int

#int TDCManager_ClearBuffer(C_TDC* c_tdc);
TDC_ClearBuffer = drv.TDCManager_ClearBuffer
TDC_ClearBuffer.argtype = ctypes.POINTER(TDC_Structure)
TDC_ClearBuffer.restype = ctypes.c_int

#int TDCManager_GetDriverVersion(const C_TDC* c_tdc);
TDC_GetDriverVersion = drv.TDCManager_GetDriverVersion
TDC_GetDriverVersion.argtype = ctypes.POINTER(TDC_Structure)
TDC_GetDriverVersion.restype = ctypes.c_int

#int TDCManager_GetTDCCount(const C_TDC* c_tdc);
TDC_GetTDCCount = drv.TDCManager_GetTDCCount
TDC_GetTDCCount.argtype = ctypes.POINTER(TDC_Structure)
TDC_GetTDCCount.restype = ctypes.c_int

#int TDCManager_GetState(const C_TDC* c_tdc);
TDC_GetState = drv.TDCManager_GetState
TDC_GetState.argtype = ctypes.POINTER(TDC_Structure)
TDC_GetState.restype = ctypes.c_int

#bool TDCManager_SetParameter(C_TDC* c_tdc, const char* config)
TDC_SetParameter = drv.TDCManager_SetParameter
TDC_SetParameter.argtypes = (ctypes.POINTER(TDC_Structure), ctypes.c_char_p)
TDC_SetParameter.restype = ctypes.c_bool

#// Sets a parameter like in the config file 
#bool SetParameter(const char * config);

#// reads config, returns false, if the file could not be found
#bool ReadConfigFile(const char * filename);

#// Reads the input of a string (may contain multiple parameters)
#bool ReadConfigString(const char *parameter);

#const char * TDCManager_GetParameter(C_TDC* c_tdc, const char *parameter)
TDC_GetParameter = drv.TDCManager_GetParameter
TDC_GetParameter.argtypes = (ctypes.POINTER(TDC_Structure), ctypes.c_char_p)
TDC_GetParameter.restype  = ctypes.c_char_p

#Define HIT = unsigned long.
#HIT = ctypes.c_ulong()

#	// reads data from the TDCs 
#	TDC_C_WRAP_API int TDCManager_Read(C_TDC* c_tdc, HIT* out, int size);
#	TDC_C_WRAP_API int TDCManager_Read(C_TDC* c_tdc, unsigned long* out, int size);
TDC_Read = drv.TDCManager_Read
TDC_Read.argtypes = (ctypes.POINTER(TDC_Structure), ctypes.POINTER(ctypes.c_ulong), ctypes.c_int)
TDC_Read.restype  = ctypes.c_int

#TDCHit =
#	struct TDCHit:
#	public:
#		const static int RISING = 1;
#		const static int FALLING = 0;
#		const static int TDC_ERROR = 2;
#
#		long long time;
#		unsigned char channel;
#		unsigned char type;
#		unsigned short bin;


class TDCHit(ctypes.Structure):
	_fields_ = [
		("RISING", 		ctypes.c_int),
		("FALLING", 	ctypes.c_int),
		("TDC_ERROR", 	ctypes.c_int),
		("time", 		ctypes.c_longlong),
		("channel", 	ctypes.c_ubyte),
		("type", 		ctypes.c_ubyte),
		("bin", 		ctypes.c_ushort)
	]

#	// Reads a hit as a struct (1ps resolution)
#	TDC_C_WRAP_API int TDCManager_ReadTDCHit(C_TDC* c_tdc, TDCHit* buffer, int length);
TDC_ReadTDCHit = drv.TDCManager_ReadTDCHit
TDC_ReadTDCHit.argtypes = (ctypes.POINTER(TDC_Structure), ctypes.POINTER(TDCHit), ctypes.c_int)
TDC_ReadTDCHit.restype = ctypes.c_int

#and TDCInfo structures
# class TDCInfo {
#public:
#	int index;
#	int channelStart;
#	int channelCount;
#	int highResChannelCount;
#	int highResChannelStart;
#	int lowResChannelCount;
#	int lowResChannelStart;
#	double resolution;
#	DWORD serialNumber;
	
#	int version;
#	int fifoSize;
#	int *INLCorrection;
#	unsigned short *DNLData;
#	bool flashValid;
#	unsigned char boardConfiguration;
#	unsigned short reserved2;
#	int bufferSize;

"""
class TDCInfo(ctypes.Structure):
	_fields_ = [
		("index", 				ctypes.c_int),		#	int index;
		("channelStart", 		ctypes.c_int),		#	int channelStart;
		("channelCount", 		ctypes.c_int),		#	int channelCount;
		("highResChannelCount", ctypes.c_int),		#	int highResChannelCount;
		("highResChannelStart", ctypes.c_int),		#	int highResChannelStart;
		("lowResChannelCount", 	ctypes.c_int),		#	int lowResChannelCount;
		("lowResChannelStart", 	ctypes.c_int),		#	int lowResChannelStart;
		("resolution", 			ctypes.c_double),	#	double resolution;
		("serialNumber", 		ctypes.c_ulong),	#	DWORD serialNumber;
				
		("version", 			ctypes.c_int),		#	int version;
		("fifoSize", 			ctypes.c_int),		#	int fifoSize;
		("INLCorrection", 		ctypes.c_int),		#	int *INLCorrection;
		("DNLData", 			ctypes.c_ushort),	#	unsigned short *DNLData;
		("flashValid", 			ctypes.c_bool),		#	bool flashValid;
		("boardConfiguration", 	ctypes.c_ubyte),	#	unsigned char boardConfiguration;
		("reserved2", 			ctypes.c_ushort),	#	unsigned short reserved2;
		("bufferSize", 			ctypes.c_int)		#	int bufferSize;
	]
"""

import numpy

class TDCManager():
	def __init__(self):
		#self.ptr = ctypes.POINTER(ctypes.Structure)
		self.ptr = TDC_New()#initialize a pointer to the TDCManager
		
	def Delete(self):
		TDC_Delete(self.ptr)
	
	def Init(self):
		TDC_Init(self.ptr)
	
	def InitDev(self, startDevice, deviceCount):
		TDC_InitDev(self.ptr, startDevice, deviceCount)
		
	def Reconfigure(self):
		TDC_Reconfigure(self.ptr)
		
	def Start(self):
		TDC_Start(self.ptr)
	
	def Stop(self):
		TDC_Stop(self.ptr)
	
	def Continue(self):
		TDC_Continue(self.ptr)
		
	def Pause(self):
		TDC_Pause(self.ptr)
	
	def GetState(self):
		return TDC_GetState(self.ptr)
	
	def GetDriverVersion(self):
		return TDC_GetDriverVersion(self.ptr)

	#_setParameter("DMAEnable true")
	def SetParameter(self, parameter):
		param_ptr = ctypes.c_char_p(parameter) 
		result = TDC_SetParameter(self.ptr, param_ptr)
		return result
	#_getParameter("MMXEnable")
	def GetParameter(self, parameter):
		param_ptr = ctypes.c_char_p(parameter)
		result = TDC_GetParameter(self.ptr, param_ptr)
		return result

#	TDC_C_WRAP_API int TDCManager_Read(C_TDC* c_tdc, unsigned long* out, int size);
	def Read(self):
		buffer = numpy.arange(1, 10)
		bufferULong = buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ulong * len(buffer))) 
		
		numOfHits = TDC_Read(self.ptr, bufferULong, ctypes.c_int(len(buffer)))
		
		""""
		bufferSize = 1000
		buffer = num
		
		buffer = (ctypes.c_ulong*bufferSize)()
		ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ulong))
		
		numOfHits = TDC_Read(self.ptr, buffer, ctypes.c_int(bufferSize))
		
		return numOfHits, buffer
		"""
		return bufferULong
		
	#def ReadTDCHit(self):
		#buffer_size = 1000
		#buffer = ndarray.empty(buffer_size, dtype=TDCHit)
		#TDC_ReadTDCHit(self.ptr, )
		
	#def read(self):
		#return data_array

import time		
if __name__ == '__main__':
	tdc = TDCManager()
	tdc.Init()
	print(tdc.GetState())
	DrvVersion = tdc.GetDriverVersion()

	tdc.SetParameter("RisingEnable none")		#default
	tdc.SetParameter("FallingEnable 0x0ff1ff") 
	tdc.SetParameter("TriggerEdge falling")
	tdc.SetParameter("TriggerChannel 8")
	tdc.SetParameter("OutputLevel false") 		#default
	tdc.SetParameter("GroupingEnable true")		#default
	tdc.SetParameter("AllowOverlap false")		#default
	tdc.SetParameter("TriggerDeadTime 60ns")		
	tdc.SetParameter("GroupRangeStart 0ns")
	tdc.SetParameter("GroupRangeEnd 50ns")
	tdc.SetParameter("ExternalClock false")		#default
	tdc.SetParameter("OutputRollovers true") 	#default
	tdc.SetParameter("VHR true")				#default 
	tdc.SetParameter("UseFineINL false")		#default
	tdc.SetParameter("GroupTimeout 0.2s")		#default
	tdc.SetParameter("BufferSize 18")			
	tdc.SetParameter("DllTapAdjust 0")			#default
	tdc.SetParameter("DelayTap 0")				#default
	tdc.SetParameter("INL 0")					#default
	tdc.SetParameter("MMXEnable true")
	tdc.SetParameter("DMAEnable true")
	tdc.SetParameter("SSEEnable false")			#default
	
	#tdc.SetParameter("BufferSize 18")
	#tdc.SetParameter("GroupRangeStart -70ns")
	#tdc.SetParameter("GroupRangeEnd 200us")
	#tdc.SetParameter("TriggerChannel 8")
	#tdc.SetParameter("TriggerDeadTime 2ms")
	#tdc.SetParameter("OutputRollovers 0")
	#tdc.SetParameter("RisingEnable 0-20")
	
	tdc.Reconfigure()
	print(tdc.GetState())

	tdc.Start()
	print(tdc.GetState())
	
	#Begin READING DATA
	data = tdc.Read()
	print[i for i in data.contents]
	"""
	for i in xrange(100):
		num_of_hits, data = tdc.Read()
		if num_of_hits !=0 :
			print("Data")
			#for i in xrange(events):
				#print(bin(data[i]
	"""
	#End READING DATA 

	tdc.Stop()
	print(tdc.GetState())
	
	print("\n")
	DrvVersion = tdc.GetDriverVersion()
	print(DrvVersion)

	tdc.Delete()
