import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import os

class PicButton(QtGui.QPushButton):
    def __init__(self,iconName,size,checkable = False):
        super(PicButton, self).__init__()

        self.imagePath = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Code\\gui\\resources\\'

        self.setStyleSheet(
            "QPushButton:checked {background-color: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #eef, stop: 1 #ccf)}")
        self.setCheckable(checkable)
        self.setMaximumWidth(size)
        self.setMinimumWidth(size)
        self.setMaximumHeight(size)
        self.setMinimumHeight(size)
        self.setIconSize( QtCore.QSize(0.95*size, 0.95*size))
        self.setIcon(iconName)


    def setIcon(self,iconName):
        super(PicButton, self).setIcon(QtGui.QIcon(self.imagePath+iconName))        
        