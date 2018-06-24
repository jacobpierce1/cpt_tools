// WW four-channel Win32 Console.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "ww257x.h"
#include <iostream>		// std:cout, std::cin
#include <fstream>		
#include <time.h>
#include <chrono>
#include <ctime>
#include <sstream>		// Conversion number to string
#include <math.h>		// Least Common Multiple function
using namespace std;

// Parameters
#define USB_ADDRESS		"ASRL6::INSTR"
#define LAN_ADDRESS		"TCPIP::192.168.0.224::23::SOCKET"
#define GPIB_ADDRESS	"GPIB::14::INSTR"
#define REMOTE_ADDRESS	USB_ADDRESS		// Remote interface selected /!\ Be sure to have same setting on the unit
#define SCLK			1E8				// Sample Clock [samples/s]
#define LEVEL_HIGH		4.0				// High level [Vdc] into a 50Ohm load (double into open circuit min 10kOhm)
#define LEVEL_LOW		-4.0			// Low Level [Vdc] into a 50Ohm load (double into open circuit min 10kOhm)
#define TRIGGER_LEVEL	2.0				// DC Trigger level [Vdc]
#define TRIGGER_SLOPE	1				// Trigger slope on falling edge as "0" or rising edge as "1"

// DO NOT CHANGE
#define MAX_MEMORY_PER_CHANNEL	2000000		// Maximum memory size per channel [samples] (2M for Opt 1 and 4M for Opt 2 on WW1074 and WW2074)
#define MAX_STEP_PER_CHANNEL	2000		// Maximum number of steps per sequence per channel
#define MIN_SIZE				16			// Minimum segment size [samples]
#define MIN_RESOLUTION			4			// Minimum segment resolution [samples]
#define MIN_SCLK				0.1			// Minimum sample clock rate [samples/s]
#define MAX_SCLK				100E6		// Maximum sample clock rate [samples/s]
#define MAX_LOOP				2000000		// Maximum number of loop per step
#define PI						3.1415926	// Pi value
#define MIN_AMPLITUDE			10E-3		// Minimum amplitude [Vpp]
#define MAX_AMPLITUDE			10.0			// Maximum amplitude [Vpp]
#define MIN_OFFSET				-4.995		// Minimum offset [Vdc]
#define MAX_OFFSET				4.995		// Maximum offset [Vdc]
#define MIN_TRIGGER_LEVEL		-5.0		// Minimum trigger level into 10kOhm [Vdc]
#define MAX_TRIGGER_LEVEL		5.0			// Maximum trigger level into 10kOhm [Vdc]
#define VIBUF_LEN				256			// Buffer size in byte

// Structure
typedef struct Table_s	// Sequence table
{
	ViInt32 segment;	// Segment number
	ViInt32 loops;		// Number of loop
	ViUInt8 sync;		// Sync state
	ViUInt8 mode;		// Advance mode
} Table;

// Trigger Slope Types
char *TriggerSlopeType[] = {
	"falling edge",		// TRIGGER_SLOPE = 0
	"rising edge"		// TRIGGER_SLOPE = 1
};

// Channels
ViChar *CH[] = { "CHAN_A", "CHAN_B", "CHAN_C", "CHAN_D" };
char *ChannelNumber[] = { "1", "2", "3", "4" };
double dphi[] = { 0.0, 180.0, 0.0, 180.0 };
double qphi[] = { 180.0, 180.0, 0.0, 0.0 };

// Declarations
ViSession local_vi = VI_NULL;
ViStatus error = VI_SUCCESS;
ViChar errMsg[2 * VIBUF_LEN];
ViRsrc resource = REMOTE_ADDRESS;
ViInt32 response;											// Query returned
ViReal64* dataNorm = new ViReal64[MAX_MEMORY_PER_CHANNEL];	// Pointer of an array of values normalized between -1 and +1. Output [V] = data [-1, 1] * Amplitude + 2 * Offset
ViInt32* wfmHandles = new ViInt32[MAX_STEP_PER_CHANNEL];	// Pointer of an array of segment per step
ViInt32* wfmLoopCounts = new ViInt32[MAX_STEP_PER_CHANNEL];	// Pointer of an array of number of loops per step
ViUInt8* wfmMode = new ViUInt8[MAX_STEP_PER_CHANNEL];		// Pointer of an array of advance mode and sync state per step
Table sequence[MAX_STEP_PER_CHANNEL];						// Sequence table structure
int counter;												// Counting number of segment loaded
long totalMemory;											// Total arbitrary memory allocated
double amplitude, dcOffset, triggerLevel;					// Amplitude [Vpp], offset [Vdc] and trigger level [Vdc]

// Functions
double Maximum(double, double);										// Function to return the maximum between two values
string CommaSeparator(long);										// Function to add comma ',' separator for thousand
int loadSquareWaveformData(double, float, ViInt32 &);				// Function to load a Square wave
int loadSineWaveformData(double, double, float, int, ViInt32 &);	// Function to load a Sine wave
int loadDCLevelWaveformData(double, double, ViInt32 &);				// Function to load a DC level waveform data

int _tmain(int argc, _TCHAR* argv[])
{
	// Declarations
	int i, n;
	double memoryUsage;

	// Open I/O session
	checkErr(ww257x_InitWithOptions(resource, VI_TRUE, VI_TRUE, "Simulate=0", &local_vi));

	// Check Sample clock rate
	checkErr(ww257x_ConfigureSampleRateSource(local_vi, WW257X_VAL_ARB_INTERNAL));	// Set internal sample rate source
	if ((SCLK < MIN_SCLK) || (SCLK > MAX_SCLK))
	{
		printf("SCLK out of range\n\n");
		cout << "Press 'Enter' button to quit the Console Application";
		cin.get();
		ww257x_close(local_vi);
		return 0;
	}
	else
		checkErr(ww257x_ConfigureSampleRate(local_vi, SCLK));				// Set sample clock rate

	// Check Voltage levels
	if (LEVEL_LOW > LEVEL_HIGH)
	{
		printf("Low level greater than high level\n\n");
		cout << "Press 'Enter' button to quit the Console Application";
		cin.get();
		ww257x_close(local_vi);
		return 0;
	}
	else
	{
		amplitude = LEVEL_HIGH - LEVEL_LOW;
		dcOffset = LEVEL_HIGH + LEVEL_LOW;
		if ((amplitude < MIN_AMPLITUDE) || (amplitude > MAX_AMPLITUDE))
		{
			printf("Amplitude out of range\n\n");
			cout << "Press 'Enter' button to quit the Console Application";
			cin.get();
			ww257x_close(local_vi);
			return 0;
		}
		else
		{
			if ((dcOffset < MIN_OFFSET) || (dcOffset > MAX_OFFSET))
			{
				printf("DC Offset out of range\n\n");
				cout << "Press 'Enter' button to quit the Console Application";
				cin.get();
				ww257x_close(local_vi);
				return 0;
			}
			else
			{
				triggerLevel = TRIGGER_LEVEL;
				if ((triggerLevel < MIN_TRIGGER_LEVEL) || (triggerLevel > MAX_TRIGGER_LEVEL))
				{
					printf("Trigger level out of range\n\n");
					cout << "Press 'Enter' button to quit the Console Application";
					cin.get();
					ww257x_close(local_vi);
					return 0;
				}
				else
				{
					if ((TRIGGER_SLOPE == 0) || (TRIGGER_SLOPE == 1))
					{
						printf("Amplitude %gVpp, DC Offset %gV and SCLK rate %s", amplitude, dcOffset, CommaSeparator((long)SCLK).c_str());
						cout << "Sa/s" << endl;
						printf("Triggering level at %gV on a %s\n\n", triggerLevel, TriggerSlopeType[TRIGGER_SLOPE]);
					}
					else
					{
						printf("Trigger slope out of range\n\n");
						cout << "Press 'Enter' button to quit the Console Application";
						cin.get();
						ww257x_close(local_vi);
						return 0;
					}
				}
			}
		}
	}
	// modifiable 
	int nsteps = 5; //  1 or 2 = wminus only, 3 or 4 = wminus + wplus, 5 = everything

	double wminus = 1600.0;
	
	double wplus = 656252.0; // 130In //646445.9 135Te// 150Ce 1164702.5; // 1118649.8;// // //133Cs = 656250.0 //142Cs = 614447.6
	double wc = 657844.5; //130I648038.4 135Te // 150Ce 1166293.3; // 1120240.8;//1797579.0;// 1181999.3;// 1121410.2;// 130In = 672935.5; // 616040.4; // 657844.5;// 133Cs = 657844.5; //// 142Cs = 616040.4

	double wminus_phase = -140.0;// -110.0;// 30.0;
	double wplus_phase = 0.0;
	double wc_phase = 0.0;

	double wminus_amp = 0.0005;// 0.0035;// 0.003;//0.0045;// 0.0075
	double wplus_amp = 0.2;//0.22;  //0.11
	double wc_amp = 0.5;

	int wminus_loops = 1; // don't change
	int wplus_loops = 100;// 133Cs = 100;
	int wc_loops = 208;// 212;// 133Cs = 210
	 
	int wminus_length = 3;// 3 ; // 2
	int wplus_length = 1;
	int wc_length = 1; // don't change

	int tacc = 68;// 220040;// 234075; // 240023;// 250063; // 190318;// 148010;// 60008 18500; // time in us
	//int tacc 55.21	// Load three arbitrary waveforms consecutively on all channels

	// modifiable

	
	for (n = 0; n < 4; n++)
	{
		counter = 0;
		totalMemory = 0;

		printf("Load on Channel #%s:\n", ChannelNumber[n]);
		checkErr(ww257x_ConfigureOutputMode(local_vi, WW257X_VAL_OUTPUT_ARB));	// Set arbitrary output
		checkErr(ww257x_SetActiveChannel(local_vi, CH[n]));						// Set active channel
		checkErr(ww257x_ClearArbWaveform(local_vi, WW257X_VAL_ALL_WAVEFORMS));	// Removes all previously created arbitrary waveforms
		error = loadSineWaveformData(wminus, wminus_phase + dphi[n], wminus_amp, wminus_loops, response);					// First waveform loaded as a 2.6kHz Square wave with 50% duty cycle
		error = loadDCLevelWaveformData(1E-6, 0.0, response);
		//error = loadSineWaveformData(wc, wc_phase + qphi[n], wc_amp, wc_loops, response);
		error = loadSineWaveformData(wplus, wplus_phase + dphi[n], wplus_amp, wplus_loops, response);//wplus, wplus_phase + dphi[n], wplus_amp, wplus_loops, response);			// Second waveform loaded as a 616.04kHz Sine wave of 351 cycles with gain 1 and 0deg starting phase
		////error = loadSineWaveformData(1600, wplus_phase + dphi[n], 0.012, 4, response);
		error = loadDCLevelWaveformData(1E-6, 0.0, response);					// Third waveform loaded as a DC level at 0V during 384us
		error = loadSineWaveformData(wc, wc_phase + qphi[n], wc_amp, wc_loops, response);
		
		if (error != VI_SUCCESS)
		{
			printf("Load %i arbitrary waveforms error\n\n", counter);
			cout << "Press 'Enter' button to quit the Console Application";
			cin.get();
			ww257x_close(local_vi);
			return 0;
		}

		// Check memory usage
		totalMemory = totalMemory + (counter - 1) * MIN_RESOLUTION;
		if (totalMemory > MAX_MEMORY_PER_CHANNEL)
		{
			printf("Memory usage exceeding limit\n\n", counter);
			cout << "Press 'Enter' button to quit the Console Application";
			cin.get();
			ww257x_close(local_vi);
			return 0;
		}
		else
		{
			memoryUsage = (double)totalMemory / MAX_MEMORY_PER_CHANNEL * 100;
			printf(" - Total of %0.1f%% memory usage with %s samples\n", memoryUsage, CommaSeparator(totalMemory).c_str());
		}

		// Load arbitrary sequence
		int steps = nsteps;							// Number of steps in the sequence table
		wfmHandles[0] = sequence[0].segment;	// Step #1 with the DC level waveform as the third waveform loaded
		wfmHandles[1] = sequence[1].segment;	// Step #2 with the Square waveform as the first waveform loaded
		wfmHandles[2] = sequence[2].segment;	// Step #3 with the Sine waveform as the second waveform loaded
		wfmHandles[3] = sequence[3].segment;
		wfmHandles[4] = sequence[4].segment;
		sequence[0].loops = wminus_length;					// Step #1 execute Once
		sequence[1].loops = 100;// 6000;
		sequence[2].loops = wplus_length;// wplus_length;					// Step #2 execute Two times
		sequence[3].loops = 1+tacc;					// Step #3 execute One time
		sequence[4].loops = wc_length;
		sequence[0].sync = 1;					// Step #1 with sync state ON
		sequence[1].sync = 0;					// Step #2 with Sync state OFF
		sequence[2].sync = 0;
		sequence[3].sync = 0;					// Step #3 will Sync state OFF
		sequence[4].sync = 0;
		sequence[0].mode = 0;					// Step #1 will advance to Step #2
		sequence[1].mode = 0;					// Step #2 will advance to Step #3
		sequence[2].mode = 0;
		sequence[3].mode = 0;					// Step #3 will advance to Step #1 if the sequence table is executed more than Once
		sequence[4].mode = 0;

		for (i = 0; i < steps; i++)
		{
			wfmLoopCounts[i] = sequence[i].loops;
			wfmMode[i] = sequence[i].sync * 2 + sequence[i].mode;
			checkErr(ww257x_ConfigureSyncSignal(local_vi, wfmHandles[i], WW257X_VAL_SYNC_BIT, VI_TRUE, 0));				// Set Sync Out position
		}
		checkErr(ww257x_ConfigureOperationMode(local_vi, CH[n], WW257X_VAL_OPERATE_TRIGGERED));							// Set trigger mode
		checkErr(ww257x_ConfigureTriggerSource(local_vi, CH[n], WW257X_VAL_EXTERNAL));									// Set trigger source
		checkErr(ww257x_ConfigureTriggerLevel(local_vi, TRIGGER_LEVEL));												// Set trigger level
		if (TRIGGER_SLOPE == 0)
			checkErr(ww257x_ConfigureTriggerSlope(local_vi, WW257X_VAL_TRIGGER_NEGATIVE));								// Set negative trigger slope
		else
			checkErr(ww257x_ConfigureTriggerSlope(local_vi, WW257X_VAL_TRIGGER_POSITIVE));								// Set positive trigger slope
		checkErr(ww257x_CreateArbitrarySequenceAdv(local_vi, steps, wfmHandles, wfmLoopCounts, wfmMode, &response));	// Load sequence table
		checkErr(ww257x_ConfigureArbSequence(local_vi, CH[n], response, amplitude, dcOffset));							// Set voltage levels
		checkErr(ww257x_ConfigureOutputMode(local_vi, WW257X_VAL_OUTPUT_SEQ));											// Set arbitrary sequence output
		checkErr(ww257x_ConfigureSequenceAdvance(local_vi, WW257X_VAL_AUTO, WW257X_VAL_EXTERNAL));						// Set sequence advance
		checkErr(ww257x_ConfigureRefClockSource(local_vi, WW257X_VAL_REF_CLOCK_EXTERNAL));
		printf(" - Sequence #%i with %i steps\n\n", response, steps);
	}

	// Enable all channels
	for (n = 0; n < 4; n++)
		checkErr(ww257x_ConfigureOutputEnabled(local_vi, CH[n], VI_TRUE));
	printf("All Channels are enabled.\n\n");

	{
		// Print File (Trenton)
		//Open File
		wfstream myfil;
		myfil.open("C:/Users/cpt/Box Sync/piicr_2018/DataRecord_march2018.txt", fstream::app);
		/*
		// Time
		std::chrono::time_point < std::chrono::system_clock > endt;
		endt = std::chrono::system_clock::now();
		std::time_t endti = std::chrono::system_clock::to_time_t(endt);
		*/

		time_t ltime;
		wchar_t buf[26];
		errno_t err;

		time(&ltime);

		err = _wctime_s(buf, 26, &ltime);


		//Print Line
		myfil << tacc << "\t" << wc << "\t" << wc_loops << "\t" << wplus << "\t" << wplus_loops << "\t"<< wminus_phase << "\t" << wminus_amp << "\t" << buf;

		//Close File
		myfil.close();
		printf("Record Uploaded!!! \n \n");

		// Exit
		cout << "Press 'Enter' button to quit the Console Application";
		cin.get();
	}

// Clean-up pointers
	delete[] dataNorm, wfmHandles, wfmLoopCounts; wfmMode;


Error:
	// Process any errors
	if (error != VI_SUCCESS)
	{
		printf("\n\nError :\n\nDriver Status:  (Hex 0x%x)\n\n", error);
		ww257x_GetError(local_vi, &error, sizeof(errMsg), errMsg);
		printf("%s", errMsg);
	}

	// Close I/O session
	ww257x_close(local_vi);

	return 0;
}

// Function to return the maximum between two values
double Maximum(double a, double b)
{
	if (a >= b)
		return a;
	else
		return b;
}

// Function to add comma ',' separator for thousand
string CommaSeparator(long size)
{
	// Conversion long to string
	stringstream ss;
	ss << size;
	string str = ss.str();

	switch (str.length())
	{
	case 4:
		str.insert(1, ",");	// 1,234
		break;
	case 5:
		str.insert(2, ",");	// 12,345
		break;
	case 6:
		str.insert(3, ",");	// 123,456
		break;
	case 7:
		str.insert(1, ",");	// 1,234567
		str.insert(5, ",");	// 1,234,567
		break;
	case 8:
		str.insert(2, ",");	// 12,345678
		str.insert(6, ",");	// 12,345,678
		break;
	case 9:
		str.insert(3, ",");	// 123,456789
		str.insert(7, ",");	// 123,456,789
		break;
	case 10:
		str.insert(1, ",");	// 1,234567891
		str.insert(4, ",");	// 1,234,567891
		str.insert(8, ",");	// 1,234,567,891
		break;
	default:
		break;
	}

	return str;
}

// Function to load a Square wave
int loadSquareWaveformData(double frequency, float dutyCycle, ViInt32 &response)
{
	// Declarations
	int size;
	div_t divperiod;
	long period;
	double frequencyEff;

	// Calculate a rough number of samples
	size = (int)(SCLK / frequency);
	if (size < MIN_SIZE)
		size = MIN_SIZE;

	// Calculate the period taking into account the minimum resolution
	divperiod = div(size, MIN_RESOLUTION);
	if (divperiod.quot * MIN_RESOLUTION < size)
		period = (divperiod.quot + 1) * MIN_RESOLUTION;
	else
		period = divperiod.quot * MIN_RESOLUTION;
	//printf("Period = %i\n", (ViInt32)period);

	// Check memory allocation
	totalMemory = totalMemory + period;
	if (totalMemory > MAX_MEMORY_PER_CHANNEL)
		return 1;	// Error
	else
		frequencyEff = SCLK / period;

	// High level wavelength
	double highLevel = period * dutyCycle;

	// Create a square waveform data normalized between -1.0 and +1.0
	for (int i = 0; i < (int)highLevel; i++)
		dataNorm[i] = 1.0;						// High level
	for (int i = (int)highLevel; i < (int)period; i++)
		dataNorm[i] = -1.0;						// Low level
	checkErr(ww257x_CreateArbWaveform(local_vi, (ViInt32)period, dataNorm, &response));
	sequence[counter].segment = response;		// Save waveform handle number
	printf(" - Segment #%i of %s samples as %.8gHz Square wave ", response, CommaSeparator(period).c_str(), frequencyEff);
	cout << dutyCycle * 100 << "% duty cycle" << endl;

	// Increment counter
	counter++;

Error:
	// Process any errors
	if (error != VI_SUCCESS)
	{
		printf("\n\nError :\n\nDriver Status:  (Hex 0x%x)\n\n", error);
		ww257x_GetError(local_vi, &error, sizeof(errMsg), errMsg);
		printf("%s", errMsg);
	}

	return 0;
}

// Function to load a Sine wave
int loadSineWaveformData(double frequency, double startPhase, float gain, int mCycles, ViInt32 &response)
{
	// Declarations
	int size;
	div_t divWavelength;
	long wavelength;
	double frequencyEff, period;

	// Check if the gain is between 0 and 1
	//!\ Better to keep gain at 1 and change the amplitude in order to have full vertical resolution on 
	if ((gain < 0) || (gain > 1))
		return 1; // Error

	// Calculate a round number of samples
	size = (int)(mCycles * SCLK / frequency);
	if (size < MIN_SIZE)
		size = MIN_SIZE;
	//printf("   size = %s\n", CommaSeparator((long)size).c_str());

	// Calculate the wavelength as a multiple of the resolution
	divWavelength = div(size, MIN_RESOLUTION);
	if (divWavelength.quot * MIN_RESOLUTION < size)
		wavelength = (divWavelength.quot + 1) * MIN_RESOLUTION;
	else
		wavelength = divWavelength.quot * MIN_RESOLUTION;

	// Check memory allocation
	totalMemory = totalMemory + wavelength;
	if (totalMemory > MAX_MEMORY_PER_CHANNEL)
		return 2;	// Error

	// Calcul period and effective frequency
	period = (double)wavelength / mCycles;
	//printf("   period = %g\n", period);
	frequencyEff = SCLK / period;

	// Create a sine waveform data of m period(s) normalized between -1.0 and +1.0
	double omega = 2 * PI * frequencyEff;
	double dT;
	for (int i = 0; i < wavelength; i++)
	{
		dT = i / SCLK;																// Time duration
		dataNorm[i] = gain * sin(fmod(omega * dT + startPhase * PI / 180, 2 * PI));	// Sine wave normalized between -1.00 and +1.00 of the DC amplitude applied
		//printf("  data[%i] = %g\n", i, dataNorm[i]);
	}
	checkErr(ww257x_CreateArbWaveform(local_vi, (ViInt32)wavelength, dataNorm, &response));
	sequence[counter].segment = response;		// Save waveform handle number
	printf(" - Segment #%i of %s samples as %.8gHz Sine wave %gdeg start phase\n", response, CommaSeparator(wavelength).c_str(), frequencyEff, startPhase);

	// Increment counter
	counter++;

Error:
	// Process any errors
	if (error != VI_SUCCESS)
	{
		printf("\n\nError :\n\nDriver Status:  (Hex 0x%x)\n\n", error);
		ww257x_GetError(local_vi, &error, sizeof(errMsg), errMsg);
		printf("%s", errMsg);
	}

	return 0;
}

// Function to load a DC level wave
int loadDCLevelWaveformData(double duration, double level, ViInt32 &response)
{
	// Declarations
	int size;
	div_t divperiod;
	long wavelength;
	double durationEff;

	// Calculate a rough number of samples
	size = (int)(duration * SCLK);
	if (size < MIN_SIZE)
		size = MIN_SIZE;

	// Calculate the period taking into account the minimum resolution
	divperiod = div(size, MIN_RESOLUTION);
	if (divperiod.quot * MIN_RESOLUTION < size)
		wavelength = (divperiod.quot + 1) * MIN_RESOLUTION;
	else
		wavelength = divperiod.quot * MIN_RESOLUTION;

	// Check memory allocation
	totalMemory = totalMemory + wavelength;
	if (totalMemory > MAX_MEMORY_PER_CHANNEL)
		return 1;	// Error
	else
		durationEff = wavelength / SCLK;

	// Check DC level
	if (level > LEVEL_HIGH)
		return 2;		// Error
	else if (level < LEVEL_LOW)
		return 3;		// Error

	// Create a DC level waveform data normalized between -1.0 and +1.0
	for (int i = 0; i < wavelength; i++)
		dataNorm[i] = (2 * level - dcOffset) / amplitude;
	checkErr(ww257x_CreateArbWaveform(local_vi, (ViInt32)wavelength, dataNorm, &response));
	sequence[counter].segment = response;		// Save waveform handle number
	printf(" - Segment #%i of %s samples as %gV DC level during %Es\n", response, CommaSeparator(wavelength).c_str(), level, durationEff);

	// Increment counter
	counter++;

Error:
	// Process any errors
	if (error != VI_SUCCESS)
	{
		printf("\n\nError :\n\nDriver Status:  (Hex 0x%x)\n\n", error);
		ww257x_GetError(local_vi, &error, sizeof(errMsg), errMsg);
		printf("%s", errMsg);
	}

	return 0;
}
