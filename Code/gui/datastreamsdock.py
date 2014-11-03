#!/usr/bin/python

"""
Dock object that has a graph in it, specifically for
monitoring the datastream

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

"""

import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import pyqtgraph.dockarea as da
import pyqtgraph.multiprocess as mp

import os
import time

import numpy as np
from pyqtgraph.Point import Point
import pyqtgraph.functions as fn
from pyqtgraph.widgets.RemoteGraphicsView import RemoteGraphicsView
from splitter import MySplitter
from dragdrop import *
from picbutton import PicButton
from graphsettings import GraphSettingsWidget
from dock import Dock
import pyqtgraph.exporters as exporter

class DataStreamsDock(Dock):

    def __init__(self,name,size,globalSession):
        Dock.__init__(self,name,size, autoOrientation=False)

        self.globalSession = globalSession

        self.title = name

        self.orientation = 'horizontal'
        self.autoOrient = False

        self.graph = DataStreamGraph(self.title, self.globalSession)
        self.addWidget(self.graph)

    def startTimer(self):
        self.graph.timer.start(30)

    def stopTimer(self):
        self.graph.timer.stop()

    def updateUI(self):
        self.graph.updateUI()

    def close(self):
        try:
            self.graph.timer.stop()
        except:
            pass
        super(da.Dock,self).close()

class DataStreamGraph(QtGui.QWidget):
    def __init__(self,title,globalSession):
        super(QtGui.QWidget,self).__init__()
        self.globalSession = globalSession
        self.title = title

        self.toPlot = []
        self.toSave = []
        self.graphs = dict()
        self.curves = dict()

        self.labelDict = {'ion': 'Ion Counts',
                          'time': 'Epoch time (s)',
                          'ai0': 'Voltage photodiode 1 (V)',
                          'ai1': 'Voltage photodiode 2 (V)',
                          'ai2': 'Voltage photodiode 3 (V)',
                          'freq': 'Wavemeter frequency (GHz)',
                          'volt': 'Scanning voltage (V)',
                          'rate': 'Rate averaged over 10 samples (Hz)',
                          'Power': 'Laser Power',
                          'Linewidth': 'Laser Linewidth (GHz)',
                          'thick': 'Thick etalon setpoint',
                          'thin': 'Thin etalon setpoint'}

        self.layout = QtGui.QGridLayout(self)

        self.graph = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.graph,0,0)

        self.settingsWidget = DataStreamSettingsWidget(self.globalSession)
        self.settingsWidget.settingsChanged.connect(self.updateSettings)
        self.settingsWidget.updateSettings()
        self.settingsWidget.setVisible(False)
        self.layout.addWidget(self.settingsWidget,0,1,2,1)
    
        self.makeGraphs()

        bLayout = QtGui.QHBoxLayout()
        bLayout.addWidget(QtGui.QWidget(),1)
        self.layout.addLayout(bLayout,1,0)

        settingsButton = PicButton('settings.png',checkable = True, size = 40)
        settingsButton.clicked.connect(self.showSettings)
        bLayout.addWidget(settingsButton)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.plot)

    def showSettings(self):
        self.settingsWidget.setVisible(not self.settingsWidget.isVisible())

    def plot(self):
        for key in self.graphs.iterkeys():
            if key in self.toPlot:
                x = self.globalSession.dataStreams['time'].data
                y = self.globalSession.dataStreams[key].data
                l = min(len(x),len(y))
                self.curves[key].setData(x[:l],y[:l], pen = 'r')
   
    
    def updateSettings(self, toPlot, toSave):

        self.toPlot = toPlot
        self.toSave = toSave

        self.makeGraphs()

    def makeGraphs(self):

        for graph in self.graphs.itervalues():
            try:
                self.graph.removeItem(graph)
            except:
                pass

        i = 0
        for key in self.globalSession.dataStreams.iterkeys():
            if key in self.toPlot:
                if not key in self.graphs.iterkeys():
                    self.graphs[key] = pg.PlotItem(title = self.labelDict[str(key)])

                    self.curves[key] = pg.PlotCurveItem()
                    self.graphs[key].addItem(self.curves[key])

                self.graph.addItem(self.graphs[key],row=i%3,col=i//3)

                i = i + 1

    def updateUI(self):
        self.settingsWidget.initUI()
        self.makeGraphs()



class DataStreamSettingsWidget(QtGui.QWidget):
    settingsChanged = QtCore.Signal(object,object)
    def __init__(self,globalSession):
        super(DataStreamSettingsWidget, self).__init__()

        self.globalSession = globalSession

        self.layout = QtGui.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.plotChecks = {}
        self.saveChecks = {}

        self.toPlot = []
        self.toSave = []


        self.initUI()

    def initUI(self):

        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        explanation = QtGui.QLabel('Select the data you want streamed to live \
graphs. The last 10 000 samples are shown as a function of time. By \
toggling the save icon, all data streams that have the \'save\' checkbox \
marked will be saved in a csv file, starting from the moment you click\
 the save icon. ')
        explanation.setWordWrap(True)

        self.layout.addWidget(explanation,0,0,1,3)

        self.layout.addWidget(QtGui.QLabel('Data Stream'),1,0)
        self.layout.addWidget(QtGui.QLabel('Plot'),1,1)
        self.layout.addWidget(QtGui.QLabel('Save'),1,2)

        for i,(key,val) in enumerate(self.globalSession.dataStreams.iteritems()):
            if not key == 'time':

                self.layout.addWidget(QtGui.QLabel(str(val.name)),i+2,0)

                self.plotChecks[key] = QtGui.QCheckBox()
                self.plotChecks[key].setChecked(True)
                self.plotChecks[key].stateChanged.connect(self.updateSettings)
                self.saveChecks[key] = QtGui.QCheckBox()
                self.saveChecks[key].stateChanged.connect(self.updateSettings)

                self.layout.addWidget(self.plotChecks[key],i+2,1)
                self.layout.addWidget(self.saveChecks[key],i+2,2)


        saveButton = QtGui.QPushButton()
        saveButton.setCheckable(True)
        saveButton.setMinimumWidth(30)
        saveButton.setMinimumHeight(30)
        saveButton.setMaximumWidth(30)
        saveButton.setMaximumHeight(30)
        saveButton.setIconSize( QtCore.QSize(25, 25))
        saveButton.setIcon(QtGui.QIcon('./gui/resources/save.png'))
        # saveButton.clicked.connect(lambda: self.saveSpectrum(self.graphs['rate']))
        saveButton.clicked.connect(self.toggleDataSave)
        self.layout.addWidget(saveButton,100,2)


    def toggleDataSave(self):
        if self.globalSession.streamsToSave == []:
            self.globalSession.streamsToSave = self.toSave
        else:
            self.globalSession.streamsToSave = []

    def updateSettings(self):

        self.toPlot = [key for key, val in self.plotChecks.iteritems() if val.checkState()]
        self.toSave = [key for key, val in self.saveChecks.iteritems() if val.checkState()]

        self.settingsChanged.emit(self.toPlot,self.toSave)
