import numpy as np
from core.spectrum import Spectrum


class MetaCapture():

    def __init__(self,cap = None):
        self.captures = []
        self.dataTypes = []
        self.x = []
        self.y = []

        self.xkey = ''
        self.ykey = ''
        self.freqMode = False
        self.mode = 'Combined'
        self.scansIncluded = []
        self.histMode = True
        self.binsize = 0.03

        self.spectra = []
        self.combSpectrum = Spectrum()


        if not cap == None:
            self.addCapture(cap)

    def addCapture(self, cap):
        if not cap in self.captures:
            self.captures.append(cap)

            self.dataTypes = list(set(self.dataTypes).union(cap.dataManager.dataTypes))

            try:
                self.getData()
            except:
                pass
            try:
                self.getSpectra()
            except:
                pass

            return True

    def setXY(self,xkey,ykey,y2key, freqMode,mode,scansIncluded,histMode,binsize):
        self.xkey = xkey
        self.ykey = ykey
        self.y2key = y2key
        self.freqMode = freqMode
        self.scansIncluded = scansIncluded
        if not mode == self.mode:
            self.mode = mode
            self.getSpectra()
        self.histMode = histMode
        self.binsize = binsize


    def getData(self):
        if self.xkey == '' or self.ykey == '' or self.y2key == '':
            return

        if self.mode ==  'Combined':
            self.x = self.getDataCombined(self.xkey)
            self.y = self.getDataCombined(self.ykey,self.y2key)
            self.errors = np.sqrt(self.y)

        elif self.mode ==  'Per Capture':
            self.x = self.getDataPerCapture(self.xkey)
            self.y = self.getDataPerCapture(self.ykey,self.y2key)
            self.errors = np.array([np.sqrt(suby) for suby in self.y])

        else:
            self.x = self.getDataPerScan(self.xkey)
            self.y = self.getDataPerScan(self.ykey,self.y2key)
            self.errors = np.array([np.sqrt(suby) for suby in self.y])

        if self.xkey == 'freq' and self.freqMode:
            self.x = self.x * 3 * 10**10
        elif self.xkey == 'freq':
            self.x = 1.0/self.x/100

        if self.xkey == 'lw':
            self.x = self.x * 1000
        if self.ykey == 'lw':
            self.y = self.y * 1000
        if self.xkey == 'power':
            self.x = self.x / 1000
        if self.ykey == 'power':
            self.y = self.y / 1000

        if self.histMode:
            self.newx = []
            self.newy = []
            self.newerrors = []
            for i,(x,y) in enumerate(zip(self.x,self.y)):
                length = min(len(x),len(y))
                if not length < 1:
                    x,y = x[:length],y[:length]
                    xhist,yhist,errors = self.calcHist(x,y,self.binsize)

                    self.newx.append(xhist)
                    self.newy.append(yhist)
                    self.newerrors.append(errors)

            self.x = np.array(self.newx)
            self.y = np.array(self.newy)
            self.errors = np.array(self.newerrors)

    def getSpectra(self):
        if self.scansIncluded == []:
            self.spectra = []
            return []

        if self.mode ==  'Combined':
            self.spectra = self.getSpectrumCombined()
        elif self.mode ==  'Per Capture':
            self.spectra = self.getSpectrumPerCapture()
        else:
            self.spectra = self.getSpectrumPerScan()

        return self.spectra

    def getDataPerScan(self,key,key2=None):
        # returns a list with all the scans of all the captures, so:
        # [[data cap 1 scan 1], [data cap 2 scan 2], ..., [data cap n scan k]]
        if key2 == None:
            return np.array([data[key] \
                for cap in self.captures \
                for scan,data in enumerate(cap.dataManager.allData) \
                if self.scansIncluded[cap.name][1][scan]])
        else:
            return np.array([data[key]/data[key2] \
                for cap in self.captures \
                for scan,data in enumerate(cap.dataManager.allData) \
                if self.scansIncluded[cap.name][1][scan]])

    def getDataPerCapture(self,key,key2=None):
        # returns the data per capture: list of lists, every sublist is 1D and contains all
        # the info of one capture
        if key2 == None:
            ret = []
            for cap in self.captures:
                capData = []
                for scan,data in enumerate(cap.dataManager.allData):
                    if self.scansIncluded[cap.name][1][scan]:
                        capData.append(data[key])
                ret.append(np.array([d for cd in capData for d in cd]))
            return np.array(ret)
        else:
            ret = []
            for cap in self.captures:
                capData = []
                for scan,data in enumerate(cap.dataManager.allData):
                    if self.scansIncluded[cap.name][1][scan]:
                        capData.append(data[key]/data[key2])
                ret.append(np.array([d for cd in capData for d in cd]))
            return np.array(ret)

    def getDataCombined(self,key,key2=None):
        # returna all the data in one big array
        # [d1, d2, ... d3]
        if key2 == None:
            return np.array([[d for cap in self.captures \
                for scan,data in enumerate(cap.dataManager.allData) for d in data[key] \
                if self.scansIncluded[cap.name][1][scan]]])
        else:
            return np.array([[d1/d2 for cap in self.captures \
                for scan,data in enumerate(cap.dataManager.allData) for d1,d2 in zip(data[key],data[key2]) \
                if self.scansIncluded[cap.name][1][scan]]])

    def getHeaderInfo(self):
        return [cap.name for cap in self.captures], [len(cap.dataManager.allData) for cap in self.captures]

    def getCurrentCapsHeaderInfo(self):
        if self.mode ==  'Combined':
            if any([l[0]==2 for l in self.scansIncluded.values()]):
                return ['C ' + ', '.join([cap.name.split(' ')[1] for cap in self.captures])]
            else:
                return []
        elif self.mode ==  'Per Capture':
            return ['C' + cap.name.split(' ')[1] for cap in self.captures if self.scansIncluded[cap.name][0]]
        else:
            ret = [['C' + cap.name.split(' ')[1] + ' s' + str(scan) \
                    for scan in range(len(cap.dataManager.allData)) if self.scansIncluded[cap.name][1][scan]] \
                    for cap in self.captures]

            ret = [item for sublist in ret for item in sublist]

            return ret
   
    def calcHist(self,x,y,binsize):

        binsize = binsize * 1.01

        if x[0] < x[-1]:
            bins = np.arange(min(x)-binsize/2, max(x) + binsize/2, binsize)
        else:
            start = round(min(x)/binsize) * binsize
            bins = np.arange(start-binsize/2, max(x) + binsize/2, binsize)

        bin_means,edges = np.histogram(x, bins, weights=y)

        errors = np.sqrt(bin_means+1)

        scale = np.histogram(x, bins)[0]

        bin_means = bin_means / scale
        errors = errors / scale

        return edges,bin_means,errors

    def getSpectrumCombined(self):
        if any([l[0]==2 for l in self.scansIncluded.values()]):
            return [self.combSpectrum]
        else:
            return []

    def getSpectrumPerCapture(self):
        return [cap.dataManager.spectrum for cap in self.captures if self.scansIncluded[cap.name][0]]

    def getSpectrumPerScan(self):
        return [cap.dataManager.spectra[scan] for cap in self.captures for scan,data in enumerate(cap.dataManager.allData)\
                    if self.scansIncluded[cap.name][1][scan]]




