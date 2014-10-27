from __future__ import division
import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import numpy as np
from lmfit import *
import time
from string import replace
from myspinbox import MySpinBox
from splitter import MySplitter

from functions import *


class AnalysisWidget(QtGui.QTabWidget):
    def __init__(self):
        super(AnalysisWidget,self).__init__()

        self.usrDefFunc = {}

        self.captures = {}
        self.xkey = ''
        self.ykey = ''

        self.currentChanged.connect(self.updateFitFunction)
            
        self.capturePanels = {}
        self.setTabsClosable(True)

        self.modelSummary = ModelSummary(self,self.captures)
        self.modelSummary.combo.connect(self.setXY)
        self.addTab(self.modelSummary, 'Model Overview')

    def addCapture(self, cap):
        self.captures[cap.name] = cap

        self.updateFitFunction()
        pos = self.count()
        self.capturePanels[pos] = CapturePanel(self,cap)
        self.capturePanels[pos].newFit.connect(self.modelSummary.summaryGraph.updateTree)

        self.addTab(self.capturePanels[pos], cap.name)

        self.modelSummary.summaryGraph.addCapture(cap)
        self.modelSummary.setComboBoxes()

    def closeCapturePanel(self,pos):
        try:
            self.capturePanels[pos].setParent(None)
            del self.capturePanels[pos]
            for i in range(pos+1,len(self.capturePanels)+1):
                self.capturePanels[i-1] = self.capturePanels[i]
                del self.capturePanels[i]
        except KeyError:
            pass

    # def updateUserFunctions(self,func):
    #     self.usrDefFunc = func
    #     self.modelSummary.fitFunctionDefiner.defineUserFunctions(self.usrDefFunc)
    #     for capture in self.capturePanels.itervalues():
    #         capture.usrDefFunc = self.usrDefFunc

    # def updateFitFunction(self):

    #     self.modelSummary.updateFitFunction()

    #     self.fitFunction = self.modelSummary.fitFunction
    #     self.params = self.modelSummary.params
    #     self.fitFunctionText = self.modelSummary.fitFunctionText

    #     for panel in self.capturePanels.itervalues():
    #         panel.updateFitFunction(self.fitFunctionText, self.params, self.fitFunction)
    #         panel.updateGraph()

    def setXY(self,xkey,ykey,errFunc):
        if not xkey == '' and not ykey == '':
            for panel in self.capturePanels.itervalues():
                panel.updatePanelSettings(str(xkey),str(ykey),str(errFunc))

# class FuncDefWindow(QtGui.QWidget):
#     close = QtCore.Signal(bool)
#     def __init__(self,textEdit):
#         super(FuncDefWindow, self).__init__()

#         self.resize(800, 600)

#         layout = QtGui.QGridLayout(self)
#         if textEdit == None:
#             self.funcText = QtGui.QTextEdit()
#         else:
#             self.funcText = textEdit

#         layout.addWidget(self.funcText, 0,0,1,10)
#         self.funcText.setTabStopWidth(8)

#         self.okButton = QtGui.QPushButton('Update functions')
#         layout.addWidget(self.okButton, 1,9,1,1)
#         self.okButton.clicked.connect(self.defineNewFunction)

#         self.show()

#     def defineNewFunction(self):
#         try:
#             self.usrDefFunc = {}
#             self.text = str(self.funcText.toPlainText())

#             code = 'import numpy as np\n' + self.text
#             eval(compile(code, '<stdin>', 'exec'),self.usrDefFunc)

#             self.close.emit(True)

#         except: 
#             pass

class ModelSummary(QtGui.QWidget):
    combo = QtCore.Signal(str,str,str)
    def __init__(self,parent,captures):
        super(ModelSummary,self).__init__(parent)

        self.captures = captures

        self.summaryGraph = SummaryGraph()

        self.layout = QtGui.QGridLayout(self)

        
        self.layout.addWidget(QtGui.QLabel('X: '),0,0)
        self.comboX = QtGui.QComboBox()
        self.comboX.currentIndexChanged.connect(self.emitCombo)
        self.layout.addWidget(self.comboX,0,1)

        self.layout.addWidget(QtGui.QLabel('Y: '),1,0)
        self.comboY = QtGui.QComboBox()
        self.comboY.currentIndexChanged.connect(self.emitCombo)
        self.layout.addWidget(self.comboY,1,1)

        self.layout.addWidget(QtGui.QLabel('error(X,Y): '),2,0)
        self.errEdit = QtGui.QLineEdit('[1 if x==0 else np.sqrt(x) for x in Y]')
        self.errEdit.editingFinished.connect(self.emitCombo)
        self.layout.addWidget(self.errEdit,2,1)


        # self.fitFunctionDefiner = FitFunctionDefiner('\'constant\'')
        # self.fitFunctionDefiner.funcEdit.textChanged.connect(self.updateFitFunction)
        # self.layout.addWidget(self.fitFunctionDefiner,3,0,1,2)

        # self.updateFitFunction()

        line = QtGui.QFrame()
        line.setFrameStyle(QtGui.QFrame.HLine)
        line.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.layout.addWidget(line,4,0,1,3)

        self.layout.addWidget(self.summaryGraph,5,0,1,3)

        self.layout.setColumnStretch(2,1)
        self.layout.setRowStretch(5,1)

    # def updateFitFunction(self):

    #     self.fitFunctionDefiner.define()

    #     self.params = self.fitFunctionDefiner.params
    #     self.fitFunction = self.fitFunctionDefiner.fitFunction
    #     self.fitFunctionText = self.fitFunctionDefiner.fitFunctionText

    #     self.summaryGraph.setParams(self.params)
    
    def setComboBoxes(self):
        try:
            dataNames = [cap.dataManager.allData[0].keys() for cap in \
                                            self.captures.values()]
            dataNames = list(set([item for sublist in dataNames for \
                                                item in sublist]))

            dataNames = [x for x in dataNames if not x in \
                [self.comboX.itemText(i) for i in range(self.comboX.count())]]

            self.comboX.addItems(dataNames)
            self.comboY.addItems(dataNames)

            self.summaryGraph.setComboBoxes()

            self.emitCombo()
        except:
            pass

    def emitCombo(self):
        self.combo.emit(str(self.comboX.currentText()),
                        str(self.comboY.currentText()),
                        str(self.errEdit.text()))


class SummaryGraph(pg.GraphicsView):
    def __init__(self):
        super(SummaryGraph,self).__init__()

        self.captures = {}

        self.toPlot = set()
        self.params = []

        self.graph = pg.PlotWidget()
        self.graph.showGrid(x=True, y=True,alpha=0.7)

        layout = QtGui.QGridLayout(self)
        layout.addWidget(self.graph,0,0,1,1)

        sublayout = QtGui.QGridLayout()
        layout.addLayout(sublayout,10,0)

        self.comboY = QtGui.QComboBox(parent = None)
        self.comboY.currentIndexChanged.connect(self.updatePlot)
        sublayout.addWidget(self.comboY,0,1)

        label = QtGui.QLabel('vs')
        sublayout.addWidget(label,0,2)

        self.comboX = QtGui.QComboBox(parent = None)
        self.comboX.currentIndexChanged.connect(self.updatePlot)
        sublayout.addWidget(self.comboX,0,3)

        sublayout.setColumnStretch(4,1)

        header = ['Capture', 'Scan']
        self.captureTree = CaptureTree(self, header)
        self.captureTree.itemChecked.connect(self.updateToPlot)
        layout.addWidget(self.captureTree)
 
    def updatePlot(self):

        if self.captures == {}:
            return

        xkey = str(self.comboX.currentText())
        ykey = str(self.comboY.currentText())

        if xkey == '' or ykey == '':
            return

        self.clearGraph()
        x=[0]
        curves= []

        for i,cap in enumerate(self.captures.itervalues()):

            pen = (i,len(self.captures))

            if xkey in self.params and ykey in self.params:
                y = np.array([cap.pDict[scan][ykey].value \
                        for scan in cap.pDict.iterkeys() if scan in self.toPlot])
                yerr = [cap.pDict[scan][ykey].stderr \
                        for scan in cap.pDict.iterkeys() if scan in self.toPlot]
                yerr = np.array([i if i is not None else 0 for i in yerr])

                x = np.array([cap.pDict[scan][xkey].value \
                        for scan in cap.pDict.iterkeys() if scan in self.toPlot])
                xerr = [cap.pDict[scan][xkey].stderr \
                        for scan in cap.pDict.iterkeys() if scan in self.toPlot]
                xerr = np.array([i if i is not None else 0 for i in xerr])

                curves.append(pg.ErrorBarItem(x=x,y=y,top=yerr,bottom=yerr,
                    left=xerr,right=xerr,pen=pen))
                curves.append(pg.ScatterPlotItem(x=x,y=y,pen=pen,brush=pen))


            elif ykey in self.params:
                y = np.array([cap.pDict[scan][ykey].value \
                        for scan in cap.pDict.iterkeys() if scan in self.toPlot])
                err = np.array([cap.pDict[scan][ykey].stderr \
                        for scan in cap.pDict.iterkeys() if scan in self.toPlot])
                x = np.arange(1,len(y)+1)+x[-1]

                curves.append(pg.ErrorBarItem(x=x,y=y,top=err,bottom=err,pen=pen))
                curves.append(pg.ScatterPlotItem(x=x,y=y,pen=pen,brush=pen))

            else:
                pass

            for curve in curves:
                try:
                    self.graph.addItem(curve,clear = False)
                except:
                    pass
                    

    def addCapture(self,capture):

        if not capture.name in self.captures.iterkeys():
            self.captures[capture.name] = capture

            item = CaptureTreeItem(self.captureTree, name = capture.name + ' all')
            item.setText(0, capture.name.split(' ')[1])

            scans = len(capture.dataManager.allData)
            for i in range(scans):
                subItem = CaptureTreeItem(item, name = capture.name +' '+ str(i))
                subItem.setText(1, str(i))
                subItem.setCheckState(1, 2)

            self.updatePlot()

    def clearGraph(self):
        self.graph.clear()

    def updateToPlot(self,number,state):

        number = str(number)

        if 'all' in number:
            return

        if state:
            self.toPlot.add(number)
        else:
            self.toPlot.remove(number)

        self.updatePlot()

    def setParams(self,params):
        self.params = params
        self.setComboBoxes()

    def setComboBoxes(self):

        self.comboX.clear()
        self.comboY.clear()

        combos = [' '] + list(self.params)

        self.comboX.addItems(combos)
        self.comboY.addItems(combos)


    def updateTree(self):

        root = self.captureTree.invisibleRootItem()

        for i in xrange(root.childCount()):
            item = root.child(i)

            name = str(item.name).strip(' all')

            for k in xrange(item.childCount()):
                scanName = name + ' ' + str(k)
                subItem = item.child(k)
                for j,(key,val) in enumerate(self.captures[name].pDict[scanName].iteritems()):
                    subItem.setText(j+2, str(round(val.value,4)) +' (' + str(round(val.stderr,4))+')')


        self.captureTree.setHeader(['Capture', 'Scan'] + list(self.params))


class CapturePanel(QtGui.QWidget):

    newFit = QtCore.Signal(object)
    def __init__(self,parent,capture):
        super(CapturePanel,self).__init__(parent)
        
        self.gLayout = pg.GraphicsLayoutWidget(parent = self)

        rhsWidget = QtGui.QWidget()
        self.rhs = QtGui.QGridLayout(rhsWidget)

        self.spinBoxLayout = QtGui.QGridLayout()
        self.rhs.addLayout(self.spinBoxLayout,3,0,1,2)

        self.previousPlotTime = time.time()

        self.spinBoxes = {}
        self.capture = capture
        self.capture.pDict = {}
        self.scansToFit = set()
        self.graphs = {}

        self.usrDefFunc = parent.usrDefFunc
        self.params = parent.params
        self.fitFunction = parent.fitFunction
        self.makeSpinboxes()

        self.createTree()

        self.fitFuncLabel = QtGui.QLabel('Y(X) = ' + parent.fitFunctionText)
        self.rhs.addWidget(self.fitFuncLabel,0,0,1,2)

        self.rhs.addWidget(QtGui.QLabel('Bin size: '),1,0,1,1)
        self.binSpinBox = pg.SpinBox(value = 0.03,
            bounds = (0,None), dec = False)
        self.binSpinBox.sigValueChanged.connect(self.updateGraph)
        self.rhs.addWidget(self.binSpinBox,1,1,1,1)

        self.layout = QtGui.QGridLayout(self)
        splitter = MySplitter('Fitting options', self.gLayout, rhsWidget)
        self.layout.addWidget(splitter,0,0)

        self.dataSets = {}
        self.errFunc = None

    def updatePanelSettings(self,xkey,ykey,errFunc):

        self.errFunc = eval('lambda X,Y:' + '(' + errFunc + ')*np.ones(len(Y))')

        self.xkey = xkey
        self.ykey = ykey
                    
        self.updateGraph()

    def makeSpinboxes(self):
        for param in self.params:
            if not param in self.spinBoxes.keys():
                self.spinBoxes[param] = MySpinBox(param)
                self.spinBoxLayout.addWidget(self.spinBoxes[param],len(self.spinBoxes)+1,0)
                self.spinBoxes[param].updateSpinBox()
                self.spinBoxes[param].spinbox.valueChanged.connect(self.spinboxChanged)
  
                self.updateParameters()

        toDel = []
        for name,spinbox in self.spinBoxes.iteritems():
            if not name in self.params:
                spinbox.setParent(None)
                toDel.append(name)

        for key in toDel:
            del self.spinBoxes[key]

    def spinboxChanged(self):
        self.capture.fitted = False
        self.updateParameters()
        self.continuousUpdateGraph()

    def updateParameters(self):
        for name in self.graphs.iterkeys():
            for spinboxNo, spinbox in self.spinBoxes.iteritems():
                val = spinbox.getCurrentValue()
                mi = spinbox.getMin()
                ma = spinbox.getMax()
                va = spinbox.getVaryCheck()==2

                if not spinboxNo in self.capture.pDict[name].iterkeys():
                    self.capture.pDict[name].add(spinbox.name, value = val,min = mi, max = ma,vary = va)
                elif not self.capture.fitted:
                    self.capture.pDict[name][spinboxNo].value = val
                    self.capture.pDict[name][spinboxNo].min = mi
                    self.capture.pDict[name][spinboxNo].max = ma
                    self.capture.pDict[name][spinboxNo].vary = va
                

            toDel = []
            for param in self.capture.pDict[name].iterkeys():
                if not param in self.spinBoxes.keys():
                    toDel.append(param)

            for key in toDel:
                del self.capture.pDict[name][key]

    def continuousUpdateGraph(self):
        if time.time() - self.previousPlotTime > 0.03:
            self.updateGraph()

    def updateGraph(self):
        self.updateParameters()

        if self.xkey == 'freq':
            try:
                offset = np.min(self.capture.dataManager.allData[0][self.xkey])*29.979
            except:
                offset = 0

            xlabel = self.xkey + ' - ' + str(offset) + ' (GHz)'
        else:
            xlabel = self.xkey


        for i,data in enumerate(self.capture.dataManager.allData):
            curves = []
            
            xData = data[self.xkey]
            yData = data[self.ykey]

            if len(xData) > 1:

                if self.xkey == 'freq':
                    xData = np.array(xData)*29.979
                    xData = xData - offset

                scanName = self.capture.name + ' ' + str(i)

                self.graphs[scanName].setLabels(title = self.capture.name + ' scan ' + str(i),
                         bottom = xlabel, left = self.ykey)
            
                if scanName in self.scansToFit:

                    binsize = self.binSpinBox.value()

                    if xData[0] < xData[-1]:
                        bins = np.arange(min(xData)-3*binsize/2, max(xData) + binsize/2, binsize)
                    else:
                        start = round(min(xData)/binsize) * binsize
                        bins=np.arange(start-binsize/2, max(xData) + 3*binsize/2, binsize)

                    bin_means = np.histogram(xData, bins, weights=yData)[0]

                    if not self.ykey == 'ion':
                        bin_means = bin_means / np.histogram(xData, bins)[0]

                    errors = self.errFunc(bins[1:],bin_means)

                    curves.append(pg.PlotCurveItem(x=bins,y=bin_means,pen = 'b',stepMode = True))

                    self.dataSets[i] = [bins[1:],bin_means,errors]

                    x = np.sort(xData)
                    curves.append(pg.PlotCurveItem(x,
                        self.fitFunction(self.capture.pDict[scanName],
                            [x]),pen ='r',stepMode = False))

                    self.graphs[scanName].clear()
                    for curve in curves:
                        self.graphs[scanName].addItem(curve,clear = False)
     

    def createTree(self):

        header = ['Scan']
        self.captureTree = CaptureTree(self,header)

        self.fitButton = QtGui.QPushButton('Fit')
        self.captureTree.layout.addWidget(self.fitButton,1,1)
        self.fitButton.clicked.connect(self.fit)
        self.captureTree.itemChecked.connect(self.createSubGraphs)
        self.rhs.addWidget(self.captureTree,2,0,1,2)

        name = self.capture.name

        for i in range(len(self.capture.dataManager.allData)):
            subItem = CaptureTreeItem(self.captureTree, name = name + ' ' + str(i))
            subItem.setText(0, 'scan '+str(i))
            subItem.setCheckState(0, 2)


    def createSubGraphs(self,text,state):

        text = str(text)
        number=int(text.split(' ')[2])

        if state:
            if not number in self.graphs.iterkeys():
                self.graphs[text] = pg.PlotItem(name = str(number))
                self.capture.pDict[text] = Parameters()
                

            col = number % 3
            row = 1 + number // 3

            self.gLayout.addItem(self.graphs[text],row=row, col = col)
            self.scansToFit.add(text)

        else:
            if text in self.graphs.iterkeys():
                self.gLayout.removeItem(self.graphs[text])
                self.scansToFit.remove(text)


    def updateFitFunction(self,text,params,func):
        self.fitFunction = func
        self.fitFuncLabel.setText('Y(X) = ' + text)
        self.params = params
        self.makeSpinboxes()

    def fit(self):
        self.updateParameters()

        np.seterr(divide='raise')

        for scanName in self.scansToFit:

            scan = int(scanName.split(' ')[2])

            try:
                self.residuals(self.capture.pDict[scanName],
                        self.dataSets[scan])

            except FloatingPointError:
                msgBox = QtGui.QMessageBox()
                msgBox.setText("Divide by zero error; make sure the errors are nonzero.")
                msgBox.exec_()

                return

            results = minimize(self.residuals,self.capture.pDict[scanName],
                    args=([self.dataSets[scan]]))

            # report_fit(self.capture.pDict[scan])
            # print results.redchi

        np.seterr(divide='print')

        self.capture.fitted = True

        self.newFit.emit(True)

        self.updateGraph()


    def residuals(self,ps,dataSet):
        return (dataSet[1] - self.fitFunction(ps,dataSet))/np.abs(dataSet[2])


class CaptureTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self,parent,name):
        QtGui.QTreeWidgetItem.__init__(self,parent)
        self.name = name

    def setData(self, column, role, value):
        if not 'all' in self.name:
            state = self.checkState(column)

        QtGui.QTreeWidgetItem.setData(self, column, role, value)
        if (role == QtCore.Qt.CheckStateRole and state != self.checkState(column)):
            treewidget = self.treeWidget()
            if treewidget is not None:
                treewidget.itemChecked.emit(self.name, int(self.checkState(column)))


class CaptureTree(QtGui.QTreeWidget):
    itemChecked = QtCore.Signal(str, int)
    def __init__(self, parent,header):
        QtGui.QTreeWidget.__init__(self,parent)
        self.layout = QtGui.QGridLayout(self)
        self.layout.setRowStretch(0,1)

        self.setHeader(header)

    def setHeader(self,header):
        self.setColumnCount(len(header))
        self.setHeaderLabels(header)

        ## Set Columns Width to match content:
        for column in range(self.columnCount()):
            self.resizeColumnToContents(column)

# class FitFunctionDefiner(QtGui.QWidget):
#     def __init__(self,text):
#         super(FitFunctionDefiner,self).__init__()

#         self.forbiddenList  = ['','X', 'Y', 'and', 'as', 'assert', 'break', 'class', 'continue',
#                   'def', 'del', 'elif', 'else', 'except', 'exec',
#                   'finally', 'for', 'from', 'global', 'if', 'import', 'in',
#                   'is', 'lambda', 'not', 'or', 'pass', 'print', 'raise',
#                   'return', 'try', 'while', 'with', 'True', 'False',
#                   'None', 'eval', 'execfile', '__import__', '__package__'] 
                                                

#         self.illegalX = ['*x', 'x*' '+x', 'x+', ' x', 'x ', 'x-', '-x', 'x/', '/x', '(x', 'x)']

#         self.numpyFunctions = ['sin','costan','arccos','arcsin','arctan','hypot','arctan2','degrees','radians',
#         'unwrap','deg2rad','rad2deg','sinh','cosh','tanh','arcsinh','arccosh','arctanh','around','round_','rint',
#         'fix','floor','ceil','trunc','prod','sum','nansum','cumprod','cumsum','diff','ediff1d','gradient',
#         'cross','trapz','exp','expm1','exp2','log','log10','log2','log1p','logaddexp','logaddexp2','i0','sinc',
#         'signbit','copysign','frexp','ldexp','add','reciprocal','negative','multiply','divide','power','subtract',
#         'true_divide','floor_divide','fmod','mod','modf','remainder','angle','real','imag','conj','convolve',
#         'clip','sqrt','square','absolute','fabs','sign','maximum','minimum','fmax','fmin','nan_to_num',
#         'real_if_close','interp']

#         self.layout = QtGui.QGridLayout(self)

#         label = QtGui.QLabel('Y(X) = ')
#         self.layout.addWidget(label,0,0)

#         self.funcEdit = QtGui.QTextEdit(text)
#         self.funcEdit.textChanged.connect(self.define)
#         self.funcEdit.setMaximumHeight(100)
#         self.layout.addWidget(self.funcEdit,0,1,1,2)

#         label = QtGui.QLabel('Interpreter Messages:')
#         self.layout.addWidget(label,1,0)

#         self.errorEdit = QtGui.QTextEdit('--No Errors--')
#         self.errorEdit.setReadOnly(True)
#         self.errorEdit.setMaximumHeight(50)
#         self.layout.addWidget(self.errorEdit,1,1,1,2)

#         self.define()

#     def define(self):
#         try:
#             self.fitFunctionText = str(self.funcEdit.toPlainText())
#             expression,self.params = self.translate(self.fitFunctionText)
#             expression = self.prepareString(expression)


#             if not expression==None and not self.params==None and not expression == '':
#                 try:
#                     self.fitFunction = eval('lambda parameters,dataSet :' + '(' + \
#                         expression + ')*np.ones(len(dataSet[0]))')

#                     self.errorEdit.setText('--No Errors--')

#                 except Exception as ex:
#                     self.raiseError(ex.__unicode__())
#                     return


#         except UnicodeEncodeError as ex:
#             self.raiseError(ex.__unicode__())


#     def raiseError(self,excString):
#         self.errorEdit.setText(excString)

#     def prepareString(self,string):

#         if '=' in string:
#             self.raiseError("Invalid expression: two = signs.")
#             return 

#         if '\n' in string or '\t' in string:
#             self.raiseError("Invalid expression, no tabs or enters please :)")
#             return

#         if '^' in string:
#             string = replace(string, '^','**')

#         if any(word in string for word in self.illegalX):

#             self.raiseError("Please use capitalized X instead of x for the x-axis variable.")
#             return 

#         for word in self.numpyFunctions:
#             if word in string and not word in self.usrDefFunc.iterkeys():
#                 string = replace(string, word,'np.' + word)

#         return string


#     def translate(self,string):

#         if any(symbol in string for symbol in [';','?','!',':','\\', 
#                                                         '[',']','{','}']):
#             self.raiseError("Expression cannot contain punctuation marks")
#             return ('', [])

#         retString = ''
#         params = set()

#         if 'HFS(X)' in string:
#             params.update(init_params())

#             before = string.partition('HFS(X)')[0]
#             after = string.partition('HFS(X)')[-1]
#             string = before + 'HFS(parameters,X)' + after

#         curString = string

#         if not '\'' in curString:
#             return (self.findX(curString), [])

#         while '\'' in curString:

#             before = curString.partition('\'')[0]
#             after = curString.partition('\'')[-1].partition('\'')[-1]

#             if curString.partition('\'')[-1].partition('\'')[1] == '\'':

#                 param = curString.partition('\'')[-1].partition('\'')[0]

#                 if param in self.forbiddenList:
#                     self.raiseError("Invalid parameter name " + param)
#                     return ('', [])
#                 elif ' ' in param:
#                     self.raiseError("Parameter name cannot contain spaces")
#                     return ('', [])         
#                 else:
#                     params.add(param)
#                     retString = retString + before + 'parameters[\'' + param + '\'].value'
            
#                     curString = after

#             else:
#                 self.raiseError("Odd number of ' detected.")
#                 return ('', []) # only one ' detected, hold evaluation
        
#         retString =  retString + curString

#         return (self.findX(retString), params)

#     def findX(self,string):
#         while 'X' in string:
#             before = string.partition('X')[0]
#             after = string.partition('X')[-1]
#             string = before + 'dataSet[0]' + after
#         else:
#             return string
