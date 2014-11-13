#!/usr/bin/python

"""
kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

"""
from gui.launcher import Launcher
from collections import OrderedDict
from multiprocessing import freeze_support
import time
import os

import sys
import threading

from PyQt4 import QtCore,QtGui

from gui.mframe import MainWindow

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

    path = os.getcwd().split('Code')[0]

    print 'checking directory structure...'

    dirs = [path + '\Data',path + '\Data\Pictures', path + '\Logbook']

    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)

    print 'Seems fine...'

    m = MainWindow(path)


    sys.exit(app.exec_())