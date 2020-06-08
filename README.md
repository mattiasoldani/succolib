# succolib

[![](https://img.shields.io/pypi/v/succolib.svg)]() [![](https://img.shields.io/badge/python-3.0-blue.svg)]()

This is **succolib**, a library of handy Python functions for High-Energy Physics beamtests data analysis. In particular, it has been developed with a focus on the event-by-event analysis of the data collected with the INSULAb detectors &mdash; see, for example, the experimental configurations described [here](http://cds.cern.ch/record/2672249), [here](http://hdl.handle.net/10277/857) and [here](http://cds.cern.ch/record/1353904).

succolib provides several tools, mainly for
* **data input** and storage in pandas DataFrames &mdash; supported input formats are formatted text files (e.g. DAT files) and ROOT TTree files;
* **data conditioning**, i.e. typical transformations applied to and calculations performed on the raw data &mdash; e.g. particle tracking data reconstruction;
* **statistical analysis**, e.g. common distributions in High-Energy Physics, given in a highly accessible form to facilitate data visualisation and fitting.

Install succolib, along with all its dependencies, via `pip install python`.

Dependencies:
[![](https://img.shields.io/badge/numpy-blue.svg)](https://numpy.org/) [![](https://img.shields.io/badge/pandas-blue.svg)](https://pandas.pydata.org/) [![](https://img.shields.io/badge/tqdm-blue.svg)](https://github.com/tqdm/tqdm) [![](https://img.shields.io/badge/uproot-blue.svg)](https://github.com/scikit-hep/uproot)
Note: ROOT itself is not required.
