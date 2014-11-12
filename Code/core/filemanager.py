#!/usr/bin/python

"""
Manages file storage, retrieval and parsing

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch


"""

import numpy as np
from settings import SessionSettings
from PyQt4 import QtCore,QtGui

import os.path

class FileManager():
    """
    Manages all writing of files, both data and settings
    """
    def __init__(self, settings):
        
        self.settings = settings
        self.scanSaveIndices = []

        
    def updateSettings(self, settings):
        """
        Changes the current settings being
        written to file
        """
        self.settings = settings

    def constructHeader(self):
        """
        Constructs the header for the csv file given
        self.settings if firstScan = True
        else just add 'save'
        """
        header = []
     
        d = self.settings.__dict__

        for k in d:
            header.append(";".join((k,str(d[k]))))

        return "\n".join(header) + "\n"

    def saveData(self,name,allData):
        while len(self.scanSaveIndices) < len(allData):
            self.scanSaveIndices.append(0)

        for i,data in enumerate(allData):

            length = np.min([len(d) for d in data.values()])

            if not self.scanSaveIndices[i] == length:

                toSave = np.column_stack((sub[self.scanSaveIndices[i]:length] for sub in data.values()))
                self.scanSaveIndices[i] = length

                if i==0:
                    magnitude = 0
                else:
                    magnitude = int(np.log10(i))
                number = '0'*(6 - magnitude) + str(i)
                filename = name + ' scan ' + number

                self.writeCapture(filename,toSave)

    def writeCapture(self, name, data):
        """
        Saves the captures to the 3 files
        """
        # Make header only once at beginning
        h = self.constructHeader() 

        # integrated count
        path = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Data\\'
        f = file(path + name + ".data.csv", 'a')

        np.savetxt(f, data, delimiter=";",
                   header = h)

        f.close()


    def getSettings(self, fileName):
        """
        Loads settings from the first lines
        of the data file
        """
        s = SessionSettings() # template
        d = s.__dict__ # get all the fields needed

        f = open(fileName, 'r')

        for line in f:
            if line[0] is '#':
                a = line[2:].strip().split(",")
                if len(a) > 1 and a[0] in d:
                    d[a[0]] = a[1]

        s.sanitise()
        return s


    def readData(self,name):

        path = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Data\\'
        (_, _, filenames) = os.walk(path).next()

        files = [f  for f in filenames if name + ' scan ' in f]

        allData = []

        for f in files:
            data = np.loadtxt(path+f, delimiter=';')
            allData.append(data)

        return allData
