from daq.acquire import acquire, fastAcquire, clearcard, acquireRILIS, acquireCW
from daq.acquireDummy import acquireDummy, laserDummy
from multiprocessing import Process, Queue, Event, Value
import numpy as np

import os
import time
import subprocess
import threading

from PyQt4 import QtCore,QtGui

class Scanner(QtCore.QObject):
    emitScanProgress = QtCore.Signal(int,str,dict)
    captureDone = QtCore.Signal(object)#Emitted when a capture is done
    def __init__(self,settings):

        super(QtCore.QObject,self).__init__()

        self.settings = settings

        # array of values to iterat though
        self.scanArray = []
        # Progress through this array
        self.pos = 0
        self.currentValue = 0
        # When in freerun: have the variables changed?
        self.variablesChanged = False

        # Acquistion mode (time, triggers, supercycle or proton pulse)
        self.mode = 'Time'
        # acquisition time for each wavelength when acquiring timed
        self.timePerStep = 10
        # Number of samples to collect
        self.samplesPerStep = 10
        # supercycles for each wavelength when acquiring per SS
        self.SSPerStep = 10
        self.totalCycles = 0
        self.noOfCycles = 0
        # proton pulse time for each wavelength when acquiring bunched
        self.pPerStep = 10
        self.startCycle = 0
        self.totalPulses = 0
        # True if the user can just tweak e.g. voltage or etalons, no
        # iteration through the scanArray is running
        self.freeScan = False

        # True if the scan restarts every time
        self.looping = False
        # True if the scan zigzags /\, False if it scans /|
        self.zigZag = False
        # True if the scan is \ in a /\ scan
        self.zag = True

        # which variable the scanarray will chagne
        self.scanVariable = 'volt'
        # contains ifno the acquisition process uses to change the wavelength
        # for every key there is a value 
        # This allows to scan by defining  e.g. a wavelength, voltage or the etalons setpoints
        self.scanVariables = {'wavelength': 0,
        'volt': 0,
        'thin': 0,
        'thick': 0
        }

        self.continueScanning = True

        self.initProcessCommunications()

    def initProcessCommunications(self):
        # Queues and events for the acquisition processes
        self.newFreqEvent = Event()
        self.controlEvent = Event()
        self.newScanEvent = Event()
        self.captureRunningEvent = Event()
        self.recordingEvent = Event()

        self.currentVolt = Value('d',0.0)
        self.currentSamples = Value('i',0)
        self.currentFreq = Value('d',0.0)
        self.currentThick = Value('d',0.0)
        self.currentThin = Value('d',0.0)
        self.currentPower = Value('d',0.0)
        self.currentLW = Value('d',0.0)
        self.currentCycle = Value('i',0)
        self.protonsPerCycle = Value('i',0)
        self.protonsForHRS = Value('i',0)
        self.protonPulse = Value('b',False)

        self.dataQueue = Queue()
        self.freqQueue = Queue()
        self.errorQueue = Queue()
        self.messageQueue = Queue()
        self.dataStreamQueue = Queue()

    def startProcesses(self):

        if self.settings.debugMode:
            targetF = acquireDummy
        else:
            targetF = acquire
    

        self.daqProcess = Process(target=targetF,
                              args=(self.settings,self.dataQueue,self.controlEvent,
                                    self.captureRunningEvent,self.recordingEvent,self.errorQueue,
                                    self.dataStreamQueue,self.messageQueue,
                                    self.currentVolt,self.currentSamples,
                                    self.currentFreq,self.currentThick,
                                    self.currentThin,self.currentPower,self.currentLW))

        if self.settings.laser == 'CW without wavemeter':
            targetF = laserDummy
        elif self.settings.laser == 'CW':
            targetF = acquireCW
        elif self.settings.laser == 'RILIS':
            targetF = acquireRILIS

        self.RILISProcess = Process(target=targetF,
                          args=(self.settings, self.freqQueue,self.controlEvent,
                            self.captureRunningEvent,self.recordingEvent,self.newFreqEvent,
                            self.errorQueue,self.messageQueue,self.currentVolt,
                            self.currentFreq,self.currentThick,self.currentThin,
                            self.currentPower,self.currentLW,self.currentCycle,
                            self.protonsPerCycle,self.protonsForHRS,self.protonPulse))
             

        self.daqProcess.start()
        self.RILISProcess.start()

        self.continueScanning = True
        self.scanThread = threading.Timer(0, self.scan).start()


        if not self.settings.laser == 'CW without wavemeter':
            relayPath = os.getcwd().split('CRISTALCLEAR')[0] + '\\CRISTALCLEAR\\Code\\builds\\CRISValueRelay\\CRISValueRelay4\\CrisValueRelay'

            self.relayProcess = subprocess.Popen(relayPath)
            self.messageQueue.put((True,'Relay VI started.'))
            

    def stopProcesses(self):
        self.messageQueue.put((True,'Terminating processes...'))

        self.continueScanning = False

        try:
            self.daqProcess.terminate()
            self.RILISProcess.terminate()
            if not self.settings.laser == 'CW without wavemeter':
                self.relayProcess.terminate()

        except:
            print "Could not stop capture processes"

    def restartProcesses(self):
        self.stopProcesses()
        self.startProcesses()

    def setScanMode(self, mode,time):
        self.mode = mode
        if self.mode == 'Time':
            self.timePerStep = time
        elif self.mode == 'Triggers':
            self.samplesPerStep = time
        elif self.mode == 'Supercycle':
            self.SSPerStep = time
        elif 'Proton Pulse':
            self.pPerStep == time

    def setVariable(self, variable):
        self.scanVariable = variable

    def toggleFreeScan(self):
        self.freeScan = not self.freeScan

    def toggleLooping(self):
        self.looping = not self.looping

    def toggleZigZag(self):
        self.zigZag = not self.zigZag

    def makeFreqArray(self, variable, points, steps):
        self.pos = 0
        self.scanArray = []
        self.scanVariable = variable

        start = points[0]
        for i, point in enumerate(points[1:]):
            newArray = np.linspace(start,point,steps[i])

            start = point

            self.scanArray = np.append(self.scanArray, newArray)

    def resetScan(self):
        self.pos = 0
        self.currentValue = self.scanArray[self.pos]

        self.emptyQueues()

    def setCurrentValue(self, scanVariable, scanVariables):
        self.scanVariable = scanVariable
        self.scanVariables = scanVariables
        self.currentValue = scanVariables[scanVariable]
        self.variablesChanged = True

    def scan(self):
        if self.freeScan:
            if self.variablesChanged:
                self.controlEvent.clear()
                self.variablesChanged = False

                # Put the new scan info on the Queue and notify the processes by setting
                # the newFreqEvent
                # Empty the queue before putting anything on it (perhaps needed for RILIS coms
                # if I have to click several times for the comms to work)
                while not self.freqQueue.empty():
                    self.freqQueue.get()

                self.freqQueue.put((self.scanVariable, self.scanVariables))

                self.newFreqEvent.set()

                # Wait for Wavelength change, once this is done: start up the
                # filling of the dataQueue for the requested times
                self.wait()
    
            else:
                time.sleep(0.05)

        else:
            if self.captureRunningEvent.is_set():
                self.controlEvent.clear()
                self.currentValue = self.scanArray[self.pos]
                self.variablesChanged = False

                self.scanVariables[self.scanVariable] = self.currentValue

                # Put the new scan info on the Queue and notify the processes by setting
                # the newFreqEvent
                # Empty the queue before putting anything on it (perhaps needed for RILIS coms
                # if I have to click several times for the comms to work)
                while not self.freqQueue.empty():
                    self.freqQueue.get()

                # Put the new scan info on the Queue and notify the processes by setting
                # the newFreqEvent
                self.freqQueue.put((self.scanVariable, self.scanVariables))
                self.newFreqEvent.set()

                # info to update the GUI
                progress = 100*(self.currentValue-self.scanArray[0])/ \
                        (self.scanArray[-1]-self.scanArray[0])
                if self.zigZag and self.zag:
                    progress = 100 - progress
                self.emitScanProgress.emit(progress, self.scanVariable, self.scanVariables)

                # Wait for Wavelength change, once this is done: start up the
                # filling of the dataQueue for the requested times
                self.wait()

            else:
                self.pos = 0
                time.sleep(0.05)

        if self.continueScanning:
            # if self.captureRunningEvent.is_set():
            #     # empty the queue just in case some stuff was left due to sync issues
            #     self.emptyQueues()
            self.scanThread = threading.Timer(0, self.scan).start()
    
    def emptyQueues(self):
        while not self.dataQueue.empty():
            self.dataQueue.get()

        while not self.freqQueue.empty():
            self.freqQueue.get()


    def wait(self):
        # Wait for the wavelength change 
        while not self.controlEvent.is_set():
            if self.interruptedSleep(0.001):
                return


        if self.captureRunningEvent.is_set():
            #########################
            ### Timed acquisition ###
            #########################
            if self.mode == 'Time':
                self.recordingEvent.set()
                time.sleep(self.timePerStep*0.001)
                self.recordingEvent.clear()

            ###########################
            ### trigger acquisition ###
            ###########################
            elif self.mode == 'Triggers':
                self.recordingEvent.set()
                while not self.currentSamples.value == self.samplesPerStep:
                    if self.interruptedSleep(0.001):
                        return


                self.currentSamples.value = 0

                self.recordingEvent.clear()                


            ##############################
            ### Supercycle acquisition ###
            ##############################
            elif self.mode == 'Supercycle':
                # we start in the middle of a proton pulse on HRS, so wait
                if self.pos == 0 and self.protonPulse.value:
                    # Remember the pulse we started on
                    startCycle = self.currentCycle.value
                    # Wait for the current ongoing cycle to end
                    while startCycle == self.currentCycle.value:
                        if self.interruptedSleep(0.001):
                            return

                # Remember the pulse we started on
                self.startCycle = self.currentCycle.value

                # Remember the total number of cycles when we started
                self.noOfCycles = self.protonsPerCycle.value

                while self.totalCycles < self.SSPerStep:
                    # Start recording
                    self.recordingEvent.set()

                    # wait until the current supercycle passes
                    while self.currentCycle.value == self.startCycle:
                        if self.interruptedSleep(0.001):
                            return

                    while not self.currentCycle.value == self.startCycle:
                        # Check if the total number of pulses in the cycle has
                        # changed if we started on the last pulse of the cycle
                        if not self.noOfCycles == self.protonsPerCycle.value:
                            self.noOfCycles = self.protonsPerCycle.value
                            # If we started on a pulse that just fell off the board:
                            # change the start pulse to the highest pulse number
                            if self.startCycle > self.protonsPerCycle.value:
                                self.startCycle = self.noOfCycles


                        if self.interruptedSleep(0.001):
                            return

                    # current pulse passed: stop recording
                    self.recordingEvent.clear()
                    self.totalCycles = self.totalCycles + 1

            ################################
            ### Proton Pulse acquisition ###
            ################################
            elif self.mode == 'Proton Pulse':
                # we start in the middle of a proton pulse on HRS, so wait
                if self.pos == 0 and self.protonPulse.value:
                    while self.protonPulse.value:
                        if self.interruptedSleep(0.001):
                            return

                while self.totalPulses < self.pPerStep:
                    # wait for a proton pulse, record what SS this happens on
                    while not self.protonPulse.value:
                        if self.interruptedSleep(0.001):
                            return
                    
                    # Start recording
                    self.recordingEvent.set()

                    self.startCycle = self.currentCycle.value

                    # wait until the current proton pulse passes
                    while self.currentCycle.value == self.startCycle:
                        if self.interruptedSleep(0.001):
                            return

                    # current pulse passed: stop recording
                    self.recordingEvent.clear()
                    self.totalPulses = self.totalPulses + 1

            self.scanToNext()

        else:
            time.sleep(0.001)


    def scanToNext(self):
        if self.pos < len(self.scanArray)-1:
            self.pos = self.pos + 1

        elif self.looping:
            self.pos = 0
            self.newScanEvent.set()

            if self.zigZag:
                self.scanArray = self.scanArray[::-1]
                self.zag = not self.zag
        else:
            self.captureDone.emit(True)
            time.sleep(0.01)
            self.pos = 0

    def interruptedSleep(self,t):
        if self.continueScanning and self.captureRunningEvent.is_set() and not self.variablesChanged:
            time.sleep(t)
            return False
        else:
            return True
