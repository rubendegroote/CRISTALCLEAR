import os
import sys
from zipfile import ZipFile
from PyQt4 import QtCore,QtGui
def myListdir(pathString):
    components = os.path.normpath(pathString).split(os.sep)
    # go through the components one by one, until one of them is a zip file 
    for item in enumerate(components):
        index = item[0]
        component = item[1]
        (root, ext) = os.path.splitext(component)
        if ext == ".zip":
            results = []
            zipPath = os.sep.join(components[0:index+1])
            archivePath = components[index+1:]
            zipobj = ZipFile(zipPath, "r")
            contents = zipobj.namelist()
            zipobj.close()
            for name in contents:
                # components in zip archive paths are always separated by forward slash
                nameComponents = name.split("/")
                if nameComponents[0:-1] == archivePath:
                   results.append(nameComponents[-1].replace(".pyc", ".py"))
            return results
    else:
       return previousListDir(pathString)
    pass

previousListDir = os.listdir
os.listdir = myListdir
#-----------------------------------------------------------------------------
# look for bitmaps in current working directory
QtGui.QPixmap.oldinit = QtGui.QPixmap.__init__


def newinit(self, filename=''):
    # if file is not found inside the pyqtgraph package, look for it
    # in the current directory
    # print filename
    # if not os.path.exists(filename):
    #     (root, tail) = os.path.split(filename)
    #     filename = os.path.join(os.getcwd(), tail) 
    QtGui.QPixmap.oldinit(self, filename)
 
QtGui.QPixmap.__init__ = newinit
#-----------------------------------------------------------------------------
# we need to remove local library paths from Qt
QtGui.QApplication.oldinit = QtGui.QApplication.__init__

def newAppInit(self, *args):
    QtGui.QApplication.oldinit(self, *args)
    if hasattr(sys, "frozen"):
        # on Windows, this will not hurt because the path just won't be there
        print "Removing /opt/local/share/qt4/plugins from path"
        self.removeLibraryPath("/opt/local/share/qt4/plugins")
        print "Library paths:"
        for aPath in self.libraryPaths():
            print aPath
    else:
        print "Application running within Python interpreter."
 
QtGui.QApplication.__init__ = newAppInit