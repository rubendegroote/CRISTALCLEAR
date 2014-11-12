#!/usr/bin/python

"""
Created when the user wishes to set up a capture. 
Interfaces between the physical device, data buffer
and gui.

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch
"""

from datamanager import DataManager
from filemanager import FileManager
from logbook import *
from dataStream import StreamedData

import threading
import ConfigParser
import time
import datetime
import os

import numpy as np

from copy import deepcopy


class CaptureSession:
    """
    Interfaces between card, gui and data buffers
    """
    def __init__(self, globalSession,name):

        self.name = name

        self.globalSession = globalSession
        self.settings = self.globalSession.settings

        self.dataManager = DataManager(self.settings, self.globalSession)

        self.fitted = False
        self.acquisitionDone = False
        self.dataInMemory = False
        
        # initialize file manager
        self.fileManager = FileManager(self.settings)

    def run(self):
        # Guarantee latest settings before running
        self.dataManager.updateSettings(self.globalSession.settings)
        self.fileManager.updateSettings(self.globalSession.settings)

        self.storeThread = threading.Timer(0.005, self.dataManager.storeData).start()
        time.sleep(0.25)
        self.saveData()

    def stopRun(self):
        self.acquisitionDone = True
        self.dataInMemory = True

        try:
            self.saveThread.cancel()
        except AttributeError:
            pass

        self.saveData()
   
    def readData(self):
        if self.acquisitionDone and not self.dataInMemory:
            allData = self.fileManager.readData(self.name)
            self.dataManager.setData(allData)
            self.dataInMemory = True

    def saveData(self):
        """
        Save session to current filename
        """
        self.fileManager.saveData(self.name,self.dataManager.getAllData())
        if self.globalSession.running and not self.globalSession.stopProgram:
            self.saveThread = threading.Timer(5, self.saveData).start()


class GlobalSession:
    """
    Mainly to deal with global settings
    """
    
    def __init__(self,captures,scanner,settings):

        self.captures = captures
        self.scanner = scanner
        self.settings = settings

        self.currentCapture = None
        self.previousCapture = None

        self.rate = 0.0

        # Has the user asked to stop this program
        self.stopProgram = False

        self.running = False

        self.streamsToSave = []

        self.createDataStream()
        self.dataStreamThread = threading.Timer(0, self.dataStream).start()

        self.logLoadThread = threading.Timer(0, self.loadLogBook).start()


    def createDataStream(self):
        
        self.dataStreams = dict()
        self.dataStreams['time'] = StreamedData('time',10000,self)
        
        if self.settings.laser == 'cw':
            self.dataStreams['volt'] = StreamedData('volt',10000,self)
        if not self.settings.laser == 'CW without wavemeter':
            self.dataStreams['freq'] = StreamedData('freq',10000,self)
        self.dataStreams['ion'] = StreamedData('ion',10000,self)
        self.dataStreams['rate'] = StreamedData('rate',10000,self)

        for nr in xrange(self.settings.noOfAi):
            self.dataStreams['ai' + str(nr)] = StreamedData('ai' + str(nr),10000,self)

        if self.settings.laser == 'RILIS':
            self.dataStreams['thick'] = StreamedData('thick',10000,self)
            self.dataStreams['thin'] = StreamedData('thin',10000,self)

        if not self.settings.laser == 'CW without wavemeter':
            self.dataStreams['Power'] = StreamedData('Power',10000,self)
            self.dataStreams['Linewidth'] = StreamedData('Linewidth',10000,self)


    def dataStream(self):

        toAdd = dict.fromkeys(self.dataStreams.keys())
        for key in toAdd.iterkeys():
            toAdd[key] = []

        while not self.scanner.dataStreamQueue.empty():
            count,ai,volt,freq,t,thick,thin,power,lw = self.scanner.dataStreamQueue.get()

            toAdd['time'].append(t)
            if self.settings.laser == 'cw':
                toAdd['volt'].append(volt)

            if not self.settings.laser == 'CW without wavemeter':
                toAdd['freq'].append(freq)
            toAdd['ion'].append(count)

            for nr in xrange(len(ai)):
                toAdd['ai' + str(nr)].append(ai[nr])

            if self.settings.laser == 'RILIS':
                toAdd['thick'].append(thick)
                toAdd['thin'].append(thin)

            if not self.settings.laser == 'CW without wavemeter':
                toAdd['Power'].append(power)
                toAdd['Linewidth'].append(lw)


        for key, val in toAdd.iteritems():

            if not key == 'rate':
                self.dataStreams[key].addData(toAdd['time'],val)

            if key == 'ion':
                try:
                    summed = np.sum(self.dataStreams[key].data[-10:]) 
                except:
                    summed = 0
            elif key =='time':
                try:
                    elapsed = self.dataStreams[key].data[-1] - self.dataStreams[key].data[-10]
                except:
                    elapsed = 1

        for i,time in enumerate(toAdd['time']):
            self.dataStreams['rate'].addData([time],[summed / elapsed])

        if not self.stopProgram:
            self.dataStreamThread = threading.Timer(0.03, self.dataStream).start()

    def getSBMessage(self):
        try:
            return self.currentCapture.dataManager.SBMessage
        except AttributeError:
            return None

    def newCapture(self,name = None, loaded = False):
        if name == None:
            number = len(self.captures)
            name = 'Capture ' + str(number)

        capture = CaptureSession(self,name)

        self.captures[name] = capture

        if loaded:
            capture.acquisitionDone = True
            self.previousCapture = capture
        else:
            self.previousCapture = self.currentCapture
            self.currentCapture = capture
        
        return capture

    def getCurrentCaptureAndLog(self):
        try:
            return self.currentCapture,self.logBook.getCaptureEntries().values()[-1]
        except:
            return None,None

    def getCurrentCapture(self):
        return self.currentCapture

    def getPreviousCapture(self):
        return self.previousCapture

    def saveEntry(self,entry):

        f = file(self.settings.logFile, 'a')
        text = '*** New Entry ***\n'+entry.reportProperties()
 
        f.write(text)

        f.close()

    def loadLogBook(self):
        try:
            f = open(self.settings.logFile, 'r')
        except IOError:
            return
        
        self.logBook = LogBook()
        latestCapture = None

        lines = f.readlines()
        i=1 # won't start at i=0, we can ignore the first line of the log (it says '*** New Entry ***')
        if len(lines) < 1:
            self.scanner.messageQueue.put((True,'Logbook loaded.'))
            return
            
        while i<len(lines):
            line = lines[i]
            if i%100 == 0:
                self.scanner.messageQueue.put(\
                    (False,'Loading Logbook \n Line {0} of {1}...'.format(str(i),
                                                                       str(len(lines)))))

            if line == '*** New Entry ***\n':

                if newEntry.__class__.__name__ == 'CaptureLogEntry':
                    # Create the capture session and load the data
                    cap = self.newCapture(newEntry.getProperty('name'), loaded = True)
                    newEntry.setCapture(cap)
                    latestCapture = cap
                        
                elif not latestCapture == None:
                    newEntry.setCapture(latestCapture)
                        
                # Add session to logbook
                self.logBook.addEntry(entry = newEntry, key = logKey)


            #Figure out what type of entry it is 
            elif 'Entry' in line:
                if 'GraphNoteEntry' in line:
                    newEntry = GraphNoteEntry()
                elif 'AdminEntry' in line:
                    newEntry = AdminEntry()
                elif 'CaptureLogEntry' in line:
                    newEntry = CaptureLogEntry()
                else:
                    newEntry = Entry()

                logKey = int(line.split('Entry key: ')[1].split('\n')[0])

            # add the properties of the entry to its dictionary
            else:
                key = line.partition('\t')[0].strip(':')
                val = line.partition('\t')[2].strip('\n')
                if key =='time':
                    newEntry.properties[key] = datetime.datetime.strptime(val,'%y/%m/%d %H:%M:%S')
                elif key=='stopTime':
                    try:
                        newEntry.properties[key] = datetime.datetime.strptime(val,'%y/%m/%d %H:%M:%S')
                    except ValueError:
                        newEntry.properties[key] = val
                elif key =='comments':
                    text=''
                    text = text + val

                    i=i+1
                    line = lines[i]
                    while not line =='#End of comment\n':
                        text = text + line

                        i=i+1
                        line = lines[i]

                    newEntry.properties[key] = text
                elif key == 'scanBreakPoints':
                    newEntry.properties[key] = eval(val)
                else:
                    newEntry.properties[key] = val

            i = i + 1

        if newEntry.__class__.__name__ == 'CaptureLogEntry':
            # Create the capture session and load the data
            cap = self.newCapture(newEntry.getProperty('name'), loaded = True)
            newEntry.setCapture(cap)
                
        elif not latestCapture == None:
            newEntry.setCapture(latestCapture)

        # Add session to logbook
        self.logBook.addEntry(entry = newEntry, key = logKey)

        self.scanner.messageQueue.put((True,'Logbook loaded.'))