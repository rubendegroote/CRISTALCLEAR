from __future__ import division
import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import numpy as np
import time
import threading
import os

from picbutton import PicButton


class ScannerWidget(QtGui.QWidget):
    captureDone = QtCore.Signal(object)#Emitted when a capture is done
    def __init__(self,globalSession):
        super(QtGui.QWidget,self).__init__()

        self.globalSession = globalSession
        self.scanner = self.globalSession.scanner
        self.scanner.emitScanProgress.connect(self.updateUI)

        self.setContentsMargins(0,0,0,0)
        
        self.layout = QtGui.QGridLayout(self)

        tabWidget = QtGui.QTabWidget()
        tabWidget.currentChanged.connect(self.toggleFreeScan)
        tabWidget.setTabPosition(QtGui.QTabWidget.West)

        self.layout.addWidget(tabWidget, 0,0,1,1)

        self.controlButton = PicButton('new', checkable = False,size = 100)
        self.layout.addWidget(self.controlButton,0,2,1,1)

        sublayout = QtGui.QVBoxLayout()

        self.modeCombo = QtGui.QComboBox()
        self.modes = ['Time','Triggers', 'Supercycle', 'Proton Pulse']
        self.modeCombo.addItems(self.modes)
        self.modeCombo.currentIndexChanged.connect(self.changeMode)
        self.modeCombo.setMaximumWidth(120)
        sublayout.addWidget(self.modeCombo)

        self.timeEdit = PicSpinBox(value = 10,step = 1, integer=True, icon = 'time')
        self.timeEdit.sigValueChanging.connect(self.changeMode)
        self.timeEdit.setMaximumWidth(120)
        sublayout.addWidget(self.timeEdit)

        self.layout.addLayout(sublayout,0,1,1,1)


        self.freeScanWidget = FreeScanWidget(parent = self, globalSession = globalSession)
        tabWidget.addTab(self.freeScanWidget,QtGui.QIcon('./gui/resources/manual'),'')

        self.autoScanWidget = QtGui.QWidget()
        layout = QtGui.QGridLayout(self.autoScanWidget)
        tabWidget.addTab(self.autoScanWidget,QtGui.QIcon('./gui/resources/auto'),'')

        self.intermediatePointsLayout = QtGui.QGridLayout()
        layout.addLayout(self.intermediatePointsLayout,1,4,1,1)
        
        self.points = []

        self.points.append(QtGui.QDoubleSpinBox())
        self.points[0].setDecimals(4)
        self.points[0].setRange(-10**7,10**7)
        self.points[0].setMaximumWidth(75)
        self.points[0].valueChanged.connect(self.updateMarkerPos)
        self.points[0].valueChanged.connect(self.makeFreqArray)
        self.intermediatePointsLayout.addWidget(self.points[0],0,0)

        self.points.append(QtGui.QDoubleSpinBox())
        self.points[-1].setDecimals(4)
        self.points[-1].setRange(-10**7,10**7)
        self.points[-1].setMaximumWidth(75)
        self.points[-1].valueChanged.connect(self.updateMarkerPos)
        self.points[-1].valueChanged.connect(self.makeFreqArray)
        self.intermediatePointsLayout.addWidget(self.points[-1],0,200)

        self.steps = []
        self.steps.append(PicSpinBox(icon = 'step.png',step = 1, integer=True))
        self.steps[-1].sigValueChanging.connect(self.makeFreqArray)
        self.intermediatePointsLayout.addWidget(self.steps[0],0,1)
        self.steps[0].setAlignment(QtCore.Qt.AlignCenter)
        self.steps[0].setValue(100)

        self.rampButton = PicButton('zig', checkable = False,size = 40)
        layout.addWidget(self.rampButton,0,0,1,1)
        self.rampButton.clicked.connect(self.toggleZigZag)

        self.loopButton = PicButton('loop', checkable = True,size = 40)
        layout.addWidget(self.loopButton,0,1,1,1)
        self.loopButton.clicked.connect(self.toggleLoop)

        # self.variables = ['volt','wavelength','thin','thick']
        # self.varCombo = QtGui.QComboBox()
        # self.varCombo.addItems(self.variables)
        # self.varCombo.currentIndexChanged.connect(self.changeVariable)
        # self.varCombo.setMaximumWidth(120)
        # layout.addWidget(self.varCombo,1,0,1,2)
        
        self.markerContainer = MarkerContainer()
        layout.addWidget(self.markerContainer,0,4,1,3)

        self.slider = NoClickSlider(orientation=QtCore.Qt.Horizontal)
        layout.addWidget(self.slider,0,4,1,3)
        self.slider.clickPos.connect(self.addPoint)

    def changeMode(self):
        if not self.scanner.captureRunningEvent.is_set():
            self.scanner.setScanMode(self.modes[self.modeCombo.currentIndex()], int(self.timeEdit.value()))

    def changeVariable(self, index):
        if not self.scanner.captureRunningEvent.is_set():
            self.scanner.setVariable(self.variables[index])

    def toggleLoop(self):
        self.scanner.toggleLooping()

    def toggleFreeScan(self):
        if not self.scanner.captureRunningEvent.is_set():
            self.scanner.toggleFreeScan()

    def toggleZigZag(self):
        if not self.scanner.captureRunningEvent.is_set():
            if self.scanner.zigZag:
                self.rampButton.setIcon('zig')
            else:
                self.rampButton.setIcon('zigzag')

            self.scanner.toggleZigZag()

    def enable(self):
        self.rampButton.setEnabled(True)
        self.timeEdit.setEnabled(True)
        self.modeCombo.setEnabled(True)
        self.timeEdit.setEnabled(True)
                
        for point in self.points:
            point.setEnabled(True)
        for step in self.steps:
            step.setEnabled(True)
        for marker in self.markerContainer.markers:
            marker.setEnabled(True)

        self.autoScanWidget.setEnabled(True)
        self.freeScanWidget.setEnabled(True)

    def disable(self):

        if self.scanner.freeScan:
            self.autoScanWidget.setDisabled(True)
        else:
            self.freeScanWidget.setDisabled(True)
            self.rampButton.setDisabled(True)
            self.timeEdit.setDisabled(True)
            self.modeCombo.setDisabled(True)
            self.timeEdit.setDisabled(True)

            for point in self.points:
                point.setDisabled(True)
            for step in self.steps:
                step.setDisabled(True)
            for marker in self.markerContainer.markers:
                marker.setDisabled(True)

    def makeFreqArray(self):
        variable = 'wavelength' #placeholder
        points = [float(p.value()) for p in self.points]
        steps = [int(s.value()) for s in self.steps]

        self.scanner.makeFreqArray(variable,points,steps)

    def updateUI(self, progress, scanVariable, scanVariables):
        
        self.slider.update(progress)

        self.freeScanWidget.updateSetPoints(scanVariables['wavelength'],
                                            scanVariables['thick'],
                                            scanVariables['thin'])


    # Methods for adding and removing points to the scanregion and correctly updating
    # their positions

    def addPoint(self, pos):

        freq = float(self.points[0].value()) + \
            (float(self.points[-1].value()) - float(self.points[0].value()))*pos

        for point in self.points[:-1]:
            if freq < point.value():
                return

        newPoint = PicSpinBox(icon = 'marker',value = freq, step = 0.001)
        self.points.insert(-1,newPoint)
        self.points[-2].setMaximumWidth(150)
        self.points[-2].sigValueChanging.connect(self.updateMarkerPos)
        self.points[-2].sigValueChanging.connect(self.makeFreqArray)
        self.intermediatePointsLayout.addWidget(self.points[-2],0,2*len(self.points[1:-1]))

        newStep = PicSpinBox(icon = 'step',step = 1, integer=True)
        self.steps.append(newStep)
        self.steps[-1].sigValueChanging.connect(self.makeFreqArray)
        self.steps[-1].setAlignment(QtCore.Qt.AlignCenter)
        self.intermediatePointsLayout.addWidget(self.steps[-1],0,2*len(self.points[1:-1])+1)

        self.markerContainer.addMarker()
        self.markerContainer.markers[-1].removeMe.connect(lambda: self.removePoint(newPoint,newStep))
        self.markerContainer.markers[-1].moved.connect(self.updatePointBox)
        self.updateMarkerPos()

    def updatePointBox(self, marker):
        i = self.markerContainer.markers.index(marker)
        delta = float(self.points[-1].value())-float(self.points[0].value())
        marker.freqPos = (marker.pos+0.5*marker.size().width())/self.slider.size().width()
        self.points[i+1].sigValueChanging.disconnect(self.updateMarkerPos)
        self.points[i+1].sigValueChanging.disconnect(self.makeFreqArray)
        self.points[i+1].setValue(marker.freqPos * delta + float(self.points[0].value()))
        self.points[i+1].sigValueChanging.connect(self.updateMarkerPos)
        self.points[i+1].sigValueChanging.connect(self.makeFreqArray)

    def removePoint(self,point,step):

        markerIndex = self.points.index(point)

        self.points.remove(point)
        self.intermediatePointsLayout.removeWidget(point)
        point.setParent(None)        

        self.steps.remove(step)
        self.intermediatePointsLayout.removeWidget(step)
        step.setParent(None)

        self.updateMarkerPos()

    def updateMarkerPos(self):

        for i,point in enumerate(self.points[1:-1]):
            delta = float(self.points[-1].value())-float(self.points[0].value())

            if not delta == 0:
                freqPos = (float(point.text())-float(self.points[0].value()))/delta
            else:
                freqPos = float(self.points[0].value())

            self.markerContainer.markers[i].freqPos = freqPos
            self.markerContainer.updateMarkers()


class Marker(QtGui.QLabel):
    removeMe = QtCore.Signal(object)
    moved = QtCore.Signal(object)
    def __init__(self, parent=None):
        super(Marker, self).__init__(parent)
        self.setGeometry(10, 10, 20, 20)
        self.setScaledContents(True)
        self.setPixmap(QtGui.QPixmap('./gui/resources/marker'))

        self.pos = 0
        self.freqPos = 0

        self.show()

    def mousePressEvent(self,ev):
        if ev.button() == QtCore.Qt.RightButton:
            self.removeMe.emit(True)
        ev.ignore()

    def mouseMoveEvent(self, ev):
        x = ev.x()
        if not x==0 :
            self.pos = self.pos + x - 0.5*self.size().width()
            self.moveMe()

        self.moved.emit(self)

    def moveMe(self):
        self.move(self.pos,0)


class MarkerContainer(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MarkerContainer, self).__init__(parent)

        self.markers = []

    def addMarker(self):
        marker = Marker(parent = self)
        self.markers.append(marker)
        marker.removeMe.connect(lambda: self.removeMarker(marker))


    def removeMarker(self,marker):
        self.markers.remove(marker)
        marker.setParent(None)
        del marker

    def updateMarkers(self):
        for marker in self.markers:
            marker.move(marker.freqPos*self.size().width()-0.5*marker.size().width(),0)

    def resizeEvent(self, event):
        super(MarkerContainer, self).resizeEvent(event)
        self.updateMarkers()

class FreeScanWidget(QtGui.QWidget):
    def __init__(self,parent, globalSession):
        super(FreeScanWidget,self).__init__(parent)

        self.globalSession = globalSession
        self.scanner = self.globalSession.scanner

        self.layout = QtGui.QGridLayout(self)

        self.freqLabel = QtGui.QLabel('Voltage Setpoint')
        self.layout.addWidget(self.freqLabel,0,3)
        self.waveLengthSpinBox = QtGui.QDoubleSpinBox(parent = self)
        self.waveLengthSpinBox.setDecimals(4)
        self.waveLengthSpinBox.setRange(-10**7,10**7)
        self.waveLengthSpinBox.setMaximumWidth(120)
        self.waveLengthSpinBox.setMinimumWidth(120)
        self.layout.addWidget(self.waveLengthSpinBox,0,4)

        self.waveReadBackLabel = QtGui.QLabel('Wavelength Readback')
        self.layout.addWidget(self.waveReadBackLabel,0,5)
        self.waveLengthReadBack = QtGui.QLineEdit()
        self.waveLengthReadBack.setMaximumWidth(120)
        self.waveLengthReadBack.setMinimumWidth(120)
        self.waveLengthReadBack.setReadOnly(True)
        self.layout.addWidget(self.waveLengthReadBack,0,6)

        # self.layout.addWidget(QtGui.QLabel('Thin Etalon Setpoint'),1,3)
        # self.thinSpinBox = pg.SpinBox(step = 1,value = 0, int = True, parent = self)
        # self.thinSpinBox.setMaximumWidth(120)
        # self.thinSpinBox.setMinimumWidth(120)
        # self.layout.addWidget(self.thinSpinBox,1,4)

        self.thinLabel = QtGui.QLabel('Thin Etalon Readback')
        self.layout.addWidget(self.thinLabel,1,5)
        self.thinReadBack = QtGui.QLineEdit()
        self.thinReadBack.setMaximumWidth(120)
        self.thinReadBack.setMinimumWidth(120)
        self.thinReadBack.setReadOnly(True)
        self.thinReadBack.setVisible(False)
        self.layout.addWidget(self.thinReadBack,1,6)

        # self.layout.addWidget(QtGui.QLabel('Thick Etalon Setpoint'),2,3)
        # self.thickSpinBox = pg.SpinBox(step = 1,value = 0, int = True, parent = self)
        # self.thickSpinBox.setMaximumWidth(120)
        # self.thickSpinBox.setMinimumWidth(120)
        # self.layout.addWidget(self.thickSpinBox,2,4)

        self.thickLabel = QtGui.QLabel('Thick Etalon Readback')
        self.layout.addWidget(self.thickLabel,2,5)
        self.thickReadBack = QtGui.QLineEdit()
        self.thickReadBack.setMaximumWidth(120)
        self.thickReadBack.setMinimumWidth(120)
        self.thickReadBack.setReadOnly(True)
        self.thickReadBack.setVisible(False)
        self.layout.addWidget(self.thickReadBack,2,6)

        self.setButtonWL = QtGui.QPushButton('Set Voltage')
        self.setButtonWL.setIconSize( QtCore.QSize(35, 35))
        # self.confirmButton.setIcon(QtGui.QIcon('./gui/resources/loop'))
        self.layout.addWidget(self.setButtonWL,1,4)
        self.setButtonWL.clicked.connect(lambda: self.freqChange('button','wavelength'))


        # self.confirmButtonThick = QtGui.QPushButton('Confirm')
        # self.confirmButtonThick.setIconSize( QtCore.QSize(35, 35))
        # # self.confirmButton.setIcon(QtGui.QIcon('./gui/resources/loop'))
        # self.layout.addWidget(self.confirmButtonThick,1,7)
        # self.confirmButtonThick.clicked.connect(lambda: self.freqChange('button','thick'))

        # self.confirmButtonThin = QtGui.QPushButton('Confirm')
        # self.confirmButtonThin.setIconSize( QtCore.QSize(35, 35))
        # # self.confirmButton.setIcon(QtGui.QIcon('./gui/resources/loop'))
        # self.layout.addWidget(self.confirmButtonThin,2,7)
        # self.confirmButtonThin.clicked.connect(lambda: self.freqChange('button','thin'))


        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.updateReadback)
        self.updateTimer.start(30)

        self.laser = 'CW'

    def updateReadback(self):
        
        if not self.laser == self.scanner.settings.laser:
            if self.scanner.settings.laser == 'CW':
                self.laser = 'CW'
                self.setButtonWL.setText('Set Voltage')
                self.freqLabel.setText('Voltage setpoint')

            elif self.scanner.settings.laser == 'RILIS':
                self.laser = 'RILIS'
                self.setButtonWL.setText('Set Wavelength')
                self.freqLabel.setText('Wavelength setpoint')
            
            else:
                self.laser = 'CW without wavemeter'

        if self.laser == 'RILIS':
            self.thinReadBack.setText(str(self.globalSession.dataStreams['thin'].getLatestValue()))
            self.thickReadBack.setText(str(self.globalSession.dataStreams['thick'].getLatestValue()))
            self.thinReadBack.setVisible(True)
            self.thinLabel.setVisible(True)
            self.thickReadBack.setVisible(True)
            self.thickLabel.setVisible(True)
        else:
            self.thinReadBack.setVisible(False)
            self.thinLabel.setVisible(False)
            self.thickReadBack.setVisible(False)
            self.thickLabel.setVisible(False)

        if not self.laser == 'CW without wavemeter':
            self.waveReadBackLabel.setVisible(True)
            self.waveLengthReadBack.setVisible(True)
            self.waveLengthReadBack.setText(str(self.globalSession.dataStreams['freq'].getLatestValue()))
        else:
            self.waveReadBackLabel.setVisible(False)
            self.waveLengthReadBack.setVisible(False)

        if self.scanner.captureRunningEvent.is_set():
            self.setDisabled(True)
        else:
            self.setEnabled(True)

    def updateSetPoints(self,wl,thick,thin):
        self.waveLengthSpinBox.setValue(round(wl,3))
        # self.thinSpinBox.setValue(thick)
        # self.thickSpinBox.setValue(thin)

    def freqChange(self, sender, variable):

        if sender == 'spinbox' and self.scanner.captureRunningEvent.is_set():
            return

        scanVariables = {'wavelength':self.waveLengthSpinBox.value(),
                    'volt':self.waveLengthSpinBox.value(), #}
                    'thin':0 ,#self.thinSpinBox.value(),
                    'thick':0 }#self.thickSpinBox.value()}

        self.scanner.setCurrentValue(variable, scanVariables)


class PicSpinBox(pg.SpinBox):

    def __init__(self, icon, step=0.01,value=0, integer = False, parent=None):
        value = float(value)
        super(PicSpinBox, self).__init__(parent,value=value,int=integer,step=step)

        imagePath = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Code\\gui\\resources\\' + icon

        self.pic = QtGui.QToolButton(self)
        self.pic.setIcon(QtGui.QIcon(imagePath))
        self.pic.setStyleSheet('border: 0px; padding: 0px;')
        self.pic.setCursor(QtCore.Qt.ArrowCursor)

        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.pic.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth*2 + 2),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth*2 + 2))

        self.setAlignment(QtCore.Qt.AlignLeft)
        # self.setMaximumWidth(150)

    def resizeEvent(self, event):
        buttonSize = self.pic.sizeHint()
        frameWidth = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.pic.move(self.rect().right() - frameWidth - 1.6*buttonSize.width(),
                         (self.rect().bottom() - buttonSize.height() + 1)/2)
        super(PicSpinBox, self).resizeEvent(event)


class NoClickSlider(QtGui.QSlider):
    clickPos = QtCore.Signal(object)
    def __init__(self, orientation):
        super(NoClickSlider,self).__init__(orientation)

    def mousePressEvent(self,ev):
        pass
        
        # if ev.button() == QtCore.Qt.LeftButton:
        #     self.clickPos.emit(ev.x()/self.size().width())
            
        # ev.ignore() 

    def wheelEvent(self,ev):
        ev.ignore()

    def keyPressEvent(self,ev):
        ev.ignore()

    def update(self, pos):
        self.setValue(pos)




