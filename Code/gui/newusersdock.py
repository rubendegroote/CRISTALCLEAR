import pyqtgraph as pg
from PyQt4 import QtCore,QtGui
from dock import Dock


class NewUsersDock(Dock):
    def __init__(self,name,size):
        Dock.__init__(self,name,size)

        self.orientation = 'horizontal'
        self.autoOrient = False

        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()

        self.scrollArea = QtGui.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        layout.addWidget(self.scrollArea)
        self.verticalLayoutScroll = QtGui.QGridLayout(self.scrollAreaWidgetContents)

        widget.setLayout(layout)
        self.addWidget(widget)


        text=QtGui.QLabel()
        text.setWordWrap(True)
        self.verticalLayoutScroll.addWidget(text)

        text.setText(
"Welcome to CRISTAL - the Code for Realtime Interactive Simultaneous laser Tuning, \
Acquisition and logging! This panel is meant to help you take your first CRISTAL \
steps.<br>\
CRISTAL aims to have a sleek, clutterless interface. All the UI \
elements you see can be moved around to a location of your choosing by clicking\
on the blue titlebar and dragging it to another spot. You can also drag a UI \
widget on top of another one; it will then be added as a Tab. They can also be \
resized, most of them can be made arbitrarily large or small. You can use this\
to hide a Ui element. By double-clicking on the blue titlebar, the UI element is \
popped out and will make it's own window. You can of course drag it back to \
somewhere else. Almost all of the UI elements have a settings panel on \
the right, which can be revealed by clicking on the vertically printed word \
\'settings\' and dragging it to the left. If settings are greyed out, it means \
CRISTAL does not want you to change them a this time; usually, thisis because a \
measurement is running at that time.<br>The standard user interface CRISTAL \
generates on start-up contains the following panels:\
<ul><li>A DAQ Control unit, which is used to start \
and stop new measurements, and changing the scan settings for these measurements.<br></li>\
<li>A set of graphs, displaying whatever you have them display using the dropdown boxes.\
 Graphs can be live. Live graphs only display data that is currently\
 being collected. The use of the non-live graphs will be explained down below.<br></li>\
<li>A Python interactive console, with Numpy and PyQtGraph imported. If you know \
some basic python, you can use this to do some quick calculations, plot some \
graphs, etc. Have fun.<br></li>\
<li> The logbook \
can contain entries, which can be shown or collapsed by clicking on the arrow in \
the top-left. Every time a new measurement is started, \
an entry is made. This entry will have a green color. Clicking and dragging the \
label which has the name and timestamp of the entry onto one of the graphs will \
plot the relevant data for that entry. You can only drag-n-drop onto non-live   \
graphs. A new entry can also be made at any point by clicking on the \'new entry\'\
button at the bottom. If you feel there is a very important parameter that should \
always be logged, you can \'Add an Entry Property\', it will always be asked for \
new entries after that point. The log \
can be filtered using the filtering widget in the Settings-panel on the right. \
Use this if you for example only want to see the green Capture logs, select only \
a certain isotope, filter out the scans you were present, etc. <br><br> \
Always try to keep the logbook up-to-date by filling in the details asked \
by the entry!<br></li></ul>\
The best way to learn how to use CRISTAL is by doing! Don't worry, you can't break\
anything. And if you do, shoot me an email!<br><br> --RPdG")
        


