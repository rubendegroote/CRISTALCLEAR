#!/usr/bin/python

"""
Testing daqtriggerbase library for multiple, 
trigger-driven acqusition.
kieran.renfrew.campbell@cern.ch
ruben.degroote@cern.ch
"""

import ctypes
import ctypes.util
import numpy as np
import os, sys



from ctypes import *
from pylab import *


from ..core.FileManager import FileManager 
from ..core.SessionSettings import SessionSettings


class ctr_test:
    def __init__(self):

        self.count = 0

        """
        let's set up some read parameters
        """
        self.settings = SessionSettings()
        self.settings.clockCyclesPerVoltage = 100
        self.settings.voltageMin = 0
        self.settings.voltageMax = 4
        self.settings.intervalsPerScan = 50
        self.settings.scans = 2
        self.settings.name = 'mycapture'

        self.voltsPerInterval = (self.settings.voltageMax - self.settings.voltageMin) \
            / float(self.settings.intervalsPerScan)

        print "Volts per interval: " + str(self.voltsPerInterval)

        self.dataArray = np.zeros( (self.settings.intervalsPerScan, ) )
        self.currentVoltage = self.settings.voltageMin
        self.currentScan = 0

        self.finished = False # tell C we're finished


    def data_callback(self, data):
        """
        Only called back every self.settings.clockCyclesPerVoltage steps
        """
        slot = self.count % self.settings.intervalsPerScan # which voltage position?
        self.dataArray[slot] += data # add count to correct voltage slot
        
        # could probably be done in more elegant way
        self.currentVoltage = self.voltsPerInterval * \
              (slot + 1)    

        self.count += 1

        if self.count == (self.settings.intervalsPerScan * self.settings.scans):
            # we're done measuring
            self.finished = True

            
    def py_get_voltage(self, cnt ):
        """
        Returns voltage to be set
        """
        return self.currentVoltage
    

    def isFinished(self, cnt):
        return self.finished

    """
    Plot all data captured
    """
    def plot_data(self):
        X = np.arange( self.settings.voltageMin, self.settings.voltageMax, 
                       self.voltsPerInterval)
        # plot(X, self.dataArray)
        # ylabel('Count')
        # xlabel('Voltage (V)')
        # show()
        f = FileManager(self.settings)
        f.writeCapture(X, self.dataArray, 
                       self.settings.name + '.csv')

    def main(self):

        
        print 'Importing libraries...'
        # import 2 required shared libraries
        ctypes.CDLL(ctypes.util.find_library("lvrtdark"), 
                    mode=ctypes.RTLD_GLOBAL)
        ctypes.CDLL(ctypes.util.find_library("nidaqmxbase"),
                    mode=ctypes.RTLD_GLOBAL)

        # import our library
        daqtriggerbase = ctypes.CDLL("libcdaq.so", 
                                     mode=ctypes.RTLD_GLOBAL)
        print "Done"


        # set all functions to void
        daqtriggerbase.setParameters.restype = None
        daqtriggerbase.printAllInfo.restype = None
        daqtriggerbase.acquire.restype = None

        # set up user settings
        readChannel = self.settings.counterChannel#virtual self.counter channel
        writeChannel = self.settings.aoChannel
        report_every = c_int(self.settings.clockCyclesPerVoltage)
    
        # set parameters
        daqtriggerbase.setParameters(readChannel, writeChannel,
                                     report_every)

        # check parameters set correctly
        daqtriggerbase.printAllInfo()

        # initialise callback function
        print "Initialising callback functions..."
        CB_CALLBACK_TYPE = CFUNCTYPE(None, c_uint)
        cb_func = CB_CALLBACK_TYPE(self.data_callback)
        
        CB_RETVOLTAGE_TYPE = CFUNCTYPE(c_double, c_uint)
        rv_func = CB_RETVOLTAGE_TYPE(self.py_get_voltage)
    
        CB_FINISHED_TYPE = CFUNCTYPE(c_bool, c_uint)
        is_done_func = CB_FINISHED_TYPE(self.isFinished)
        print "Done"

        # acquire data
        print "Calling acquire..."
        daqtriggerbase.acquire(cb_func, rv_func, is_done_func)
        print "Done"
        # print self.count


        print('Total callbacks: ' + str(self.count))

        print(self.dataArray)
        self.plot_data()

        f = FileManager(self.settings)
        s = f.getSettings(self.settings.name + '.csv')
        print str(s.__dict__)


if __name__ == "__main__":
    c = ctr_test()
    c.main()
