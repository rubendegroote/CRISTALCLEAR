from __future__ import division
import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import numpy as np
from lmfit import *
import time
import sys
from copy import deepcopy
from string import replace
import re


class newGraph(pg.GraphicsView):
    def __init__(self):
        super(newGraph, self).__init__()

        self.layout = QtGui.QGridLayout(self)


        graph = pg.PlotWidget()
        self.layout.addWidget(graph,0,0,1,1)

        sublayout = QtGui.QGridLayout()
        self.layout.addLayout(sublayout,1,0)

        check = QtGui.QCheckBox("Live Updating")
        check.setStyleSheet("QCheckBox { color : white; }")
        sublayout.addWidget(check,0,0)

        combo = QtGui.QComboBox(parent = None)
        sublayout.addWidget(combo,0,1)

        label = QtGui.QLabel('vs')
        label.setStyleSheet("QLabel { color : white; }")
        sublayout.addWidget(label,0,2)

        combo2 = QtGui.QComboBox(parent = None)
        sublayout.addWidget(combo2,0,3)

        sublayout.setColumnStretch(4,1)

        self.show()




def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = newGraph()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()