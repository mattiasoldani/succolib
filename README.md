# succolib

This is **succolib**, a library of handy Python functions for High-Energy Physics beamtests data analysis. In particular, it has been developed with a focus on the event-by-event analysis of the data collected with the INSULAb detectors &mdash; see, for example, the experimental configurations described [here](http://cds.cern.ch/record/2672249), [here](http://hdl.handle.net/10277/857) and [here](http://cds.cern.ch/record/1353904).

succolib provides several tools, mainly for
* **data input** and storage in pandas DataFrames &mdash; supported input formats are formatted text files (e.g. DAT files) and ROOT TTree files;
* **data conditioning**, i.e. typical transformations applied to and calculations performed on the raw data &mdash; e.g. particle tracking data reconstruction;
* **statistical analysis**, e.g. common distributions in High-Energy Physics, given in a highly accessible form to facilitate data visualisation and fitting.
