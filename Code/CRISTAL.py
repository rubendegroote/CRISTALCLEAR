#!/usr/bin/python

"""
kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

"""
from gui.launcher import Launcher
from core.settings import SessionSettings
from collections import OrderedDict
from multiprocessing import freeze_support
import time

import sys
import threading

from PyQt4 import QtCore,QtGui

import pyqtgraph as pg
from pyqtgraph import setConfigOption

# OpenGL seems to buggy (refresh issues, crashes, etc.)
# setConfigOption('useOpenGL', False)
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

if __name__ == "__main__":
    
    # add freeze support
    freeze_support()

    app = QtGui.QApplication(sys.argv)

    settings = SessionSettings()
    
    launcher = Launcher(settings)
    launcher.show()

    sys.exit(app.exec_())