import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from FrameLayout import FrameLayout
from collections import OrderedDict

class GraphSettingsWidget(QtGui.QScrollArea):

    updatePlot = QtCore.Signal(object)
    def __init__(self):    
        super(GraphSettingsWidget,self).__init__()

        self.setMinimumWidth(200)
        self.setMaximumWidth(200)

        self.grid = QtGui.QGridLayout(self)
        self.grid.setAlignment(QtCore.Qt.AlignTop)

        self.color = (255,0,0,255)
        self.fill = (0,255,0,100)

        self.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.setWidget(self.scrollAreaWidgetContents)

        self.scansLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.scansLayout.setAlignment(QtCore.Qt.AlignTop)

        self.resetScans()

    def setUI(self,headerInfo):

        if headerInfo == self.headerInfo:
            return

        self.headerInfo = headerInfo

        pos = 0

        for i, name in enumerate(headerInfo[0]):

            if not name in self.checks:

                self.checks[name] = [QtGui.QCheckBox(name), []]
                self.checks[name][0].setCheckState(2)
                self.checks[name][0].stateChanged.connect(self.onCheckChanged)
                self.scansLayout.addWidget(self.checks[name][0],pos,0)

                self.colButtons[name] = [pg.ColorButton(),[]]
                self.colButtons[name][0].sigColorChanging.connect(self.onStyleChanged)
                self.scansLayout.addWidget(self.colButtons[name][0],pos,1)

                self.fillButtons[name] = [pg.ColorButton(),[]]
                self.fillButtons[name][0].sigColorChanging.connect(self.onStyleChanged)
                self.scansLayout.addWidget(self.fillButtons[name][0],pos,2)

                self.colButtons[name][0].setColor(self.color)
                self.fillButtons[name][0].setColor(self.fill)

            pos = pos + 1 

            for j in xrange(headerInfo[1][i]):

                if j >= len(self.checks[name][1]):

                    self.checks[name][1].append(QtGui.QCheckBox('scan ' + str(j)))
                    self.checks[name][1][-1].setCheckState(2)
                    self.checks[name][1][-1].stateChanged.connect(self.onCheckChanged)
                    self.scansLayout.addWidget(self.checks[name][1][-1],pos,0)

                    self.colButtons[name][1].append(pg.ColorButton())
                    self.colButtons[name][1][-1].sigColorChanging.connect(self.onStyleChanged)
                    self.scansLayout.addWidget(self.colButtons[name][1][-1],pos,1)

                    self.fillButtons[name][1].append(pg.ColorButton())
                    self.fillButtons[name][1][-1].sigColorChanging.connect(self.onStyleChanged)
                    self.scansLayout.addWidget(self.fillButtons[name][1][-1],pos,2)

                    self.colButtons[name][1][-1].setColor(self.color)
                    self.fillButtons[name][1][-1].setColor(self.fill)
                    
                pos = pos + 1

    def resetScans(self):
        for i in reversed(range(self.scansLayout.count())):
            self.scansLayout.itemAt(i).widget().setParent(None)

        self.checks = OrderedDict()        
        self.colButtons = OrderedDict()
        self.fillButtons = OrderedDict()
        self.headerInfo = []

    def onCheckChanged(self):
        for scanChecks in self.checks.itervalues():
            if not scanChecks[0].checkState():
                for c in scanChecks[1]:
                    c.stateChanged.disconnect(self.onCheckChanged)
                    c.setCheckState(False)
                    c.stateChanged.connect(self.onCheckChanged)

        self.updatePlot.emit(True)

    def getCheckStates(self):
        return {name : [checks[0].checkState(),[c.checkState() for c in checks[1]]] \
                        for name, checks in self.checks.iteritems()}

    def onStyleChanged(self):
        self.updatePlot.emit(True)

    def getStyles(self):
        scansIncluded = self.getCheckStates()
        return {'color':{name : \
                    [col[0].color(),[c.color() for scan,c in enumerate(col[1]) \
                        if scansIncluded[name][1][scan]]] \
                    for name, col in self.colButtons.iteritems()},
                'fill':{name : \
                    [fill[0].color(),[f.color() for scan,f in enumerate(fill[1])\
                        if scansIncluded[name][1][scan]]] \
                    for name, fill in self.fillButtons.iteritems()}}

