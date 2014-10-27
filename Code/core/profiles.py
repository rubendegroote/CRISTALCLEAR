import numpy as np


class Profile(object):

    """Baseclass for the lineprofiles.
    Do not use this, except as baseclass."""

    def __init__(self, fwhm=None, mu=None, amp=None):
        super(Profile, self).__init__()
        self._changeNorm = True
        self.fwhm = np.abs(fwhm) if fwhm is not None else 1.0
        self.mu = mu if mu is not None else 0.0
        self.amp = amp if amp is not None else 1.0

    def __call__(self, vals):
        vals = vals / self._normFactor
        return self.amp * vals


class Gaussian(Profile):

    """A callable normalized Gaussian profile.

    Parameters
    ----------
    fwhm : float, optional
        Full Width At Half Maximum, defaults to 1
    mu : float, optional
        Location of the center, defaults to 0
    amp : float, optional
        Amplitude of the profile, defaults to 1

    See Also
    --------
    Lorentzian, Irrational, HyperbolicSquared, PseudoVoigt, ExtendedVoigt

    Notes
    -----
    Formula taken from the MathWorld webpage
    http://mathworld.wolfram.com/GaussianFunction.html"""

    __method__ = """The formula used is

                            [               2]
                            [   1  (x - mu)  ]
        G(x; FWHM, mu) = exp[-  -  (------)  ]
                            [   2  (  s   )  ]
                           ---------------------
                                  _______
                               \ / 2 pi | s
                                V

    with

        FWHM = 2 sqrt(2 ln(2)) s"""

    def __init__(self, fwhm=None, mu=None, amp=None):
        super(Gaussian, self).__init__(fwhm=fwhm, mu=mu,
                                       amp=amp)

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        self._fwhm = value
        self.sigma = self.fwhm / (2 * np.sqrt(2 * np.log(2)))
        if self._changeNorm:
            self._normFactor = (self.sigma * np.sqrt(2 * np.pi)) ** (-1)

    def __call__(self, x):
        x = x - self.mu
        expPart = np.exp(-0.5 * (x / self.sigma) ** 2)
        normPart = self.sigma * np.sqrt(2 * np.pi)
        return super(Gaussian, self).__call__(expPart / normPart)


class Lorentzian(Profile):

    """A callable normalized Lorentzian profile.

    Parameters
    ----------
    fwhm : float, optional
        Full Width At Half Maximum, defaults to 1
    mu : float, optional
        Location of the center, defaults to 0
    amp : float, optional
        Amplitude of the profile, defaults to 1

    See Also
    --------
    Gaussian, Irrational, HyperbolicSquared, PseudoVoigt, ExtendedVoigt

    Notes
    -----
    Formula taken from the MathWorld webpage
    http://mathworld.wolfram.com/LorentzianFunction.html"""

    __method__ = """A callable Lorentzian profile.
    The formula used is

                                   w
        L(x; FWHM, m) = ---------------------
                           (         2    2)2
                        pi ( (x - mu)  + w )
                           (               )

    with w the HWHM."""

    def __init__(self, fwhm=None, mu=None, amp=None):
        super(Lorentzian, self).__init__(fwhm=fwhm, mu=mu,
                                         amp=amp)

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        self._fwhm = value
        self.gamma = 0.5 * self.fwhm
        if self._changeNorm:
            self._normFactor = 1.0 / (self.gamma * np.pi)

    def __call__(self, x):
        x = x - self.mu
        topPart = self.gamma
        bottomPart = (x ** 2 + self.gamma ** 2) * np.pi
        return super(Lorentzian, self).__call__(topPart / bottomPart)


class Irrational(Profile):

    """A callable normalized Irrational profile.

    Parameters
    ----------
    fwhm : float, optional
        Full Width At Half Maximum, defaults to 1
    mu : float, optional
        Location of the center, defaults to 0
    amp : float, optional
        Amplitude of the profile, defaults to 1

    See Also
    --------
    Gaussian, Lorentzian, HyperbolicSquared, PseudoVoigt, ExtendedVoigt

    Notes
    -----
    Formula taken from T. Ida et al., J. Appl. Cryst. 33, 1311 (2000), code
    inspired by the PhD thesis of Deyan Yordanov, 'From 27Mg to 33Mg:
    transition to the Island of Inversion' (KULeuven, 2007)."""

    __method__ =  """The used formula is

                               [              2]-3/2
        I(x; FWHM, mu) = (1/2g)[1 + ((x-mu)/g) ]
                               [               ]

    with

               ( 2/3   )1/2
        FWHM = (2   - 1)    g
               (       )"""

    def __init__(self, fwhm=None, mu=None, amp=None):
        super(Irrational, self).__init__(fwhm=fwhm, mu=mu,
                                         amp=amp)

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        self._fwhm = value
        self.gamma = self.fwhm / np.sqrt(np.power(2, 2.0 / 3) - 1)
        if self._changeNorm:
            self._normFactor = (1.0 ** (-1.5)) / (2 * self.gamma)

    def __call__(self, x):
        x = x - self.mu
        val = ((1.0 + (x / self.gamma) ** 2) ** (-1.5)) / (2 * self.gamma)
        return super(Irrational, self).__call__(val)


class HyperbolicSquared(Profile):

    """A callable normalized HyperbolicSquared profile.

    Parameters
    ----------
    fwhm : float, optional
        Full Width At Half Maximum, defaults to 1
    mu : float, optional
        Location of the center, defaults to 0
    amp : float, optional
        Amplitude of the profile, defaults to 1

    See Also
    --------
    Gaussian, Lorentzian, Irrational, PseudoVoigt, ExtendedVoigt

    Notes
    -----
    Formula taken from T. Ida et al., J. Appl. Cryst. 33, 1311 (2000), code
    inspired by the PhD thesis of Deyan Yordanov, 'From 27Mg to 33Mg:
    transition to the Island of Inversion' (KULeuven, 2007)."""

    __method__ = """The used formula is

                                    2
        H(x; FWHM, mu) = (1/2g) sech [(x-mu)/g]

    with

                [    1/2   ]
        FWHM = 2[ln(2   +1)]g
                [          ]"""

    def __init__(self, fwhm=None, mu=None, amp=None):
        super(HyperbolicSquared, self).__init__(fwhm=fwhm, mu=mu,
                                                amp=amp)

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        self._fwhm = value
        self.gamma = self.fwhm / (2 * np.log(np.sqrt(2) + 1))
        if self._changeNorm:
            self._normFactor = 1.0 / (2 * self.gamma)

    def __call__(self, x):
        x = x - self.mu
        coshPart = (1.0 / np.cosh(x / self.gamma)) ** 2
        simplePart = 2 * self.gamma
        return super(HyperbolicSquared, self).__call__(coshPart / simplePart)


class PseudoVoigt(Profile):

    """A callable normalized PseudoVoigt profile.

    Parameters
    ----------
    fwhm : float, optional
        Full Width At Half Maximum, defaults to 1
    mu : float, optional
        Location of the center, defaults to 0
    amp : float, optional
        Amplitude of the profile, defaults to 1

    See Also
    --------
    Gaussain, Lorentzian, Irrational, HyperbolicSquared, ExtendedVoigt"""

    __method__ = """The formula used is

        PV(x; FWHM, n, mu) = n Lorentzian(x; FWHM, mu) +
                             (1-n) Gaussian(x; FWHM, mu)

    Approach taken from the Wikipedia website
    http://en.wikipedia.org/wiki/Voigt_profile#Pseudo-Voigt_Approximation"""

    def __init__(self, eta=None, fwhm=None, mu=None,
                 amp=None):
        self.L = Lorentzian()
        self.G = Gaussian()
        self._n = np.abs(eta) if eta is not None else 0.5
        if self._n > 1:
            self._n = self._n - int(self._n)
        super(PseudoVoigt, self).__init__(fwhm=fwhm, mu=mu,
                                          amp=amp)

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        value = np.abs(value)
        self._fwhm = value
        self.L.fwhm = value
        self.G.fwhm = value
        self._normFactor = self.n * self.L._normFactor
        self._normFactor += (1.0 - self.n) * self.G._normFactor

    @property
    def n(self):
        return self._n

    @n.setter
    def n(self, value):
        value = np.abs(value)
        if value > 1:
            value = value - int(value)
        self._n = value
        if self._changeNorm:
            self._normFactor = self.n * self.L._normFactor
            self._normFactor += (1.0 - self.n) * self.G._normFactor

    def __call__(self, x):
        x = x - self.mu
        val = self.n * self.L(x) + (1.0 - self.n) * self.G(x)
        return super(PseudoVoigt, self).__call__(val)


class ExtendedVoigt(Profile):

    """A callable normalized ExtendedVoigt profile.

    Parameters
    ----------
    fwhm : float or list of floats, optional
        Full Width At Half Maximum, defaults to 1. If only one value is
        given, or a list of more than 2 values, the first value is used for
        both the Gaussian and Lorentzian parts. If a list of length 2 is
        given, the first value is used as the Gaussian width, the second as
        the Lorentzian width.
    mu : float, optional
        Location of the center, defaults to 0
    amp : float, optional
        Amplitude of the profile, defaults to 1

    See Also
    --------
    Gaussian, Lorentzian, Irrational, HyperbolicSquared, PseudoVoigt

    Notes
    -----
    The resulting FWHM differs from the supplied values. This is the
    only profile subclass that does this!

    Formula taken from T. Ida et al., J. Appl. Cryst. 33, 1311 (2000), code
    inspired by the PhD thesis of Deyan Yordanov, 'From 27Mg to 33Mg:
    transition to the Island of Inversion' (KULeuven, 2007)."""

    __method__ = """This class uses a weighted sum of the Gaussian,
    Lorentzian, Irrational and HyperbolicSquared profiles. More information
    can be found in the paper by T. Ida et al.,
    J. Appl. Cryst. 33, 1311 (2000)."""

    def __init__(self, fwhm=None, mu=None, amp=None):
        super(ExtendedVoigt, self).__init__(fwhm=fwhm, mu=mu,
                                            amp=amp)

    @property
    def fwhm(self):
        return self._fwhm

    @fwhm.setter
    def fwhm(self, value):
        self._fwhm = np.abs(value)
        try:
            if len(self._fwhm) is not 2:
                self.fwhm = [self._fwhm[0], self._fwhm[0]]
        except TypeError:
            self.fwhm = [self._fwhm, self._fwhm]
        self.setParams()

    def setParams(self):
        a = np.array(
            [-2.95553, 8.48252, -9.48291,
             4.74052, -1.24984, 0.15021, 0.66])
        b = np.array(
            [3.19974, -16.50453, 29.14158,
             -23.45651, 10.30003, -1.25693, -0.42179])
        c = np.array(
            [-17.80614, 57.92559, -73.61822,
             47.06071, -15.36331,  1.43021, 1.19913])
        d = np.array(
            [-1.26571, 4.05475, -4.55466,
             2.76622, -0.68688, -0.47745, 1.10186])
        f = np.array(
            [3.7029, -21.18862, 34.96491,
             -24.10743, 9.3155, -1.38927, -0.30165])
        g = np.array(
            [9.76947, -24.12407, 22.10544,
             -11.09215, 3.23653, -0.14107, 0.25437])
        h = np.array(
            [-10.02142, 32.83023, -39.71134,
             23.59717, -9.21815, 1.50429, 1.01579])

        self.fwhmG = self.fwhm[0]
        self.fwhmL = self.fwhm[1]
        s = sum(self.fwhm)
        self.rho = self.fwhmL / s
        self.wG = np.polyval(a, self.rho)
        self.wL = np.polyval(b, self.rho)
        self.wI = np.polyval(c, self.rho)
        self.wH = np.polyval(d, self.rho)
        self.nL = np.polyval(f, self.rho)
        self.nI = np.polyval(g, self.rho)
        self.nH = np.polyval(h, self.rho)

        self.wG = s * (1 - self.rho * self.wG)
        self.wL = s * (1 - (1 - self.rho) * self.wL)
        self.wI = s * self.wI
        self.wH = s * self.wH
        self.nL = self.rho * (1 + (1 - self.rho) * self.nL)
        self.nI = self.rho * (1 - self.rho) * self.nI
        self.nH = self.rho * (1 - self.rho) * self.nH

        self.G = Gaussian(fwhm=self.wG)
        self.L = Lorentzian(fwhm=self.wL)
        self.I = Irrational(fwhm=self.wI)
        self.H = HyperbolicSquared(fwhm=self.wH)

        self.fwhmV = (self.fwhmG ** 5 +
                      2.69269 * (self.fwhmG ** 4) * self.fwhmL +
                      2.42843 * (self.fwhmG ** 3) * (self.fwhmL ** 2) +
                      4.47163 * (self.fwhmG ** 2) * (self.fwhmL ** 3) +
                      0.07842 * self.fwhmG * (self.fwhmL ** 4) +
                      self.fwhmL ** 5
                      ) ** (1.0 / 5)
        if self._changeNorm:
            self._normFactor = 1

    def __call__(self, x):
        x = x - self.mu
        Gauss = (1 - self.nL - self.nI - self.nH) * self.G(x)
        Lorentz = self.nL * self.L(x)
        Irrat = self.nI * self.I(x)
        Hyper = self.nH * self.H(x)
        val = Gauss + Lorentz + Irrat + Hyper
        return super(ExtendedVoigt, self).__call__(val)
