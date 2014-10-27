#!/usr/bin/python

"""

ruben.degroote@cern.ch
CRIS LIfetime Measurements Software

"""


import sys

import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from multiprocessing import Process, Queue
import pyqtgraph.ptime as pgt
import time as time
import pyqtgraph.widgets.RemoteGraphicsView

import numpy as np
from copy import deepcopy

from PyDAQmx import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxFunctions import *

from gui.splitter import MySplitter

class LifetimeWindow(QtGui.QMainWindow):

    def __init__(self,parent):
        super(LifetimeWindow, self).__init__(parent)
        
        self.setGeometry(300, 300, 250, 150)
        
        self.q = Queue()
        self.data = {}
        self.data['ion'] = []
        self.data['time'] = []

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.storeData)

        self.plotTimer = QtCore.QTimer()
        self.plotTimer.timeout.connect(self.plotData)

        self.InitUI()

        self.runButton.clicked.connect(self.startAcquistion)
        self.stopButton.clicked.connect(self.stopAcquisition)

        self.dataNumber = 0

    def InitUI(self):
        """
        UI initialisation
        """
        self.sb=self.statusBar()
        self.sb.showMessage('Ready')

        contents = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(contents)

        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)

        self.settings = LifetimeSettings(self)


        buttonWidget = QtGui.QWidget()
        buttonLayout = QtGui.QVBoxLayout(buttonWidget)
        self.runButton = QtGui.QPushButton('Run')
        buttonLayout.addWidget(self.runButton)

        self.stopButton = QtGui.QPushButton('Stop')
        buttonLayout.addWidget(self.stopButton)

        splitter = MySplitter('Settings', buttonWidget, self.settings)
        layout.addWidget(splitter)
        
        self.setCentralWidget(contents)

        self.show()

    def startAcquistion(self):

        self.running = True
        self.daqProcess = Process(target=acquireCounts,
                            args=(self.settings.getSettings(), 
                            self.q, self.running))
        self.timer.start()
        self.plotTimer.start(100)

        self.daqProcess.start()

    def storeData(self):

        while not self.q.empty():

            count,time = self.q.get()

            self.data['ion'].append(count)
            self.data['time'].append(time)


    def plotData(self):

        self.plot.plot(self.data['time'],self.data['ion'], pen='r',
            clear = True)

        print len(self.data['ion'])
   
    def stopAcquisition(self):
        self.running = False

        try:
            self.daqProcess.terminate()
        except:
            print "Could not stop capture process"

        time.sleep(1)
        self.timer.stop()
        self.plotTimer.stop()

        self.saveData(name = 'lifetime' + str(self.dataNumber))

        print len(self.data['ion'])/(self.data['time'][-1]-self.data['time'][0])

        self.data['ion'] = []
        self.data['time'] = []

        self.dataNumber = self.dataNumber + 1

    def saveData(self, name):

        f = file(name + ".csv", 'a')

        data = np.column_stack((self.data['time'],self.data['ion']))

        np.savetxt(f, data, delimiter=";",
           header = name)

    def closeEvent(self,event):
        """
        Called to exit program
        """
        try:
            self.globalSession.currentCapture.saveSession()
        except AttributeError:
            pass # Gets thrown if no captures have been started when closing the program

        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message', 
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            try:
                self.stopAcquisition()
            except:
                # thrown if the scan was already stopped
                pass
            event.accept()
        else:
            event.ignore()

class LifetimeSettings(QtGui.QWidget):     

    def __init__(self,parent):
        super(LifetimeSettings, self).__init__(parent)

        self.setMaximumWidth(300)

        layout = QtGui.QGridLayout(self)
        label1 = QtGui.QLabel('Counter Channel')
        label1.setMaximumWidth(120)
        layout.addWidget(label1, 0,0)
        self.text1 = QtGui.QLineEdit('/Dev1/ctr1')
        self.text1.setMaximumWidth(120)
        layout.addWidget(self.text1, 0,1)

        label2 = QtGui.QLabel('Clock Channel')
        label2.setMaximumWidth(120)
        layout.addWidget(label2, 1,0)
        self.text2 = QtGui.QLineEdit('/Dev1/PFI1')
        self.text2.setMaximumWidth(120)
        layout.addWidget(self.text2, 1,1)

        layout.setRowStretch(2,2)

    def getSettings(self):
        return (str(self.text1.text()),str(self.text2.text()))

def acquireCounts(channels, queue, running):

    counterChannel = channels[0]
    clockChannel = channels[1]


    # constants
    timeout = 100.0 # arbitrary - change in future
    maxRate = 1000.0

    # create task handles
    countTaskHandle = TaskHandle(0)
    # create tasks
    DAQmxCreateTask("", byref(countTaskHandle))
    DAQmxCreateCICountEdgesChan(countTaskHandle, 
                                counterChannel, "",
                                DAQmx_Val_Falling, 0, DAQmx_Val_CountUp)

    DAQmxCfgSampClkTiming(countTaskHandle, 
                          clockChannel,
                          maxRate, DAQmx_Val_Falling, 
                          DAQmx_Val_ContSamps, 1)

    # start tasks
    DAQmxStartTask(countTaskHandle)
    lastCount = uInt32(0)
    countData = uInt32(0) # the counter
    # need to perform a count here that we then throw away
    # otherwise get mysterious low first count
    DAQmxReadCounterScalarU32(countTaskHandle,
                              timeout,
                              byref(countData), None)

    while running:

        lastCount.value = countData.value

        DAQmxReadCounterScalarU32(countTaskHandle, 
                                  timeout,
                                  byref(countData), None)

        c = countData.value - lastCount.value

        timestamp = pgt.time()

        queue.put((c,timestamp))

    clearcard(countTaskHandle)

def clearcard(countTaskHandle):
    """
    Clears all tasks from the card
    """
    DAQmxStopTask(countTaskHandle)

    DAQmxClearTask(countTaskHandle)

    
    


def main():

    # application variables
    title = "crislims - Data Acquisition for lifetime measurements with CRIS"

    app = QtGui.QApplication(sys.argv)

    main_window = LifetimeWindow(parent = None)
    main_window.setObjectName(title)
    main_window.setWindowTitle(title)
    main_window.showMaximized()
    sys.exit(app.exec_())




if __name__ == "__main__":
    main()
    




