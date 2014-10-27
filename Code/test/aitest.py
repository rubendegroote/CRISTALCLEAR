from PyDAQmx import *
import numpy

# Declaration of variable passed by reference
taskHandle = TaskHandle()
read = int32()
data = numpy.zeros((1000,), dtype=numpy.float64)

# DAQmx Configure Code
DAQmxCreateTask("",byref(taskHandle))
DAQmxCreateAIVoltageChan(taskHandle,"Dev1/ai2","",
                         DAQmx_Val_RSE,-10.0,10.0,
                         DAQmx_Val_Volts,None)

DAQmxCfgSampClkTiming(taskHandle,"",10000.0,DAQmx_Val_Rising,
                      DAQmx_Val_FiniteSamps,1000)

#DAQmx Start Code
DAQmxStartTask(taskHandle)

#DAQmx Read Code
DAQmxReadAnalogF64(taskHandle,1000,10.0,DAQmx_Val_GroupByChannel,data,1000,byref(read),None)

print data
