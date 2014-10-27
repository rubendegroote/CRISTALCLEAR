# -*- coding: utf-8 -*-
"""
This example demonstrates a very basic use of flowcharts: filter data,
displaying both the input and output of the filter. The behavior of
he filter can be reprogrammed by the user.

Basic steps are:
  - create a flowchart and two plots
  - input noisy data to the flowchart
  - flowchart connects data to the first plot, where it is displayed
  - add a gaussian filter to lowpass the data, then display it in the second plot.
"""
from pyqtgraph.flowchart import Flowchart
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import pyqtgraph.metaarray as metaarray

app = QtGui.QApplication([])

## Create main window with grid layout
win = QtGui.QMainWindow()
win.setWindowTitle('pyqtgraph example: Flowchart')
cw = QtGui.QWidget()
win.setCentralWidget(cw)
layout = QtGui.QGridLayout()
cw.setLayout(layout)

## Create flowchart, define input/output terminals
terminals = {}
for i in range(1,10):
    key = 'dataIn' + str(i)
    val = {'io':'in'}
    terminals[key]=val

fc = Flowchart(terminals=terminals)
w = fc.widget()

## Add flowchart control panel to the main window
layout.addWidget(fc.widget(), 0, 0, 2, 1)

## Add two plot widgets
pw1 = pg.PlotWidget()
pw2 = pg.PlotWidget()
layout.addWidget(pw1, 0, 1)
layout.addWidget(pw2, 1, 1)

win.show()

## generate signal data to pass through the flowchart
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

## Feed data into the input terminal of the flowchart
fc.setInput(dataIn1=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn2=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn3=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn4=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn5=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn6=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn7=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn8=data)
data = np.random.normal(size=1000)
data[200:300] += 1
data += np.sin(np.linspace(0, 100, 1000))
data2 = -data
data = metaarray.MetaArray(data, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data))}, {}])
data2 = metaarray.MetaArray(data2, info=[{'name': 'Time', 'values': np.linspace(0, 1.0, len(data2))}, {}])

fc.setInput(dataIn9=data)


## populate the flowchart with a basic set of processing nodes. 
## (usually we let the user do this)
pw1Node = fc.createNode('PlotWidget', pos=(0, -150))
pw1Node.setPlot(pw1)

pw2Node = fc.createNode('PlotWidget', pos=(150, -150))
pw2Node.setPlot(pw2)


fc.removeNode(fc.outputNode)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
