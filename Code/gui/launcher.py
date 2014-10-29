import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import pyqtgraph.dockarea as da
import numpy as np
import os
import time

from gui.mframe import MainWindow
from core.session import GlobalSession
from core.scanner import Scanner
from centraldockarea import CentralDockArea
from core.session import GlobalSession
from statusindicator import StatusIndicator
from scannerwidget import ScannerWidget
from picbutton import PicButton



class Launcher(QtGui.QWidget):
    """

    Main frame class for the cristal
    data acquisition project

    kieran.renfrew.campbell@cern.ch
    ruben.degroote@cern.ch

    """
    def __init__(self,settings):
        super(Launcher, self).__init__()

        self.settings = settings

        self.layout = QtGui.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        picLabel = QtGui.QLabel()
        pixmap = QtGui.QPixmap(os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Code\\gui\\resources\\splash_loading')
        picLabel.setPixmap(pixmap)

        self.layout.addWidget(picLabel)

        settingsLayout = QtGui.QGridLayout()
        self.layout.addLayout(settingsLayout,1,0)


        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique')) #looks pretty!

        settingsLayout.addWidget(QtGui.QLabel('Device:'), 0,0)

        self.deviceCombo = QtGui.QComboBox()
        self.deviceCombo.addItems(['None', 'NI 6221'])
        self.deviceCombo.currentIndexChanged.connect(self.selectDevice)
        settingsLayout.addWidget(self.deviceCombo, 0,1)

        self.label6 = QtGui.QLabel(self, text="Counter channel")
        self.label6.setDisabled(True)
        self.label6.setMaximumWidth(140)
        self.label6.setMinimumWidth(140)
        settingsLayout.addWidget(self.label6, 1,0)

        self.ctrEdit = QtGui.QLineEdit(self)
        self.ctrEdit.setDisabled(True)
        settingsLayout.addWidget(self.ctrEdit, 1,1)
        
        self.label8 = QtGui.QLabel(self, text="AO channel")
        self.label8.setDisabled(True)
        self.label8.setMaximumWidth(140)
        self.label8.setMinimumWidth(140)
        settingsLayout.addWidget(self.label8, 2,0)
        
        self.AOEdit = QtGui.QLineEdit(self)
        self.AOEdit.setDisabled(True)
        settingsLayout.addWidget(self.AOEdit, 2,1)
       
        self.label9 = QtGui.QLabel(self, text="AI channel")
        self.label9.setDisabled(True)
        self.label9.setMaximumWidth(140)
        self.label9.setMinimumWidth(140)    
        settingsLayout.addWidget(self.label9, 4,0)
        
        self.AIEdit = QtGui.QLineEdit(self)
        self.AIEdit.setDisabled(True)
        settingsLayout.addWidget(self.AIEdit, 4,1)

        
        self.label10 = QtGui.QLabel(self, text="Clock channel")
        self.label10.setDisabled(True)
        self.label10.setMaximumWidth(140)
        self.label10.setMinimumWidth(140)
        settingsLayout.addWidget(self.label10, 5,0)

        self.clockEdit = QtGui.QLineEdit(self)
        self.clockEdit.setDisabled(True)
        settingsLayout.addWidget(self.clockEdit, 5,1)

        self.label11 = QtGui.QLabel(self, text="Laser System")
        self.label11.setMaximumWidth(140)
        self.label11.setMinimumWidth(140)
        settingsLayout.addWidget(self.label11, 6,0)

        self.laserCombo = QtGui.QComboBox(self)
        self.laserCombo.addItems(['CW', 'RILIS', 'CW without wavemeter'])
        self.laserCombo.setCurrentIndex(2)
        settingsLayout.addWidget(self.laserCombo, 6,1)        

        self.setTextFields()

        self.logButton = QtGui.QPushButton(self,text = 'Choose logbook file')
        self.logButton.clicked.connect(self.chooseLogBook)
        settingsLayout.addWidget(self.logButton,7,1)

        self.cristalCheck = QtGui.QCheckBox('CRISTAL')
        self.cristalCheck.setChecked(True)
        self.cristalCheck.stateChanged.connect(self.selectDevice)
        settingsLayout.addWidget(self.cristalCheck,8,0)

        self.clearCheck = QtGui.QCheckBox('CLEAR')
        self.clearCheck.setChecked(True)
        self.clearCheck.stateChanged.connect(self.selectDevice)
        settingsLayout.addWidget(self.clearCheck,8,1)


        self.launchButton = QtGui.QPushButton(self,text = 'Ok')
        self.launchButton.setDisabled(True)
        self.launchButton.clicked.connect(self.launch)
        settingsLayout.addWidget(self.launchButton,9,1)


    def selectDevice(self):

        if self.cristalCheck.checkState() == 0:
            self.deviceCombo.setDisabled(True) 
            self.laserCombo.setDisabled(True)
        else:
            self.deviceCombo.setEnabled(True) 
            self.laserCombo.setEnabled(True)

        if str(self.deviceCombo.currentText()) == 'None' or self.cristalCheck.checkState() == 0:
            self.label6.setDisabled(True)
            self.ctrEdit.setDisabled(True)
            self.label8.setDisabled(True)
            self.AOEdit.setDisabled(True)
            self.label9.setDisabled(True)
            self.AIEdit.setDisabled(True)
            self.label10.setDisabled(True)
            self.clockEdit.setDisabled(True)
            self.laserCombo.setCurrentIndex(2)

        else:
            self.label6.setEnabled(True)
            self.ctrEdit.setEnabled(True)
            self.label8.setEnabled(True)
            self.AOEdit.setEnabled(True)
            self.label9.setEnabled(True)
            self.AIEdit.setEnabled(True)
            self.label10.setEnabled(True)
            self.clockEdit.setEnabled(True)


    def chooseLogBook(self):
        folder = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Logbook\\'
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Choose logbook file', folder)

        self.settings.logFile = fileName

        self.launchButton.setEnabled(True)

    def setTextFields(self):
        self.ctrEdit.setText(str(self.settings.counterChannel))
        self.AOEdit.setText(str(self.settings.aoChannel))
        self.AIEdit.setText(str(self.settings.aiChannel))
        self.clockEdit.setText(str(self.settings.clockChannel))  

    def setSettings(self):

        if str(self.deviceCombo.currentText()) == 'None':
            self.settings.debugMode = True
            self.settings.laser = str(self.laserCombo.currentText())

        else:
            self.settings.debugMode = False
            self.settings.counterChannel = self.ctrEdit.text()
            self.settings.aoChannel = self.AOEdit.text()
            self.settings.aiChannel = self.AIEdit.text()
            self.settings.clockChannel = self.clockEdit.text()
            self.settings.laser = str(self.laserCombo.currentText())

        self.settings.cristalMode = self.cristalCheck.checkState() == 2
        self.settings.clearMode = self.clearCheck.checkState() == 2

        self.settings.sanitise()

    def launch(self):

        self.setSettings()
        
        if self.settings.laser == 'CW without wavemeter':
            totalProc = 2
        else:
            totalProc = 3
        
        if not self.settings.cristalMode:
            totalProc = 0
            
        # application variables
        title = "cristal - Data Acquisition for CRIS"
        self.progress = 0
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setStyleSheet(""" 
                QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                }

                QProgressBar::chunk {
                background-color: #52bdec;
                width: 20px;
                }
                """)
        self.progressBar.setRange(0,totalProc+1)

        self.layout.addWidget(self.progressBar,20,0,1,2)

        self.progressLabel = QtGui.QLabel()
        self.layout.addWidget(self.progressLabel,21,0,1,2)

        QtGui.QApplication.processEvents()
            
        captures = {}

        scanner = Scanner(self.settings)
        globalSession = GlobalSession(captures,scanner,self.settings)

        QtGui.QApplication.processEvents()

        mainWindow = MainWindow(parent = self,\
            globalSession = globalSession)
        mainWindow.setWindowTitle('CRISTAL')
        mainWindow.setObjectName(title)


        while self.progress < totalProc:
            self.progress = self.progress + 1

            message = scanner.messageQueue.get()
            if message[0]:
                self.updateProgressBar(message[1])

            QtGui.QApplication.processEvents()


        self.setHidden(True)
        mainWindow.showMaximized()


    def updateProgressBar(self,text):
        self.progressLabel.setText(text)
        self.progressBar.setValue(self.progress)

