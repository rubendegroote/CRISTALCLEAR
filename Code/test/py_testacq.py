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
import sys

from ctypes import *
from pylab import *

all_data = None
data_points = 0

"""
Function called when data is received.
'length' is the number of measurments per trigger
"""
def data_callback(data, length):
    global all_data
    global data_points
    data_array = np.fromiter(data, dtype=np.float64, count=length)
    all_data = np.hstack([all_data, data_array])
    data_points += length

"""
Plot all data captured
"""
def plot_data():
    global data_points
    X = np.arange( data_points)
    plot(X, all_data)
    show()

if __name__ == "__main__":
    # initialise data
    all_data = np.zeros([1,]) #zeros((,), dtype=np.float64)

    # import 2 required shared libraries
    ctypes.CDLL(ctypes.util.find_library("lvrtdark"), 
                mode=ctypes.RTLD_GLOBAL)
    ctypes.CDLL(ctypes.util.find_library("nidaqmxbase"),
                mode=ctypes.RTLD_GLOBAL)

    # import our library
    daqtriggerbase = ctypes.CDLL("libcdaq.so", 
                                 mode=ctypes.RTLD_GLOBAL)

    # set all functions to void
    daqtriggerbase.setParameters.restype = None
    daqtriggerbase.printAllInfo.restype = None
    daqtriggerbase.acquire.restype = None

    # set up user settings
    channel = "/Dev1/ctr1" # virtual counter channel
    triggerSource = "/Dev1/PFI0"
    report = c_bool(False)
    
    # set parameters
    daqtriggerbase.setParameters(channel, sampleRate,
                                 triggerSource, noTriggers,
                                 report)

    # check parameters set correctly
    daqtriggerbase.printAllInfo()

    # initialise callback function
    CB_CALLBACK_TYPE = CFUNCTYPE(None, POINTER(c_double), c_uint)
    cb_func = CB_CALLBACK_TYPE(data_callback)

    
    
    # acquire data
    daqtriggerbase.acquire(cb_func)

    # trim the initial 0 from the start of all_data
    all_data = np.trim_zeros(all_data, 'f')

    # plot measured data
    #plot_data()
