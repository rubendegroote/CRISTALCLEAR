import pyqtgraph as pg
from PyQt4 import QtCore,QtGui

class mySlider(QtGui.QWidget):
    def __init__(self,name):
        super(mySlider, self).__init__()

        self.scale = 10**3

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

        xpos = (v*self.scale-self.slider.minimum())/(self.slider.maximum()-self.slider.minimum())\
                        *(self.slider.size().width()-50)

        self.curLabel.move(xpos,2)

    def updateSlider(self):
        minval = self.getMin()
        maxVal = self.getMax()

        self.slider.setMinimum(int(minval*self.scale))
        self.slider.setMaximum(int(maxVal*self.scale))

        self.updateLabel()

    def getCurrentValue(self):
        return float(self.slider.value())/self.scale

    def getMin(self):
        return float(self.minBox.text())

    def getMax(self):
        return float(self.maxBox.text())

    def setCurrentValue(self,val):
        self.slider.setValue(int(self.scale*val))

    def getVaryCheck(self):
        return self.varyCheck.checkState()

    def setCurrentValue(self,val):
        self.slider.setValue(float(val)*self.scale)
