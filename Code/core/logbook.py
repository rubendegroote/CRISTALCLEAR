from collections import OrderedDict
import datetime
import time
"""
Notes to self: collections.Counter can be used to get quick tallies, e.g. count 
the number of scans for a certain mass or taken by a certain person.
"""


class LogBook(OrderedDict):
    def __init__(self):
        OrderedDict.__init__(self)
        self.prop = set()
        self.types = set()
        self.usrProp = {}
        self.tags = set()


    def addEntry(self, entry=None, key=None):
        if key==None:
            key = len(self)
            # add the user-defined properties to all new entries
            entry.properties = dict(entry.properties.items() + self.usrProp.items())
        else:
            for k,v in entry.properties.iteritems():
                # if there are user-defined properties in the loaded entries, let the log know
                if '#Custom' in k:
                    self.usrProp[k] = ''
                else:
                    self.prop.add(k)
                    
        name = entry.__class__.__name__
        if not name in self.types:
            self.types.add(name)

        self[key] = entry
        entry.key = key

        return key,entry

    def getEntriesAfter(self,time = None, entry = None):
        if not time == None:
            return OrderedDict([(k,v) for (k,v) in self.iteritems() \
                                        if v.properties['time']>time])
        elif not entry == None:
            return OrderedDict([(k,v) for (k,v) in self.iteritems() \
                    if v.properties['time']>entry.properties['time']])
        else:
            return None

    def getSimilarEntries(self, **kwargs):
        retDict = LogBook()

        for (k,v) in self.iteritems():
            add = True
            for (pkey,pval) in v.properties.iteritems():
                try:
                    if type(pval) == list:
                        if not set(kwargs[pkey]) <= set(pval):
                            add = False
                    else:    
                        if not kwargs[pkey] == pval:
                            add = False    
                except KeyError:
                    pass
            if add == True:
                retDict[k] = v

        return retDict

    def getCaptureEntries(self):
        retDict = LogBook()
        for (k,v) in self.iteritems():
            if v.__class__.__name__ == 'CaptureLogEntry':
                retDict[k] = v
        return retDict

    def addProperty(self,key,val=''):
        # adds a property to all of its future entries
        self.usrProp[key] = val

    def getWholeLogbook(self):
        text = ''
        for (k,v) in self.iteritems():
            text = text + '########\n'
            text = text + v.reportProperties() + '\n'

        return text


class Entry():
    def __init__(self,capture=None):
        self.properties = OrderedDict()
        self.properties['people'] = tuple()
        self.properties['comments'] = ''
        self.properties['capture'] = capture
        if not capture == None:
            self.properties['name'] = capture.name
        self.properties['time'] = datetime.datetime.now()
        self.properties['tags'] = set([])

    def setCapture(self,capture):
        self.properties['capture'] = capture
        self.properties['name'] = capture.name

    def getProperty(self,key):
        if key == 'time':# I don't need sub-second precision in this report
            return self.properties[key].strftime('%y/%m/%d %H:%M:%S')
        else:
            return str(self.properties[key])

    def getProperty(self,key):
        if key == 'time':# I don't need sub-second precision
            return self.properties[key].strftime('%y/%m/%d %H:%M:%S')
        elif key == 'capture':
            return self.properties[key].name
        elif (type(self.properties[key]) == tuple) or (type(self.properties[key]) == set):
            #only show the contents of the list
            return ', '.join(self.properties[key])
        else:
            return str(self.properties[key])

    def reportProperties(self):
        report = self.__class__.__name__ + '\tEntry key: ' + str(self.key) + '\n'
        for key in self.properties.iterkeys():
            if not key == 'capture':
                report = report + str(key) + ':\t' + self.getProperty(key) + '\n'
                if key == 'comments':
                    report = report + '#End of comment\n'

        return report
            

class GraphNoteEntry(Entry):
    def __init__(self, capture=None, volt = 0,graph = ''):
        Entry.__init__(self,capture)
        self.properties['graph'] = graph
        self.properties['volt'] = volt



class CaptureLogEntry(Entry):
    def __init__(self,**kwargs):

        isoArg = False

        if 'isotope' in kwargs:
            isotope = kwargs.pop('isotope')
            isoArg = True

        Entry.__init__(self, **kwargs)
        self.properties['stopTime'] = 0
        self.properties['isotope']  = ''

        if isoArg:
            self.properties['isotope'] = isotope

    def getProperty(self,key):

        if key == 'stopTime':
            try:
                return self.properties[key].strftime('%y/%m/%d %H:%M:%S')
            except AttributeError:
                return 'Scan not stopped yet'
        else:
            return Entry.getProperty(self,key)

    def addSettingsToProperties(self):

        # When the capture is started, the settings of the capture are also added to the logfile
        self.properties = OrderedDict(self.properties.items() + 
            self.properties['capture'].settings.getSettingsOrderedDict().items())



class ProblemEntry(Entry):
    def __init__(self,**kwargs):

        self.properties['problem'] = self.properties['comments']
        self.property['solution'] = ''