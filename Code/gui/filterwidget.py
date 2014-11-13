import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from core.logbook import *
from FrameLayout import FrameLayout
import string
import re



class FilterWidget(QtGui.QWidget):
    analyseThis = QtCore.Signal(object)
    newLogFiltered = QtCore.Signal(object)
    def __init__(self,logBook):

        QtGui.QWidget.__init__(self)

        self.layout = QtGui.QGridLayout(self)

        self.logBook = logBook

    def initUI(self):

        # Clear layout in case we are re-initializing the UI
        for i in reversed(range(self.layout.count())):
            try:
                self.layout.itemAt(i).widget().setParent(None)
            except AttributeError:
                layout = self.layout.itemAt(i)
                for i in reversed(range(layout.count())):
                    layout.itemAt(i).widget().setParent(None)


        self.splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)

        self.splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.layout.addWidget(self.splitter2,0,0)

        types = list(self.logBook.types)
        self.typesWidget = TypesWidget(types)
        self.typesWidget.requestSearch.connect(self.search)
        self.splitter1.addWidget(self.typesWidget)

        self.properties = [''] + self.trimDownProps(
                list(self.logBook.prop) + list(self.logBook.usrProp))

        self.searchWidgets = []
        searchContainer = QtGui.QWidget()
        self.searchWidgetsLayout = QtGui.QVBoxLayout(searchContainer)

        self.searchModeCheckBox = QtGui.QCheckBox('Match all conditions')
        self.searchModeCheckBox.setToolTip('Check this if you ant all your\
 search criteria to be matched simultaneously (i.e. taking the logical \'and\'\
 of all the criteria rather than the \'or\'.')
        self.searchWidgetsLayout.addWidget(self.searchModeCheckBox)
        self.searchModeCheckBox.stateChanged.connect(self.search)
        self.splitter2.addWidget(searchContainer)
        
        self.searchWidgets.append(SearchWidget(self.properties))
        self.searchWidgetsLayout.addWidget(self.searchWidgets[-1])
        self.searchWidgets[-1].propChanged.connect(self.addSearchWidget)
        self.searchWidgets[-1].requestSearch.connect(self.search)


        self.tags = list(self.logBook.tags)

        self.tagSelectorWidgets = []
        tagContainer = QtGui.QWidget()
        self.tagSelectorWidgetsLayout = QtGui.QVBoxLayout(tagContainer)

        self.tagModeCheckBox = QtGui.QCheckBox('Match all tags')
        self.tagModeCheckBox.setToolTip('Check this if you ant all your\
 tags to be matched simultaneously (i.e. taking the logical \'and\'\
 of all the tags rather than the \'or\'.')
        self.tagSelectorWidgetsLayout.addWidget(self.tagModeCheckBox)
        self.tagModeCheckBox.stateChanged.connect(self.search)
        self.splitter1.addWidget(tagContainer)

        self.tagSelectorWidgets.append(TagSelector([''] + self.tags))
        self.tagSelectorWidgetsLayout.addWidget(self.tagSelectorWidgets[-1])
        self.tagSelectorWidgets[-1].tagChanged.connect(self.addTagSelectorWidget)
        self.tagSelectorWidgets[-1].tagChanged.connect(self.search)

        self.newLog = []

    def addSearchWidget(self, sender):
        prop = sender.propSelector.currentText()
        if prop == '':
            self.searchWidgetsLayout.removeWidget(sender)
            self.searchWidgets.remove(sender)
            sender.setParent(None)
        elif not any([f.propSelector.currentText()=='' for f in self.searchWidgets]):
            self.searchWidgets.append(SearchWidget(self.properties))
            self.searchWidgetsLayout.addWidget(self.searchWidgets[-1])
            self.searchWidgets[-1].propChanged.connect(self.addSearchWidget)
            self.searchWidgets[-1].requestSearch.connect(self.search)

    def addTagSelectorWidget(self, sender):
        tag = sender.currentText()
        if tag == '':
            self.tagSelectorWidgetsLayout.removeWidget(sender)
            self.tagSelectorWidgets.remove(sender)
            sender.setParent(None)
        elif not any([f.currentText()=='' for f in self.tagSelectorWidgets]):
            self.tagSelectorWidgets.append(TagSelector([''] + self.tags))
            self.tagSelectorWidgetsLayout.addWidget(self.tagSelectorWidgets[-1])
            self.tagSelectorWidgets[-1].tagChanged.connect(self.addTagSelectorWidget)
            self.tagSelectorWidgets[-1].tagChanged.connect(self.search)

    def updateToCurrentLog(self, logBook):

        self.logBook = logBook

        props = [''] + self.trimDownProps(
                list(self.logBook.prop) + list(self.logBook.usrProp))

        for w in self.searchWidgets:
            currentItems = [str(w.propSelector.itemText(i)) for i in range(w.propSelector.count())]
            toAdd = set(props) - set(currentItems)
            w.propSelector.addItems(list(toAdd))
        
        self.tags = list(self.logBook.tags)

        for w in self.tagSelectorWidgets:
            currentItems = [str(w.itemText(i)) for i in range(w.count())]
            toAdd = set(self.tags) - set(currentItems)
            w.addItems(list(toAdd))

        types  = self.logBook.types
        self.typesWidget.initUI(types)

    def search(self):
        
        newLogs = []
        types = self.typesWidget.getTypes()
        tags = [str(t.currentText()) for t in self.tagSelectorWidgets if not str(t.currentText())=='']
    

        if tags == []:
            if self.tagModeCheckBox.checkState() == 2:
                taggedLog = dict()
            else:
                taggedLog = self.logBook

        else:
            if self.tagModeCheckBox.checkState() == 2:
                taggedLog = {key:entry for (key,entry) in self.logBook.iteritems()
                                if all([tag in entry.properties['tags'] for tag in tags])}
            else:
                taggedLog = {key:entry for (key,entry) in self.logBook.iteritems()
                                if any([tag in entry.properties['tags'] for tag in tags])}

        if len(self.searchWidgets) == 1:
            text = str(self.searchWidgets[0].searchBar.text())
            propName = str(self.searchWidgets[0].propSelector.currentText())
            if text == '' and propName == '':
                self.newLogFiltered.emit([entry for entry in taggedLog.values() 
                    if entry.__class__.__name__ in types])
                return

        for sWidget in self.searchWidgets:

            newLog = []
            text = str(sWidget.searchBar.text())
            wordList = set(re.sub("[^\w]", " ",  text).split())
            propName = str(sWidget.propSelector.currentText())

            if text == '' and propName == '':
                break
            elif not text == '' and propName == '':
                allProps = True
            else:
                allProps = False

            for key,entry in taggedLog.iteritems():
                if entry.__class__.__name__ in types:
                    if not allProps:
                        try:
                            prop = entry.properties[propName]
                            if all([True if (text.lower() in str(prop).lower()) else False for text in wordList])  \
                                    and not entry in newLog:
                                newLog.append(entry)
                        except:
                            pass
                    else:
                        for name,prop in entry.properties.iteritems():
                            if not name == 'tags':
                                try:
                                    if all([True if (text.lower() in str(prop).lower()) else False for text in wordList])  \
                                            and not entry in newLog:
                                        newLog.append(entry)
                                except:
                                    pass

            newLogs.append(newLog) 

        if self.searchModeCheckBox.checkState()==2:
            if len(newLogs)>0:
                filtering = set(newLogs[0])
                for s in newLogs[1:]:
                    filtering.intersection_update(s)
            else:
                filtering = list(newLogs)
        else:
            filtering = list(set([item for sublist in newLogs for item in sublist]))

        self.newLog = filtering

        self.newLogFiltered.emit(self.newLog)


    def toAnalysis(self):
        captures = []
        for log in self.newLog:
            if log.__class__.__name__ == 'CaptureLogEntry':
                captures.append(log.properties['capture'])

        self.analyseThis.emit(captures)

    def doStuff(self):
        pass

    def trimDownProps(self, props):
        toRemove = []
        for prop in props:
            if 'channel' in prop.lower() or 'time' in prop.lower():
                toRemove.append(prop)
        for prop in toRemove:
            props.remove(prop)

        try:
            props.remove('capture')
        except:
            pass

        try:
            props.remove('graph')
        except:
            pass

        try:
            props.remove('scan')
        except:
            pass

        try:
            props.remove('tags')
        except:
            pass
            
        return props


class TypesWidget(QtGui.QWidget):
    requestSearch = QtCore.Signal(object)
    def __init__(self, types):
        super(TypesWidget,self).__init__()

        self.layout = QtGui.QGridLayout(self)
        self.initUI(types)

    def initUI(self,types):

        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

        self.checks = {}

        i=0
        for i,t in enumerate(types):
            check = QtGui.QCheckBox(t)
            check.setToolTip('Check this if you want to add this type of entry to the filter.')
            self.checks[t] = check
            check.setChecked(True)
            check.stateChanged.connect(self.requestSearch.emit)
            self.layout.addWidget(check,i/2,i%2,1,1)

        self.layout.setRowStretch(i/2+1, 1)

    def getTypes(self):
        return [key for key,val in self.checks.iteritems() if val.checkState()==2]

class TimeFilterWidget(QtGui.QWidget):
    def __init__(self, types):
        super(TimeFilterWidget,self).__init__()

        layout = QtGui.QGridLayout(self)

        self.fromSlider = QtGui.QSlider(orientation=QtCore.Qt.Horizontal)
        self.toSlider = QtGui.QSlider(orientation=QtCore.Qt.Horizontal)

        layout.addWidget(self.fromSlider)
        layout.addWidget(self.toSlider)
        layout.setRowStretch(3,1)

    def getTimes(self):
        return self.fromSlider.currentValue(),self.toSlider.currentValue()

class SearchWidget(QtGui.QWidget):
    propChanged = QtCore.Signal(object)
    requestSearch = QtCore.Signal()
    def __init__(self, props):
        super(SearchWidget,self).__init__()

        self.props = props

        self.layout = QtGui.QHBoxLayout(self)

        self.propSelector = QtGui.QComboBox()
        self.propSelector.addItems(self.props)
        self.propSelector.currentIndexChanged.connect(
            lambda: self.propChanged.emit(self))
        self.layout.addWidget(self.propSelector)

        self.searchBar = QtGui.QLineEdit()
        self.searchBar.returnPressed.connect(self.requestSearch)
        self.layout.addWidget(self.searchBar)

        self.propSelector.setToolTip('Use this to choose a property you want to filter by.')
        self.searchBar.setToolTip('Type something here to filter the property you pick with\
 the combobox to the left.')

class TagSelector(QtGui.QComboBox):
    tagChanged = QtCore.Signal(object)
    def __init__(self, tags):
        super(TagSelector,self).__init__()

        self.tags = tags

        self.addItems(self.tags)
        self.currentIndexChanged.connect(
            lambda: self.tagChanged.emit(self))

        self.setToolTip('Use this to choose a tag you want to filter by.')

