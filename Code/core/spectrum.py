import numpy as np
import lmfit as lm
import profiles as p
from Wigner import W6J
import pylab as pl

class Spectrum(object):

    """Class for the construction of a HFS spectrum, consisting of different
    peaks described by a certain profile. The number of peaks and their
    positions is governed by the atomic HFS.

    Parameters
    ----------
    Atomic structure:
    I: float
        The nuclear spin.
    J: list of two floats
        The spins of the fine structure levels.
    AB: list of four floats
        The hyperfine structure constants A and B for ground- and excited fine level.
    f: float
        The energy of the excited fine level expressed in frequency space (Hz),
        for the reference isotope.
    df: float
        The energy of the excited fine level (Hz),
        for any isotope relative to the reference.

    Spectrum information:
    rAmp: Boolean
        If True, Fixes the relative peak intensities to the Racah intensities.
        Otherwise, gives them equal intensities and allows them to vary during fitting.
    shape : string
        Sets the transition shape. String is converted to lowercase. For
        possible values, see Spectrum.__shapes__.keys()
        Defaults to Gaussian if an incorrect value is supplied.

    Attributes
    ----------
    F: list of floats
        A list of the total angular momentum of the hyperfine levels
    energies: list of floats
        A list of the energies of the hyperfine levels
    mu : list of floats
        A list of the locations of the HFS peaks.
        
    fwhm : float
        Sets the FWHM for all the transtions.
    relAmp : list of floats
        Sets the relative intensities of the transitions.
    amp : float
        Sets the amplitude of the global spectrum."""

    __shapes__ = {'gaussian': p.Gaussian,
                  'lorentzian': p.Lorentzian,
                  'irrational': p.Irrational,
                  'hyperbolic': p.HyperbolicSquared,
                  'extendedvoigt': p.ExtendedVoigt,
                  'pseudovoigt': p.PseudoVoigt}

    def __init__(self, I=0., J=[0.,0.], AB=[0.,0.,0.,0.], f=0, units = 'hz', shape="ExtendedVoigt"):
        super(Spectrum, self).__init__()
        shape = shape.lower()
        if shape not in self.__shapes__:
            print """Given profile shape not yet supported.
Defaulting to Gaussian lineshape."""
            shape = 'gaussian'

        self._I = I
        self._J = J
        self._AB = AB
        self._f = f

        self._df = 0
        self._energies = []
        self._mu = []

        self.shape = shape
        self._relAmp = []
        self.parts = []
        self._fwhm = [1.0,1.0]
        self.amp = 1.0
        self.bkg = 0

        self.units = units

        self.calculateLevels()
        self.calculateInt()
        self.defineParameters()

    @property
    def I(self):
        return self._I

    @I.setter
    def I(self,value):
        self._I = value
        self.calculateLevels()
        self.calculateInt()
        self.defineParameters()

    @property
    def J(self):
        return self._J

    @J.setter
    def J(self,value):
        self._J = value
        self.calculateLevels()
        self.calculateInt()
        self.defineParameters()

    @property
    def AB(self):
        return self._AB

    @AB.setter
    def AB(self,value):
        self._AB = value
        self.calculateTransitions()

    @property
    def f(self):
        return self._f

    @f.setter
    def f(self,value):
        self._f = value
        self.calculateTransitions()

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self,value):
        self._df = value
        self.calculateTransitions()

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, value):
        self._amp = np.abs(value)
        for prof, val in zip(self.parts, self._relAmp):
            prof.amp = val * self.amp

    @property
    def relAmp(self):
        return self._relAmp

    @relAmp.setter
    def relAmp(self, value):
        if value == []:
            return
        if len(value) is len(self.parts):
            value = np.array(value, dtype='float')
            self._relAmp = value
            for prof, val in zip(self.parts, value):
                prof.amp = val * self.amp

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        self._fwhm = value
        for prof in self.parts:
            prof.fwhm = value

    @property
    def mu(self):
        return self._mu

    @mu.setter
    def mu(self, value):
        if len(value) is len(self.parts):
            self._mu = value
            for prof, val in zip(self.parts, value):
                prof.mu = val

    def calculateLevels(self):
        self._F = [np.arange(abs(self._I - self._J[0]), self._I + self._J[0]+1,1),
            np.arange(abs(self._I - self._J[1]), self._I + self._J[1]+1,1)]

        self.calculateTransitions()
        
    def calculateTransitions(self):
        
        self._energies = [[self.calculateEnergy(0, F) for F in self._F[0]],
            [self.calculateEnergy(1, F) for F in self._F[1]]]

        mu = []
        for i,F1 in enumerate(self._F[0]):
            for j,F2 in enumerate(self._F[1]):
                if abs(F2 - F1) <= 1:
                    mu.append(self._energies[1][j] - self._energies[0][i])

        if not len(self.parts) is len(mu):
            self.parts = tuple(
                self.__shapes__[self.shape]() for _ in range(len(mu)))
    
        self.mu = mu

    def calculateInt(self):
        ampl = []
        for i,F1 in enumerate(self._F[0]):
            for j,F2 in enumerate(self._F[1]):
                if abs(F2 - F1) <= 1:    
                    ampl.append(self.calculateRacah(self._J[0],self._J[1],F1,F2))
                    
        self.relAmp = ampl
    
    def calculateRacah(self,J1,J2,F1,F2):
        return (2*F1+1)*(2*F2+1)*W6J(J2, F2,self._I,F1,J1, 1.0)**2

    def calculateEnergy(self, level, F):
        I = self._I
        J = self._J[level]
        A = self._AB[level]
        B = self._AB[level+2]

        if level==0:
            f = 0
            df = 0
        else:
            f = self._f
            df = self._df
            
            
        if (I==0 or J==0):
            C_F=0
            D_F=0
        elif (I==.5 or J==.5):
            C_F= F*(F+1) - I*(I+1) - J*(J+1)
            D_F= 0
        else:
            C_F = F*(F+1) - I*(I+1) - J*(J+1)
            D_F=(3*C_F*(C_F+1) - \
                4*I*(I+1)*J*(J+1)) / (2*I*(2*I-1)*J*(2*J-1))

        return df + f + 0.5*A*C_F + 0.25*B*D_F

    def FitToBinnedData(self, x, y, yerr):
        valids = np.logical_not(np.isnan(y))

        X = 0.5*(x[:-1] + x[1:])
        X = X[valids]
        Y = y[valids]
        ERR = yerr[valids]

        self.FitToData(X,Y,ERR)

    def FitToSpectroscopicData(self, x, y):
        yerr = np.sqrt(y)
        yerr[np.isclose(yerr, 0.0)] = 1.0
        return self.FitToData(x, y, yerr)

    def FitToData(self, x, y, yerr):

        def Model(params):
            self.parToVar(params)
            return (y - self(x)) / yerr

        self.scaleParameters()

        if self.units == 'Hz':
            scale = 1.0 / 10**6
        elif self.units == 'm':
            scale = 10**9

        x = x*scale

        self.results = lm.minimize(Model, self.par)
        self.results = lm.minimize(Model, self.par)
        self.results = lm.minimize(Model, self.par)

        # self.plotFit(x,y,yerr)

        self.unscaleParameters()

        self.par = self.results.params


    def plotFit(self,x,y,yerr):

        # Quick matplotlib helper function to plot the results

        mean = np.mean(x)
        pl.errorbar(x-mean,y,yerr = yerr, \
            fmt='bo', markeredgecolor='b' ,markerfacecolor='white',\
            label = 'exp')
        x2 = np.linspace(min(x),max(x),5000)
        pl.plot(x2-mean,self(x2),'r')

        pl.show()


    def defineParameters(self):
        self.par = lm.Parameters()
        if self.shape not in ['extendedvoigt']:
            self.par.add('FWHM', value=self.fwhm, min=0)
            if self.shape in ['pseudovoigt']:
                self.par.add('eta', value=self.parts[0].n, min=0, max=1)
        else:
            self.par.add('FWHMG', value=self.fwhm[0], min=0)
            self.par.add('FWHML', value=self.fwhm[1], min=0)

        self.par.add('Amp', value=self.amp, min = 0)
        for i, prof in enumerate(self.parts):
            self.par.add('Amp_' + str(i), value=self._relAmp[i], min = 0)

        self.par.add('A0', value=self._AB[0])
        self.par.add('A1', value=self._AB[1])

        if self._I > 0.5 and self._J[0] > 0.5:
            self.par.add('B0', value=self._AB[2], vary = True)
        if self._I > 0.5 and self._J[1] > 0.5:
            self.par.add('B1', value=self._AB[3], vary = True)

        self.par.add('df', value = self._df)
    
        self.par.add('bkg', value=0.0)

    def parToVar(self,params):
        if self.shape not in ['extendedvoigt']:
           self.fwhm = params['FWHM'].value
           if self.shape in ['pseudovoigt']:
               for prof in self.parts:
                   prof.n = params['eta'].value
        else:
            for prof in self.parts:
                prof.fwhm = [params['FWHMG'].value, params['FWHML'].value]
 
        self.amp = params['Amp'].value
        for i, prof in enumerate(self.parts):
            prof.amp = params['Amp_' + str(i)].value * self.amp
        
        try:
            B0 = params['B0'].value
        except:
            B0 = 0
        try:
            B1 = params['B1'].value
        except:
            B1 = 0
        
        self.AB = [params['A0'].value,params['A1'].value,B0,B1]
        self.df = params['df'].value
        self.bkg = params['bkg'].value

    def scaleParameters(self):

        if self.units == 'Hz':
            scale = 1.0 / 10**6
        elif self.units == 'm':
            scale = 10**9

        self.f = self.f * scale

        for key,p in self.par.iteritems():
            if key in ['A0', 'B0', 'A1', 'B1', 'df', 'FWHM','FWHML','FWHMG']:
                p.value = p.value * scale
                try:
                    p.stderr = p.stderr * scale
                except:
                    pass
                p.min = p.min * scale
                p.max = p.max * scale

        self.parToVar(self.par)

    def unscaleParameters(self):
        if self.units == 'Hz':
            scale = 10**6
        elif self.units == 'm':
            scale = 1.0/10**9

        self.f = self.f * scale

        for key,p in self.par.iteritems():
            if key in ['A0', 'B0', 'A1', 'B1', 'df', 'FWHM','FWHML','FWHMG']:
                p.value = p.value * scale
                try:
                    p.stderr = p.stderr * scale
                except:
                    pass
                p.min = p.min * scale
                p.max = p.max * scale

        self.parToVar(self.par)

    def __call__(self, x):

        return self.bkg +  sum([prof(x) for prof in self.parts])


