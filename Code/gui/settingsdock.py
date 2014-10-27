import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from pyqtgraph.dockarea import Dock

from splitter import MySplitter
from core.settings import SessionSettings
from scanregioncreator import ScanRegionCreator
from FrameLayout import FrameLayout

class SettingsDock(Dock):
    def __init__(self,name,size,globalSession):
        Dock.__init__(self,name,size)

        self.orientation = 'horizontal'
        self.autoOrient = False

        self.settingsWidget = SettingsWidget(globalSession)

        self.addWidget(self.settingsWidget)


class SettingsWidget(QtGui.QWidget):

    settingsUpdated = QtCore.Signal(object)

    def __init__(self, globalSession):
        super(SettingsWidget, self).__init__()

        self.globalSession = globalSession
        self.settings = self.globalSession.settings

        self.layout = QtGui.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop)


        self.layout.addWidget(QtGui.QLabel('Device:'), 0,0)

        self.deviceCombo = QtGui.QComboBox()
        self.deviceCombo.addItems(['None', 'NI 6221'])
        self.deviceCombo.currentIndexChanged.connect(self.selectDevice)
        self.layout.addWidget(self.deviceCombo, 0,1)

        self.label6 = QtGui.QLabel(self, text="Counter channel")
        self.label6.setDisabled(True)
        self.label6.setMaximumWidth(140)
        self.label6.setMinimumWidth(140)
        self.layout.addWidget(self.label6, 1,0)

        self.ctrEdit = QtGui.QLineEdit(self)
        self.ctrEdit.setDisabled(True)
        self.layout.addWidget(self.ctrEdit, 1,1)
        
        self.label8 = QtGui.QLabel(self, text="AO channel")
        self.label8.setDisabled(True)
        self.label8.setMaximumWidth(140)
        self.label8.setMinimumWidth(140)
        self.layout.addWidget(self.label8, 2,0)
        
        self.AOEdit = QtGui.QLineEdit(self)
        self.AOEdit.setDisabled(True)
        self.layout.addWidget(self.AOEdit, 2,1)
       
        self.label9 = QtGui.QLabel(self, text="AI channel")
        self.label9.setDisabled(True)
        self.label9.setMaximumWidth(140)
        self.label9.setMinimumWidth(140)    
        self.layout.addWidget(self.label9, 4,0)
        
        self.AIEdit = QtGui.QLineEdit(self)
        self.AIEdit.setDisabled(True)
        self.layout.addWidget(self.AIEdit, 4,1)

        
        self.label10 = QtGui.QLabel(self, text="Clock channel")
        self.label10.setDisabled(True)
        self.label10.setMaximumWidth(140)
        self.label10.setMinimumWidth(140)
        self.layout.addWidget(self.label10, 5,0)

        self.clockEdit = QtGui.QLineEdit(self)
        self.clockEdit.setDisabled(True)
        self.layout.addWidget(self.clockEdit, 5,1)

        self.label11 = QtGui.QLabel(self, text="Laser System")
        self.label11.setMaximumWidth(140)
        self.label11.setMinimumWidth(140)
        self.layout.addWidget(self.label11, 6,0)

        self.laserCombo = QtGui.QComboBox(self)
        self.laserCombo.addItems(['CW', 'RILIS', 'CW without wavemeter'])
        self.laserCombo.setCurrentIndex(2)
        self.layout.addWidget(self.laserCombo, 6,1)        

        self.setTextFields()

        self.retryConnectionsButton = QtGui.QPushButton('Confirm changes and reconnect to devices')
        self.retryConnectionsButton.clicked.connect(self.restartProcesses)
        self.layout.addWidget(self.retryConnectionsButton,8,1)

        # self.printPRLButton = QtGui.QPushButton('Print PRL')
        # self.printPRLButton.clicked.connect(self.printPRL)
        # self.layout.addWidget(self.printPRLButton,6,1)

    def printPRL(self):

        reply = QtGui.QMessageBox.question(self, 'PRL printer',
            'Are we settling for a PRL now? I am disappointed in you.')


    def restartProcesses(self):

        reply = QtGui.QMessageBox.question(self, 'Reconnect info',
            'Reconnecting could temporarily freeze application, please be patient.')

        self.setSettings()
        
        self.retryConnectionsButton.setDisabled(1)
        self.globalSession.createDataStream()
        self.globalSession.scanner.restartProcesses()

        self.settingsUpdated.emit(True)

        success = True


        #not the most elegant way, but meh
        message = self.globalSession.scanner.messageQueue.get()
        if not message[0]:
            success = False

        message = self.globalSession.scanner.messageQueue.get()
        if not message[0]:
            success = False

        message = self.globalSession.scanner.messageQueue.get()
        if not message[0]:
            success = False

        if not self.settings.laser == 'CW without wavemeter':
            message = self.globalSession.scanner.messageQueue.get()
            if not message[0]:
                success = False


        if success:
            message = 'Connections successful. Carry on!'
        else:
            message = 'Connections Failed. Please close CRISTAL and restart.'

        reply = QtGui.QMessageBox.question(self, 'Reconnect info',message)

        self.retryConnectionsButton.setEnabled(1)

    def restoreDefault(self):
        self.settings.resetDefaults()
        self.setTextFields(self.settings)

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

        self.settings.sanitise()

        self.globalSession.scanner.settings = self.settings

    def selectDevice(self):

        if str(self.deviceCombo.currentText()) == 'None':
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

    def setStatus(self, status):
        if status:
          self.ctrEdit.setEnabled(1)
          self.AOEdit.setEnabled(1)
          self.AIEdit.setEnabled(1)
          self.clockEdit.setEnabled(1)
          self.laserCombo.setEnabled(1)
          self.retryConnectionsButton.setEnabled(1)

        else:
          self.ctrEdit.setDisabled(1)
          self.AOEdit.setDisabled(1)
          self.AIEdit.setDisabled(1)
          self.clockEdit.setDisabled(1)
          self.laserCombo.setDisabled(1)
          self.retryConnectionsButton.setDisabled(1)

    def getSettings(self):
        self.setSettings()
        return self.settings


    def chooseLogBook(self):
        folder = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Logbook\\'
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Choose logbook file', folder)

        self.settings.logFile = fileName

        self.launchButton.setEnabled(True)
