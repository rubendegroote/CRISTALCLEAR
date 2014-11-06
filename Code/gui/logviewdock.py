import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import threading

from splitter import MySplitter
from filterwidget import FilterWidget
from dock import Dock
from dragdrop import *
from FrameLayout import FrameLayout
from picbutton import PicButton
from core.logbook import *
from graphdock import MyGraph
from core.metacapture import MetaCapture

import datetime
import os

class LogViewDock(Dock):
    """
    Shows the logbook
    """

    analyseThis = QtCore.Signal(object)

    def __init__(self, globalSession,name,size):
        Dock.__init__(self,name,size)

        self.orientation = 'horizontal'
        self.autoOrient = False

        self.viewer = LogViewer(globalSession)
        self.viewer.filterWidget.analyseThis.connect(self.emitAnalyseThis)
        self.viewer.filterWidget.newLogFiltered.connect(self.viewer.newLog)

        self.layout.addWidget(self.viewer,1,0)

    def emitAnalyseThis(self,captures):
        self.analyseThis.emit(captures)


class LogViewer(QtGui.QWidget):
    """
    Shows the logbook
    """
    updated = QtCore.Signal(object) #emitted the new entry when added, passes 
                                    #signal from LogEntryWidget instance

    def __init__(self,globalSession):
        super(LogViewer, self).__init__()

        self.globalSession = globalSession
        self.logBook = self.globalSession.logBook
        self.collapsed = True

        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(self.layout)

     
        self.collapseAllButton = PicButton('collapse.png', checkable = False, size = 40)
        self.collapseAllButton.clicked.connect(self.collapse)
        self.layout.addWidget(self.collapseAllButton,0,0)

        self.newEntryButton = PicButton('newentry.png', checkable = False, size = 40)
        self.newEntryButton.clicked.connect(lambda: self.newEntry())
        self.layout.addWidget(self.newEntryButton,0,1)

        self.editEntryInfoButton = PicButton('newProp.png', checkable = False, size = 40)
        self.editEntryInfoButton.clicked.connect(self.addEntryProperty)
        self.layout.addWidget(self.editEntryInfoButton,0,2)


        self.filterButton = PicButton('filter.png', checkable = True, size = 40)
        self.filterButton.clicked.connect(self.toggleFilter)
        self.layout.addWidget(self.filterButton,0,4)

        self.openArchivedButton = PicButton('open.png', checkable = False, size = 40)
        self.openArchivedButton.clicked.connect(self.openLogbook)
        self.layout.addWidget(self.openArchivedButton,0,5)

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.layout.addWidget(self.scrollArea,1,0,1,6)

        # Need multiple containers, for some reason the scroll area widget 
        # cannot contain more than ~110 widgets...
        self.entryContainersLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.entryContainers = []
        self.newEntryContainer()

        self.filterWidget = FilterWidget(self.logBook)
        self.filterWidget.setVisible(False)
        self.layout.setRowStretch(1,1)
        self.layout.addWidget(self.filterWidget,2,1,1,5)

        self.resetLayout()

    def openLogbook(self):
        folder = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Logbook\\'
        fileName = QtGui.QFileDialog.getOpenFileName(self, 'Choose logbook file', folder)

        self.globalSession.setttings.logFile = fileName
        self.globalSession.loadLogBook()

        self.resetLayout()


    def newEntryContainer(self):
        entryContainer = QtGui.QGridLayout()
        self.entryContainersLayout.addLayout(entryContainer)
        entryContainer.setAlignment(QtCore.Qt.AlignTop)
        self.entryContainers.append(entryContainer)

    def newLog(self,newLog):
        self.filteredLog = newLog
        self.update()

    def newEntry(self, entry=None, capture = False):

        if entry==None:
            cap = self.globalSession.getCurrentCapture()
            if cap == None:
                if capture:
                    entry = CaptureLogEntry(capture = self.globalSession.getPreviousCapture())
                else:
                    entry = Entry(capture = self.globalSession.getPreviousCapture())
            else:
                if capture:
                    entry = CaptureLogEntry(capture = cap)
                else:
                    entry = Entry(capture = cap)

        self.logBook.addEntry(entry)
        self.saveLog(entry)
        self.filteredLog.append(entry)
        self.update()

    def saveLog(self,entry):
        self.globalSession.saveEntry(entry)

    def newGraphNoteEntry(self,volt,graph):
        
        msg = 'You ctrl+clicked on the plot. \n Make logbook entry on voltage '\
                                             + str(volt) + '?'

        box = QtGui.QDialog(self)
        box.setModal(False)
        layout = QtGui.QVBoxLayout(box)
        text = QtGui.QLabel(msg)
        layout.addWidget(text)

        buttonbox = QtGui.QDialogButtonBox()

        ok = QtGui.QPushButton('Ok')
        cancel = QtGui.QPushButton('Cancel')
        buttonbox.addButton(ok, QtGui.QDialogButtonBox.AcceptRole)
        buttonbox.addButton(cancel, QtGui.QDialogButtonBox.RejectRole)
        
        buttonbox.accepted.connect(lambda volt=volt,graph=graph: self.acceptGraphNote(volt,graph))
        buttonbox.accepted.connect(box.close)
        buttonbox.rejected.connect(box.close)

        layout.addWidget(buttonbox)

        box.show()

    def acceptGraphNote(self,volt,graph):
        cap = self.globalSession.getCurrentCapture()

        graph = graph.split('_')[1]+'(' +graph.split('_')[0] + ')'
        self.newEntry(entry=ScanEntry(volt=volt,
            capture = cap,graph=graph))
        self.update()

    def addEntryProperty(self):
        text, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'New item name:')

        if ok:
            self.logBook.addProperty(key='#Custom ' + str(text))
            self.filterWidget.updateToCurrentLog(self.logBook)

    def collapse(self):
        for val in self.logEntryWigets.itervalues():
            if not val.isCollapsed:
                val.collapse()

    def resetLayout(self):

        self.logBook = self.globalSession.logBook
        self.filteredLog = self.logBook.values()

        self.filterWidget.initUI()
        self.filterWidget.updateToCurrentLog(self.logBook)
        self.filterWidget.search()

        for container in self.entryContainers:
            for i in reversed(range(container.count())): 
                widgetToRemove = container.itemAt(i).widget() 
                # get it out of the layout list 
                container.removeWidget(widgetToRemove) 
                # remove it form the gui 
                widgetToRemove.setParent(None)

        self.logEntryWigets = {}
        self.entryContainers = []
        self.newEntryContainer()

        self.update()

    def update(self):
        # print 'make filter update as well!'
        for (key, entry) in self.logBook.iteritems():
            
            if entry in self.filteredLog:
                
                if key not in self.logEntryWigets.keys():
                    name = ''
                    if not entry.properties['capture'] == None:
                        name = name + entry.getProperty('name')

                    if not entry.__class__.__name__ == 'CaptureLogEntry':
                        name = name + '\t' + entry.__class__.__name__ 
                        
                    text = entry.getProperty('time')+'\t'+ name + '\t'
                    self.logEntryWigets[key] = LogEntryWidget(self.globalSession,text=text, entry = entry)
                    self.logEntryWigets[key].visibleProp = self.logEntryWigets[key].visibleProp + \
                                                            self.logBook.usrProp.keys()
                    self.logEntryWigets[key].createFrame()
                    self.logEntryWigets[key].updated.connect(self.saveLog)
                    self.logEntryWigets[key].updated.connect(
                        lambda: self.filterWidget.updateToCurrentLog(self.logBook))

                    self.entryContainers[-1].addWidget(self.logEntryWigets[key],key,0)

                    QtGui.QApplication.processEvents()

                    if self.entryContainers[-1].count() > 100:
                        self.newEntryContainer()
                else:
                    self.logEntryWigets[key].setVisible(True)
                    self.logEntryWigets[key].collapse()


                # Update label for the capture entries
                if entry.__class__.__name__ == 'CaptureLogEntry':
                    text = self.logEntryWigets[key].text
                    if entry.properties['capture'].acquisitionDone == True:
                        text = text + entry.getProperty('stopTime')
                    elif self.globalSession.running == True:
                        text = text + 'Running'
                    elif self.globalSession.running == None:
                        text = text + 'Not Started'
                    else:
                        text = text + entry.getProperty('stopTime')

                    self.logEntryWigets[key].setText(text)

            else:
                if key in self.logEntryWigets.keys():
                    self.logEntryWigets[key].setVisible(False)

        self.collapse()

    def timeStampCapture(self):
        cap,log = self.globalSession.getCurrentCaptureAndLog()
        log.properties['stopTime'] = datetime.datetime.now()
        self.saveLog(log)
        self.update()

    def toggleFilter(self):
        if not self.filterWidget.isVisible():
            self.filterWidget.setVisible(True)
        else:
            self.filterWidget.setVisible(False)

            
        
class LogEntryWidget(FrameLayout):
    updated = QtCore.Signal(object) #emitted the new entry when added

    def __init__(self,globalSession,text = '', entry=None):
        super(LogEntryWidget, self).__init__(text=text)

        self.entry = entry
        self.globalSession = globalSession
        self.logBook = self.globalSession.logBook

        self.tags = set()

        self.labels = {}
        self.texts = {}

        self.visibleProp = ['people','comments','isotope','volt','scan','graph','tags']
        self.unEditableProp = ['volt','scan','graph']

        self.widget = QtGui.QWidget(self)
        self.grid = QtGui.QGridLayout()


    def createFrame(self):

        self.tagButton = PicButton('tag.png',checkable = False,size = 25)
        self.tagButton.clicked.connect(lambda: self.addTag(tag = None))
        self.grid.addWidget(self.tagButton,0,0)

        self.tagsLayout = QtGui.QHBoxLayout()
        self.tagsLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.tagsLayout.addStretch(1)
        self.grid.addLayout(self.tagsLayout,0,1)

        teller = 1
        for pkey in self.entry.properties.iterkeys():

            if pkey in self.visibleProp:
                if '#Custom' in pkey:
                    propname = pkey.split('#Custom')[1]
                else:
                    propname = str(pkey)
                if pkey=='comments':
                    self.texts[pkey] = QtGui.QTextEdit()
                    self.texts[pkey].setText(self.entry.getProperty(pkey))
                elif pkey == 'tags':
                    tags = self.entry.getProperty(pkey)
                    if not tags == '':
                        self.tags = set(tags.split(', '))
                        for tag in self.tags:
                            self.logBook.tags.add(tag)

                        self.addTags(self.tags)

                elif pkey in self.unEditableProp:
                    self.texts[pkey] = QtGui.QLabel(self.entry.getProperty(pkey))
                    self.texts[pkey].setStyleSheet("border: 0px;");
                else:
                    self.texts[pkey] = QtGui.QLineEdit(text = self.entry.getProperty(pkey))

                if not pkey == 'tags':
                    self.labels[pkey] = QtGui.QLabel(text = propname)
                    self.labels[pkey].setStyleSheet("border: 0px;");
                    self.grid.addWidget(self.labels[pkey],teller,0)
                    self.grid.addWidget(self.texts[pkey],teller,1)
                    teller = teller + 1           

        self.editButton = QtGui.QPushButton(text = 'Confirm')
        self.editButton.clicked.connect(self.confirmEntry)
        self.grid.addWidget(self.editButton,teller,1)

        if self.entry.__class__.__name__ == 'CaptureLogEntry':
     
            self.graphButton = PicButton('graph.png',checkable = True,size = 40)
            self.graphButton.clicked.connect(self.toggleGraph)
            self.grid.addWidget(self.graphButton, teller,0,1,1)

        self.widget.setLayout(self.grid)
        self.addWidget(self.widget)

        self.chooseColor()


    def addTag(self,tag = None):

        if tag == None:
            newTag = True
            tag, ok = QtGui.QInputDialog.getItem(self, 'Tag Input Dialog', 
                'Choose a tag or enter new tag:', list(self.logBook.tags))
            if not ok:
                return

        else:
            newTag = False
                
        self.logBook.tags.add(str(tag))
        self.tags.add(str(tag))
        self.entry.properties['tags'] = self.tags

        tag = Tag(str(tag))
        tag.remove.connect(self.removeTag)
        self.tagsLayout.addWidget(tag)

        if newTag:
            self.updated.emit(self.entry)

    def addTags(self,tags):
        for tag in tags:
            self.addTag(tag)

    def removeTag(self,text):
        self.tags.remove(str(text))
        self.updated.emit(self.entry)        

    def toggleGraph(self):
        try:
            if not self.graph.isVisible():
                self.graph.setVisible(True)
            else:
                self.graph.setVisible(False)
        except:
            cap = self.entry.properties['capture']
            cap.readData()
            self.graph = MyGraph(self.entry.properties['name'],self.globalSession)
            self.graph.setMetaCap(MetaCapture(cap))

            self.graph.setMinimumHeight(500)
            self.grid.addWidget(self.graph, 100, 0, 1,2)
            self.graph.plot()

    def confirmEntry(self):
        for (key,textItem) in self.texts.iteritems():
            textItem.setDisabled(True)
            try:
                newText = textItem.text()
            except AttributeError:
                newText = textItem.toPlainText()

            self.entry.properties[key] = newText

        self.confirmed = True

        self.editButton.setText('Edit')
        self.editButton.clicked.disconnect(self.confirmEntry)
        self.editButton.clicked.connect(self.editEntry)

        self.updated.emit(self.entry)

    def editEntry(self):
        for text in self.texts.itervalues():
            text.setEnabled(True)

        self.confirmed = False

        self.editButton.setText('Confirm')
        self.editButton.clicked.disconnect(self.editEntry)
        self.editButton.clicked.connect(self.confirmEntry)

    def chooseColor(self):
        imagePath = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Code\\gui\\resources\\'

        if self.entry.__class__.__name__ == 'CaptureLogEntry':
            self.titleFrame.setStyleSheet("QFrame {\
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #43aa44, stop: 1 #66cc66);\
            border-top: 1px solid rgba(192, 192, 192, 255);\
            border-left: 1px solid rgba(192, 192, 192, 255);\
            border-right: 1px solid rgba(64, 64, 64, 255);\
            border-bottom: 1px solid rgba(64, 64, 64, 255);\
            margin: 0px, 0px, 0px, 0px;\
            padding: 0px, 0px, 0px, 0px;\
            }")

            self.arrow.setStyleSheet("QFrame {\
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #43aa44, stop: 1 #66cc66);\
            border-top: 1px solid rgba(192, 192, 192, 255);\
            border-left: 1px solid rgba(192, 192, 192, 255);\
            border-right: 1px solid rgba(32, 32, 32, 255);\
            border-bottom: 1px solid rgba(64, 64, 64, 255);\
            margin: 0px, 0px, 0px, 0px;\
            padding: 0px, 0px, 0px, 0px;}\
            QFrame:hover {background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #43aa44, stop: 1 #66cc66);\
            }")

            self.arrow.arrowNameTrue =  imagePath + 'minimizeGreen.png'
            self.arrow.arrowNameFalse = imagePath + 'maximizeGreen.png'

        elif self.entry.__class__.__name__ == 'GraphNoteEntry':
            self.titleFrame.setStyleSheet("QFrame {\
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #a9aa43, stop: 1 #cbcc66);\
            border-top: 1px solid rgba(192, 192, 192, 255);\
            border-left: 1px solid rgba(192, 192, 192, 255);\
            border-right: 1px solid rgba(64, 64, 64, 255);\
            border-bottom: 1px solid rgba(64, 64, 64, 255);\
            margin: 0px, 0px, 0px, 0px;\
            padding: 0px, 0px, 0px, 0px;\
            }")

            self.arrow.setStyleSheet("QFrame {\
            background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #a9aa43, stop: 1 #cbcc66);\
            border-top: 1px solid rgba(192, 192, 192, 255);\
            border-left: 1px solid rgba(192, 192, 192, 255);\
            border-right: 1px solid rgba(32, 32, 32, 255);\
            border-bottom: 1px solid rgba(64, 64, 64, 255);\
            margin: 0px, 0px, 0px, 0px;\
            padding: 0px, 0px, 0px, 0px;}\
            QFrame:hover {background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #a9aa43, stop: 1 #cbcc66);\
            }")

            self.arrow.arrowNameTrue =  imagePath + 'minimizeYellow.png'
            self.arrow.arrowNameFalse = imagePath + 'maximizeYellow.png'

class Tag(QtGui.QFrame):
    remove = QtCore.Signal(object)
    def __init__(self, text = ''):
        super(Tag,self).__init__()

        layout = QtGui.QHBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignLeft)
        self.text = text
        self.label = QtGui.QLabel(text)
        self.label.setStyleSheet("border: 0px;")

        layout.addWidget(self.label)

        imagePath = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Code\\gui\\resources\\'
        self.closeButton = QtGui.QPushButton(self)
        self.closeButton.setMinimumWidth(15)
        self.closeButton.setMinimumHeight(15)
        self.closeButton.setMaximumWidth(15)
        self.closeButton.setMaximumHeight(15)
        self.closeButton.setIconSize(QtCore.QSize(15, 15))
        self.closeButton.setIcon(QtGui.QIcon(imagePath + 'close.png'))
        self.closeButton.clicked.connect(self.removeTag)

        layout.addWidget(self.closeButton)

        height = self.label.sizeHint().height() 
        self.setMaximumHeight(height + 30)
        width = self.label.sizeHint().width()
        self.setMaximumWidth(width + 50)

        self.setStyleSheet("""background-color: #C0C0C0;\
                            padding: 0px, 0px, 0px, 0px;\
                            border: 0px;
                            """)

    def setText(self,text):
        self.text = text
        self.label.setText(text)

    def removeTag(self):
        self.remove.emit(self.text)
        self.setParent(None)