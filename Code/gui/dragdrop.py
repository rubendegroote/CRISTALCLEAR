import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import pyqtgraph.dockarea as da


class DragCaptureLabel(QtGui.QLabel):
 
    def __init__(self, parent=None,text =''):
        super(DragCaptureLabel, self).__init__(text,parent=parent)

 
    def mousePressEvent(self, event):

        text = self.text()
        
        itemData   = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        dataStream.writeString(text)
        dataStream << QtCore.QPoint(event.pos() - self.rect().topLeft())


        mimeData = QtCore.QMimeData()
        mimeData.setData('captureName', itemData)
        mimeData.setText(text)

 
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        dropAction = drag.exec_(QtCore.Qt.CopyAction|QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)

 
class DragGroupLabel(QtGui.QLabel):
 
    def __init__(self, parent=None,text =''):
        super(DragGroupLabel, self).__init__(text,parent=parent)

 
    def mousePressEvent(self, event):

        text = self.text()
        
        itemData   = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        dataStream.writeString(text)
        dataStream << QtCore.QPoint(event.pos() - self.rect().topLeft())


        mimeData = QtCore.QMimeData()
        mimeData.setData('group', itemData)
        mimeData.setText(text)

 
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)

        dropAction = drag.exec_(QtCore.Qt.CopyAction|QtCore.Qt.MoveAction, QtCore.Qt.CopyAction)

 

