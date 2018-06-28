#include "global.h" 

void mySleep(int sleepMs)
{
#ifdef WINDOWS
    Sleep(sleepMs);
#else
    usleep(sleepMs * 1000);   // usleep takes sleep time in us (1 millionth of a second)
#endif
}
