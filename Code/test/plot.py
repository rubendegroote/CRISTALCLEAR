import pylab as pl
import numpy as np
import os
import lmfit

binsize = 10

directory = "C:\\CRISTALCLEAR\\DATA\\"

(_, _, filenames) = os.walk('C:\\CRISTALCLEAR\\data\\').next()

files = [f  for f in filenames if 'Capture 268' in f]



freq = np.array([])
counts = np.array([])

for f in files:
    data = np.loadtxt(directory + f, delimiter=';')
    freq = np.append(freq,data.T[2][1:])
    t = data.T[0]
    counts = np.append(counts,data.T[5][1:]/(np.diff(t)))


freq = freq * 3*10**4
freq = freq-freq[10]

bins = np.arange(min(freq)-3*binsize/2, max(freq) + binsize/2, binsize)
bin_means = (np.histogram(freq, bins, weights=counts)[0] /
                 np.histogram(freq, bins)[0])

bins = bins[~np.isnan(bin_means)]
bin_means = bin_means[~np.isnan(bin_means)]


pl.errorbar(bins,bin_means)

positions = [-234, -72,195]



p = lmfit.Parameters()
p.add_many(('width',80),('bkg',1),('scale1',0.2),('scale2',0.2),('scale3',0.6),('offset',550))




def fitfunc(p,x, y):

    fit = np.zeros(len(y))
    fit = fit + p['bkg'].value
    for i,pos in enumerate(positions):
        fit = fit + p['scale'+str(i+1)].value*np.exp(-(x - pos - p['offset'].value)**2/p['width'].value**2)

    return fit

def residual(p,x, y):

    fit = fitfunc(p,x,y)

    return y - fit

lmfit.minimize(residual, p, args=(freq, counts))
lmfit.report_fit(p)

pl.plot(bins, fitfunc(p,bins, bin_means), label = 'fit')

pl.xlabel('Relative frequency (MHz)')
pl.ylabel('Ion rate (Hz)')


pl.legend()
pl.show()

