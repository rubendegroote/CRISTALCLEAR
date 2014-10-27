
import sys
from PyQt4 import QtCore, QtGui, uic
import pyqtgraph as pg


class UI(QtGui.QMainWindow):

    def __init__( self, parent=None ):
        super(UI, self).__init__( parent )

        self.centralwidget = QtGui.QWidget(self)
        self.layout = QtGui.QGridLayout(self.centralwidget)

        self.gLayout = pg.GraphicsLayoutWidget()
        self.layout.addWidget(self.gLayout,0,0,2,1)
        self.graphs = {}

        self.treeWidget = TreeWidget(self.centralwidget)
        self.treeWidget.itemChecked.connect(self.handleItemChecked)
        self.layout.addWidget(self.treeWidget,0,1)
        self.setCentralWidget(self.centralwidget)

        # ----------------
        # Set TreeWidget Headers
        # ----------------
        HEADER =  ["DataSets","Scans in set","" ]
        self.treeWidget.setColumnCount( 1 )
        self.treeWidget.setHeaderLabels( HEADER )

        # ----------------
        # Add Custom QTreeWidgetItem
        # ----------------
        ## Add Items:
        for row,name in enumerate([ 'rock', 'paper', 'scissors' ]):
            
            item = TreeWidgetItem( self.treeWidget,row )
            item.setText(0,name)
            item.setCheckState(0, 2)


            for i in range(3):
                subItem = TreeWidgetItem( item,row )
                subItem.setText(1,name+' '+str(i))
                subItem.setCheckState(1, 2)


        ## Set Columns Width to match content:
        for column in range( self.treeWidget.columnCount() ):
            self.treeWidget.resizeColumnToContents( column )


        checkAllButton = QtGui.QPushButton('(Un-)Check all')
        self.layout.addWidget(checkAllButton,1,1)
        checkAllButton.clicked.connect(self.checkAll)


    def checkAll(self):
        for i in range(self.treeWidget.topLevelItemCount()):
            item = self.treeWidget.topLevelItem(i)

            if item.checkState(0)==2:
                state = 0
            else:
                state = 2

            item.setCheckState(0, state)

            for j in range(item.childCount()):
                child = item.child(j)

                if child.checkState(1)==2:
                    state = 0
                else:
                    state = 2

                child.setCheckState(1, state)

    def handleItemChecked(self, row,text, state):
        if state:
            if not text in self.graphs.iterkeys():
                self.graphs[text] = pg.PlotItem(name = text, title = text)
                self.graphs[text].setXLink(str(text).partition(' ')[0])

            col = str(text).partition(' ')[-1]
            if col == '':
                col = 0
                row = 2*row
                colspan = 4
            else:
                col = int(col)
                row = 2*row+1
                colspan = 1
            self.gLayout.addItem(self.graphs[text],row=row, col = col,colspan = colspan)
        else:
            if text in self.graphs.iterkeys():
                self.gLayout.removeItem(self.graphs[text])
            

class TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self,parent,name):
        QtGui.QTreeWidgetItem.__init__(self,parent)
        self.name = name

    def setData(self, column, role, value):
        state = self.checkState(column)
        QtGui.QTreeWidgetItem.setData(self, column, role, value)
        if (role == QtCore.Qt.CheckStateRole and state != self.checkState(column)):
            treewidget = self.treeWidget()
            if treewidget is not None:
                treewidget.itemChecked.emit(self.name,self.text(column), int(self.checkState(column)))


class TreeWidget(QtGui.QTreeWidget):
    itemChecked = QtCore.pyqtSignal(int,str, int)
    def __init__(self, parent):
        QtGui.QTreeWidget.__init__(self,parent)
        self.setMaximumWidth(300)

