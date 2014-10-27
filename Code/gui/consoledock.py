import pyqtgraph as pg
import numpy as np
from pyqtgraph.dockarea import Dock
import pyqtgraph.console

class ConsoleDock(Dock):
    def __init__(self,name,size):
        Dock.__init__(self,name,size)



        self.orientation = 'horizontal'
        self.autoOrient = False

        ## build an initial namespace for console commands to be executed in (this is optional;
        ## the user can always import these modules manually)
        namespace = {'pg': pg, 'np': np}

        ## initial text to display in the console
        text = """
        Numpy and pyqtgraph have already been imported 
        as 'np' and 'pg'. 
        """
        console = pyqtgraph.console.ConsoleWidget(namespace=namespace, text=text)
        console.setWindowTitle('Python Console')

        self.addWidget(console)