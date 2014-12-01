import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import pyqtgraph.dockarea as da
import numpy as np
import os
import time

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
    launched = QtCore.Signal(object)
    def __init__(self, settings):
        super(Launcher, self).__init__()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.settings = settings

        self.layout = QtGui.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)

        picLabel = QtGui.QLabel()
        imagePath = self.settings.path + 'Code\\gui\\resources\\splash_loading'

        pixmap = QtGui.QPixmap(imagePath)
        picLabel.setPixmap(pixmap)

        self.layout.addWidget(picLabel)

        settingsLayout = QtGui.QGridLayout()
        self.layout.addLayout(settingsLayout,1,0)


        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique')) #looks pretty!

        settingsLayout.addWidget(QtGui.QLabel('Device:'), 0,0)

        self.deviceCombo = QtGui.QComboBox()
        self.deviceCombo.setToolTip('Choose the type of device you are using.\
 <b>None</b> generates random number data.')
        self.deviceCombo.addItems(['None', 'NI 6211'])
        self.deviceCombo.currentIndexChanged.connect(self.selectDevice)
        settingsLayout.addWidget(self.deviceCombo, 0,1)

        self.label6 = QtGui.QLabel(self, text="Counter channel")
        self.label6.setDisabled(True)
        self.label6.setMaximumWidth(140)
        self.label6.setMinimumWidth(140)
        settingsLayout.addWidget(self.label6, 1,0)

        self.ctrEdit = QtGui.QLineEdit(self)
        self.ctrEdit.setToolTip('Here you want to write the counter channel\
 of the NI Card. ctr1 corresponds to the physical channel <b>PFI3</b>.')
        self.ctrEdit.setDisabled(True)
        settingsLayout.addWidget(self.ctrEdit, 1,1)
        
        self.label8 = QtGui.QLabel(self, text="AO channel")
        self.label8.setDisabled(True)
        self.label8.setMaximumWidth(140)
        self.label8.setMinimumWidth(140)
        settingsLayout.addWidget(self.label8, 2,0)
        
        self.AOEdit = QtGui.QLineEdit(self)
        self.AOEdit.setToolTip('Here you want to write the analog output channel\
 of the NI Card you intend to use for laser control.')
        self.AOEdit.setDisabled(True)
        settingsLayout.addWidget(self.AOEdit, 2,1)
       
        self.label9 = QtGui.QLabel(self, text="AI channel")
        self.label9.setDisabled(True)
        self.label9.setMaximumWidth(140)
        self.label9.setMinimumWidth(140)    
        settingsLayout.addWidget(self.label9, 4,0)
        
        self.AIEdit = QtGui.QLineEdit(self)
        self.AIEdit.setToolTip('Here you want to write the analog input channels\
 of the NI Card <b> separated by a comma </b>.')
        self.AIEdit.setDisabled(True)
        settingsLayout.addWidget(self.AIEdit, 4,1)

        
        self.label10 = QtGui.QLabel(self, text="Clock channel")
        self.label10.setDisabled(True)
        self.label10.setMaximumWidth(140)
        self.label10.setMinimumWidth(140)
        settingsLayout.addWidget(self.label10, 5,0)

        self.clockEdit = QtGui.QLineEdit(self)
        self.clockEdit.setToolTip('Here you want to write the clock channel\
 of the NI Card you intend to use. This clock will be the synchronization point\
 for all the DAQ. <b> The maximal period the program can cope with is 3ms! <\b>')
        self.clockEdit.setDisabled(True)
        settingsLayout.addWidget(self.clockEdit, 5,1)

        self.label11 = QtGui.QLabel(self, text="Laser System")
        self.label11.setMaximumWidth(140)
        self.label11.setMinimumWidth(140)
        settingsLayout.addWidget(self.label11, 6,0)

        self.laserCombo = QtGui.QComboBox(self)
        self.laserCombo.setToolTip('Use this to select the laser system ypu want to\
 control. The option Without Wavemeter does not require a working labview\
 installation, the others do.')
        self.laserCombo.addItems(['CW Laser Voltage Scan', 'RILIS', 
            'CW Laser Voltage Scan Without Wavemeter', 'Matisse Manual Scan'])
        self.laserCombo.setCurrentIndex(2)
        settingsLayout.addWidget(self.laserCombo, 6,1)        

        self.setTextFields()

        self.logButton = QtGui.QPushButton(self,text = 'Choose logbook file')
        self.logButton.setToolTip('Click this to browse for a lobook file.\
 If this is your first time, and empty .txt file will do.')
        self.logButton.clicked.connect(self.chooseLogBook)
        settingsLayout.addWidget(self.logButton,7,1)

        self.cristalCheck = QtGui.QCheckBox('CRISTAL')
        self.cristalCheck.setToolTip('Check this box if ypu want to use CRISTAL\
 to acquire new data.')
        self.cristalCheck.setChecked(True)
        self.cristalCheck.stateChanged.connect(self.selectDevice)
        settingsLayout.addWidget(self.cristalCheck,8,0)

        self.clearCheck = QtGui.QCheckBox('CLEAR')
        self.clearCheck.setToolTip('Check this box if ypu want to use CLEAR\
 to analyse the acquried data.')
        self.clearCheck.setChecked(True)
        self.clearCheck.stateChanged.connect(self.selectDevice)
        settingsLayout.addWidget(self.clearCheck,8,1)


        self.launchButton = QtGui.QPushButton(self,text = 'Ok')
        self.launchButton.setToolTip('Clicking this button will launch the application\
 <b> once you have chosen an logbook file!<\b>')        
        self.launchButton.setDisabled(True)
        self.launchButton.clicked.connect(self.launch)
        settingsLayout.addWidget(self.launchButton,9,1)


        self.progText = ''

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
        folder =self.settings.path + 'Logbook\\'
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

    def disableAll(self):
        self.cristalCheck.setDisabled(True)
        self.clearCheck.setDisabled(True)
        self.deviceCombo.setDisabled(True)
        self.laserCombo.setDisabled(True)
        self.label6.setDisabled(True)
        self.ctrEdit.setDisabled(True)
        self.label8.setDisabled(True)
        self.AOEdit.setDisabled(True)
        self.label9.setDisabled(True)
        self.AIEdit.setDisabled(True)
        self.label10.setDisabled(True)
        self.clockEdit.setDisabled(True)
        self.laserCombo.setDisabled(True)
        self.launchButton.setDisabled(True)
        self.logButton.setDisabled(True)   

    def launch(self):

        self.setSettings()

        self.disableAll()
        
        if self.settings.laser == 'CW Laser Voltage Scan Without Wavemeter'                                                                                         :
            totalProc = 3
        else:
            totalProc = 4
        
        if not self.settings.cristalMode:
            totalProc = 1
            
        # application variables
        title = "cristal - Data Acquisition for CRIS"
        self.progress = 0
        self.progressBar = QtGui.QProgressBar(\
            format = 'Work package %v out of %m complete')
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
        self.progressBar.setRange(0,totalProc)

        self.layout.addWidget(self.progressBar,20,0,1,2)

        self.progressEdit = QtGui.QTextEdit()
        self.progressEdit.setReadOnly(True)
        self.progressEdit.setMinimumHeight(60)
        self.layout.addWidget(self.progressEdit,21,0,1,2)

        QtGui.QApplication.processEvents()
            
        captures = {}

        scanner = Scanner(self.settings)
        globalSession = GlobalSession(captures,scanner,self.settings)
        scanner.startProcesses()

        QtGui.QApplication.processEvents()

        while self.progress < totalProc:

            try:
                message = scanner.messageQueue.get_nowait()
                if message[0]:
                    self.progress = self.progress + 1
                    self.updateProgressBar(message[1])
                else:
                    self.updateProgressBar(message[1])
            except:
                time.sleep(0.005)

            QtGui.QApplication.processEvents()

        self.progressEdit.setHtml('Launching CRISTAL...')

        self.launched.emit(globalSession)

    def updateProgressBar(self,text):
        text = self.formatProgressText(text, error = 'fail' in text)
        if not 'logbook' in text:
            self.progText += text + "<br />"
            self.progressEdit.setHtml(self.progText)
        else:
            self.progressEdit.setHtml(text + '<br />' + self.progText)
            

        self.progressBar.setValue(self.progress)


    def formatProgressText(self,text,error = False):

        if error:
            color = 'red'
        else:
            color = 'green'

        text = text.replace('\n', '\n\t')
        first, newline, rest = text.partition('\n')
        text = "<font color=\"{0}\">".format(color) + first.split('\n')[0] + newline +\
               "<font color=\"black\">" + rest


        text = text.replace('\t', "&nbsp;&nbsp;&nbsp;&nbsp;")
        text = text.replace("\n", "<br />") + "<br />"

        return text
        

