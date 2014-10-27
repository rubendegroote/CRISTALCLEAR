#!/usr/bin/python

"""
kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

"""

from core.session import GlobalSession
from core.scanner import Scanner
from core.settings import SessionSettings
from multiprocessing import freeze_support

import sys,os

from PyQt4 import QtCore,QtGui

import pyqtgraph as pg
import pyqtgraph.dockarea as da
from gui.logviewdock import LogViewDock
from gui.analysisdock import AnalysisDock
from pyqtgraphBundleUtils import *
from pyqtgraph.graphicsItems import TextItem
from pyqtgraph import setConfigOption
from scipy.sparse.csgraph import _validation

# OpenGL seems to buggy (refresh issues, crashes, etc.)
setConfigOption('useOpenGL', False)
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


class MainWindow(QtGui.QMainWindow):
    """

    Main frame class for the cristal
    data acquisition project

    kieran.renfrew.campbell@cern.ch
    ruben.degroote@cern.ch

    """

    def __init__(self, parent, globalSession):
        super(MainWindow, self).__init__(parent)

        self.globalSession = globalSession

        self.InitUI()

    def InitUI(self):
        """
        UI initialisation
        """

        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('plastique')) #looks pretty!
        
        self.dockArea = da.DockArea()
        self.setCentralWidget(self.dockArea)

        self.logViewDock = LogViewDock(globalSession = self.globalSession, 
            name='Log Book',size = (1,1))
        self.logViewer = self.logViewDock.viewer
        self.logViewer.openLogbook()
        self.dockArea.addDock(self.logViewDock)

        self.analysisDock = AnalysisDock(name = 'Analysis', size = (1,1), 
                        globalSession = self.globalSession)
        self.dockArea.addDock(self.analysisDock,'right')


if __name__ == "__main__":

    # add freeze support
    freeze_support()

    # application variables
    title = "CRISTAL Logbook Viewer"

    app = QtGui.QApplication(sys.argv)

    captures = {}
    settings = SessionSettings()
    scanner = Scanner(settings)
    globalSession = GlobalSession(captures,scanner,settings)
    globalSession.stopProgram = True #this is not an acquisition program, so prevent threads to be spawned

    mainWindow = MainWindow(parent = None,\
        globalSession = globalSession)

    mainWindow.setWindowTitle('CRISTAL Logbook Viewer')
    mainWindow.setObjectName(title)
    mainWindow.showMaximized()
    sys.exit(app.exec_())