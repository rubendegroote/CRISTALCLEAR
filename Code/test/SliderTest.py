# -*- coding: utf-8 -*-
## Add path to library (just for examples; you do not need this)                                                                         
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import math

class Example(QtGui.QMainWindow):
    def __init__(self):
        super(Example, self).__init__()
        
        self.initui()


    def initui(self):

        self.wid = QtGui.QWidget()
        self.wid.resize(800,800)
        self.layout = QtGui.QGridLayout(self.wid)

        self.setCentralWidget(self.wid)

        for i in xrange (10):
            self.layout.addWidget(mySlider(), i,0)

        self.show()




def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()