import os
from PyQt4 import QtGui, QtCore
from dragdrop import *

class CollapsibleArrow(QtGui.QPushButton):
    def __init__(self, parent = None,path = None):
        QtGui.QPushButton.__init__(self, parent = parent)
        
        self.isCollapsed = False
        self.setMaximumSize(24, 24)
        self.setStyleSheet("QFrame {\
        background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #44a, stop: 1 #66c);\
        border-top: 1px solid rgba(192, 192, 192, 255);\
        border-left: 1px solid rgba(192, 192, 192, 255);\
        border-right: 1px solid rgba(32, 32, 32, 255);\
        border-bottom: 1px solid rgba(64, 64, 64, 255);\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;}\
        QFrame:hover {background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #44a, stop: 1 #66c);\
        }")
        imagePath = path + 'Code\\gui\\resources\\'
        self.arrowNameTrue = imagePath + 'minimizeBlue.png'
        self.arrowNameFalse = imagePath + 'maximizeBlue.png'

        self.setToolTip('Click to maximize/minimize.')
        
    def setArrow(self, arrowDir = True):
        pass
        if arrowDir:
            self.setIcon(QtGui.QIcon(self.arrowNameTrue)) 
            self.isCollapsed = True    
        else:
            self.setIcon(QtGui.QIcon(self.arrowNameFalse))
            self.isCollapsed = False

    def mousePressEvent(self, event):
        self.emit(QtCore.SIGNAL('clicked()'))
        return super(CollapsibleArrow, self).mousePressEvent(event)
        

        
class TitleLabelCapture(DragCaptureLabel):
    def __init__(self, parent = None,text = ''):
        DragCaptureLabel.__init__(self, parent = parent,text = text)
        self.setStyleSheet("TitleLabelCapture {background-color: rgba(0, 0, 0, 0);\
        color: white;\
        border-left: 1px solid rgba(128, 128, 128, 255);\
        border-top: 0px transparent;\
        border-right: 0px transparent;\
        border-bottom: 0px transparent;\
        }")

        
class TitleLabelGroup(DragGroupLabel):
    def __init__(self, parent = None,text = ''):
        DragGroupLabel.__init__(self, parent = parent,text = text)
        self.setStyleSheet("TitleLabelGroup {background-color: rgba(0, 0, 0, 0);\
        color: white;\
        border-left: 1px solid rgba(128, 128, 128, 255);\
        border-top: 0px transparent;\
        border-right: 0px transparent;\
        border-bottom: 0px transparent;\
        }")

class TitleLabel(QtGui.QLabel):
    def __init__(self, parent = None,text = ''):
        QtGui.QLabel.__init__(self, parent = parent,text = text)
        self.setStyleSheet("TitleLabel {background-color: rgba(0, 0, 0, 0);\
        color: white;\
        border-left: 0px transparent;\
        border-top: 0px transparent;\
        border-right: 0px transparent;\
        border-bottom: 0px transparent;\
        }")
        

class TitleFrame(QtGui.QFrame):
    def __init__(self, parent = None, text = '',path = None):
        QtGui.QFrame.__init__(self, parent = parent)
        
        self.titleLabel = None
        self.arrow = None
        self.path = path
        self.initTitleFrame(text)
        
    def initArrow(self):
        self.arrow = CollapsibleArrow(self,self.path)
        
    def initTitleLabel(self,text):
        if 'Capture' in text:
            self.titleLabel = TitleLabelCapture(self,text)
        elif 'Group' in text:
            self.titleLabel = TitleLabelGroup(self,text)
        else:
            self.titleLabel = TitleLabel(self,text)

        self.titleLabel.setMinimumHeight(24)
        self.titleLabel.setMinimumWidth(350)
        self.titleLabel.move(QtCore.QPoint(24, 0))
        
    def initTitleFrame(self,text):
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumHeight(24)
        self.setStyleSheet("QFrame {\
        background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #44a, stop: 1 #66c);\
        border-top: 1px solid rgba(192, 192, 192, 255);\
        border-left: 1px solid rgba(192, 192, 192, 255);\
        border-right: 1px solid rgba(64, 64, 64, 255);\
        border-bottom: 1px solid rgba(64, 64, 64, 255);\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;\
        }")
        
        self.initArrow()
        self.initTitleLabel(text)    
   
    def mouseDoubleClickEvent(self, event):
        self.emit(QtCore.SIGNAL('doubleClicked()'))
        return super(TitleFrame, self).mouseDoubleClickEvent(event)         
        
        
class FrameLayout(QtGui.QFrame):
    def __init__(self, parent = None, text = None, path=None):
        QtGui.QFrame.__init__(self, parent = parent)
        
        self.text = text
        self.path = path
        self.isCollapsed = False
        self.mainLayout = None
        self.titleFrame = None
        self.contentFrame = None
        self.contentLayout = None
        self.label = None
        self.arrow = None
        
        self.initFrameLayout()
        
    def text(self):
        return self.text
        
    def addWidget(self, widget):
        self.contentLayout.addWidget(widget)

    def initMainLayout(self):
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)
        
    def initTitleFrame(self):
        self.titleFrame = TitleFrame(text=self.text,path=self.path)
        self.mainLayout.addWidget(self.titleFrame)
        
    def initContentFrame(self):
        self.contentFrame = QtGui.QFrame()
        self.contentFrame.setContentsMargins(0, 0, 0, 0)
        self.contentFrame.setStyleSheet("QFrame {\
        border-top: 1px solid rgba(64, 64, 64, 255);\
        border-left: 1px solid rgba(64, 64, 64, 255);\
        border-right: 1px solid rgba(192, 192, 192, 255);\
        border-bottom: 1px solid rgba(192, 192, 192, 255);\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;\
        }")
        
        self.contentLayout = QtGui.QVBoxLayout()
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)
        self.contentFrame.setLayout(self.contentLayout)
        self.mainLayout.addWidget(self.contentFrame)
        
 
    def toggleCollapsed(self):
        if self.isCollapsed:
            self.show()
        else:
            self.collapse()
    
    def collapse(self):
        self.contentFrame.setVisible(False)
        self.setVisible(True)
        self.isCollapsed = True
        self.arrow.setArrow(False)

    def show(self):
        self.contentFrame.setVisible(True)
        self.isCollapsed = False
        self.arrow.setArrow(True)

    def setText(self, text):
        self.label.setText(text)  
        
    def initFrameLayout(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QFrame {\
        border: 0px solid;\
        margin: 0px, 0px, 0px, 0px;\
        padding: 0px, 0px, 0px, 0px;\
        }")
        
        self.initMainLayout()
        self.initTitleFrame()
        self.initContentFrame()
        self.arrow = self.titleFrame.arrow
        self.label = self.titleFrame.titleLabel
        QtCore.QObject.connect(self.arrow, QtCore.SIGNAL('clicked()'), self.toggleCollapsed)
