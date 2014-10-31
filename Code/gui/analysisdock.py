import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from dock import Dock
# from analysiswidget import AnalysisWidget
from newanalysiswidget import NewAnalysisWidget

class AnalysisDock(Dock):
    def __init__(self,name,size, globalSession):
        Dock.__init__(self,name,size)

        self.orientation = 'horizontal'
        self.autoOrient = False

        self.globalSession = globalSession

        self.analysisWidget = NewAnalysisWidget(globalSession)

        self.addWidget(self.analysisWidget)

    def addCaptures(self,captures):
        for cap in captures:
            self.analysisWidget.addCapture(cap)

    def captureDropped(self,text):
        captureName = text.split('\t')[1]

        cap = self.globalSession.captures[captureName]
        cap.readData()

        self.analysisWidget.addCapture(cap)

    def dragEnterEvent(self, ev):
        src = ev.source()
        if hasattr(src, 'implements') and src.implements('dock'):
            ev.accept()
        elif ev.mimeData().hasFormat('captureName'):
            ev.accept()
        else:
            ev.ignore()

    def dropEvent(self, ev):
        src = ev.source()

        if hasattr(src, 'implements') and src.implements('dock'):
            area = self.dropArea
            if area is None:
                return
            if area == 'center':
                area = 'above'
            self.area.moveDock(ev.source(), area, self)
            self.dropArea = None
            self.overlay.setDropArea(self.dropArea)

        elif ev.mimeData().hasFormat('captureName'):
            mime       = ev.mimeData()
            itemData   = mime.data('captureName')
            dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.ReadOnly)

            text = QtCore.QByteArray()
            offset = QtCore.QPoint()
            dataStream >> text >> offset

            self.captureDropped(str(ev.mimeData().text()))
            self.dropArea = None
            self.overlay.setDropArea(self.dropArea)