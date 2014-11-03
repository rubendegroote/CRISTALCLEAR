from spectrum import Spectrum
import numpy as np
import matplotlib.pyplot as plt
from lmfit import *


x = np.linspace(-500,500,200) + 10**8

structure = Spectrum(1.5,[0.5,0.5],[231,27,0,0],10**8+30,
                     shape = 'gaussian', rAmp = True)

structure.fwhm = 45
structure.amp = 50

structure2 = Spectrum(1.5,[0.5,0.5],[231,27,0,0],10**8,
                      shape = 'pseudovoigt', rAmp = False)

structure2.AB = [225.0,25.0,0,0]
structure2.fwhm = 35
structure2.df = 20
structure2.amp = 50

print 'starting fit'

y = structure(x)

y = abs((np.random.normal(y,np.sqrt(y+1))))


results = structure2.FitToSpectroscopicData(x,y)
print fit_report(results.params)

plt.errorbar(x, y, np.sqrt(y), fmt='ko')
plt.plot(x, structure2(x))
plt.show()

