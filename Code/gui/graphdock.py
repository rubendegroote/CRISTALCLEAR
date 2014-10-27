#!/usr/bin/python

"""
Dock object that has a graph in it

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

"""

import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import pyqtgraph.dockarea as da
import time
import os

import numpy as np
from pyqtgraph.Point import Point
import pyqtgraph.functions as fn
from pyqtgraph.widgets.RemoteGraphicsView import RemoteGraphicsView
from splitter import MySplitter
from dragdrop import *
from picbutton import PicButton
from graphsettings import GraphSettingsWidget
from pyqtgraph.dockarea import Dock
import pyqtgraph.exporters as exporter
from core.metacapture import MetaCapture


units = {'ion': 'Hz',
         'time': 's',
         'ai0': 'V',
         'ai1': 'V',
         'ai2': 'V',
         'freq': 'm',
         'volt': 'V',
         'power': 'W',
         'lw': 'Hz',
         'thick': None,
         'thin': None}

class GraphDock(Dock):

    def __init__(self,title,size,globalSession):
        Dock.__init__(self,title,size, autoOrientation=False,closable = True)

        self.globalSession = globalSession

        self.title = title

        self.graph = MyGraph(self.title, self.globalSession)
        self.addWidget(self.graph)

    def close(self):
        try:
            self.graph.timer.stop()
        except:
            pass
        super(da.Dock,self).close()

    def updateToCurrentCapture(self):
        cap = self.globalSession.getCurrentCapture()
        metaCap = MetaCapture(cap)
        self.graph.setMetaCap(metaCap)
        
class ViewBoxLog(pg.ViewBox):

    logSignal = QtCore.Signal(object)

    def __init__(self, *args, **kwargs):
        pg.ViewBox.__init__(self,*args, **kwargs)

    def emitLogSignal(self,volt):
        self.logSignal.emit(volt)

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton and self.menuEnabled():
            ev.accept()
            self.raiseContextMenu(ev)
        elif ev.modifiers() & QtCore.Qt.ControlModifier:
            ev.accept()
            mousePoint = self.mapToView(ev.pos())
            volt = mousePoint.x()
            self.emitLogSignal(volt)

    def wheelEvent(self,event,axis=None):
        event.accept()

class MyGraph(QtGui.QWidget):
    logSignal = QtCore.Signal(object,object) # Emitted when a log entry at a certain voltage should be made
    madePlot = QtCore.Signal(object)
    def __init__(self,title,globalSession):
        super(QtGui.QWidget,self).__init__()

        self.metaCap = None
        self.curves = []
        self.fitCurves = []

        self.globalSession = globalSession

        self.data = None

        self.layout = QtGui.QGridLayout(self)

        self.title = title

        self.labelDict = {'ion': 'ion rate',
                          'time': 'Epoch time',
                          'ai0': 'Voltage photodiode 1',
                          'ai1': 'Voltage photodiode 2',
                          'ai2': 'Voltage photodiode 3',
                          'freq': 'Wavelength',
                          'volt': 'Scanning voltage',
                          'power': 'Power of laser',
                          'lw': 'Linewidth of laser',
                          'thick': 'Thick etalon setpoint',
                          'thin': 'Thin etalon setpoint'}


        self.labelStyle = {'font-size': '18pt'}

        gView = pg.GraphicsView()

        self.vb = ViewBoxLog()
        self.vb.logSignal.connect(self.emitLogSignal)

        self.graph = pg.PlotWidget(viewBox = self.vb)
        self.graph.showGrid(x=True, y=True,alpha=0.7)

        layout = QtGui.QGridLayout(gView)
        layout.addWidget(self.graph,0,0,1,1)

        self.sublayout = QtGui.QGridLayout()
        layout.addLayout(self.sublayout,1,0)

        self.comboY = QtGui.QComboBox(parent = None)
        self.comboY.currentIndexChanged.connect(self.updatePlot)
        self.sublayout.addWidget(self.comboY,0,1)

        label = QtGui.QLabel('vs')
        label.setStyleSheet("border: 0px;");
        self.sublayout.addWidget(label,0,2)

        self.comboX = QtGui.QComboBox(parent = None)
        self.comboX.currentIndexChanged.connect(self.updatePlot)
        self.sublayout.addWidget(self.comboX,0,3)

        self.freqUnitSelector = QtGui.QComboBox(parent = None)
        self.freqUnitSelector.addItems(['Frequency','Wavelength'])
        self.freqUnitSelector.currentIndexChanged.connect(self.updatePlot)
        self.sublayout.addWidget(self.freqUnitSelector,0,4)

        self.meanStyles = ['Combined','Per Capture', 'Seperate']
        self.meanBox = QtGui.QComboBox(self)
        self.meanBox.addItems(self.meanStyles)
        self.meanBox.setCurrentIndex(1)
        self.meanBox.setMaximumWidth(110)
        self.meanBox.currentIndexChanged.connect(self.updatePlot)
        self.sublayout.addWidget(self.meanBox,1,1)

        self.graphStyles = ['Step (histogram)', 'Line']#, 'Point']

        self.graphBox = QtGui.QComboBox(self)
        self.graphBox.addItems(self.graphStyles)
        self.graphBox.setCurrentIndex(0)
        self.graphBox.setMaximumWidth(110)
        self.graphBox.currentIndexChanged.connect(self.updatePlot)
        self.sublayout.addWidget(self.graphBox,1,2)

        self.binLabel = QtGui.QLabel(self, text="Bin size: ")
        self.binSpinBox = pg.SpinBox(value = 0.03,
            bounds = (0,None), dec = False)
        self.binSpinBox.setMaximumWidth(110)
        self.binSpinBox.sigValueChanged.connect(self.updatePlot)
        
        self.sublayout.addWidget(self.binLabel,1,3)
        self.sublayout.addWidget(self.binSpinBox,1,4)      
        

        self.saveButton = PicButton('save',checkable = False,size = 25)
        self.saveButton.clicked.connect(self.saveSpectrum)
        self.sublayout.addWidget(self.saveButton, 0,7,1,1)

        self.settingsButton = PicButton('settings',checkable = True,size = 25)
        self.settingsButton.clicked.connect(self.showSettings)
        self.sublayout.addWidget(self.settingsButton, 0,8,1,1)

        self.sublayout.setColumnStretch(6,1)

        self.settingsWidget = GraphSettingsWidget()
        self.settingsWidget.updatePlot.connect(self.updatePlot)
        self.meanBox.currentIndexChanged.connect(self.settingsWidget.onStyleChanged) 
            #line above is MEGAHACK to have updating results table in analysiswidget
        self.settingsWidget.setVisible(False)

        self.layout.addWidget(gView,0,0)
        self.layout.addWidget(self.settingsWidget,0,1)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.plot)

    def initializeGraph(self):

        self.x = str(self.comboX.currentText())
        self.y = str(self.comboY.currentText())

        if self.x == 'freq':
            self.freqUnitSelector.setVisible(True)
        else:
            self.freqUnitSelector.setVisible(False)

        try:
            self.plot()
        except KeyError:
            #happens if data is not initialized yet
            pass

    def showSettings(self):
        self.settingsWidget.setVisible(not self.settingsWidget.isVisible())

    def plot(self):

        try:
            if not self.globalSession.scanner.captureRunningEvent.is_set():
                self.timer.stop()
                self.madePlot.emit(True)
        except:
            pass

        self.settingsWidget.setUI(self.metaCap.getHeaderInfo())
        self.setXY()

        while len(self.curves)<len(self.metaCap.x):

            i = len(self.curves)
           
            x,y = self.metaCap.x[i],self.metaCap.y[i]
            y = np.nan_to_num(y)


            self.curves.append(pg.PlotCurveItem())
            if not len(x) < 2:
                self.curves[-1].setData(x,y, 
                    pen = self.colors[-1], 
                    brush = self.fills[-1],
                    fillLevel = 0,
                    stepMode = str(self.graphBox.currentText()) == 'Step (histogram)')


            self.graph.addItem(self.curves[i])

        else:
            if len(self.curves)>0:
                x,y = self.metaCap.x[-1],self.metaCap.y[-1]
                y = np.nan_to_num(y)
                
                if not len(x) < 2:
                    self.curves[-1].setData(x,y, 
                        pen = self.colors[-1], 
                        brush = self.fills[-1],
                        fillLevel = 0,
                        stepMode = str(self.graphBox.currentText()) == 'Step (histogram)')


    def setMetaCap(self,metaCap):
        self.metaCap = metaCap
        self.settingsWidget.resetScans()
        self.settingsWidget.setUI(self.metaCap.getHeaderInfo())
        self.setXY()
        self.setComboBoxes()

        if self.globalSession.scanner.captureRunningEvent.is_set():
            self.timer.start(30)

    def clearPlot(self):
        self.fitCurves = []
        self.curves = []
        self.graph.clear()

    def setComboBoxes(self):
        if not self.metaCap == None:
            t = self.metaCap.dataTypes
            curX = str(self.comboX.currentText())
            curY = str(self.comboY.currentText())
            self.comboX.clear()
            self.comboX.addItems(t)
            self.comboY.clear()
            self.comboY.addItems(t)

            try:
                self.comboX.setCurrentIndex(t.index(curX))
                self.comboY.setCurrentIndex(t.index(curY))
            except:
                pass

    def updatePlot(self):
        self.clearPlot()
        self.setXY()
        self.plot()

    def setXY(self):
        self.x = str(self.comboX.currentText())
        self.y = str(self.comboY.currentText())
        freqMode = str(self.freqUnitSelector.currentText()) == 'Frequency'
        mode = str(self.meanBox.currentText())
        scansIncluded = self.settingsWidget.getCheckStates()
        histMode = str(self.graphBox.currentText()) == 'Step (histogram)'
        
        if self.x == 'freq':
            if freqMode:
                binsize = self.binSpinBox.value()*10**6
            else:
                binsize = self.binSpinBox.value()*10**(-15)

            self.freqUnitSelector.setVisible(True)

            if str(self.freqUnitSelector.currentText()) == 'Frequency':
                self.binLabel.setText("Bin size (MHz): ")
            else:
                self.binLabel.setText("Bin size (fm): ")
        else:
            binsize = self.binSpinBox.value()
            self.freqUnitSelector.setVisible(False)
            self.binLabel.setText("Bin size: ")

        self.setLabels()

        if not self.metaCap == None and not self.x == '' and not self.y == '':
            self.metaCap.setXY(xkey=self.x,ykey=self.y,
                freqMode = freqMode,
                mode = mode,
                scansIncluded = scansIncluded,
                histMode = histMode,
                binsize = binsize)

            self.metaCap.getData()

        styles = self.settingsWidget.getStyles()
        mode = str(self.meanBox.currentText())

        if mode ==  'Combined':
            self.colors = [styles['color'].values()[0][0]]
            self.fills = [styles['fill'].values()[0][0]]
        elif mode == 'Per Capture':
            self.colors = [s[0] for s in styles['color'].values()]
            self.fills = [s[0] for s in styles['fill'].values()]
        else:
            self.colors = [s for st in styles['color'].values() for s in st[1]]
            self.fills = [s for st in styles['fill'].values() for s in st[1]]

        for i,curve in enumerate(self.curves):
            curve.setPen(self.colors[i])
            curve.setBrush(self.fills[i])
        
    def setLabels(self):
        if not self.x == '' and not self.y == '':
            if self.x == 'freq':
                if str(self.freqUnitSelector.currentText()) == 'Wavelength':
                    xunit = 'm'
                else:
                    xunit = 'Hz'
            else:
                xunit = units[self.x]

            if self.y == 'freq':
                if str(self.freqUnitSelector.currentText()) == 'Wavelength':
                    yunit = 'm'
                else:
                    yunit = 'Hz'
            else:
                yunit = units[self.y]

            self.graph.setLabel('bottom', text = self.x, units = xunit)
            self.graph.setLabel('left', text = self.y, units = yunit)

    def emitLogSignal(self,volt):
        if not str(self.comboX.currentText()) =='' \
                and not str(self.comboY.currentText())  == '':
            self.logSignal.emit(volt, self.x + '_'+self.y)

    def saveSpectrum(self):
        exp = exporter.ImageExporter(self.graph.plotItem)

        path = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Data\\Pictures\\'

        name = QtGui.QFileDialog.getSaveFileName(self, "Save file", path, ".png")

        exp.parameters()['width'] = 200
        exp.parameters()['height'] = 1000
        exp.export(name)

        exp = exporter.CSVExporter(self.graph.plotItem)
        exp.export(str(name).strip('.png')+'.csv')


