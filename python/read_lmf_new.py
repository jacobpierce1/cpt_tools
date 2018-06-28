#2017_05_02
#by Dmitry A. Gorelov
#Read LMF-file with Python2 code
#tested on version 2.7.12 
#

import struct
import time

import numpy as np
import pandas as pd

def read_lmf(fileName):
    kx = 1.29
    ky = 1.31

    ##Read the file
    #fileName = "133Cs_ref_2017-04-28_670ms_morning.lmf"
    #fileName = "/Users/ray/Manitoba/CPT/ANL\ 2017/Analysis/2017\ June\ 26-30\ Run/c6h6_ref2_2017-06-30_120ms.lmf"
    file = open(fileName, 'rb')                                           ## 'rb' r for read, b for binary
    file.seek(0, 2)                                                       ##Go to the last byte of the file '2'=os.SEEK_END
    LMFileSize = file.tell()                                              ##Returns the position of the last byte = file's size
    file.seek(0, 0)                                                       ##Go to the beginning of the file '0'=os.SEEK_BEG
    LMHeadVersion = (struct.unpack('<I', file.read(4)))[0]                ##Read 4 bytes and converts them to unsigned int
    LMDataFormat = struct.unpack('<I', file.read(4))[0]                   ##Read 4 bytes and converts them to unsigned int
    LM64NumberOfCoordinates = struct.unpack('<Q', file.read(8))[0]        ##Read 8 bytes and converts them to unsigned int
    LM64HeaderSize = struct.unpack('<Q', file.read(8))[0]                 ##Read 8 bytes and converts them to unsigned int
    LM64UserHeaderSize = struct.unpack('<Q', file.read(8))[0]             ##Read 8 bytes and converts them to unsigned int
    LM64NumberOfEvents = struct.unpack('<Q', file.read(8))[0]             ##Read 8 bytes and converts them to unsigned int
    file.seek(4, 1)                                                       ##skip 4B '1'=os.SEEK_CUR              
    LMStartTime = struct.unpack('<Q', file.read(8))[0]                    ##Read 8 bytes and converts them to unsigned int
    file.seek(4, 1)                                                       ##skip 4B '1'=os.SEEK_CUR
    LMStopTime = struct.unpack('<Q', file.read(8))[0]                     ##Read 8 bytes and converts them to unsigned int

    ##Read the data block
    dataBlockOffset = LM64HeaderSize + LM64UserHeaderSize
    dataBlockSize = LMFileSize - dataBlockOffset
    file.seek(dataBlockOffset, 0)
    dataBlock = file.read(dataBlockSize)

    file.close()
    ##END Read the file

    dataOffset=0
    ##absolute position in the dataBlock

    eventList = [] 
    ##eventList stores events
    ##only events with 1, 2, 3, 4 and 7 non-zero channels aSre stored

    ##Loop through all events in the file 
    k=0
    for event in range(0, LM64NumberOfEvents):
        eventSize = dataBlock[dataOffset: dataOffset+4]
        eventSize = struct.unpack('<I', eventSize)[0]
        dataOffset += 4

        eventTrigger = dataBlock[dataOffset: dataOffset+4]
        eventTrigger = struct.unpack('<I', eventTrigger)[0]
        dataOffset += 4

        eventNumber = dataBlock[dataOffset: dataOffset+8]
        eventNumber = struct.unpack('<Q', eventNumber)[0]
        dataOffset += 8
        
        eventTimeStamp = dataBlock[dataOffset: dataOffset+8]
        eventTimeStamp = struct.unpack('<Q', eventTimeStamp)[0]
        dataOffset += 8

        ##eventTimeStamp is counted from the first event 
        ##absolute TimeStamp might be more useful
        if event == 0:
            eventTimeStampOffset = eventTimeStamp
        
        eventTimeStamp -= eventTimeStampOffset

        eventID = 0x0000
        TDC = [0]*8
        ##Loop through all 8 channels
        for channel in range(0, 8):
            channelStatus = 0
            channelValue = 0
            
            channelStatus = dataBlock[dataOffset: dataOffset+2]
            channelStatus = struct.unpack('<H', channelStatus)[0]
            dataOffset += 2
            
            if channelStatus != 0:
                channelValue = dataBlock[dataOffset: dataOffset+4]
                channelValue = struct.unpack('<i', channelValue)[0]
                dataOffset += 4
            
            TDC[channel] = channelValue
            eventID <<= 1
            eventID = eventID | channelStatus
        
        ##Skip reading Clock and Trigger channels of TDC   
        dataOffset += 2*(2 + 4)
        
        ##If an event has non-zero channels 1, 2, 3, 4 and 7, 
        ##then it is appended to the eventList 
        if (eventID & 0x00F2) == 0x00F2:
            x = 0.5*kx*(TDC[0] - TDC[1])*0.001
            y = 0.5*ky*(TDC[2] - TDC[3])*0.001
            tof = TDC[6]*0.001
            timeStamp = eventTimeStamp * (1.0e-12)
            eventList.append([x, y, tof, timeStamp])
            
    ##END Loop through all events in the file

    ##Output time information 
    print "Start:         (%d)" %LMStartTime, " ", time.strftime('%H:%M:%S %Y-%m-%d', (time.localtime(LMStartTime)))
    print "Stop:          (%d)" %LMStopTime, " ", time.strftime('%H:%M:%S %Y-%m-%d', (time.localtime(LMStopTime)))
    print "Run[secs]:      %d" %(LMStopTime-LMStartTime)

    ##Convertion of eventList to DataFrame
    dataLM = pd.DataFrame(eventList, columns=['X', 'Y', 'Tof', 'TStamp'])

    ##Converting pd.dataframe to np.array
    Data=dataLM.values
    
    ##Convertion of timeStamp strings to integers 

    LMStartTime_int = int(LMStartTime)
    LMStopTime_int = int(LMStopTime)
    
    return Data, LMStartTime_int, LMStopTime_int
#    return dataLM, LMStartTime_int, LMStopTime_int

    ##[X] = mm
    ##[Y] = mm
    ##[Tof] = ns
    ##[TStamp] = sec









