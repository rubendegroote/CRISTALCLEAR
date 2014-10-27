#!/usr/bin/python

"""
Demonstrates voltage stepping with
event counting.
"""

import ctypes

from PyDAQmx import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxFunctions import *

import numpy as np

if __name__ == "__main__":

    # constants
    timout = 100.0

    vMin = 0.0
    vMax = 5.0
    intervalsPerScan = 500
    scans = 1
    voltsPerInterval = (vMax - vMin) / intervalsPerScan

    counterChannel = "Dev1/ctr1"
    clockChannel = "/Dev1/PFI1"
    aoChannel = "/Dev1/ao0"
    aiChannel = "/Dev1/ai2"

    maxRate = 1000.0

    # create task handles
    countTaskHandle = TaskHandle(0)
    writeTaskHandle = TaskHandle(1)
    aiTaskHandle = TaskHandle(2)

    # create tasks
    DAQmxCreateTask("", byref(countTaskHandle))
    DAQmxCreateTask("", byref(writeTaskHandle))
    DAQmxCreateTask("", byref(aiTaskHandle))

    # configure channels
    DAQmxCreateCICountEdgesChan(countTaskHandle, counterChannel, "",
                                DAQmx_Val_Rising, 0, DAQmx_Val_CountUp)
    DAQmxCfgSampClkTiming(countTaskHandle, clockChannel, maxRate,
                          DAQmx_Val_Rising, DAQmx_Val_ContSamps, 1)

    DAQmxCreateAOVoltageChan(writeTaskHandle, aoChannel, "", vMin, vMax,
                             DAQmx_Val_Volts, None)
    DAQmxCreateAIVoltageChan(aiTaskHandle,aiChannel, "", 
                             DAQmx_Val_RSE, -10.0, 10.0,
                             DAQmx_Val_Volts, 
                             None)
    # DAQmxCfgSampClkTiming(aiTaskHandle,"OnboardClock",maxRate, 
    #                       DAQmx_Val_Rising, DAQmx_Val_ContSamps,1)

    # start tasks
    DAQmxStartTask(countTaskHandle)
    DAQmxStartTask(writeTaskHandle)
    DAQmxStartTask(aiTaskHandle)

    data = uInt32(0) # the counter

    combinedData = np.zeros((scans, intervalsPerScan), dtype=uInt32)
    
    r = float64(0)
    readVolts = np.zeros((scans, intervalsPerScan), dtype=float64)
    # begin acquisition loop
    for i in range(scans):
        for j in range(intervalsPerScan):
            DAQmxReadCounterScalarU32(countTaskHandle, timout,
                                      byref(data), None)
            DAQmxReadAnalogScalarF64(aiTaskHandle, timout, byref(r), None)
            readVolts[i][j] = r.value
            combinedData[i][j] = data.value
            voltage = j * voltsPerInterval
            DAQmxWriteAnalogScalarF64(writeTaskHandle, True, timout,
                                      voltage, None)


    # end tasks
    DAQmxStopTask(countTaskHandle)
    DAQmxStopTask(writeTaskHandle)
    DAQmxStopTask(aiTaskHandle)
    
    print readVolts


    
    
