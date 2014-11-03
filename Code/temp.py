import pylab as pl
import numpy as np
import time
import timeit

# x = [24.85,32.03,37.14,39.85,42.89,46.87,50.71,58.2]
# y = [12,14,16,17,18,28,32,39,44]


# pl.figure()
# pl.plot(x,'kd')
# pl.plot(10*np.sqrt(y),'ro')

# pl.show()


# volts = [2.0,1.9,1.8,1.7,1.6,1.5,1.4,1.3,1.2,1.1,1.0,0.9,0.8,0.7,0.5,0.3,0.1]
# angles = 2*(np.array([208,212,212,214,218,216,218,218,216,212,214,210,208,204,202,198,192])-190)
# powers = np.array([4.2,3.7,3.0,2.3,1.8,1.2,0.8,0.62,0.52,0.55,0.7,0.9,1.1,1.28,1.37,1.1,0.7])
# powers_high = np.array([7.7,8.3,8.9,9.25,9.4,9.4,9.3,9.1,8.5,7.9,7.3,6.4,5.6,4.6,2.9,1.6,0.7])

# pl.figure()
# pl.plot(volts, angles/5,label = 'PC Rotation (x0.2) ')
# # pl.plot(volts,powers, label = 'Power when OFF')
# pl.plot(volts,powers_high, label = 'Power when ON')
# pl.legend(loc = 2)

# pl.show()




# x = [69.88,75.40,87.72,80.28,81.88,83.32,85.08,88.12,88.92]
# y = [32,39,44]

# pl.figure()
# pl.plot(np.sort(x),'kd')
# pl.plot(12*np.sqrt(np.sort(y)),'ro')

# pl.show()

# filename = os.getcwd()

# data = np.loadtxt(filename)

# tof = dat.T[0]
# ions = data.T[1]


array = [0]
array = np.roll(array,-len([]))
print array