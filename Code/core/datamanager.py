#!/usr/bin/python

"""
kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch
DataManager - 
passed data from the card to store & save

"""

import numpy as np

import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from multiprocessing import Queue
import threading as threading
import time
from copy import deepcopy
from collections import OrderedDict
from spectrum import Spectrum

class DataManager():


    def __init__(self, settings, globalSession):

        self.settings = settings

        # global session
        self.globalSession = globalSession
        self.scanner = self.globalSession.scanner

        self.rate = 0.0
        self.currentIndex = 0
        self.lastSavedIndex = 0

        self.currentSuperCycle = 0
        self.cycles = 0
        self.pulses = 0

        # array that holds the data for each scan
        # Each entry in this array is a dictionary with data in it

        self.dataTypes = ['time','volt','freq','ion','thick','thin','power','lw','iscool']
        for i in xrange(self.settings.aiChannel.count(',')+1):
            self.dataTypes.append('ai'+str(i))

        self.allData = []
        self.spectrum = Spectrum()
        self.spectra = []

        self.addScan()



    def addScan(self):
        # dictionary that will hold all data for the new scan
        data = OrderedDict() # Ordered dictionary, so that we save the data with consistency

        for t in self.dataTypes:
            data[t] = np.array([])
            
        self.allData.append(data)
        self.spectra.append(Spectrum())

    def updateSettings(self,settings):
        self.settings = settings

    def storeData(self):

        if self.scanner.newScanEvent.is_set():
            self.addScan()
            self.scanner.newScanEvent.clear()
            
        try:
            count,ai,volt,freq, t,thick,thin,power,lw,iscool  = self.scanner.dataQueue.get_nowait()
            self.allData[-1]['time'] = np.append(self.allData[-1]['time'],t)
            self.allData[-1]['ion'] = np.append(self.allData[-1]['ion'],count)
            for nr,val in enumerate(ai):
                self.allData[-1]['ai' + str(nr)] = np.append(self.allData[-1]['ai' + str(nr)],val)
            self.allData[-1]['volt'] = np.append(self.allData[-1]['volt'],volt)
            self.allData[-1]['freq'] = np.append(self.allData[-1]['freq'],freq)

            self.allData[-1]['thick'] = np.append(self.allData[-1]['thick'],thick)
            self.allData[-1]['thin'] = np.append(self.allData[-1]['thin'],thin)
            self.allData[-1]['power'] = np.append(self.allData[-1]['power'],power)
            self.allData[-1]['lw'] = np.append(self.allData[-1]['lw'],lw)
            self.allData[-1]['iscool'] = np.append(self.allData[-1]['iscool'],lw)

            self.currentIndex = self.currentIndex + 1
        except:
            time.sleep(0.001)
        
        if self.scanner.captureRunningEvent.is_set():
            self.storeThread = threading.Timer(0, self.storeData).start()
        
    def getAllData(self):
        return deepcopy(self.allData)

    def setData(self, allData):

        aiChannels = self.settings.aiChannel.count(',') + 1

        for scan,data in enumerate(allData):

            if not scan==0:
                self.addScan()

            self.allData[-1]['time'] = data.T[0]
            self.allData[-1]['volt'] = data.T[1]
            self.allData[-1]['freq'] = data.T[2]
            self.allData[-1]['ion'] = data.T[3]

            #bit clumsy from here on, but it works I guess
            for nr in xrange(aiChannels):
                self.allData[-1]['ai'+str(nr)] = data.T[4+nr]

            self.allData[-1]['thick'] = data.T[5+aiChannels]
            self.allData[-1]['thin'] = data.T[6+aiChannels]
            self.allData[-1]['power'] = data.T[7+aiChannels]
            self.allData[-1]['lw'] = data.T[8+aiChannels]

            try:
                self.allData[-1]['iscool'] = data.T[9+aiChannels]
            except IndexError:
                pass