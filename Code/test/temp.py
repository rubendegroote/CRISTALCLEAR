import numpy as np
import pylab as pl
import time



powers = [2.3,2.5,5.5,30,25,16,30,40,33,45,34,31]

rates = [10,20,60,700,400,250,900,500,900,700,800,980]

powers_2 = [45,30,27,23,15,6]
rates_2 = [800,1000,400,180,60,0]

powers_3 = [0.35,0.6,1.5,2.5,3.5,10,6,18,30,50,42,60,90,110,115]
rates_3 = [120,150,220,230,260,350,330,380,460,700,620,700,780,1040,1040]

pl.plot(powers,rates, 'ko')
pl.plot(powers_2,rates_2, 'rd')
# pl.plot(powers_3,rates_3, 'rd')
pl.show()

# x =  time.time() + np.linspace(0,1,10**2)
# # x = np.append(x,np.linspace(10.,20,0.5*10**4+1))
# # x = np.append(x,np.linspace(20.,30,10**4+1))

# y = 10+np.random.random(10**2)

# binsize = 0.1
# bins=np.arange(min(x), max(x)+0.5*binsize, binsize)


# now = time.time()
# method2 = 0.1*np.histogram(x, bins, weights=y)[0] #/
#              # np.histogram(x, bins)[0])
# print time.time()-now
# print bins

# pl.figure()
# pl.plot(x,y)
# pl.plot(bins[:-1]+binsize/2,method2,'o')

# pl.show()
