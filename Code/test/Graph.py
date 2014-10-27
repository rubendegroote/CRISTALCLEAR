#!/usr/bin/python

"""
Main graphing facility

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch


"""

import wxmplot
import numpy as np

class Graph:
    """
    Main graphing of voltage / count plots
    """
    
    def __init__(self, data):
        self.X = data.T[0]
        self.Y = data.T[1]

        pframe = wxmplot.PlotFrame()
        pframe.plot(self.X, self.Y, title="Counts per voltage",
                    xlabel = "Voltage (V)", ylabel = "Counts",
                    marker='+', size=5, color='Black')
        pframe.Show()

