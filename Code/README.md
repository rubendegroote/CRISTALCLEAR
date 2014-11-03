### Package structure

* `core` provides the classes for data handling, file handling, and managing each capture session (including settings)
* `daq` physically interfaces the card, and only asks for a callback function to report data to `core.DataManager`
* `gui` provides the user interface using wxPython
* `test` is for all the code written but not used, which might come in handy one day