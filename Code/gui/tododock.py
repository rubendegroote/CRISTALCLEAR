import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from dock import Dock

class ToDoDock(Dock):
    def __init__(self,name,size):
        Dock.__init__(self,name,size)

        self.orientation = 'horizontal'
        self.autoOrient = False

        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        layout.addWidget(self.scrollArea)
        self.verticalLayoutScroll = QtGui.QGridLayout(self.scrollAreaWidgetContents)

        widget.setLayout(layout)
        self.addWidget(widget)


        text=QtGui.QLabel()
        text.setWordWrap(True)
        self.verticalLayoutScroll.addWidget(text)

        text.setText('\
<ul><li>Filtering options for logbook</li>\
<li>Unsaved entries counter for logbook</li>\
<li>Make planning widget</li>\
<li>Make checklist widget</li>\
<li>Overlaying of graphs and peak fitting</li>\
<li>Version history of logbook</li>\
<li>Compile changes into new .exe</li></lu>')
        



