#!/usr/bin/python

"""

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

Example usage:
interface = Interface(self.settings, callbackFunc)
interface.acquire()
interface.stopTasks()

Note - must call interface.stopTasks()
after data acquisition is complete, otherwise
channels will block.

"""


from PyDAQmx import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxFunctions import *

from multiprocessing import Pipe

class Interface:
    """
    Provides physical interface & callback using PyDAQmx
    """
    def __init__(self, callbackFunc):

        self.settings = None

        self.callbackFunc = callbackFunc # to report data to


    def createTask(self, settings):
        self.settings = settings
        self.settings.sanitise() # don't want things to go wrong here

        # constants
        self.timeout = 100.0 # arbitrary - change in future
        self.maxRate = 1000.0

        # create task handles
        self.countTaskHandle = TaskHandle(0)
        self.aoTaskHandle = TaskHandle(0)
        self.aiTaskHandle = TaskHandle(0)

        # create tasks
        DAQmxCreateTask("", byref(self.countTaskHandle))
        DAQmxCreateTask("", byref(self.aoTaskHandle))
        DAQmxCreateTask("", byref(self.aiTaskHandle))

        # configure channels
        DAQmxCreateCICountEdgesChan(self.countTaskHandle, 
                                    self.settings.counterChannel, "",
                                    DAQmx_Val_Rising, 0, DAQmx_Val_CountUp)
        DAQmxCfgSampClkTiming(self.countTaskHandle, 
                              self.settings.clockChannel,
                              self.maxRate, DAQmx_Val_Rising, 
                              DAQmx_Val_ContSamps, 1)

        DAQmxCreateAOVoltageChan(self.aoTaskHandle, 
                                 self.settings.aoChannel,
                                 "", self.settings.voltageMin,
                                 self.settings.voltageMax,
                                 DAQmx_Val_Volts, None)

        DAQmxCreateAIVoltageChan(self.aiTaskHandle,
                                 self.settings.aiChannel, "",
                                 DAQmx_Val_RSE, -10.0, 10.0,
                                 DAQmx_Val_Volts, None)

        # start tasks
        DAQmxStartTask(self.countTaskHandle)
        DAQmxStartTask(self.aoTaskHandle)
        DAQmxStartTask(self.aiTaskHandle)

    def acquire(self, queue):
        """
        Main acquire loop
        """
        lastCount = uInt32(0)
        countData = uInt32(0) # the counter
        aiData = float64(0)
        
        # set initial voltage
        aoVoltage = self.settings.voltageMin

        voltsPerInterval = (self.settings.voltageMax - \
                            self.settings.voltageMin) \
                           / float(self.settings.intervalsPerScan)


        DAQmxWriteAnalogScalarF64(self.aoTaskHandle, True, 
                                  self.timeout,
                                  aoVoltage, None)

        # begin acquisition loop
        for i in range(self.settings.scans):
            for j in range(self.settings.intervalsPerScan):

                DAQmxReadCounterScalarU32(self.countTaskHandle, 
                                          self.timeout,
                                          byref(countData), None)
                DAQmxReadAnalogScalarF64(self.aiTaskHandle, self.timeout,
                                         byref(aiData), None)

                aoVoltage = j * voltsPerInterval
                DAQmxWriteAnalogScalarF64(self.aoTaskHandle, 
                                          True, self.timeout,
                                          aoVoltage, None)

                # self.callbackFunc(i, j, countData.value - lastCount.value,
                #                   aiData.value)
                c = countData.value - lastCount.value
                queue.put( [i, j, c, aiData.value ] )
                
                lastCount.value = countData.value


        self.stopTasks()

            
    def stopTasks(self):
        """
        Halts current tasks
        """
        DAQmxStopTask(self.countTaskHandle)
        DAQmxStopTask(self.aoTaskHandle)
        DAQmxStopTask(self.aiTaskHandle)

        DAQmxClearTask(self.countTaskHandle)
        DAQmxClearTask(self.aoTaskHandle)
        DAQmxClearTask(self.aiTaskHandle)



    
    
