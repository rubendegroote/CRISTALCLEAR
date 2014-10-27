rmdir /S /Q dist
rmdir /S /Q build
python .\setupWindows.py py2exe --includes sip
copy redist\auto.png dist
rmdir /S /Q dist\tcl
del dist\tk85.dll
del dist\tcl85.dll
pause
