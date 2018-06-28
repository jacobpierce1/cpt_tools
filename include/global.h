#ifndef GLOBAL_H
#define GLOBAL_H


#ifdef WINDOWS
#include <windows.h>
#else
#include <unistd.h>
#endif

void mySleep(int sleepMs)
{
#ifdef WINDOWS
    Sleep(sleepMs);
#else
    usleep(sleepMs * 1000);   // usleep takes sleep time in us (1 millionth of a second)
#endif
}



#endif 
