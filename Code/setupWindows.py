from distutils.core import setup
from glob import glob
import py2exe
import sys
sys.path.append(r'C:\Users\MyStuff\Dropbox\PhD\CRIS DAQ\CRISTALCLEAR\Code\redist\x86')
data_files = [("Microsoft.VC90.CRT", glob(r'C:\Users\MyStuff\Dropbox\PhD\CRIS DAQ\CRISTALCLEAR\Code\redist\x86\*.*'))]
setup(
    name="CRISTAL Log Viewer",
    version="1.0",
    author="Ruben de Groote",
    author_email="ruben.degroote@fys.kuleuven.be",
    data_files=data_files,
    windows=['LogViewer.py'] ,
    options={"py2exe": {"excludes":["Tkconstants", "Tkinter", "tcl"]}}
) 