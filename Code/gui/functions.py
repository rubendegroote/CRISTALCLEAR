import numpy as np
from Wigner import W3J,W6J
from lmfit import Parameters, Parameter

def gauss(x,x0,fwhm):
    s = fwhm / (2 * np.sqrt(2 * np.log(2)))
    return np.exp(-0.5 * ((x-x0) / s) ** 2) / (s * np.sqrt(2 * np.pi))

def lorentz(x,x0,fwhm):
    gamma = 0.5 * fwhm
    return gamma / ((x-x0) ** 2 + gamma ** 2) * np.pi

def voigt(x,x0,fwhm,eta):
    return eta * lorentz(x,x0,fwhm) + (1 - eta)*gauss(x,x0,fwhm)

def HFS(p,x):

    retval = np.zeros(len(x))

    for ratio in [key if 'ratio' in key for key in p.keys()]:

        F1 = float(key.split('ratio: ')[1].split(',')[0])
        F2 = float(key.split('ratio: ')[1].split(',')[1])

        split = CalculateFreq(I, J1,F0, p['A0'].value,p['B0'].value) - \
                CalculateFreq(I, J2,F1, p['A1'].value,p['B1'].value)
        retval = retval + p['scale'].value*ratio.value*pVoigt(x,p['centroid'].value + split,
                                    p['FWHM'].value,p['eta'].value)

    return retval + p['bkg'].value


def init_params(I,J1,J2):

    p = []

    p.append('centroid')

    p.append('A0')
    p.append('A1')

    p.append('B0')
    p.append('B1')

    p.append('FWHM')
    p.append('eta')

    p.append('bkg')

    p.append('scale')

    for i in range(NumberOfPossibleCouplings(I, J1)):
        F1 = I +  J1 - i
        for j in range(NumberOfPossibleCouplings(I, J2)):
            F2 = I +  J2 - j
            if allowedTransition(F0,F1):
                p.append('ratio: ' + str(F1) + ',' + str(F2))

    return p

def NumberOfPossibleCouplings(I1,I2):
    res=0

    if (I1 < I2):
        res = int(2*I1+1)
    else:
        res = int(2*I2+1)

    return res


def allowedTransition(F0,F1):
    return abs(F0-F1)<=1

def CalculateFreq(I,J,F, A, B):
            
    if (I==0 or J==0):
        C_F=0
        D_F=0
    elif (I==.5 or J==.5):
        C_F= F*(F+1) - I*(I+1) - J*(J+1)
        D_F= 0
    else:
        C_F = F*(F+1) - I*(I+1) - J*(J+1)
        D_F=(3*C_F*(C_F+1) - 4*I*(I+1)*J*(J+1))/(2*I*(2*I-1)*J*(2*J-1))
    corr = .5*A*C_F + .25*B*D_F

    return  -corr
