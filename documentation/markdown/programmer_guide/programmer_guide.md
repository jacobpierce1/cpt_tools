# Phase Imaging Control System: Programmer Guide 

## Overview 

This program was written to replace and extend the functionality of CoboldPC, the software written by RoentDek to communicate with the TDC, visualize aggregated data, and perform data cuts and fits. CoboldPC served its purpose well while it was used, but presented several problems which could not be fixed without completely new software, including the following:

* Inability to communicate with Tabor from same program controlling TDC
	* 	Inability to track Tabor parameters, so that they needed to be saved separately from the TDC data
	*  User liability of remembering to pause the TDC during Tabor switching
	*  User liability of naming files, occasionally leading to the wrong Tabor parameters being associated with a file
*  Lack of knowledge of the specific event grouping algorithm used
*  No error analysis
*  Lack of any form of real-time data analysis for integrating multiple data sessions (i.e. performing phase-imaging analysis)
*  Unclear user interface, unable to be used effectively without copious instruction
*  Unable to modify source code to add any of the above features

Because of these problems, CoboldPC presented an overall roadblock in quickly estimating ion frequencies, which are important for setting the electrode RF excitation parameters.

## TDC Controls

### Overview

RoentDek provided a C API for communicating with the TDC. I have no idea where it came from, since I didn't see it on their website -- I inherited the code from Dmitry (Insert last name). I think that he contacted RoentDek via email to obatin it. 

The module `tdc.py` imports the TDC API using the `ctypes` module which, believe it or not, worked with no hassle at all. In the module, the class `TDC` is implemented which wraps most of the functionality exposed by the API, not some of the never-used functions though. 

The TDC module is currently implemented to perform the bare minimum of functionality that you would ever want out of the TDC. That means there is no phase-imaging related processing done in this class. I designed it this way because if anyone in the group ever wanted to use this TDC or an identical RoentDek TDC for another application, this module would be exactly what you need for handling the data acquisition without having to worry about figuring out how to connect to the TDC, unpack the binary data, sort it, and compute timestamps. If someone were to use the TDC for another application, it is possible that they would want to use some of the functionality in the API which I didn't implement. It should be easy to do so by looking at the functions in the API and repeating the way I wrapped them in this module.


### Configuration File

There is a configuration file in the same directory as the gui called `global.cfg`. This file contains the configuration parameters that are supplied to the TDC every time a new connection is made to the TDC. Don't move this file, because otherwise it will not be found when the program is loaded. The specific settings in the configuration file are important for the DAQ working properly. For example, all the pulses coming out of the discriminators and entering the TDC are negative, so only falling transitions need to be recorded. If rising transitions were recorded, then the transitions back to 0 from the negative pulses would be recorded, unnecessarily doubling the amount of data to be processed. For more details on what parameters are set here, refer to the TDC manual. 


### Data Stream

The TDC does not store all hits in a giant array, but rather one buffer for all information. When a positive or negative pulse above the TDC threshold in magnitude (specific numbers are in the TDC manual) is achieved, a `Hit` (typedef of a 32-bit integer) is added to the TDC data buffer. The `Hit` contains the channel number, whether the pulse was rising or falling, and the time of the transition modulo 512 micro-seconds (more on this in the Rollovers section). 

When the data comes out of the TDC, it is only partially sorted by time, meaning that if you look at all the data output from a read, it is _mostly_ sorted by time, but far from completely sorted. The most efficient way to do event grouping requires the data to be sorted, which is actually somewhat tricky (see the section on Rollovers). To see how the data is sorted, take a look at the function `TDC.sort_data`. 

### Rollovers 

Given the femto-second timing resolution of the TDC, it is not possible for absolute timestamps to be recorded without requiring an arbitrarily large size for each data time. The TDC's way of working around this is to only count relative timestamps up to a certain time (2^24 * , then transmit the number of "rollovers", or times that the 512 micro-second counter has reached its maximum capacity, that have thus far been achieved. The absolute timestamp of a given event can then be computed as:
	
	absolute time =  number of rollovers * 2^24 + relative time

where relative time is the time of the event as reported by the TDC, i.e. the time elapsed since the last rollover was reported. There is an analogous counter for when the maximum number of rollovers (also 2^24) is achieved. After this, the time will be incremented appropriately, even though the rollover counter resets, because there is a counter for the number of times the rollover counter is reset (called `num_rollover_loops`).

The rollovers have another important property, which is that while data between rollovers may not be sequential, rollovers _are_ sequential, both relative to each other and other real data. In other words, if the rollover counter is achieved while data is being collected (which doesn't happen very frequently, but I did notice it happening), then a rollover is issued before any other new data is. That means that the user doesn't need to manually check for counter resets since the rollovers are always sequentially reported (again, unlike the other data). 

The fact that the rollovers are reliably sequential is also critical for properly sorting the data. Suppose we get the following sequence of data, where the first entry of each tuple is the channel number or "r" for rollover and the next number is the relative time or rollover count: 

	(0,100), (r,12), (1,50)

If we just sorted all the data by time without paying attention to the rollover, then it would appear that the event on channel 1 occurred first. The presence of the rollover means that it actually happened second. Since the non-rollover data is only partially sorted, the way to properly sort it is to sort each subset of the data contained between groups of rollovers. For example, if the sequence is `(0,3), (0,2), (0,1), (r,12), (r,13), (r,13), (1,3), (1,2), (1,1)`, then the algorithm to sort the data is to sort the hits on channel 0 (ignoring the rest of the data), skip through the group of sequential rollovers, then sort the data on channel 1. 

Note that this is unrealistic data, it is just meant to illustrate the point that the sorting is performed on chunks of data located between sequential rollovers. See the function `tdc.sort_data` for the implementation.


### Other information

The grouping mode does not work for batch reads. If you try to use the grouping mode (set in global.cfg) and read data where there were N hits, you will just read the oldest hit that was not previously read. In principle you could keep constantly reading data, but it seemed to me that even constantly reading at the fastest rate could not keep up with typical data rates. Thus, I recommend to continue operating the TDC not in group mode.



## `LiveCPTdata`: Event Detection and Processing

### Overview 

Once the raw TDC binary data has been extracted to channels and times and is sorted, the data needs to be processed in a way specific for phase-imaging to detect events and compute the MCP position and time of flight (the time between the Penning trap eject pulse and the MCP hit, also known as TOF) for each event. 

Two classes are provided for this: `CPTdata`, which is a data container for non-real-time processing, and `LiveCPTdata`, which is the same data container with functions modified to avoid redundant computations in real-time processing. The `LiveCPTdata` is used for DAQ and saving of processed data. That is where the functions for event detection and processing are implemented. The `CPTdata` has no connection to the TDC, and is only used for loading data that has previously been saved by the `LiveCPTdata`. 


### Event detection algorithm


### MCP position and TOF


### Setting Cuts


### Adding more cuts to the current code 

With the current implementation, adding more cuts is easy, but requires changes in a number of places. Just repeat the code in `live_cpt_data.set_cuts`, add a variable in `live_cpt_data.__init__` which will track the current cut, copy the code in `live_cpt_data.apply_cuts`, repeat the analogous code in the class `cpt_data`, and copy all the references to cuts in `plotter_widget`. 


## GUI 

### Overview 



## Features that can be added 

Here is a list of features that can be added. Once a feature is added, make sure to add the corresponding documentation to this manual and the user guide. 

* Button that loads previous session's Tabor settings
* Ability to fit any spectrum by clicking regions in plot  
* Implementation of the phase predictions 
* Option to save the tables of measured angles and predictions, since it takes time to put the numbers in the table 
* Other plots
* Other displayed metadata (e.g. number of events is currently displayed metadata)
* More cut options 
* Error estimates in mass identifier from AME mass error estimates

## Bugs that may occur

Off the top of my head, here are things I haven't tested as much that may occur:

* Absolute timestamp accuracy

## Contact 
Jacob Pierce, Sep 2017 – Sep 2018

* Initially architected and developed system

Dwaipayan Ray

* First PhD student to test system

**Add other contributors here, so that if someone has questions about the program in the future, they know who they can contact.**

