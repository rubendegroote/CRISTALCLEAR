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

labelDict = {'ion': 'Ion Counts',
             'time': 'Epoch time',
             'ai0': 'Voltage photodiode 1',
             'ai1': 'Voltage photodiode 2',
             'ai2': 'Voltage photodiode 3',
             'freq': 'Wavemeter frequency',
             'volt': 'Scanning voltage',
             'rate': 'Rate averaged over 10 samples',
             'Power': 'Laser Power',
             'Linewidth': 'Laser Linewidth',
             'thick': 'Thick etalon setpoint',
             'thin': 'Thin etalon setpoint'}

unitsDict = {'ion': 'Hz',
             'time': 's',
             'ai0': 'V',
             'ai1': 'V',
             'ai2': 'V',
             'freq': 'Hz',
             'volt': 'V',
             'rate': 'Hz',
             'Power': 'mW',
             'Linewidth': 'Hz',
             'thick': '',
             'thin': ''}

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
        self.graphs = dict()
        self.curves = dict()
        self.t0 = time.time()
        self.t0_formatted = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(self.t0))

        self.layout = QtGui.QGridLayout(self)

        self.graph = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.graph,0,0)

        self.settingsWidget = DataStreamSettingsWidget(self.globalSession)
        self.settingsWidget.settingsChanged.connect(self.updateSettings)
        self.settingsWidget.updateSettings()
        self.layout.addWidget(self.settingsWidget,0,1,2,1)
    
        self.makeGraphs()

        bLayout = QtGui.QHBoxLayout()
        bLayout.addWidget(QtGui.QWidget(),1)
        self.layout.addLayout(bLayout,1,0)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.plot)


    def plot(self):
        for key in self.graphs.iterkeys():
            if key in self.toPlot:
                x = self.globalSession.dataStreams['time'].data - self.t0
                y = self.globalSession.dataStreams[key].data
                l = min(len(x),len(y))
                self.curves[key].setData(x[:l],y[:l], pen = 'r')
   
    
    def updateSettings(self, toPlot):

        self.toPlot = toPlot

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
                    self.graphs[key] = pg.PlotItem()
                    # self.t0 = self.globalSession.dataStreams['time'].data[0]
                    self.graphs[key].setLabel('bottom', 
                        text = 'Time since {0}'.format(self.t0_formatted), units = 's')
                    self.graphs[key].setLabel('left', text = labelDict[str(key)],
                                                      units = unitsDict[str(key)])

                    self.curves[key] = pg.PlotCurveItem()
                    self.graphs[key].addItem(self.curves[key])

                self.graph.addItem(self.graphs[key],row=i%3,col=i//3)

                i = i + 1

    def updateUI(self):
        self.settingsWidget.initUI()
        self.makeGraphs()



class DataStreamSettingsWidget(QtGui.QWidget):
    settingsChanged = QtCore.Signal(object)
    def __init__(self,globalSession):
        super(DataStreamSettingsWidget, self).__init__()

        self.globalSession = globalSession

        self.layout = QtGui.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.plotChecks = {}
        self.saveChecks = {}

        self.toPlot = []

        self.initUI()

    def initUI(self):

        for i in reversed(range(self.layout.count())): 
            self.layout.itemAt(i).widget().setParent(None)

        for i,(key,val) in enumerate(self.globalSession.dataStreams.iteritems()):
            if not key == 'time':

                self.layout.addWidget(QtGui.QLabel(str(val.name)),i+2,0)

                self.plotChecks[key] = QtGui.QCheckBox()
                self.plotChecks[key].setToolTip('Check this if you want to\
 display the {0} data stream.'.format(str(key)))
                self.plotChecks[key].setChecked(True)
                self.plotChecks[key].stateChanged.connect(self.updateSettings)
                self.saveChecks[key] = QtGui.QCheckBox()
                self.saveChecks[key].stateChanged.connect(self.updateSettings)
                self.layout.addWidget(self.plotChecks[key],i+2,1)


    def updateSettings(self):
        self.toPlot = [key for key, val in self.plotChecks.iteritems() if val.checkState()]
        self.settingsChanged.emit(self.toPlot)
