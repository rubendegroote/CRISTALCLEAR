import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from pyqtgraph.dockarea import Dock

from splitter import MySplitter
from core.settings import SessionSettings
from scanregioncreator import ScanRegionCreator
from FrameLayout import FrameLayout

class ControlDock(Dock):
    def __init__(self,name,size):
        Dock.__init__(self,name,size)

        self.setMinimumWidth(500)
        self.setMaximumWidth(500)
        self.setMinimumHeight(650)
        

        self.orientation = 'horizontal'
        self.autoOrient = False

        scanWidget = QtGui.QWidget()
        grid = QtGui.QGridLayout(scanWidget)
        self.controlButton = QtGui.QPushButton('New')
        self.controlButton.setMinimumHeight(140)
        self.controlButton.setMaximumHeight(140)
        self.controlButton.setMinimumWidth(140)
        self.controlButton.setMaximumWidth(140)
        grid.addWidget(self.controlButton,0,0)

        self.newGraphButton = QtGui.QPushButton('New Graph')
        grid.addWidget(self.newGraphButton,1,0)

        self.settingsWidget = SessionSettingsWidget(init = SessionSettings())
        self.settingsWidget.setStatus(False)
        grid.addWidget(self.settingsWidget,0,1,1,2)

        self.layout.setRowStretch(2,1)

        self.scanRegionCreator = ScanRegionCreator()

        self.addWidget(scanWidget)
        self.addWidget(self.scanRegionCreator)


class SessionSettingsWidget(QtGui.QWidget):

    def __init__(self, init):
        super(SessionSettingsWidget, self).__init__()

        self.setMaximumWidth(300)
        # self.setMinimumWidth(255)

        self.layout = QtGui.QGridLayout(self)
        self.layout.setSpacing(0)
        self.capSettings = {}

        # texts

        label6 = QtGui.QLabel(self, text="Counter channel")
        label6.setMaximumWidth(140)
        label6.setMinimumWidth(140)
        label7 = QtGui.QLabel(self, text="AO channel")
        label7.setMaximumWidth(140)
        label7.setMinimumWidth(140)
        label8 = QtGui.QLabel(self, text="AI channel")
        label8.setMaximumWidth(140)
        label8.setMinimumWidth(140)    
        label9 = QtGui.QLabel(self, text="Clock channel")
        label9.setMaximumWidth(140)
        label9.setMinimumWidth(140)


        self.layout.addWidget(label6, 0,0)
        self.layout.addWidget(label7, 1,0)
        self.layout.addWidget(label8, 2,0)
        self.layout.addWidget(label9, 3,0)


        # text boxes
        self.txt6 = QtGui.QLineEdit(self)
        self.txt7 = QtGui.QLineEdit(self)
        self.txt8 = QtGui.QLineEdit(self)
        self.txt9 = QtGui.QLineEdit(self)


        self.setTextFields(init)

        self.txt6.textEdited.connect(self.setSettingsFromUI)
        self.txt7.textEdited.connect(self.setSettingsFromUI)
        self.txt8.textEdited.connect(self.setSettingsFromUI)
        self.txt9.textEdited.connect(self.setSettingsFromUI)

        
        self.layout.addWidget(self.txt6, 0,1)
        self.layout.addWidget(self.txt7, 1,1)
        self.layout.addWidget(self.txt8, 2,1)
        self.layout.addWidget(self.txt9, 3,1)


    def restoreDefault(self):
        self.settings.resetDefaults()
        self.setTextFields(self.settings)

    def setTextFields(self, settings):

        self.settings = settings
        self.txt6.setText(str(self.settings.counterChannel))
        self.txt7.setText(str(self.settings.aoChannel))
        self.txt8.setText(str(self.settings.aiChannel))
        self.txt9.setText(str(self.settings.clockChannel))



    def setSettingsFromUI(self):
        # do self settings here

        try:
            self.settings.counterChannel = self.txt6.text()
            self.settings.aoChannel = self.txt7.text()
            self.settings.aiChannel = self.txt8.text()
            self.settings.clockChannel = self.txt9.text()


            self.settings.sanitise()

        except ValueError:
            pass

    def setStatus(self, status):

        if status:

          self.txt6.setEnabled(1)
          self.txt7.setEnabled(1)
          self.txt8.setEnabled(1)
          self.txt9.setEnabled(1)
        else:

          self.txt6.setDisabled(1)
          self.txt7.setDisabled(1)
          self.txt8.setDisabled(1)
          self.txt9.setDisabled(1)



    def getSettings(self):
        self.setSettingsFromUI()
        return self.settings

