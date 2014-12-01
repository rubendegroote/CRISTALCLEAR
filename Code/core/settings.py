#!/usr/bin/python

"""

kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch

SessionSettings

Stores the settings for a given capture session.


"""
from collections import OrderedDict

class SessionSettings(dict):

    def __init__(self,path):

        self.path = path

        self.debugMode = False

        self.counterChannel = "/Dev1/ctr1" # corresponds to PFI3
        self.aoChannel = "/Dev1/ao0"
        self.aiChannel = "/Dev1/ai1,/Dev1/ai2"
        self.noOfAi = self.aiChannel.count(',') + 1
        self.clockChannel = "/Dev1/PFI1"
        self.timePerStep = 1
        self.laser = 'CW Laser Voltage Scan'

        self.cristalMode = True
        self.clearMode = True

        self.logFile = ''
        self.zigZag = False
        self.dataFormat = dict()

    def resetDefaults(self):
        
        self.debugMode = False

        self.counterChannel = "/Dev1/ctr1" # corresponds to PFI3
        self.aoChannel = "/Dev1/ao0"
        self.aiChannel = "/Dev1/ai1,/Dev1/ai2"
        self.noOfAi = self.aiChannel.count(',') + 1
        self.clockChannel = "/Dev1/PFI1"
        self.timePerStep = 1
        self.laser = 'CW Laser Voltage Scan'

        self.zigZag = False

    def setSettingsFromDict(self,settingsDict):

        try:
            self.counterChannel = settingsDict['counterChannel']
            self.aoChannel = settingsDict['aoChannel']
            self.aiChannel = settingsDict['aiChannel']
            self.noOfAi = self.aiChannel.count(',') + 1
            self.clockChannel = settingsDict['clockChannel']
            self.timePerStep = settingsDict['timePerStep']
            self.laser = settingsDict['laser']

            self.zigZag = settingsDict['zigZag']

        except KeyError:
            pass
        self.sanitise()


    def sanitise(self):
        """ 
        Makes sure the ints are ints and
        the strings are strings, as reading from
        file normally makes everything a string
        """
        try:
            self.counterChannel = str(self.counterChannel)
            self.aoChannel = str(self.aoChannel)
            self.aiChannel = str(self.aiChannel)
            self.noOfAi = self.aiChannel.count(',') + 1
            self.clockChannel = str(self.clockChannel)
            self.timePerStep = int(self.timePerStep)
            self.laser = str(self.laser)

            self.zigZag = self.zigZag
        except ValueError:
            pass

    def getSettingsOrderedDict(self):

        retDict = OrderedDict()

        retDict['counterChannel'] = self.counterChannel
        retDict['aoChannel'] = self.aoChannel
        retDict['aiChannel'] = self.aiChannel
        retDict['clockChannel'] = self.clockChannel
        retDict['timePerStep'] = self.timePerStep
        retDict['laser'] = self.laser

        retDict['zigZag'] = self.zigZag
        
        return retDict
