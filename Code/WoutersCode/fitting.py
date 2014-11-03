import numpy as np
import pylab as pl
from spectrum import Spectrum
import os
from lmfit import *

name = 'Capture 69'

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


    minFreq = min(min(dataDicts[scan]['freq']),minFreq)
    maxFreq = max(max(dataDicts[scan]['freq']),minFreq)

print 'Data reading done...'

print 'Binning data...'

bins = np.arange(minFreq,maxFreq,10)
totY = np.zeros(len(bins)-1)
totErr = np.zeros(len(bins)-1)

for scan, data in enumerate(dataDicts):

    x = data['freq']
    y = data['ion']

    bin_means = np.histogram(x, bins, weights=y)[0]
    errors = np.sqrt(bin_means+1)

    X = 0.5*(bins[:-1] + bins[1:])
    Y = bin_means
    Err = errors

    totY = totY + Y
    totErr = np.sqrt(totErr**2 + Err**2)

    pl.errorbar(X,Y,Err)

    data['binnedX'] = X
    data['binnedY'] = Y
    data['binnedErr'] = Err

pl.errorbar(X,totY,totErr)

pl.show()


print 'Moving on to the fitting...'

centralF = np.mean(X)
freq =np.linspace(X[0],X[-1],500)

for scan, data in enumerate(dataDicts):
	print 'fitting ' + str(scan+1) + ' of ' + str(len(dataDicts))
	model = Spectrum(1.5, [0.5,0.5], [231,27,0,0], centralF, shape="extendedvoigt", rAmp = False)
	model.fwhm = 25
	model.amp = 20
	model.df = -50

	results = model.FitToData(data['binnedX'],data['binnedY'],data['binnedErr'])
	# print fit_report(results.params)

	data['results'] = results.params

	# pl.figure()
	# pl.errorbar(data['binnedX'],data['binnedY'],data['binnedErr'], fmt = 'ko')
	# pl.plot(freq,model(freq))

	# pl.show()


for name,param in dataDicts[0]['results'].iteritems():
	if param.vary:
		
		y = [data['results'][name].value for data in dataDicts]
		yerr = [data['results'][name].stderr for data in dataDicts]
		w = [1/err**2 for err in yerr]

		av = np.average(y, weights = w)
		dev = np.sqrt(np.average((y-av)**2, weights=w)) / (1 - (sum([v**2 for v in w]))/(sum(w)**2))
		print name, av, dev
			
		pl.figure()
		pl.errorbar(x = range(len(dataDicts)), y = y, yerr = yerr, fmt = 'ko')
		pl.fill_between(range(len(dataDicts)), av+dev, av-dev, alpha = 0.3)
		pl.plot(range(len(dataDicts)),av*np.ones(len(dataDicts)))
		pl.title(name)

pl.show()

print 'fitting the summed spectrum...'


model = Spectrum(1.5, [0.5,0.5], [231,27.7,0,0], centralF, shape="extendedvoigt", rAmp = False)
model.fwhm = 25
model.amp = 60
model.df = -50

pl.figure()
pl.errorbar(X,totY,totErr, fmt = 'ko')
pl.plot(freq,model(freq))
pl.show()

results = model.FitToData(X,totY,totErr)
print results.redchi
print fit_report(results.params)
pl.figure()
pl.errorbar(X,totY,totErr, fmt = 'ko')
pl.plot(freq,model(freq))


pl.show()