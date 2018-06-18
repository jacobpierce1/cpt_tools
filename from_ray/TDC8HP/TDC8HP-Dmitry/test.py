from ctypes import *

drv = cdll.LoadLibrary("hptdc_driver_3.4.3_x86_c_wrap.dll")

tdc = drv.TDCManager_New()

drv.TDCManager_SetParameter(tdc, "MMXEnable true")
drv.TDCManager_SetParameter(tdc, "SSEEnable false")
drv.TDCManager_SetParameter(tdc, "DMAEnable true")
drv.TDCManager_SetParameter(tdc, "TriggerEdge falling")
drv.TDCManager_SetParameter(tdc, "AllowOverlap false")
drv.TDCManager_SetParameter(tdc, "OutputLevel false")
drv.TDCManager_SetParameter(tdc, "RisingEnable none")
drv.TDCManager_SetParameter(tdc, "GroupingEnable false")
drv.TDCManager_SetParameter(tdc, "FallingEnable 0-7")
drv.TDCManager_SetParameter(tdc, "VHR true")
drv.TDCManager_SetParameter(tdc, "UseFineINL true")
drv.TDCManager_SetParameter(tdc, "GroupRangeStart -1ns")
drv.TDCManager_SetParameter(tdc, "GroupRangeEnd 1ns")
drv.TDCManager_SetParameter(tdc, "TriggerDeadTime 1ns")

drv.TDCManager_Reconfigure(tdc)

print(drv.TDCManager_GetState(tdc))

drv.TDCManager_Start(tdc)

drv.TDCManager_Stop(tdc)
drv.TDCManager_CleanUp(tdc)

drv.TDCManager_Delete(tdc)














