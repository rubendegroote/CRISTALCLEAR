from __future__ import division
import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
import numpy as np
from lmfit import *
import time
import sys
from copy import deepcopy
from string import replace
import re


class mySlider(QtGui.QWidget):
    def __init__(self,name):
        super(mySlider, self).__init__()

        self.layout = QtGui.QGridLayout(self)

        self.setMinimumWidth(300)

        self.varyCheck = QtGui.QCheckBox('')
        self.varyCheck.setChecked(True)
        self.layout.addWidget(self.varyCheck,0,0)

        self.name = QtGui.QLabel(name)
        self.layout.addWidget(self.name,0,1)
        self.name.setMinimumWidth(75)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.slider = QtGui.QSlider(orientation=QtCore.Qt.Horizontal)
        self.slider.setMinimumHeight(12)
        self.slider.setStyleSheet("""QSlider::groove:horizontal {    
                                border: 1px solid #bbb;
                                background: white;
                                height: 10px;
                                border-radius: 4px;
                                }

                                QSlider::handle:horizontal {
                                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                    stop:0 #eee, stop:1 #ccc);
                                border: 1px solid #777;
                                width: 50px;
                                height: 10px;
                                margin-top: -2px;
                                margin-bottom: -2px;
                                border-radius: 4px;
                                }""")

        self.layout.addWidget(self.slider,0,3)

        self.curLabel = QtGui.QLabel('test', parent = self.slider)
        self.curLabel.setMinimumWidth(50)
        self.curLabel.setMaximumWidth(50)
        self.curLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.slider.valueChanged.connect(self.updateLabel)

        self.minBox = QtGui.QLineEdit('0')
        self.layout.addWidget(self.minBox,0,2)
        self.minBox.setMaximumWidth(50)

        self.maxBox = QtGui.QLineEdit('10')
        self.layout.addWidget(self.maxBox,0,4)
        self.maxBox.setMaximumWidth(50)

        self.minBox.editingFinished.connect(self.updateSlider)
        self.maxBox.editingFinished.connect(self.updateSlider)

        self.updateSlider()

    def updateLabel(self):
        v = self.getCurrentValue()

        self.curLabel.setText(str(v))

        xpos = (v*1000-self.slider.minimum())/(self.slider.maximum()-self.slider.minimum())\
                        *(self.slider.size().width()-50)

        self.curLabel.move(xpos,2)

    def updateSlider(self):
        minval = self.getMin()
        maxVal = self.getMax()

        self.slider.setMinimum(int(minval*1000))
        self.slider.setMaximum(int(maxVal*1000))

        self.updateLabel()

    def getCurrentValue(self):
        return float(self.slider.value())/1000

    def getMin(self):
        return float(self.minBox.text())

    def getMax(self):
        return float(self.maxBox.text())

    def setCurrentValue(self,val):
        self.slider.setValue(int(1000*val))

    def getVaryCheck(self):
        return self.varyCheck.checkState()

class ModelPanel(QtGui.QWidget):
    updateRequested = QtCore.Signal(object)
    forceUpdate = QtCore.Signal(object)
    def __init__(self,dataSets):
        super(ModelPanel,self).__init__()

        self.sliders = {}
        self.pDict = {}
        self.dataCheckBoxes = {}
        self.usrDefFunc = {}

        self.setMinimumWidth(350)

        self.layout = QtGui.QGridLayout(self)

        self.sliderLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.sliderLayout,2,0,1,3)

        self.dataLayout = QtGui.QGridLayout()
        self.layout.addLayout(self.dataLayout,4,0,1,3)\

        self.dataSets = dataSets

        for i,dataSet in self.dataSets.iteritems():
            self.dataCheckBoxes[i] = QtGui.QCheckBox('Fit dataset '+ str(i))
            self.dataCheckBoxes[i].stateChanged.connect(self.emitForceUpdate)
            self.dataCheckBoxes[i].setChecked(True)
            self.dataLayout.addWidget(self.dataCheckBoxes[i],i,0)

            ps = Parameters()
            self.pDict[i] = ps
            
        self.fitButton = QtGui.QPushButton('Fit')
        self.setMaximumWidth(100)
        self.fitButton.clicked.connect(self.fit)
        self.layout.addWidget(self.fitButton,5,0)

        self.usrDefFunc = {}
        self.fitDef = FitFunctionDefiner('\'constant\'')
        self.layout.addWidget(self.fitDef,0,0,1,3)
        self.fitDef.newFitFunction.connect(self.defineFitFunction)

        self.layout.setRowStretch(3,1)

        self.fitDef.confirm()

    def addSlider(self,name = None):
        if not name == None:
            for ps in self.pDict.itervalues():
                try:
                    if not name in self.sliders:
                        self.sliders[name] = mySlider(name)
                        self.sliderLayout.addWidget(self.sliders[name],len(self.sliders)+1,0)
                        self.sliders[name].updateLabel()

                        self.sliders[name].slider.valueChanged.connect(self.updateParameters)
                        self.sliders[name].slider.valueChanged.connect(self.emitUpdateRequested)
                        self.sliders[name].slider.sliderReleased.connect(self.emitForceUpdate)

                        break
        
                except:
                    pass #invalid name

        self.updateParameters()

    def removeSlider(self,name):
        for ps in self.pDict.itervalues():
            del(ps[name])
            if name in self.sliders:
                self.sliders[name].setParent(None)
                del(self.sliders[name])

        for i,slider in enumerate(self.sliders.itervalues()):
            self.sliderLayout.removeWidget(slider)
            self.sliderLayout.addWidget(slider,i+1,0)


    def updateParameters(self):
        for name, slider in self.sliders.iteritems():
            for ps in self.pDict.itervalues():

                val = slider.getCurrentValue()
                mi = slider.getMin()
                ma = slider.getMax()
                va = slider.getVaryCheck()==2

                ps.add(name, value = val,min = mi, max = ma,vary = va)

    def resizeEvent(self,event):
        super(ModelPanel, self).resizeEvent(event)

        for slider in self.sliders.itervalues():
            slider.updateLabel()

    def emitForceUpdate(self):
        self.forceUpdate.emit(True)

    def emitUpdateRequested(self):
        self.updateRequested.emit(True)

    def defineFitFunction(self, info):

        parameters, fitFunction = info

        for p in parameters:
            self.addSlider(name = p)

        for name in self.sliders.keys():
            if not name in parameters:
                self.removeSlider(name)

        self.fitFunction = fitFunction
        self.emitForceUpdate()

    def defineUserFunctions(self,functions):
        print functions.keys()
        self.usrDefFunc = functions
        self.fitDef.defineUserFunctions(functions)
        self.fitDef.confirm()

    def fit(self,dataSets):
        self.updateParameters()

        for key,dataSet in self.dataSets.iteritems():
            if self.dataCheckBoxes[key].checkState() == 2:

                results = minimize(self.residuals,self.pDict[key],args=(dataSet,self.usrDefFunc))

                report_fit(self.pDict[key])
                print results.redchi

        self.emitForceUpdate()
    
    def residuals(self,ps,dataSet,userdeff):
        return np.sqrt((np.square(dataSet[1] - self.fitFunction(userdeff,ps,dataSet))/np.square(dataSet[2])))

    def fitFunc(self,key,data):
        return self.fitFunction(self.usrDefFunc,self.pDict[key],data)


class FitFunctionDefiner(QtGui.QWidget):
    newFitFunction = QtCore.Signal(object)
    def __init__(self,text):
        super(FitFunctionDefiner,self).__init__()

        self.layout = QtGui.QGridLayout(self)

        self.usrDefFunc = {}

        label = QtGui.QLabel('Y(X) = ')
        self.layout.addWidget(label,0,0)

        self.funcEdit = QtGui.QTextEdit(text)
        self.funcEdit.textChanged.connect(self.confirm)
        self.funcEdit.setMaximumHeight(100)
        self.layout.addWidget(self.funcEdit,0,1,1,2)

        label = QtGui.QLabel('Errors:')
        self.layout.addWidget(label,1,0)

        self.errorEdit = QtGui.QTextEdit('--No Errors--')
        self.errorEdit.setReadOnly(True)
        self.errorEdit.setMaximumHeight(50)
        self.layout.addWidget(self.errorEdit,1,1,1,2)


        self.forbiddenList  = ['','X', 'Y', 'and', 'as', 'assert', 'break', 'class', 'continue',
                  'def', 'del', 'elif', 'else', 'except', 'exec',
                  'finally', 'for', 'from', 'global', 'if', 'import', 'in',
                  'is', 'lambda', 'not', 'or', 'pass', 'print', 'raise',
                  'return', 'try', 'while', 'with', 'True', 'False',
                  'None', 'eval', 'execfile', '__import__', '__package__'] 
                                                

        self.illegalX = ['*x', 'x*' '+x', 'x+', ' x', 'x ', 'x-', '-x', 'x/', '/x', '(x', 'x)']

        self.numpyFunctions = ['sin','costan','arccos','arcsin','arctan','hypot','arctan2','degrees','radians',
        'unwrap','deg2rad','rad2deg','sinh','cosh','tanh','arcsinh','arccosh','arctanh','around','round_','rint',
        'fix','floor','ceil','trunc','prod','sum','nansum','cumprod','cumsum','diff','ediff1d','gradient',
        'cross','trapz','exp','expm1','exp2','log','log10','log2','log1p','logaddexp','logaddexp2','i0','sinc',
        'signbit','copysign','frexp','ldexp','add','reciprocal','negative','multiply','divide','power','subtract',
        'true_divide','floor_divide','fmod','mod','modf','remainder','angle','real','imag','conj','convolve',
        'clip','sqrt','square','absolute','fabs','sign','maximum','minimum','fmax','fmin','nan_to_num',
        'real_if_close','interp']

    def defineUserFunctions(self,functions):
        self.usrDefFunc = functions

    def confirm(self):

        try:
            expression,params = self.translate(str(self.funcEdit.toPlainText()))
            expression = self.prepareString(expression)

            if not expression==None and not params==None and not expression == '':
                try:
                    self.fitFunction = eval('lambda usrDefFunc,parameters,dataSet :' + '(' + \
                        expression + ')*np.ones(len(dataSet[0]))')

                    self.errorEdit.setText('--No Errors--')

                    self.newFitFunction.emit((params,self.fitFunction))

                except Exception as ex:
                    self.raiseError(ex.__unicode__())
                    return


        except UnicodeEncodeError as ex:
            self.raiseError(ex.__unicode__())



    def raiseError(self,excString):
        self.errorEdit.setText(excString)

    def prepareString(self,string):

        if '=' in string:
            self.raiseError("Invalid expression: two = signs.")
            return 

        if '\n' in string or '\t' in string:
            self.raiseError("Invalid expression, no tabs or enters please :)")
            return

        if '^' in string:
            string = replace(string, '^','**')

        if any(word in string for word in self.illegalX):

            self.raiseError("Please use capitalized X instead of x for the x-axis variable.")
            return 

        for key in sorted(self.usrDefFunc.keys(),key = len, reverse = True):
            if key+'(' in string:
                string = replace(string, key+'(','usrDefFunc[\'' + key + '\'](')

        for word in self.numpyFunctions:
            if word in string and not word in self.usrDefFunc.iterkeys():
                string = replace(string, word,'np.' + word)

        return string


    def translate(self,string):

        if any(symbol in string for symbol in ['.',';','?','!',':','\\', 
                                                        '[',']','{','}']):
            self.raiseError("Expression annot contain punctuation marks")
            return ('', [])

        retString = ''
        params = []

        curString = string

        if not '\'' in curString:
            return (self.findX(curString), [])

        while '\'' in curString:

            before = curString.partition('\'')[0]
            after = curString.partition('\'')[-1].partition('\'')[-1]

            if curString.partition('\'')[-1].partition('\'')[1] == '\'':

                param = curString.partition('\'')[-1].partition('\'')[0]

                if param in self.forbiddenList:
                    self.raiseError("Invalid parameter name " + param)
                    return ('', [])
                elif ' ' in param:
                    self.raiseError("Parameter name cannot contain spaces")
                    return ('', [])         
                else:
                    params.append(param)
                    retString = retString + before + 'parameters[\'' + param + '\'].value'
            
                    curString = after

            else:
                self.raiseError("Odd number of ' detected.")
                return ('', []) # only one ' detected, hold evaluation
        
        retString =  retString + curString

        return (self.findX(retString), params)



    def findX(self,string):
        while 'X' in string:
            before = string.partition('X')[0]
            after = string.partition('X')[-1]
            string = before + 'dataSet[0]' + after
        else:
            return string




class AnalysisGuiTest(QtGui.QWidget):
    
    def __init__(self):
        super(AnalysisGuiTest, self).__init__()
        
        self.initUI()
        
    def initUI(self):      

        self.layout = QtGui.QGridLayout(self)
        
        self.graph = pg.PlotWidget()
        self.layout.addWidget(self.graph,0,0,100,100)
        self.previousPlotTime = time.time()
       
        self.usrDefFunc = {}

        funcTextWidget = QtGui.QWidget()
        layout = QtGui.QGridLayout(funcTextWidget)

        self.funcText = QtGui.QTextEdit()
        layout.addWidget(self.funcText, 0,0,1,10)
        self.funcText.setTabStopWidth(8)

        self.okButton = QtGui.QPushButton('Update functions')
        layout.addWidget(self.okButton, 1,9,1,1)
        self.okButton.clicked.connect(self.defineNewFunction)


        self.tabs = QtGui.QTabWidget()
        self.layout.addWidget(self.tabs,0,0,100,100)
        self.tabs.addTab(self.graph, 'Graph')
        self.tabs.addTab(funcTextWidget, 'Function definer')

        self.dataSets = {}

        x = np.linspace(0,250,250)
        y = np.random.standard_normal(250,)+\
        np.linspace(0,7,250) + np.random.rand(1)*5
        err = np.zeros(250) + 1

        self.dataSets[0] = [x,y,err]

        x = np.linspace(0,250,250)
        y = np.random.standard_normal(250,)+\
        np.linspace(0,5,250) - np.random.rand(1)*3
        err = np.zeros(250) + 1

        self.dataSets[1] = [x,y,err]

        
        self.modelPanels = {}
        self.modelTabs = QtGui.QTabWidget()
        self.modelTabs.setMinimumWidth(300)
        self.modelTabs.tabCloseRequested.connect(self.closeModelPanel)
        self.modelTabs.setTabsClosable(True)
        self.layout.addWidget(self.modelTabs, 0,101,100,10)

        self.addModelPanel(name = 'Model 1')

        self.addModelButton = QtGui.QPushButton('New')
        self.addModelButton.setMaximumWidth(40)
        self.addModelButton.clicked.connect(self.addModelPanel)
        self.layout.addWidget(self.addModelButton,0,110,1,1)

        self.setWindowTitle('Analysis')
        self.show()

        time.sleep(0.04)
        self.updateGraph()

    def defineNewFunction(self):

        try:
            self.usrDefFunc = {}
            text = str(self.funcText.toPlainText())
            code = 'import numpy as np\n' + text
            eval(compile(code, '<stdin>', 'exec'),self.usrDefFunc)

            for modelPanel in self.modelPanels.itervalues():
                modelPanel.defineUserFunctions(self.usrDefFunc)

            self.updateGraph()


        except: 
            pass


    def resizeEvent(self,event):
        super(AnalysisGuiTest, self).resizeEvent(event)
        for modelPanel in self.modelPanels.itervalues():
            modelPanel.resizeEvent(event)

    def liveUpdateGraph(self):
        if time.time() - self.previousPlotTime > 0.03:
            self.updateGraph()

    def updateGraph(self):

        self.graph.clear()
        self.previousPlotTime = time.time()
        for key,data in self.dataSets.iteritems():

            err = pg.ErrorBarItem(x=data[0],y=data[1],top=data[2],bottom=data[2],
                                        beam = data[0][1]-data[0][0],pen=(key,len(self.dataSets)))
            self.graph.addItem(err)

            try:
                for modelPanel in self.modelPanels.itervalues():
                    fit = modelPanel.fitFunc(data=data,key=key)
                    if modelPanel.dataCheckBoxes[key].checkState() == 2:
                        self.graph.plot(fit, clear=False,pen=(key,len(self.dataSets)))

            except Exception as ex:
                self.raiseModelPanelError(modelPanel, ex.__unicode__())

    def addModelPanel(self, name = None):
        if not name:
            name, ok = QtGui.QInputDialog.getText(self, 'Input Dialog', 
                'Enter Model Name')
        else:
            ok = True

        if ok:
            for naam in [self.modelTabs.tabText(i) for i in range(self.modelTabs.count())]:
                if name == naam:
                    name = name + '\''

            pos = self.modelTabs.count()
            self.modelPanels[pos] = ModelPanel(self.dataSets)
            self.modelPanels[pos].updateRequested.connect(self.liveUpdateGraph)
            self.modelPanels[pos].forceUpdate.connect(self.updateGraph)
            self.modelPanels[pos].defineUserFunctions(self.usrDefFunc)

            self.modelTabs.addTab(self.modelPanels[pos], name)

    def closeModelPanel(self,pos):
        self.modelPanels[pos].setParent(None)
        del self.modelPanels[pos]
        for i in range(pos+1,len(self.modelPanels)+1):
            self.modelPanels[i-1] = self.modelPanels[i]
            del self.modelPanels[i]


        self.updateGraph()
        
    def raiseModelPanelError(self,modelPanel,excString):
        modelPanel.fitDef.raiseError(excString)


def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = AnalysisGuiTest()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()