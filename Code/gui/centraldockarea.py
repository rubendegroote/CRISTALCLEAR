#!/usr/bin/python

"""
Main dockarea that owns the captures and the widgets

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

"""

import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import pyqtgraph.dockarea as da
import threading

from core.logbook import *
from graphdock import GraphDock
from logviewdock import LogViewDock
from settingsdock import SettingsDock
from consoledock import ConsoleDock
from newusersdock import NewUsersDock
from tododock import ToDoDock
from analysisdock import AnalysisDock
from datastreamsdock import DataStreamsDock

class CentralDockArea(da.DockArea):
    """
    SuperDock class
    """
    def __init__(self,globalSession):

        da.DockArea.__init__(self,globalSession)

        self.globalSession = globalSession

        self.logViewer = None

        self.createUIDocks()

    def createUIDocks(self):

        if self.globalSession.settings.cristalMode:
            # self.settingsDock = SettingsDock(name='Settings',size = (1,1), globalSession = self.globalSession)
            # self.settingsWidget = self.settingsDock.settingsWidget
            # self.settingsWidget.settingsUpdated.connect(self.updateDataStreams)
            # self.addDock(self.settingsDock, 'right')
            # self.settingsDock.setVisible(False)

            self.dataStreamsDock = DataStreamsDock(name='Data streams',
                size = (1,1),globalSession=self.globalSession)
            
            self.toDoDock = ToDoDock(name ='To Do', size = (1,1))

            self.addDock(self.dataStreamsDock, 'right')
            self.dataStreamsDock.setVisible(False)

        self.consoleDock = ConsoleDock(name = 'Python Console', size = (1,1))
        self.addDock(self.consoleDock, 'right')
        self.consoleDock.setVisible(False)
        
        self.logViewDock = LogViewDock(globalSession = self.globalSession, 
            name='Log Book',size = (1,1))
        self.logViewer = self.logViewDock.viewer
        self.addDock(self.logViewDock, 'right')
        self.logViewDock.setVisible(False)
        
        if self.globalSession.settings.clearMode:

            self.analysisDock = AnalysisDock(name = 'Analysis', size = (1,1), 
                            globalSession = self.globalSession)

            self.logViewDock.analyseThis.connect(self.analysisDock.addCaptures)

            self.addDock(self.analysisDock, 'right')
            self.analysisDock.setVisible(False)


    def isGraphDock(self,dock):
        return self.docks[dock].__class__.__name__ == 'GraphDock'

    def newGraph(self,title = None):
        if title == None or type(title)==bool:
            title = 'Graph ' + str(1+len([key for key in self.docks.iterkeys() if 'Graph' in key]))

        dock = GraphDock(title = title,size = (1,1), 
            globalSession = self.globalSession)
        dock.updateToCurrentCapture()
        dock.graph.logSignal.connect(self.logViewer.newGraphNoteEntry)
        
        try:
            self.addDock(dock,'bottom', 
                self.docks[[key for key in self.docks.keys() if 'Graph' in key][-1]])
        except:
            self.addDock(dock,'right')
            
    def updateDataStreams(self):
        self.dataStreamsDock.updateUI()

    def addTempArea(self):
        """
        Re-implemenation using a subclass of QMainWindow to prevent
        closing of the docks
        """
        if self.home is None:
            area = da.DockArea(temporary=True, home=self)
            self.tempAreas.append(area)
            win = QMainWindow_unclosable()
            win.setCentralWidget(area)
            area.win = win
            win.show()
        else:
            area = self.home.addTempArea()
        #print "added temp area", area, area.window()
        return area

    def removeTempArea(self, area):
        """
        Re-implemenation: change canExit to true if the dock 
        is dragged back to the main GUI application dockarea.
        """
        self.tempAreas.remove(area)
        #print "close window", area.window()
        area.window().canExit = True
        area.window().close()

class QMainWindow_unclosable(QtGui.QMainWindow):
    def __init__(self):
        super(QMainWindow_unclosable, self).__init__()
        self.canExit = False        

    def closeEvent(self,event):
        if self.canExit:
            event.accept
        else:
            event.ignore()






