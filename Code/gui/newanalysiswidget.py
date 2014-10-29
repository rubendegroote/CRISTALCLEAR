from __future__ import division
import pyqtgraph as pg
import pyqtgraph.functions as fn
from PyQt4 import QtCore,QtGui
import numpy as np
from lmfit import *
import time
import sys, csv
from collections import OrderedDict

from myspinbox import MySpinBox,FormattedSpinbox
from picbutton import PicButton
from splitter import MySplitter
from graphdock import MyGraph
from core.session import CaptureSession
from core.spectrum import Spectrum
from core.metacapture import MetaCapture
from gui.graphdock import MyGraph

def weightedAverage(values,errors):
    if len(values)>1:
        try:
            weights = 1.0/errors**2
        except TypeError:
            weights = 1.0*np.ones(len(errors)) / len(errors)

        weights = weights/np.sum(weights)

        val = np.average(values, weights = weights)
        err = np.sqrt(np.average((values-val)**2, weights=weights)) / \
                    (1-np.sum(weights**2))
    else:
        val = values[0]
        err = errors[0]

        if val == None:
            val = 0
        if err == None:
            err = 0

    return val,err



class NewAnalysisWidget(QtGui.QTabWidget):
    def __init__(self,globalSession):
        super(NewAnalysisWidget,self).__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.removeMetaCapture)

        self.metas = []
        self.graphs = []
        self.analysisPanels = []

        self.globalSession = globalSession
        self.layout = QtGui.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)

        self.metaButton = QtGui.QPushButton('Create Meta')
        self.layout.addWidget(self.metaButton,0,0)
        self.metaButton.clicked.connect(self.createMetaCapture)

    def createMetaCapture(self):
        name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
            'Enter meta capture name')

        if not ok:
            return

        name = str(name)

        self.metas.append(MetaCapture())

        graph = MyGraph(name, self.globalSession)
        self.graphs.append(graph)

        panel = AnalysisPanel(self.metas[-1])
        self.analysisPanels.append(panel)
        panel.model.newPlotRequested.connect(graph.clearPlot)
        panel.model.newPlotRequested.connect(graph.plot)


        graph.layout.addWidget(panel,1,0,1,2)
        graph.layout.setRowStretch(0,1)
        graph.settingsWidget.updatePlot.connect(\
                panel.results.updateUI)

        graph.comboX.currentIndexChanged.connect(\
                panel.model.createParameterBoxes)
        graph.comboY.currentIndexChanged.connect(\
                panel.model.createParameterBoxes)
        graph.freqUnitSelector.currentIndexChanged.connect(\
                panel.model.createParameterBoxes)

        graph.meanBox.currentIndexChanged.connect(\
                panel.model.updateSpectra)
        graph.madePlot.connect(lambda: self.plotFitCurves(graph))

        self.addTab(graph, name)

    def removeMetaCapture(self,index):
        del self.metas[index]
        self.graphs[index].setParent(None)
        del self.graphs[index]

    def addCapture(self,cap):
        index = self.currentIndex()
        if not cap in self.metas[index].captures:
            self.metas[index].addCapture(cap)

            self.graphs[index].setMetaCap(self.metas[index])
            self.analysisPanels[index].model.createParameterBoxes()
            self.analysisPanels[index].results.updateUI()
      
    def plotFitCurves(self,graph):

        metaCap = graph.metaCap

        m = np.min([np.min(d) for d in metaCap.x])
        M = np.max([np.max(d) for d in metaCap.x])

        x = np.linspace(m,M,1500)

        for s in metaCap.getSpectra():
            curve = pg.PlotCurveItem(x,s(x))
            curve.setPen(color='b', width=2.5)
            graph.fitCurves.append(curve)
            graph.graph.addItem(graph.fitCurves[-1])

class AnalysisPanel(QtGui.QTabWidget):

    def __init__(self,metaCapture):
        super(AnalysisPanel,self).__init__()

        self.layout = QtGui.QGridLayout(self)

        self.metaCap = metaCapture

        self.model = ModelWidget(metaCapture)
        self.addTab(self.model, 'Model')
        self.results = ResultWidget(metaCapture)
        self.results.initFitButton.clicked.connect(self.initFit)
        self.addTab(self.results, 'Results')

        self.currentChanged.connect(self.switchTabs)

    def switchTabs(self,no):
        if no == 1:
            self.results.updateUI()

    def initFit(self):
        self.model.setParameters(self.results.hHeaders, self.results.averages)

class ModelWidget(QtGui.QWidget):
    newPlotRequested = QtCore.Signal()
    def __init__(self,metaCapture):
        super(ModelWidget,self).__init__()

        self.metaCap = metaCapture
        self.parBoxes = {}

        self.layout = QtGui.QGridLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        sublayout = QtGui.QGridLayout()
        sublayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout.addLayout(sublayout,0,0)

        self.IField = QtGui.QDoubleSpinBox()
        self.IField.setDecimals(1)
        self.IField.setSingleStep(0.5)
        self.IField.valueChanged.connect(self.createParameterBoxes)
        sublayout.addWidget(QtGui.QLabel('I'),0,0)
        sublayout.addWidget(self.IField,0,1)
        sublayout.setColumnStretch(1,1)

        self.J0Field = QtGui.QDoubleSpinBox()
        self.J0Field.setDecimals(1)
        self.J0Field.setSingleStep(0.5)
        self.J0Field.valueChanged.connect(self.createParameterBoxes)
        sublayout.addWidget(QtGui.QLabel('J0'),0,2)
        sublayout.addWidget(self.J0Field,0,3)
        sublayout.setColumnStretch(3,1)

        self.J1Field = QtGui.QDoubleSpinBox()
        self.J1Field.setDecimals(1)
        self.J1Field.setSingleStep(0.5)
        self.J1Field.valueChanged.connect(self.createParameterBoxes)
        sublayout.addWidget(QtGui.QLabel('J1'),0,4)
        sublayout.addWidget(self.J1Field,0,5)
        sublayout.setColumnStretch(5,1)

        if self.metaCap.freqMode:
            freqSuff = 'Hz'
        else:
            freqSuff = 'm'

        self.FField = FormattedSpinbox(siPrefix = True, suffix = freqSuff, \
                    step = 0.01, dec = True,decimals = 8)

        self.FField.setRange(-10**99,10**99)
        self.FField.sigValueChanged.connect(self.spinboxChanged)
        sublayout.addWidget(QtGui.QLabel('f'),0,6)
        sublayout.addWidget(self.FField,0,7)
        sublayout.setColumnStretch(7,1)

        self.fitButton = QtGui.QPushButton('Fit')
        sublayout.addWidget(self.fitButton,0,8)
        self.fitButton.clicked.connect(self.fit)

        self.parScrollArea = QtGui.QScrollArea(self)
        self.parScrollArea.setMinimumHeight(300)
        self.parScrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.parScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(self.parScrollArea,1,0)

        self.parBoxLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.parBoxLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

    def updateSpectra(self):
        self.spectra = self.metaCap.getSpectra()

        if self.spectra == []:
            return

        for spect in self.spectra:
            spect.I = float(self.IField.value())
            spect.J = [float(self.J0Field.value()),
                            float(self.J1Field.value())]
            spect.f = float(self.FField.value())
            if self.metaCap.freqMode:
                spect.units = 'Hz'
            else:
                spect.units = 'm'

    def createParameterBoxes(self):  
        self.updateSpectra()

        try:
            for i in reversed(range(self.parBoxLayout.count())): 
                widget = self.parBoxLayout.itemAt(i).widget()
                self.parBoxLayout.removeWidget(widget)
                widget.setParent(None)

            self.parBoxes = {}

        except:
            pass

        if not self.metaCap.ykey == 'ion':
            return

        if self.metaCap.xkey == 'volt':
            suffix = 'V'
        else:
            if self.metaCap.freqMode:
                suffix = 'Hz'
            else:
                suffix = 'm'

        self.FField.setOpts(suffix = suffix)
        self.FField.setValue(np.mean(([np.mean(d) for d in self.metaCap.x])))

        for p in self.spectra[0].par.itervalues():
            if not p.name == 'bkg' and not 'Amp' in p.name:
                if self.metaCap.xkey == 'volt':
                    suffix = 'V'
                elif self.metaCap.freqMode:
                    suffix = 'Hz'
                else:
                    suffix = 'm'
            elif not 'Amp' in p.name:
                suffix = 'Hz'

            newSpinBox = MySpinBox(p.name, suffix = suffix)
            self.parBoxes[p.name] = newSpinBox
            newSpinBox.setCurrentValue(p.value)
            newSpinBox.parInfoChanged.connect(self.updateParInfo) # update the boundaries and vary check
            newSpinBox.valueChanged.connect(self.spinboxChanged) # update the value
            self.parBoxLayout.addWidget(newSpinBox)

    def fit(self):
        print 'fitting'

        self.spectra = self.metaCap.getSpectra()

        for parBox in self.parBoxes.itervalues():
            self.updateParInfo(parBox)

        print self.spectra

        for data,spect in zip( \
                    zip(self.metaCap.x,self.metaCap.y,self.metaCap.errors),
                    self.spectra):



            spect.FitToBinnedData(data[0],data[1],data[2])

        self.newPlotRequested.emit()

    def spinboxChanged(self):

        for spect in self.spectra:

            if self.sender() == self.FField:
                spect.f = float(self.FField.value())

            else:
                val = self.sender().getCurrentValue()
                name = self.sender().name

                if 'A0' in name:
                    v = spect.AB
                    v[0] = val
                    spect.AB = v

                elif 'A1' in name:
                    v = spect.AB
                    v[1] = val
                    spect.AB = v

                elif 'B0' in name:
                    v = spect.AB
                    v[2] = val
                    spect.AB = v

                elif 'B1' in name:
                    v = spect.AB
                    v[3] = val
                    spect.AB = v

                elif 'Amp_' in name:
                    nr = int(name.split('_')[-1])

                    v = spect.relAmp
                    v[nr] = val

                    spect.relAmp = v

                elif 'Amp' in name:
                    spect.amp = val

                elif 'FWHM' in name:
                    spect.fwhm = [self.parBoxes['FWHMG'].getCurrentValue(),
                                  self.parBoxes['FWHML'].getCurrentValue()]

                    

                elif 'df' in name:
                    spect.df = val

                elif 'bkg' in name:
                    spect.bkg = val

                spect.par[name].value = val

        self.newPlotRequested.emit()

    def updateParInfo(self, parBox):
        for spect in self.spectra:
            spect.par[parBox.name].value = parBox.getCurrentValue()
            spect.par[parBox.name].vary = parBox.getVaryCheck() == 2
            spect.par[parBox.name].min = parBox.getMin()
            spect.par[parBox.name].max = parBox.getMax()

    def setParameters(self,names,values):
        for name,value in zip(names,values):
            try:
                self.parBoxes[name].setCurrentValue(float(value))
            except KeyError:
                pass

class ResultWidget(QtGui.QWidget):
    def __init__(self,metaCapture):
        super(ResultWidget,self).__init__()

        self.metaCap = metaCapture

        self.averages = []

        self.layout = QtGui.QGridLayout(self)
        sublayout = QtGui.QHBoxLayout()
        sublayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.layout.addLayout(sublayout,0,0)

        self.table = CopyTable(1,1,self)
        self.layout.addWidget(self.table,1,0)

        saveButton = QtGui.QPushButton('Save as CSV')
        saveButton.clicked.connect(self.table.handleSave)
        sublayout.addWidget(saveButton)
        
        self.initFitButton = QtGui.QPushButton('Use as Init')
        sublayout.addWidget(self.initFitButton)

    def updateUI(self):

        spectra = self.metaCap.getSpectra()

        print spectra 

        self.averages = []
        self.errors = []

        if len(spectra) == 0:
            return

        self.table.setRowCount(len(spectra)+1)
        self.table.setColumnCount(len(spectra[0].par.keys()))

        self.hHeaders= ['Reduced chi2']
        self.hHeaders.extend(spectra[0].par.keys())
        for i,t in enumerate(self.hHeaders):
            self.table.setHorizontalHeaderItem(i,QtGui.QTableWidgetItem(t))
        
        self.vHeaders = self.metaCap.getCurrentCapsHeaderInfo()
        for i,t in enumerate(spectra):
            self.table.setVerticalHeaderItem(i,QtGui.QTableWidgetItem(self.vHeaders[i]))

        self.table.setVerticalHeaderItem(self.table.rowCount()-1,QtGui.QTableWidgetItem('Weighted mean'))

        for i,spect in enumerate(spectra):
            try:
                self.table.setItem(i,0,QtGui.QTableWidgetItem(str(round(spect.results.redchi,4))))
            except:
                self.table.setItem(i,0,QtGui.QTableWidgetItem('0'))

            for j,p in enumerate(spect.par.values()):
                try:
                    val = str(round(p.value,4))
                    err = str(round(p.stderr,4))
                except:
                    val = '0'
                    err = '0'
                text = val + '(' + err + ')'
                self.table.setItem(i,j+1,QtGui.QTableWidgetItem(text))

        for j,k in enumerate(spectra[0].par.keys()):

            values = np.array([spect.par[k].value for spect in spectra])
            errors = np.array([spect.par[k].stderr for spect in spectra])

            val,err = weightedAverage(values,errors)

            self.averages.append(val)

            val = str(round(val,4))
            err = str(round(err,4))
            text = val + '(' + err + ')'

            self.table.setItem(self.table.rowCount()-1,j+1,QtGui.QTableWidgetItem(text))


class CopyTable(QtGui.QTableWidget):
    def __init__(self,*args,**kwargs):
        super(CopyTable,self).__init__(*args,**kwargs)
        self.plots = []
        self.clip = QtGui.QApplication.clipboard()

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        plotAllAction = menu.addAction("Plot Selected")
        if self.XYValid():
            XYPlotAction = menu.addAction("XY Plot")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == plotAllAction:
            self.plotResults(XY = False)
        elif self.XYValid() and action == XYPlotAction:
            self.plotResults(XY = True)

    def XYValid(self):
        selected = self.selectedRanges()

        valid = True

        headers = []
        for sel in selected:
            for i,c in enumerate(xrange(sel.leftColumn(), sel.rightColumn()+1)):
                headers.append(str(self.horizontalHeaderItem(i+sel.leftColumn()).text()))

        return len(set(headers)) == 2


    def plotResults(self, XY = False):
        data = self.getDataFromSelection(self.selectedRanges())

        summary = SummaryPlot()
        self.plots.append(summary)
        summary.show()

        if XY:
            summary.plotXY(data)
        else:
            summary.plotAll(data)

    def getDataFromSelection(self,selected):

        data = {}   
        for sel in selected:
            for i,c in enumerate(xrange(sel.leftColumn(), sel.rightColumn()+1)):
                header = str(self.horizontalHeaderItem(i+sel.leftColumn()).text())
                if not header in data.keys():
                    data[header] = OrderedDict()

                    data[header]['averages'] = 0
                    data[header]['avErrors'] = 0
                    data[header]['data'] = []
                    data[header]['error'] = []

                for j,r in enumerate(xrange(sel.topRow(), sel.bottomRow()+1)):
                    try:
                        if j+sel.topRow() == self.rowCount()-1:
                            data[header]['averages'] = float(self.item(r,c).text().split('(')[0])
                            data[header]['avErrors'] = float(self.item(r,c).text().split('(')[1].split(')')[0])
                        else:
                            data[header]['data'].append(float(self.item(r,c).text().split('(')[0]))
                            data[header]['error'].append(float(self.item(r,c).text().split('(')[1].split(')')[0]))
                    except AttributeError:
                        pass

        return data


    def handleSave(self):
        path = QtGui.QFileDialog.getSaveFileName(
                self, 'Save File', '', 'CSV(*.csv)')
        if not path.isEmpty():
            with open(unicode(path), 'wb') as stream:
                writer = csv.writer(stream,delimiter=';', dialect='excel')

                header = ['']
                header.extend([str(self.horizontalHeaderItem(i).text())\
                        for i in xrange(self.columnCount())])
                writer.writerow(header)

                for i,row in enumerate(xrange(self.rowCount())):
                    rowdata = []
                    rowdata.append(str(self.verticalHeaderItem(i).text()))
                    for column in range(self.columnCount()):
                        item = self.item(row, column)
                        if item is not None:
                            rowdata.append(
                                unicode(item.text()).encode('utf8'))
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)

    # def handleOpen(self):
    #     path = QtGui.QFileDialog.getOpenFileName(
    #             self, 'Open File', '', 'CSV(*.csv)')
    #     if not path.isEmpty():
    #         with open(unicode(path), 'rb') as stream:
    #             self.setRowCount(0)
    #             self.setColumnCount(0)
    #             for rowdata in csv.reader(stream):
    #                 row = self.rowCount()
    #                 self.insertRow(row)
    #                 self.setColumnCount(len(rowdata))
    #                 for column, data in enumerate(rowdata):
    #                     item = QtGui.QTableWidgetItem(data.decode('utf8'))
    #                     self.setItem(row, column, item)

    def keyPressEvent(self, e):
        if (e.modifiers() & QtCore.Qt.ControlModifier):
            selected = self.selectedRanges()

            if e.key() == QtCore.Qt.Key_C: #copy

                s = ''

                for sel in selected:
                    for i,c in enumerate(xrange(sel.leftColumn(), sel.rightColumn()+1)):
                        s = s + 'scan' +'\t'+ str(self.horizontalHeaderItem(i+sel.leftColumn()).text()) + '\n'
                        for j,r in enumerate(xrange(sel.topRow(), sel.bottomRow()+1)):
                            try:
                                s = s + str(self.verticalHeaderItem(j+sel.topRow()).text()) + '\t'
                                s += str(self.item(r,c).text()) + "\n"
                            except AttributeError:
                                s += "\n"
                        s = s + '\n'
                                    
                    s = s + '\n'
                self.clip.setText(s)

class SummaryPlot(pg.PlotWidget):
    def __init__(self,*args,**kwargs):
        super(SummaryPlot,self).__init__(*args,**kwargs)

    def plotAll(self,data):

        legend = self.getPlotItem().addLegend()

        for i,(h,dat) in enumerate(data.iteritems()):
            pen = (i,len(data))
            y = np.array(dat['data'])
            e = np.array(dat['error'])
            x = np.arange(len(y))

            curve = pg.ErrorBarItem(x = x, y = y, bottom = e, top = e,pen = pen)
            self.addItem(curve)

            curve = pg.ScatterPlotItem(x = x, y = y,pen = pen,brush = pen)
            self.addItem(curve)

            legend.addItem(curve,'\t '+ h)

            try:
                average = dat['averages']
                avError = dat['avErrors']

                self.addItem(pg.PlotCurveItem(x=x, 
                    y = np.ones(len(x))*average,pen = pen))
                c = pg.PlotCurveItem(x = x, y = np.ones(len(x))*(average+avError),
                        brush = (150, 150, 150,100), fillLevel = average-avError)
                self.addItem(c)
            except:
                pass
            
    
    def plotXY(self,data):

        legend = self.getPlotItem().addLegend()

        headers = data.keys()
        x,y = data[headers[0]]['data'], data[headers[1]]['data']
        xerr,yerr = data[headers[0]]['error'], data[headers[1]]['error']

        curve = pg.ErrorBarItem(x = np.array(x), y =  np.array(y), 
                bottom =  np.array(yerr), top =  np.array(yerr), 
                left =  np.array(xerr), right =  np.array(xerr),pen = 'r')
        self.addItem(curve)

        curve = pg.ScatterPlotItem(x =  np.array(x), y =  np.array(y),
                pen = 'r', brush = 'r')
        self.addItem(curve)

        legend.addItem(curve,'\t '+ headers[0] + ' vs ' + headers[1])

        try:
            xav,yav = data[headers[0]]['averages'],\
                        data[headers[1]]['averages']
            xaverr,yaverr = data[headers[0]]['avErrors'],\
                        data[headers[1]]['avErrors']

            x = np.linspace(xav-xaverr,xav+xaverr,10)
            c = pg.PlotCurveItem(x = x, y = np.ones(len(x))*(yav+yaverr),
                    brush = (150, 150, 150,100), fillLevel = yav-yaverr)
            self.addItem(c)
        except:
            pass