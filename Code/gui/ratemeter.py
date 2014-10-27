import pyqtgraph as pg
from PyQt4 import QtCore,QtGui

class StatusIndicator(QtGui.QLabel):
    def __init__(self, globalSession):
        super(StatusIndicator,self).__init__('Event rate: 0.0 Hz')

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.setStyleSheet("StatusIndicator { color : green; font: bold 34px; }")
        self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        self.globalSession = globalSession

        self.text = 'Event rate: 0.0 Hz'

    def setRate(self):

        try:
            rate = self.globalSession.dataStreams['rate'].getLatestValue()
            text = 'Rate: '+str(round(rate,3)) + ' Hz'
        except:
            text = 'Rate: 0.0 Hz'
            
        if not text == self.text:
            self.setText(text)
            self.text = text



