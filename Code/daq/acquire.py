#!/usr/bin/python

"""

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

This is the only non-oo module in the package.
When we use multiprocessing to fork, we have to
be able to pickle whatever function we send, which can't
be done with class instance methods, so this is the replacement.


"""

from PyDAQmx import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxFunctions import *

from multiprocessing import Queue

import numpy as np
import OpenOPC
import time
import ctypes



def acquire(settings,dataQueue,controlEvent,captureRunningEvent,recordingEvent,errorQueue,
    dataStreamQueue,messageQueue,currentVolt,currentSamples,currentFreq,
    currentThick,currentThin,currentPower,currentLW):

    settings.sanitise() # don't want things to go wrong here

    # constants
    timeout = 1000.0 # arbitrary - change in future
    maxRate = 10000.0

    # create task handles
    countTaskHandle = TaskHandle(0)
    aoTaskHandle = TaskHandle(0)
    aiTaskHandle = TaskHandle(0)

    # create tasks
    DAQmxCreateTask("", byref(countTaskHandle))
    DAQmxCreateTask("", byref(aoTaskHandle))
    DAQmxCreateTask("", byref(aiTaskHandle))

    # configure channels
    DAQmxCreateCICountEdgesChan(countTaskHandle, 
                                settings.counterChannel, "",
                                DAQmx_Val_Falling, 0, DAQmx_Val_CountUp)

    DAQmxCfgSampClkTiming(countTaskHandle, 
                          settings.clockChannel,
                          maxRate, DAQmx_Val_Falling, 
                          DAQmx_Val_ContSamps, 1)

    DAQmxCreateAOVoltageChan(aoTaskHandle, 
                             settings.aoChannel,
                             "", -10,
                             10,
                             DAQmx_Val_Volts, None)

    DAQmxCreateAIVoltageChan(aiTaskHandle,
                             settings.aiChannel, "",
                             DAQmx_Val_RSE, -10.0, 10.0,
                             DAQmx_Val_Volts, None)

    # start tasks
    DAQmxStartTask(countTaskHandle)
    DAQmxStartTask(aoTaskHandle)
    DAQmxStartTask(aiTaskHandle)

    lastCount = uInt32(0)
    countData = uInt32(0) # the counter
    
    AIChannels = settings.aiChannel.count(',')+1
    aiData = np.zeros((AIChannels,),dtype=np.float64) 

    # need to perform a count here that we then throw away
    # otherwise get mysterious low first count
    DAQmxReadCounterScalarU32(countTaskHandle,
                              timeout,
                              byref(countData), None)
    
    messageQueue.put((True, "NI Communication established..."))
    # begin acquisition loop
    while True:
        # try:
            DAQmxWriteAnalogScalarF64(aoTaskHandle, 
                                      True, timeout,
                                      currentVolt.value, None)
            
            timestamp = time.time()

            DAQmxReadCounterScalarU32(countTaskHandle, 
                                      timeout,
                                      byref(countData), None)

            counts = countData.value - lastCount.value
            lastCount.value = countData.value

            DAQmxReadAnalogF64(aiTaskHandle,-1, timeout,
                DAQmx_Val_GroupByChannel,aiData, 
                AIChannels,byref(ctypes.c_long()),None)
            
            if captureRunningEvent.is_set() and recordingEvent.is_set():
                currentSamples.value = currentSamples.value + 1
                
                dataQueue.put((counts, aiData,currentVolt.value,currentFreq.value, timestamp,
                        currentThick.value,currentThin.value,currentPower.value,currentLW.value))
                
            dataStreamQueue.put((counts, aiData,currentVolt.value,currentFreq.value, timestamp,
                    currentThick.value,currentThin.value,currentPower.value,currentLW.value))

        # except:
        #     errorQueue.put(True)
        #     time.sleep(0.01)

def acquireCW(settings, freqQueue,controlEvent,captureRunningEvent,recordingEvent,
    newFreqEvent,errorQueue,messageQueue,currentVolt,
    currentFreq,currentThick,currentThin,currentPower,
    currentLW,currentCycle,pPerCycle,pForHRS,pPulse):

    settings.sanitise() # don't want things to go wrong here

    path = 'CRIS local SVs for Python'

    opc = OpenOPC.client()
    opc.connect('National Instruments.Variable Engine.1')

    tags = ['.Wavenumber Channel 1',
            '.Power Channel 1',
            '.PythonSuperCycleBunches',
            '.PythonHRSBunches',
            '.PythonSuperCycleBunches',
            '.PythonSuperCycleStart']

    tags = [path+tag for tag in tags]
    opc.read(tags, group = 'CW Variables')

    messageQueue.put((True, "CW Communications established"))

    controlEvent.set()

    while True:
        # try:
            if newFreqEvent.is_set():
                newFreqEvent.clear()
                scanVariables = freqQueue.get()

                variable = scanVariables[0]

                currentVolt.value = scanVariables[1][variable]

                time.sleep(0.01)

                controlEvent.set()

            else:
                variables = opc.read(group = 'CW Variables')

                currentFreq.value = variables[0][1]
                currentPower.value = variables[1][1]
                currentCycle.value = variables[2][1]
                pForHRS.value = variables[3][1]
                pPerCycle.value = variables[4][1]
                pPulse.value = variables[5][1]

                time.sleep(0.003)


        # except:
        #     errorQueue.put(True)
        #     time.sleep(0.01)


def acquireRILIS(settings, freqQueue,controlEvent,captureRunningEvent,recordingEvent,
    newFreqEvent,errorQueue,messageQueue,currentVolt,
    currentFreq,currentThick,currentThin,currentPower,
    currentLW,currentCycle,pPerCycle,pForHRS,pPulse):

    settings.sanitise() # don't want things to go wrong here

    path = 'CRIS local SVs for Python'

    opc = OpenOPC.client()
    opc.connect('National Instruments.Variable Engine.1')

    tags = ['.PythonWaveReadback',
            '.PythonThickReadback',
            '.PythonThinReadback',
            '.PythonPowerReadback',
            '.PythonLinewidthReadback',
            '.PythonSuperCycleBunches',
            '.PythonHRSBunches',
            '.PythonSuperCycleBunches',
            '.PythonSuperCycleStart']

    tags = [path+tag for tag in tags]
    opc.read(tags, group = 'RILISVariables')

    messageQueue.put((True, "RILIS Communications established"))

    controlEvent.set()

    opc.write((path + '.PythonIsNew',False))
    opc.write((path + '.PythonIsOK',False))

    while True:
        # try:
            if newFreqEvent.is_set():
                newFreqEvent.clear()
                scanVariables = freqQueue.get()

                variable = scanVariables[0]
                
                opc.write((path + '.PythonIsNew',False))

                if variable == 'wavelength':
                    opc.write((path + '.PythonWaveSet',scanVariables[1][variable]))

                elif variable == 'thin':
                    opc.write((path + '.PythonThinSet',scanVariables[1][variable]))

                elif variable == 'thick':
                    opc.write((path + '.PythonThickSet',scanVariables[1][variable]))

                time.sleep(0.1)

                opc.write((path + '.PythonIsNew',True))

                now = time.time()
                time.sleep(1.0)

                while not opc.read(path + '.PythonIsOk')[0]:
                    time.sleep(0.25)

                controlEvent.set()

            else:
                variables = opc.read(group = 'RILISVariables')

                currentFreq.value = variables[0][1]
                currentThick.value = variables[1][1]
                currentThin.value = variables[2][1]
                currentPower.value = variables[3][1]
                currentLW.value = variables[4][1]
                currentCycle.value = variables[5][1]
                pForHRS.value = variables[6][1]
                pPerCycle.value = variables[7][1]
                pPulse.value = variables[8][1]


                time.sleep(0.001)


        # except:
        #     errorQueue.put(True)
        #     time.sleep(0.01)


def clearcard(handles):
    """
    Clears all tasks from the card
    """

    for handle in handles:
      DAQmxStopTask(handle)
      DAQmxClearTask(handle)























def fastAcquire(settings,dataQueue,controlEvent,errorQueue,
    dataStreamQueue,messageQueue,currentFreq,currentThick,
    currentThin,currentPower,currentLW):

    settings.sanitise() # don't want things to go wrong here

    # constants
    timeout = 100000.0 # arbitrary - change in future
    maxRate = 10000.0

    # create task handles
    countTaskHandle = TaskHandle(0)
    aoTaskHandle = TaskHandle(0)
    aiTaskHandle = TaskHandle(0)

    # create tasks
    DAQmxCreateTask("", byref(countTaskHandle))
    DAQmxCreateTask("", byref(aoTaskHandle))
    DAQmxCreateTask("", byref(aiTaskHandle))

    # configure channels
    DAQmxCreateCICountEdgesChan(countTaskHandle, 
                                settings.counterChannel, "",
                                DAQmx_Val_Falling, 0, DAQmx_Val_CountUp)

    DAQmxCfgSampClkTiming(countTaskHandle, 
                          settings.clockChannel,
                          maxRate, DAQmx_Val_Falling, 
                          DAQmx_Val_ContSamps, 1)

    DAQmxCreateAOVoltageChan(aoTaskHandle, 
                             settings.aoChannel,
                             "", -10,
                             10,
                             DAQmx_Val_Volts, None)

    DAQmxCreateAIVoltageChan(aiTaskHandle,
                             settings.aiChannel, "",
                             DAQmx_Val_RSE, -10.0, 10.0,
                             DAQmx_Val_Volts, None)

    # start tasks
    DAQmxStartTask(countTaskHandle)
    DAQmxStartTask(aoTaskHandle)
    DAQmxStartTask(aiTaskHandle)

    nos = 10**4 #number of samples
    lastCount = 0
    countData = np.zeros(nos,dtype=np.uint32)
    aiData = np.zeros((settings.aiChannel.count(',')+1,),dtype=np.float64) 
    aiArrays = np.zeros((settings.aiChannel.count(',')+1,nos))

    messageQueue.put((True, "NI Communication established..."))

    # begin acquisition loop
    while True:
        try:
            DAQmxWriteAnalogScalarF64(aoTaskHandle, 
                                      True, timeout,
                                      currentVolt.value, None)
            t0 = time.time()
            DAQmxReadCounterU32(countTaskHandle, nos, timeout,
                                countData, nos, byref(ctypes.c_long()), None)
            t1 = time.time()

            DAQmxReadAnalogF64(aiTaskHandle,-1, timeout,
                DAQmx_Val_GroupByChannel,aiData, 
                2,byref(ctypes.c_long()),None)

            #Make arrays
            timeArray = np.linspace(t0,t1,nos)
            freqArray = np.repeat(currentVolt.value, nos)
            for i,ai in enumerate(aiData):
                aiArrays[i] = np.repeat(ai,nos)


            counts = np.append(countData[0]-lastCount,np.diff(countData))
            lastCount = countData[-1]
            
            if controlEvent.is_set():
                dataQueue.put((counts, aiArrays,freqArray, timeArray))
                dataStreamQueue.put((counts,aiArrays,freqArray,timeArray))
            else:
                dataStreamQueue.put((counts,aiArrays,freqArray,timeArray))
        except:
            errorQueue.put(True)
            time.sleep(0.01)
