import pyqtgraph as pg
import pyqtgraph.functions as fn
from PyQt4 import QtCore,QtGui

# freqNames = ['A0','A1','B0','B1','FWHMG','FWHML','df']

class MySpinBox(QtGui.QWidget):
    parInfoChanged = QtCore.Signal(object)
    valueChanged = QtCore.Signal()
    def __init__(self,name,suffix = None):
        super(MySpinBox, self).__init__()

        self.suffix = suffix

        self.layout = QtGui.QGridLayout(self)

        self.varyCheck = QtGui.QCheckBox('')
        self.varyCheck.setChecked(True)
        self.varyCheck.stateChanged.connect(self.updateSpinBox)
        self.layout.addWidget(self.varyCheck,0,0)

        self.name = name
        self.nameLabel = QtGui.QLabel(name)
        self.layout.addWidget(self.nameLabel,0,1)
        self.nameLabel.setMinimumWidth(75)
        
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.minBox = FormattedSpinbox(value = 0, siPrefix = True, suffix = suffix, \
                    step = 0.01, dec = True,decimals = 8, minStep = 0)
        self.layout.addWidget(self.minBox,0,2)

        self.spinbox = FormattedSpinbox(siPrefix = True, suffix = suffix, \
                    step = 0.01, dec = True,decimals = 8, minStep = 0)
        self.spinbox.name = self.name
        self.layout.addWidget(self.spinbox,0,3)
        self.layout.setColumnStretch(3,1)

        if suffix == 'Hz':
            m = 10**10
        elif suffix == 'V':
            m = 10
        else:
            m = 10**(-9)

        self.maxBox = FormattedSpinbox(value = m, siPrefix = True, suffix = suffix, \
                    step = 0.01, dec = True,decimals = 8, minStep = 0)
        self.layout.addWidget(self.maxBox,0,4)

        self.minBox.valueChanged.connect(self.updateSpinBox)
        self.maxBox.valueChanged.connect(self.updateSpinBox)

        self.spinbox.sigValueChanged.connect(self.valueChanged.emit)

        self.updateSpinBox()

    def updateSpinBox(self):
        minval = self.getMin()
        maxVal = self.getMax()

        self.spinbox.setMinimum(minval)
        self.spinbox.setMaximum(maxVal)

        self.parInfoChanged.emit(self)

    def getCurrentValue(self):
        return float(self.spinbox.value())

    def getMin(self):
        return float(self.minBox.value())

    def getMax(self):
        return float(self.maxBox.value())

    def setCurrentValue(self,val):
        self.spinbox.setValue(float(val))

    def getVaryCheck(self):
        return self.varyCheck.checkState()

class FormattedSpinbox(pg.SpinBox):

    def updateText(self, prev=None):
        #print "Update text."
        self.skipValidate = True
        if self.opts['siPrefix']:
            if self.val == 0 and prev is not None:
                (s, p) = fn.siScale(prev)
                txt = "0.0 %s%s" % (p, self.opts['suffix'])
            else:
                txt = fn.siFormat(float(self.val), 
                    precision = self.opts['decimals'],suffix=self.opts['suffix'])
        else:
            txt = '%g%s' % (self.val , self.opts['suffix'])

        self.lineEdit().setText(txt)
        self.lastText = txt
        self.skipValidate = False
