from multiprocessing import Queue
import time as time
import sys

import pyqtgraph as pg

import numpy as np

def acquireDummy(settings,dataQueue,controlEvent,captureRunningEvent,recordingEvent,errorQueue,
    dataStreamQueue,messageQueue,currentVolt,currentSamples,currentFreq,
    currentThick,currentThin,currentPower,currentLW,iscool):

    settings.sanitise() # don't want things to go wrong here

    messageQueue.put((True, "NI Communication established..."))

    # begin acquisition loop
    while True:
        try:
            timestamp = time.time()

            time.sleep(0.005)

            counts = 100*(np.exp(-(currentFreq.value-2.0)**2/0.1**2) + np.exp(-(currentFreq.value-3.0)**2/0.1**2))
            counts = counts + np.abs(np.random.normal(0, np.sqrt(counts+1)))

            ais = []
            for nr in xrange(settings.noOfAi):
                ais.append(50 + 25*np.sin(currentFreq.value * 4) + np.random.normal(0,1))


            if captureRunningEvent.is_set() and recordingEvent.is_set():
                currentSamples.value = currentSamples.value + 1
                
                dataQueue.put((counts, ais,currentVolt.value,currentFreq.value, timestamp,
                        currentThick.value,currentThin.value,currentPower.value,currentLW.value,iscool.value))
                
            dataStreamQueue.put((counts, ais,currentVolt.value,currentFreq.value, timestamp,
                    currentThick.value,currentThin.value,currentPower.value,currentLW.value,iscool.value))

        except Exception as err:
            errorQueue.put(str(err))
            break


def laserDummy(settings, freqQueue,controlEvent,captureRunningEvent,recordingEvent,
    newFreqEvent,errorQueue,messageQueue,currentVolt,
    currentFreq,currentThick,currentThin,currentPower,
    currentLW,currentCycle,pPerCycle,pForHRS,pPulse):

    settings.sanitise() # don't want things to go wrong here

    # begin RILIS communications loop
    messageQueue.put((True, "Laser Communications established..."))
    controlEvent.set()
    
    while True:
        try:
            if newFreqEvent.is_set():
                newFreqEvent.clear()
                scanVariables = freqQueue.get()

                variable = scanVariables[0]

                currentVolt.value = scanVariables[1][variable]

                time.sleep(0.01)

                controlEvent.set()

            else:
                time.sleep(0.001)

                time.sleep(10)
        
        except Exception as err:
            errorQueue.put(str(err))
            break

