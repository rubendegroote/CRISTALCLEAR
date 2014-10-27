from detect_peaks import detect_peaks
import numpy as np
import os
import pylab as pl
import time
from scipy.interpolate import InterpolatedUnivariateSpline

name = 'Capture 208'

print 'begin data reading...'

path = os.getcwd().split('CRISTALCLEAR')[0] + 'CRISTALCLEAR\\Data\\'
(_, _, filenames) = os.walk(path).next()

files = [f  for f in filenames if name + ' scan ' in f]

allData = []

for f in files:
    data = np.loadtxt(path+f, delimiter=';')
    allData.append(data)


dataDicts = [{'time':[],
         'volt':[],
         'freq':[],
         'ai0':[],
         'ai1':[],
         'ion':[],
         'thick':[],
         'thin':[],
         'power':[],
         'lw':[]} for scan in range(len(allData))]


minFreq = 10**50
maxFreq = 0
for scan,data in enumerate(allData):

    # print 'scan ' + str(scan+1) + ' of ' + str(len(allData))

    dataDicts[scan]['time'] = data.T[0]
    dataDicts[scan]['volt'] = data.T[1]
    dataDicts[scan]['freq'] = data.T[2]*3*10**4

    #bit clumsy from here on, but it works I guess
    for nr in xrange(2):
        dataDicts[scan]['ai'+str(nr)] = data.T[3+nr]

    dataDicts[scan]['ion'] = data.T[3+2]
    dataDicts[scan]['thick'] = data.T[4+2]
    dataDicts[scan]['thin'] = data.T[5+2]
    dataDicts[scan]['power'] = data.T[6+2]
    dataDicts[scan]['lw'] = data.T[7+2]
    minFreq = min(min(dataDicts[scan]['volt']),minFreq)
    maxFreq = max(max(dataDicts[scan]['volt']),minFreq)

print 'Data reading done...'

print 'Binning data...'

bins = np.arange(minFreq,maxFreq,0.02)
totY = np.zeros(len(bins)-1)
totErr = np.zeros(len(bins)-1)

for scan, data in enumerate(dataDicts):

    x = data['volt']
    y = data['ai0']

    bin_means = np.histogram(x, bins, weights=y)[0]
    errors = np.sqrt(bin_means+1)

    X = 0.5*(bins[:-1] + bins[1:])
    Y = bin_means
    Err = errors

    totY = totY + Y
    totErr = np.sqrt(totErr**2 + Err**2)

    # pl.errorbar(X,Y,Err)

    data['binnedX'] = X
    data['binnedY'] = Y
    data['binnedErr'] = Err



S = InterpolatedUnivariateSpline(X,Y)
x = np.linspace(minFreq,maxFreq,1000000)
y = S(x)


print detect_peaks(y,mpd = 200000, show = False)

start = time.clock()
for i in xrange(100):
    ind = detect_peaks(y,mpd = 200000, show=False)

print (time.clock() - start)/100