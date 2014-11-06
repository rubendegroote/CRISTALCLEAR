#!/usr/bin/python

"""

Main frame of cristal application.

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch


"""

import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import pyqtgraph.dockarea as da
import numpy as np
import os

from centraldockarea import CentralDockArea
from core.session import GlobalSession
from statusindicator import StatusIndicator
from scannerwidget import ScannerWidget
from picbutton import PicButton
from gui.launcher import Launcher
from core.settings import SessionSettings



class MainWindow(QtGui.QMainWindow):
    """

    Main frame class for the cristal
    data acquisition project

    kieran.renfrew.campbell@cern.ch
    ruben.degroote@cern.ch

    """

    def __init__(self):
        super(MainWindow, self).__init__()

        settings = SessionSettings()
    
        self.launcher = Launcher(settings)
        self.launcher.show()

        self.launcher.launched.connect(self.startFromLauncher)


    def startFromLauncher(self,globalSession):


        self.globalSession = globalSession
        self.settings = self.globalSession.settings
        self.scanner = self.globalSession.scanner

        self.InitUI()

        if self.settings.cristalMode:
            self.statusTimer = QtCore.QTimer()
            self.statusTimer.timeout.connect(self.statusIndicator.updateStatus)
            self.statusTimer.start(100)

        self.showMaximized()
        self.launcher.close()

    def InitUI(self):
        """
        UI initialisation
        """
        if self.settings.cristalMode:

            self.freqToolBar = QtGui.QToolBar('CRISTALFREQ')
            self.freqToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.addToolBar(self.freqToolBar)

        self.createDockArea()


        if self.settings.cristalMode:
            self.scannerWidget = ScannerWidget(self.globalSession)
            self.scanner.captureDone.connect(self.onStopCapture)
            self.freqToolBar.addWidget(self.scannerWidget)

            self.controlButton = self.scannerWidget.controlButton
            self.controlButton.clicked.connect(self.onNew)

        self.helpButton = PicButton('help',size = 70)
        self.helpButton.clicked.connect(self.onDocumentation)

        if self.settings.cristalMode:
            self.graphButton = PicButton('graph', checkable = True,size = 70)
            self.graphButton.clicked.connect(self.showDataStream)
            
            self.plotButton = PicButton('plot.png',size = 70)
            self.plotButton.clicked.connect(self.centralDock.newGraph)

            self.settingsButton = PicButton('Settings.png',checkable = True,size = 70)
            self.settingsButton.clicked.connect(self.showSettings)

            self.statusIndicator = StatusIndicator(self.globalSession)

        self.consoleButton = PicButton('console.png',checkable = True,size = 70)
        self.consoleButton.clicked.connect(self.showConsole)

        if self.settings.clearMode:
            self.analyseButton = PicButton('analyse.png',checkable = True,size = 70)
            self.analyseButton.clicked.connect(self.showAnalysis)

        self.logBookButton = PicButton('logbook.png',checkable = True,size = 70)
        self.logBookButton.clicked.connect(self.showLogbook)

        self.toolbar = QtGui.QToolBar('CRISTAL')
        self.toolbar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        if self.settings.cristalMode:
            self.toolbar.addWidget(self.settingsButton)

        self.toolbar.addWidget(self.consoleButton)
        self.toolbar.addWidget(self.logBookButton)

        if self.settings.clearMode:
            self.toolbar.addWidget(self.analyseButton)

        if self.settings.cristalMode:
            self.toolbar.addWidget(self.plotButton)
            self.toolbar.addWidget(self.graphButton)
        
        self.toolbar.addWidget(self.helpButton)
        
        if self.settings.cristalMode:
            self.toolbar.addSeparator()
            self.toolbar.addWidget(self.statusIndicator)

        self.addToolBar(QtCore.Qt.BottomToolBarArea,self.toolbar)

    def onNew(self):
        self.controlButton.setIcon('start.png')
        self.controlButton.clicked.disconnect(self.onNew)
        self.controlButton.clicked.connect(self.onStartCapture)

        newCapture = self.globalSession.newCapture()
            
        # Make a new entry for the new capture
        self.centralDock.logViewer.newEntry(capture = True)

    def onStartCapture(self):
        self.scanner.resetScan()

        cap,capLog = self.globalSession.getCurrentCaptureAndLog()
        self.scanner.captureRunningEvent.set()
        self.scannerWidget.disable()

        self.globalSession.running = True
        self.centralDock.settingsWidget.setStatus(False)

        # Get the latest settings from the UI
        cap.settings = self.centralDock.settingsWidget.getSettings()
        cap.settings.zigZag = self.scanner.zigZag
        cap.settings.scanLength = len(self.scanner.scanArray)
        cap.settings.timePerStep = self.scanner.timePerStep
        cap.settings.sanitise()

        # adds these settings to the logbook
        capLog.addSettingsToProperties()
        self.centralDock.logViewer.update()

        #Start Acquisistion
        cap.run()

        for dock in [dock for dock in self.centralDock.docks \
                if self.centralDock.isGraphDock(dock)]:
            self.centralDock.docks[dock].updateToCurrentCapture()

        self.controlButton.setIcon('stop.png')
        self.controlButton.clicked.disconnect(self.onStartCapture)
        self.controlButton.clicked.connect(self.onStopCapture)

    def onStopCapture(self):
        self.scanner.captureRunningEvent.clear()
        self.scanner.recordingEvent.clear()

        self.scannerWidget.autoScanWidget.setEnabled(True)
        self.scannerWidget.freeScanWidget.setEnabled(True)
        self.scannerWidget.enable()
        
        self.controlButton.setIcon('new.png')
        self.controlButton.clicked.disconnect(self.onStopCapture)
        self.controlButton.clicked.connect(self.onNew)

        cap = self.globalSession.getCurrentCapture()
        cap.stopRun()

        self.centralDock.logViewer.timeStampCapture()
        self.centralDock.logViewer.update()
        
        self.globalSession.running = False

        self.centralDock.settingsWidget.setStatus(True)

    def showLogbook(self):
        if not self.centralDock.logViewDock.isVisible():
            self.centralDock.logViewDock.setVisible(True)
        else:
            self.centralDock.logViewDock.setVisible(False)

    def showAnalysis(self):
        if not self.centralDock.analysisDock.isVisible():
            self.centralDock.analysisDock.setVisible(True)
        else:
            self.centralDock.analysisDock.setVisible(False)

    def showConsole(self):
        if not self.centralDock.consoleDock.isVisible():
            self.centralDock.consoleDock.setVisible(True)
        else:
            self.centralDock.consoleDock.setVisible(False)

    def showToDo(self):
        if not self.centralDock.toDoDock.isVisible():
            self.centralDock.toDoDock.setVisible(True)
        else:
            self.centralDock.toDoDock.setVisible(False)

    def showSettings(self):
        if not self.centralDock.settingsDock.isVisible():
            self.centralDock.settingsDock.setVisible(True)
        else:
            self.centralDock.settingsDock.setVisible(False)

    def showDataStream(self):
        if not self.centralDock.dataStreamsDock.isVisible():
            self.centralDock.dataStreamsDock.setVisible(True)
            self.centralDock.dataStreamsDock.startTimer()
        else:
            self.centralDock.dataStreamsDock.setVisible(False)
            self.centralDock.dataStreamsDock.stopTimer()


    def createDockArea(self):
        """
        Creates main Dock Area
        """
        self.centralDock = CentralDockArea(self.globalSession)
        self.setCentralWidget(self.centralDock)

    def setSBText(self, text):
        """
        Sets the text on the status bar
        """
        if not text == None:
            self.sb.showMessage(text)
        else:
            self.sb.showMessage('Ready')

    def onDocumentation(self):
        """
        When user clicks help -> documentation
        """
        import os
        path = os.getcwd().split('Code')[0] + 'doc\\report.pdf'
        os.startfile(path)

    def closeEvent(self,event):
        """
        Called to exit program
        """

        try:
            if self.globalSession.running:
                event.ignore()
                return
        except:
            pass


        quit_msg = "Are you sure you want to exit the program?"
        reply = QtGui.QMessageBox.question(self, 'Message', 
                         quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            
            self.scanner.stopProcesses()
            self.globalSession.stopProgram = True

            try:
                self.globalSession.currentCapture.saveSession()
                self.statusTimer.stop()
            except AttributeError:
                pass # Gets thrown if no captures have been started when closing the program

            event.accept()
        else:
            event.ignore()

