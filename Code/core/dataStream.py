import numpy as np
import time
import os

class StreamedData():
    """
    Stores data as function of time
    Has a maximum length saved up
    """
    def __init__(self, name, length,globalSession):

        self.name = name
        self.length = length
        self.globalSession = globalSession

        self.data = np.array([])
        self.times = np.array([])

        self.rate = 0.0

        self.teller = 0

        self.fileNo = 0

        self.saveFile = None


    def addData(self,times, data):
        if len(data) == 0:
            return
            
        if len(self.data) < self.length:
            self.data = np.append(self.data,np.array(data))
            self.times = np.append(self.times,np.array(times))
        else:
            self.data = np.roll(self.data,-len(data))
            self.data[-len(data):] = data
            
            self.times = np.roll(self.times,-len(times))
            self.times[-len(times):] = times

        if self.name in self.globalSession.streamsToSave:

            if self.saveFile == None:
                self.makeNewFile()

            self.teller = self.teller + 1
            self.totalSaved = self.totalSaved + 1

            if self.teller > 50:
                now = time.time()
                toSave = np.column_stack([self.times[-self.teller:],
                                            self.data[-self.teller:]])
                
                np.savetxt(self.saveFile,toSave, delimiter=";")
                
                self.teller = 0

                if self.totalSaved > 5*10**5:
                    self.makeNewFile()

        else:
            self.teller = 0

    def makeNewFile(self):
        self.totalSaved = 0

        self.saveFile = file(os.getcwd().split('Code')[0]+'data\\streams\\' + self.name + "Stream" + str(self.fileNo) +  ".csv", 'a')

        self.fileNo = self.fileNo + 1


    def getData(self):
        return self.data

    def getLatestValue(self):
        try:
            return self.data[-1]
        except:
            return None

    def setLengthWithTime(self,time=10,updateTime = 0.001):
        length = int(float(time) / updateTime)
        self.changeLength(length)


