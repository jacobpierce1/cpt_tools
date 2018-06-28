#ifndef GLOBAL_H
#define GLOBAL_H


#ifdef WINDOWS
#include <windows.h>
#else
#include <unistd.h>
#endif



void mySleep(int sleepMs);


#endif 
