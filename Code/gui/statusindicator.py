import pyqtgraph as pg
from PyQt4 import QtCore,QtGui

class StatusIndicator(QtGui.QWidget):
    def __init__(self, globalSession):
        super(StatusIndicator,self).__init__()

        self.globalSession = globalSession
        self.scanner = self.globalSession.scanner

        self.layout = QtGui.QGridLayout(self)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        # self.setStyleSheet("StatusIndicator { color : green; font: bold 34px; }")
        # self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.rateLabel = QtGui.QLabel('')
        self.rateLayout = QtGui.QHBoxLayout()
        self.rateLayout.setAlignment(QtCore.Qt.AlignRight)
        self.layout.addLayout(self.rateLayout,0,0)        
        self.rateLayout.addWidget(QtGui.QLabel('Rate:'))
        self.rateLayout.addWidget(self.rateLabel)

        self.freqLabel = QtGui.QLabel('')
        self.freqLayout = QtGui.QHBoxLayout()
        self.freqLayout.setAlignment(QtCore.Qt.AlignRight)
        self.layout.addLayout(self.freqLayout,1,0)
        self.freqLayout.addWidget(QtGui.QLabel('Frequency:'))
        self.freqLayout.addWidget(self.freqLabel)

        self.runningLabel = QtGui.QLabel('')
        self.runningLayout = QtGui.QHBoxLayout()
        self.runningLayout.setAlignment(QtCore.Qt.AlignRight)
        self.layout.addLayout(self.runningLayout,0,1)
        self.runningLayout.addWidget(QtGui.QLabel('Scan running:'))
        self.runningLayout.addWidget(self.runningLabel)

        self.laserOKLabel = QtGui.QLabel('')
        self.laserLayout = QtGui.QHBoxLayout()
        self.laserLayout.setAlignment(QtCore.Qt.AlignRight)
        self.layout.addLayout(self.laserLayout,1,1)        
        self.laserLayout.addWidget(QtGui.QLabel('Laser status:'))
        self.laserLayout.addWidget(self.laserOKLabel)

        self.superCycleLabel = QtGui.QLabel('')
        self.superCycleLayout = QtGui.QHBoxLayout()
        self.superCycleLayout.setAlignment(QtCore.Qt.AlignRight)
        self.layout.addLayout(self.superCycleLayout,0,2)        
        self.superCycleLayout.addWidget(QtGui.QLabel('SuperCycle number:'))
        self.superCycleLayout.addWidget(self.superCycleLabel)

        self.pForHRSLabel = QtGui.QLabel('')
        self.pForHRSLayout = QtGui.QHBoxLayout()
        self.pForHRSLayout.setAlignment(QtCore.Qt.AlignRight)
        self.layout.addLayout(self.pForHRSLayout,1,2)        
        self.pForHRSLayout.addWidget(QtGui.QLabel('Protons on HRS:'))
        self.pForHRSLayout.addWidget(self.pForHRSLabel)

    def updateStatus(self):

        try:
            rate = self.globalSession.dataStreams['rate'].getLatestValue()
            self.rateLabel.setText(str(round(rate)) + ' Hz')
        except:
            self.rateLabel.setText('0.0 Hz')

        try:
            freq = self.globalSession.dataStreams['freq'].getLatestValue()
            self.freqLabel.setText(str(freq))
        except:
            self.freqLabel.setText('0.0 Hz')

        if self.scanner.captureRunningEvent.is_set():
            self.runningLabel.setStyleSheet("QLabel { background-color: green }" )
        else:
            self.runningLabel.setStyleSheet("QLabel { background-color: red }" )

        if self.scanner.controlEvent.is_set():
            self.laserOKLabel.setStyleSheet("QLabel { background-color: green }" )
        else:
            self.laserOKLabel.setStyleSheet("QLabel { background-color: red }" )

        if self.scanner.protonPulse.value:
            self.pForHRSLabel.setStyleSheet("QLabel { background-color: green }" )
        else:
            self.pForHRSLabel.setStyleSheet("QLabel { background-color: red }" )

        self.superCycleLabel.setText(str(self.scanner.currentCycle.value) +\
            '/' + str(self.scanner.protonsPerCycle.value))








