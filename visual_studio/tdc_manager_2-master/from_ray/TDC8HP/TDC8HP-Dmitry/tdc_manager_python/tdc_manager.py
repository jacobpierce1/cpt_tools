from ctypes import * 

#Load DLL library
mydll = windll.LoadLibrary("TDC8HP_wrapper_x86.dll")
mydll.TDC8HP_GetState()
