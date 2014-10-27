#!/usr/bin/python

"""

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

Main error for cristal stuff

"""


class Error(Exception):
    """
    The most basic of error classes
    for passing things to the gui
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
        
