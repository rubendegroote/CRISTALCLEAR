import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from dock import Dock

from splitter import MySplitter
from settingswidget import SessionSettingsWidget
from core.settings import SessionSettings
from FrameLayout import FrameLayout


class GraphControlDock(Dock):
    def __init__(self,name,size):
        Dock.__init__(self,name,size)

        self.setMinimumWidth(500)
        # self.setMaximumWidth(500)
        self.setMinimumHeight(300)
        # self.setMaximumHeight(325)


        self.orientation = 'horizontal'
        self.autoOrient = False

        widget = QtGui.QWidget()
        grid = QtGui.QGridLayout()

        self.graphDockControlWidget = GraphDockControlWidget()
        grid.addWidget(self.graphDockControlWidget)

        self.createButton = QtGui.QPushButton('Create New Graph')
        self.createButton.setMinimumHeight(140)
        self.createButton.setMaximumHeight(140)


        grid.setRowStretch(0,1)
        grid.addWidget(self.createButton,1,0,1,2)

        label1 = QtGui.QLabel(self, text="Title")
        label1.setStyleSheet("border: 0px;")
        label1.setMaximumWidth(70)
        label1.setMinimumWidth(70)
        label2 = QtGui.QLabel(self, text="Variables")
        label2.setStyleSheet("border: 0px;")
        label2.setMaximumWidth(70)
        label2.setMinimumWidth(70)
        label3 = QtGui.QLabel(self, text="x:")
        label3.setStyleSheet("border: 0px;")
        label3.setAlignment(QtCore.Qt.AlignLeft)
        label4 = QtGui.QLabel(self, text="y:")
        label4.setStyleSheet("border: 0px;")
        label4.setAlignment(QtCore.Qt.AlignLeft)
        label5 = QtGui.QLabel(self, text="Live updating")
        label5.setStyleSheet("border: 0px;")
        label5.setMaximumWidth(70)
        label5.setMinimumWidth(70)

        self.vars = ['time','volt', 'ion', 'ai1','ai2']

        grid.addWidget(label1, 2,0)
        grid.addWidget(label2, 3,0)
        grid.addWidget(label3, 4,0)
        grid.addWidget(label4, 5,0)
        grid.addWidget(label5, 6,0)

        # text boxes
        self.title = QtGui.QLineEdit(self)
        self.title.setMaximumWidth(95)
        self.title.setMinimumWidth(95)
        self.title.setText('New Graph')
        self.varx = QtGui.QComboBox(self)
        self.varx.setMaximumWidth(70)
        self.varx.setMinimumWidth(70)
        self.varx.addItems(self.vars)
        self.vary = QtGui.QComboBox(self)
        self.vary.setMaximumWidth(70)
        self.vary.setMinimumWidth(70)
        self.vary.addItems(self.vars)
        self.checkBox = QtGui.QCheckBox(self)

        grid.addWidget(self.title, 2,1)
        grid.addWidget(self.varx, 4,1)
        grid.addWidget(self.vary, 5,1)
        grid.addWidget(self.checkBox, 6,1)
        grid.setRowStretch(7,1)

        widget.setLayout(grid)

        splitter = MySplitter('Settings', widget, 
            self.graphDockControlWidget)
        splitter.toggleSizes()
        self.addWidget(splitter)

    def getValues(self):
        return {'title':str(self.title.text()),
                'x':str(self.varx.currentText()),
                'y':str(self.vary.currentText()),
                'live':self.checkBox.checkState()}



class GraphDockControlWidget(QtGui.QWidget):
    emitRemoveGraph = QtCore.Signal(object)
    def __init__(self):

        super(GraphDockControlWidget, self).__init__()

        self.setMaximumWidth(300)
        # self.setMinimumWidth(255)

        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.graphDockSettings = {}

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget(
                                        self.scrollArea)
        self.scrollArea.setWidget(
                        self.scrollAreaWidgetContents)

        self.layout.addWidget(self.scrollArea)
        self.verticalLayoutScroll = QtGui.QGridLayout(self.scrollAreaWidgetContents)

        self.noOfGraphs = 0

    def addGraph(self,graphDock):
        self.graphDockSettings[graphDock] = GraphDockSettingsWidget(graphDock)
        self.graphDockSettings[graphDock].removeButton.clicked.connect(
                                lambda:self.removeGraph(graphDock))
        self.update()

    def removeGraph(self,graphDock):
        self.graphDockSettings[graphDock].close()
        self.verticalLayoutScroll.removeWidget(self.graphDockSettings[graphDock])
        del self.graphDockSettings[graphDock]

        self.emitRemoveGraph.emit(graphDock)

        self.update()

    def update(self):
        self.noOfGraphs = 0
        for (key,val) in self.graphDockSettings.iteritems():
            self.noOfGraphs = self.noOfGraphs + 1
            self.verticalLayoutScroll.addWidget(val,self.noOfGraphs,0)
            self.verticalLayoutScroll.setRowStretch(self.noOfGraphs,0)
        self.verticalLayoutScroll.setRowStretch(self.noOfGraphs+1,1)


class GraphDockSettingsWidget(FrameLayout):
    def __init__(self, graphDock,*args,**kwargs):  
        title, xvar, yvar, live = (graphDock.name(),
                          graphDock.xy.split('_')[0],
                          graphDock.xy.split('_')[1],
                          graphDock.live)
        FrameLayout.__init__(self,text = ' ' + title,*args,**kwargs)

        self.graphDock = graphDock

        widget = QtGui.QWidget()
        self.grid = QtGui.QGridLayout()
        widget.setLayout(self.grid)
        self.addWidget(widget)


        label1 = QtGui.QLabel(self, text="Title")
        label1.setStyleSheet("border: 0px;")
        label1.setMaximumWidth(100)
        label1.setMinimumWidth(100)
        label2 = QtGui.QLabel(self, text="Variables")
        label2.setStyleSheet("border: 0px;")
        label2.setMaximumWidth(100)
        label2.setMinimumWidth(100)
        label3 = QtGui.QLabel(self, text="x:")
        label3.setStyleSheet("border: 0px;")
        label3.setAlignment(QtCore.Qt.AlignRight)
        label3.setMaximumWidth(100)
        label3.setMinimumWidth(100)
        label4 = QtGui.QLabel(self, text="y:")
        label4.setStyleSheet("border: 0px;")
        label4.setAlignment(QtCore.Qt.AlignRight)
        label4.setMaximumWidth(100)
        label4.setMinimumWidth(100)
        label5 = QtGui.QLabel(self, text="Live updating")
        label5.setStyleSheet("border: 0px;")
        label5.setMaximumWidth(100)
        label5.setMinimumWidth(100)

        self.vars = ['time','volt', 'ion', 'ai1','ai2']

        self.removeButton = QtGui.QPushButton(self, text="Remove")

        self.grid.addWidget(self.removeButton, 0,0)
        
        self.grid.addWidget(label1, 1,0)
        self.grid.addWidget(label2, 2,0)
        self.grid.addWidget(label3, 3,0)
        self.grid.addWidget(label4, 4,0)
        self.grid.addWidget(label5, 5,0)

        # text boxes
        self.title = QtGui.QLineEdit(self)
        self.title.setText(title)
        self.title.setDisabled(True)
        self.varx = QtGui.QComboBox(self)
        self.varx.addItems(self.vars)
        self.varx.setCurrentIndex(self.vars.index(xvar))
        self.varx.setDisabled(True)
        self.vary = QtGui.QComboBox(self)
        self.vary.addItems(self.vars)
        self.vary.setCurrentIndex(self.vars.index(yvar))
        self.vary.setDisabled(True)
        self.checkBox = QtGui.QCheckBox(self)
        self.checkBox.setDisabled(True)
        self.checkBox.setChecked(live)

        self.grid.addWidget(self.title, 1,1)
        self.grid.addWidget(self.varx, 3,1)
        self.grid.addWidget(self.vary, 4,1)
        self.grid.addWidget(self.checkBox, 5,1)
        self.grid.setRowStretch(6,1)


    def getValues(self):
        return {'title':str(self.title.text()),
                'x':str(self.varx.currentText()),
                'y':str(self.vary.currentText()),
                'live':self.checkBox.checkState()}