#ifndef TDC8HP_wrapper_IS_INCLUDED
	#define TDC8HP_wrapper_IS_INCLUDED

	const static int STATE_UNINITIALIZED = 0;
	const static int STATE_NOT_CONFIGURED = 1;
	const static int STATE_CONFIGURED = 2;
	const static int STATE_RUNNING = 3;
	const static int STATE_PAUSED = 4;
	const static int STATE_SHUTDOWN = 5;

	typedef unsigned long HIT;


	struct TDCHit {
		public:
			const static int RISING = 1;
			const static int FALLING = 0;
			const static int TDC_ERROR = 2;

			long long time;
			unsigned char channel;
			unsigned char type;
			unsigned short bin;
	};


	class TDCInfo {
		public:
			int index;
			int channelStart;
			int channelCount;
			int highResChannelCount;
			int highResChannelStart;
			int lowResChannelCount;
			int lowResChannelStart;
			double resolution;
			unsigned int serialNumber;
	
			int version;
			int fifoSize;
			int *INLCorrection;
			unsigned short *DNLData;
			bool flashValid;
			unsigned char boardConfiguration;
			unsigned short reserved2;
			int bufferSize;
	};



	int  TDC8HP_GetState();
	void TDC8HP_Pause();
	void TDC8HP_Continue();
	void TDC8HP_Reconfigure();
	void TDC8HP_Start();
	void TDC8HP_Stop();
	bool TDC8HP_SetParameter(const char * config);
	void TDC8HP_GetTDCInfo(TDCInfo &TDC_info);
	double TDC8HP_Get_TDC_binsize_in_ns();

	// Reads a hit as a struct (1ps resolution)
	int TDC8HP_ReadTDCHit(TDCHit *buffer, int length);

	// reads data from the TDCs 
	int TDC8HP_Read(HIT *out, int size);

	

#endif