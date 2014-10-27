import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from pyqtgraph.widgets.VerticalLabel import VerticalLabel

class MySplitter(QtGui.QSplitter):
    def __init__(self,text,wid1,wid2,*args,**kwargs):
        QtGui.QSplitter.__init__(self,*args,**kwargs)

        self.setHandleWidth(17)
        
        self.addWidget(wid1)
        self.addWidget(wid2)
        
        handle = self.handle(1)
        handle.setStyleSheet("QSplitterHandle {background: transparent}")

        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        handle.setLayout(layout)

        self.label = ClickLabel(text=text)
        layout.addWidget(self.label)
        self.label.sigClicked.connect(self.toggleSizes)

        self.setSizes([1, 0])

    def toggleSizes(self):
        if not all(self.sizes()):
            self.setSizes([1, 1])
        else:
            self.setSizes([1, 0])

class ClickLabel(VerticalLabel):

    sigClicked = QtCore.Signal(object) # Emitted when a new capure was dropped here

    def __init__(self,text):

        self.fixedWidth = False
        VerticalLabel.__init__(self, text, orientation='vertical', forceWidth=False)
        self.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        self.setAutoFillBackground(False)
        self.updateStyle()

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.sigClicked.emit(True)
            return super(ClickLabel, self).mouseDoubleClickEvent(event) 

    def mouseDragEvent(self, ev):
        pass

    def updateStyle(self):
        r = '3px'
       
        self.vStyle = """ClickLabel { 
            border-top-right-radius: 0px; 
            border-top-left-radius: %s; 
            border-bottom-right-radius: 0px; 
            border-bottom-left-radius: %s; 
            padding-top: 3px;
            padding-bottom: 3px;
            border-color;
        }""" % (r, r)
        self.setStyleSheet(self.vStyle)
