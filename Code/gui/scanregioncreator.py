import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import numpy as np


class ScanRegionCreator(QtGui.QWidget):
    
    def __init__(self):
        super(ScanRegionCreator, self).__init__()
        
        self.initUI()

        self.scanLength = np.linspace(0,5,1000)
        self.scanVolts = self.scanLength

        self.updatePlot()
        
    def initUI(self):      

        self.layout = QtGui.QGridLayout(self)

        self.selectorLevel1 = QtGui.QFrame()
        self.layout.addWidget(self.selectorLevel1,1,0,1,2)
        self.selectorLayoutLevel1 = QtGui.QGridLayout(self.selectorLevel1)


        self.selectorLevel2 = QtGui.QFrame()
        self.selectorLayoutLevel2 = QtGui.QGridLayout(self.selectorLevel2)
        self.selectorLayoutLevel1.addWidget(self.selectorLevel2,0,0,1,6)

        label = QtGui.QLabel('Wait for ')
        self.selectorLayoutLevel2.addWidget(label, 2,0)

        self.cyclesSpinBox = pg.SpinBox(value=1, int=True,step=1, bounds = (1,None))
        self.cyclesSpinBox.setMinimumWidth(70)
        self.selectorLayoutLevel2.addWidget(self.cyclesSpinBox,2,1)

        label = QtGui.QLabel('CPU cycles each step')
        self.selectorLayoutLevel2.addWidget(label, 2,2,1,3)


        label = QtGui.QLabel('Scan from')
        self.selectorLayoutLevel2.addWidget(label, 1,0)

        self.fromSpinBox = pg.SpinBox(value=0,suffix = 'V',decimals = 10)
        self.fromSpinBox.setMinimumWidth(50)
        self.selectorLayoutLevel2.addWidget(self.fromSpinBox,1,1)

        label = QtGui.QLabel('to')
        self.selectorLayoutLevel2.addWidget(label, 1,2)

        self.toSpinBox = pg.SpinBox(value=5,suffix = 'V',decimals = 10)
        self.toSpinBox.setMinimumWidth(50)
        self.selectorLayoutLevel2.addWidget(self.toSpinBox,1,3)

        self.stepComboBox = QtGui.QComboBox()
        self.stepComboBox.setMinimumWidth(80)
        self.stepComboBox.addItem('in steps of')
        self.stepComboBox.addItem('in')
        self.stepOption = 0
        self.stepComboBox.activated.connect(self.changeStepOption)
        self.selectorLayoutLevel2.addWidget(self.stepComboBox,1,4)

        self.stepSpinBox = pg.SpinBox(value=0.01,suffix = 'V',decimals = 10,bounds = (0,None))
        self.stepSpinBox.setMinimumWidth(70)
        self.selectorLayoutLevel2.addWidget(self.stepSpinBox,1,5)

        self.clearButton = QtGui.QPushButton('Delete Base')
        self.clearButton.setMinimumWidth(75)
        self.clearButton.clicked.connect(self.clearBaseSeg)
        self.selectorLayoutLevel2.addWidget(self.clearButton, 3,4)

        self.addButton = QtGui.QPushButton('Add')
        self.addButton.setMinimumWidth(75)
        self.addButton.clicked.connect(self.add)
        self.selectorLayoutLevel2.addWidget(self.addButton, 3,5)

        self.selectorLayoutLevel2.setColumnStretch(6,1)

        label = QtGui.QLabel('Repeat')
        self.selectorLayoutLevel1.addWidget(label, 2,0)
        
        self.repeatSpinBox = pg.SpinBox(value=1, int=True,suffix = ' times',step=1, bounds = (0,None))
        self.repeatSpinBox.setMinimumWidth(70)
        self.repeatSpinBox.setMaximumWidth(140)
        self.selectorLayoutLevel1.addWidget(self.repeatSpinBox,2,1)

        label = QtGui.QLabel('in a ')
        self.selectorLayoutLevel1.addWidget(label, 2,2)

        self.patternComboBox = QtGui.QComboBox()
        self.patternComboBox.setMinimumWidth(70)
        self.patternComboBox.addItem('sawtooth')
        self.patternComboBox.addItem('triangular')
        self.patternOption = 0
        self.patternComboBox.activated.connect(self.changePatternOption)
        self.selectorLayoutLevel1.addWidget(self.patternComboBox,2,3)

        label = QtGui.QLabel('pattern.')
        self.selectorLayoutLevel1.addWidget(label, 2,4)

        self.undoRepButton = QtGui.QPushButton('Undo')
        self.undoRepButton.setMinimumWidth(75)
        self.undoRepButton.clicked.connect(self.undoRep)
        self.selectorLayoutLevel1.addWidget(self.undoRepButton, 3,4)

        self.repeatButton = QtGui.QPushButton('Repeat Base')
        self.repeatButton.setMinimumWidth(75)
        self.repeatButton.clicked.connect(self.repeat)
        self.selectorLayoutLevel1.addWidget(self.repeatButton, 3,5)

        self.selectorLayoutLevel1.setColumnStretch(7,1)

        gView = pg.GraphicsView()
        self.voltGraph = pg.PlotWidget()
        self.voltGraph.setMaximumHeight(250)
        self.selectorLayoutLevel1.addWidget(self.voltGraph,1,0,1,6)

        self.buttonsLayout = QtGui.QHBoxLayout()
        self.layout.addLayout(self.buttonsLayout,2,1)

        self.layout.setRowStretch(3,1)


        self.setWindowTitle('Scan Region Selection')


    def add(self):

        V0 = self.fromSpinBox.value()
        V1 = self.toSpinBox.value()
        dV = self.stepSpinBox.value()
        cycles = self.cyclesSpinBox.value()

        if self.stepOption==0:
            if V0<V1:
                newBit = np.repeat(np.arange(V0, V1, dV), cycles)
                self.scanLength = np.append(self.scanLength,newBit)
            else:
                newBit = np.repeat(np.arange(V1, V0, dV)[::-1], cycles)
                self.scanLength = np.append(self.scanLength,newBit)
        else:
            newBit = np.repeat(np.linspace(V0, V1, dV), cycles)
            self.scanLength = np.append(self.scanLength,newBit)

        self.scanVolts = self.scanLength

        self.updatePlot()

    def repeat(self):

        self.scanVolts = np.array([])
        
        for i in xrange(self.repeatSpinBox.value()):
                if self.patternOption == 1 and i%2==1:
                    self.scanVolts = np.append(self.scanVolts,self.scanLength[::-1])
                else:
                    self.scanVolts = np.append(self.scanVolts,self.scanLength)

        self.updatePlot()


    def updatePlot(self):
        self.voltGraph.plot(self.scanVolts, clear=True,pen='r')

    def undoRep(self):
        self.scanVolts = np.array([])
        self.voltGraph.plot(self.scanLength, clear=True,pen='r')

    def clearBaseSeg(self):
        self.scanLength = np.array([])
        self.scanVolts = np.array([])
        self.updatePlot()

    def changePatternOption(self,option):
        self.patternOption = option

    def changeStepOption(self,option):
        self.stepSpinBox.setParent(None)
        self.stepOption = option
        if option == 0:
            self.stepSpinBox = pg.SpinBox(value=0.01,suffix = 'V',decimals = 10,bounds = (0,None))
            self.stepSpinBox.setMinimumWidth(70)
            self.selectorLayoutLevel2.addWidget(self.stepSpinBox,1,5)
        else:
            self.stepSpinBox = pg.SpinBox(value=100, int=True,suffix = ' steps',step=1, bounds = (0,None))
            self.stepSpinBox.setMinimumWidth(70)
            self.selectorLayoutLevel2.addWidget(self.stepSpinBox,1,5)

    def getVoltage(self):
        return len(self.scanLength),self.scanVolts
