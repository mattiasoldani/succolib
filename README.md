# succolib

[![pypiProject](https://img.shields.io/pypi/v/succolib.svg)](https://pypi.org/project/succolib/) [![python](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)

This is **succolib**, a library of handy Python functions for High-Energy Physics beamtests data analysis. In particular, it has been developed with a focus on the event-by-event analysis of the data collected with the INSULAb detectors &mdash; see, for example, the experimental configurations described [here](http://cds.cern.ch/record/2672249), [here](https://drive.google.com/file/d/1w_P8LQVJ1eL3zyOfR4Vrj7hdDUFoZ81M/view) and [here](http://cds.cern.ch/record/1353904).

succolib provides several tools, mainly for
* **data input** and storage in pandas DataFrames &mdash; supported input formats are formatted text files (e.g. DAT files) and ROOT tree files;
* **data conditioning**, i.e. typical transformations applied to and calculations performed on the raw data &mdash; e.g. particle tracking data reconstruction;
* **statistical analysis**, e.g. common distributions in High-Energy Physics, given in a highly accessible form to facilitate data analysis, visualisation and fitting.

Install succolib, along with all its dependencies, via `pip install succolib`.

Dependencies:

[![numpy](https://img.shields.io/badge/numpy-grey.svg)](https://numpy.org/) [![pandas](https://img.shields.io/badge/pandas-grey.svg)](https://pandas.pydata.org/) [![tqdm](https://img.shields.io/badge/tqdm-grey.svg)](https://github.com/tqdm/tqdm) [![uproot](https://img.shields.io/badge/uproot-3-blue.svg)](https://github.com/scikit-hep/uproot)

Note: [ROOT](https://root.cern.ch/) itself is not required.

Found a bug? Or simply have any questions, comments or suggestions you'd like to talk about? Feel free to contact me at <mattiasoldani93@gmail.com>. And brace yourself, for the best is yet to come!

---

### Data input and handling

Functions are provided to open
* sets of equally formatted text files (e.g. DAT files), and
* sets of ROOT files containing equally structured [tree objects](https://root.cern.ch/doc/master/classTTree.html):

```python
asciiToDfMulti(
    nameFormat,
    fileIndex,
    asciiMap,
    fileIndexName = "iIndex",
    nLinesEv = 1,
    descFrac = {},
    mirrorMap = {},
    bVerbose = False,
    bProgress = False,
)
```
and
```python
rootToDfMulti(
    nameFormat,
    fileIndex,
    treeName,
    fileIndexName = "iIndex",
    descFrac = {},
    treeMap = {},
    mirrorMap = {},
    bVerbose = False,
    bProgress = False,
)
```
respectively. Here
* `nameFormat` is the global filename format (as string) &mdash; see below; 
* `fileIndex` is the list of the fileset IDs (as strings), i.e. the indexes that identify different filesets, to be opened &mdash; see below; 
* `fileIndexName` (optional) is the name given to the column added to the newly created DataFrame with the fileset IDs as strings &mdash; it has to be set to `""` in order to skip this addition; 
* `descFrac` (optional) is the fraction of events to be loaded per file &mdash; it is a dictionary with fileset IDs as keys and values between 0 and 1;
* `mirrorMap` (optional) is a dictionary with fileset IDs as keys and the corresponding lists of the DataFrame variables to be mirrored, i.e. *x* &rarr; *&ndash;x*, as values;
* `bVerbose` (optional) is a boolean that toggles the verbose (quiet) mode if set to `True` (`False`);
* `bProgress` (optional) is a boolean that enables (disables) the progressbar visualisation if set to `True` (`False`); it has lower priority than `bVerbose`, i.e. the progressbar is never visualised if `bVerbose = False`;
* `asciiMap` (`asciiToDfMulti` only) is the list of the names to be given to the file columns, from left to right &mdash; in case of multiple rows per event (see `nLinesEv`) names must fill the list from left to right for each row, from top to bottom;
* `nLinesEv` (optional &mdash; `asciiToDfMulti` only) is the number of text file lines associated to each event;
* `treeName` (`rootToDfMulti` only) is the name of the ROOT trees to be opened &mdash; same for all the ROOT files;
* `treeMap` (optional &mdash; `rootToDfMulti` only) is a dictionary used to replace the ROOT tree variable names with custom ones &mdash; set the custom (original) names as keys (values).

Both functions return a single [pandas DataFrame](https://pandas.pydata.org/pandas-docs/stable/reference/frame.html) and the elapsed time in seconds.

##### Filesets structure

Multiple filesets can be opened at a time, a fileset being a set of files coming from the same data taking run. In turn, each fileset can consist of multiple files. All the filenames must share the same format, differing only in one (optionally two) part(s): the part which unambiguously identifies the fileset, i.e. the fileset ID and, in case of multiple files per fileset, the part that differentiates the names of the single files. For example, the file list
```shell
run000000_spill00001.dat
run000000_spill00009.dat
run000000_spill00099.dat
run0001_spillFirst.dat
run0001_spillSecond.dat
runABC_spillIJK.dat
```
consists of 3 different filesets, whose IDs are "000000", "0001" and "ABC", which in turn comprise 3, 2 and 1 files respectively; all these name formats are valid.

`nameFormat` must specify the filename structure, with "XXXXXX" in place of the fileset IDs and "YYYYYY" in place of the single-file IDs. For each `fileIndex` entry, the corresponding whole fileset (i.e. all the files which share the same fileset ID, for every value of "YYYYYY")  is opened. For instance, setting
```python
nameFormat = "PATH/TO/FILES/runXXXXXX_spillYYYYYY.dat"
fileIndex = ["000000", "0001", "ABC"]
```
in the `asciiToDfMulti()` arguments will open the whole file list of the example above.

##### Miscellaneous

* Use the `dfReshape(df, map, bBrackets=True)` function to rename the variables in the already existing `df` DataFrame and, if `bBrackets` is set to `True` (as it is in `rootToDfMulti()`), to remove square brackets from all the DataFrame variable names. The `map` format is the same as `treeMap` in `rootToDfMulti()`. The updated `df` is returned.
* `dfMirror(df, map)` perform the transformation *x* &rarr; *&ndash;x* to the variables in the already existing `df` DataFrame whose names are listed in the `map` list. The updated `df` is returned.

---

### Basic particle tracking

Tools are provided to reconstruct the particle trajectories starting from the single tracking detectors data. Focus has been put on 2D tracking with 1D-sensitive detectors (e.g. silicon microstrip layers, drift tube chambers, plastic hodoscopes, etcetera) in fixed-target experiments. 

<p align="center">
    <img src="./readme_pics/succolib_tracking_scheme.png" alt="readme_pics/succolib_tracking_scheme.png" width="628" height="300">
</p>

In particular, let *z* be the hypothetical beam direction and *x* be the transverse coordinate measured by the tracking modules series (as depicted in the figure above); given the linear trajectory determined by the pairs *(x0, z0)* and *(x1, z1)*, *x0* and *x1* corresponding to the (single) particle hit positions measured by an upstream (at *z0*) and a downstream (at *z1*) tracking module respectively:
* `zAngle(x1, z1, x0, z0)` returns the trajectory angle with respect to the beam direction in the *xz* plane, in radians.
* `zProj(x1, z1, x0, z0, z2)` returns the transverse position `x2` of the trajectory projected to the longitudinal position `z2`.

All the arguments can be either scalars or [numpy.array](https://numpy.org/doc/stable/reference/arrays.ndarray.html)/[pandas.Series](https://pandas.pydata.org/pandas-docs/stable/reference/series.html) objects. The units of measurement have to be consistent to each other.

---

### Some mathematical, statistical and visualisation tools

##### Probability distributions and physical quantities

Many frequently used functions are provided in a highly accessible form, such as:
* the Gaussian distribution `fGaus(x, A, u, sigma)`, defined as

<p align="center">
    <img src="https://render.githubusercontent.com/render/math?math=\large f(x) = A \exp \big[ {-(x - u)^2} \over {2 \sigma^2} \big].">
</p>

* The Moyal approximation of the Landau distribution, given in both the original and mirrored (*x*&ndash;mpv &rarr; mpv&ndash;*x*) versions &mdash; `fLandau(x, A, mpv, width)` and `fLandauMirror(x, A, mpv, width)` respectively; it is defined as

<p align="center">    
    <img src="https://render.githubusercontent.com/render/math?math=\large f(x) = A \exp \big\{ - {1 \over 2} \big[ {{x - \mathrm{mpv}} \over \mathrm{width}} %2B {\exp\big( {{x - \mathrm{mpv}} \over \mathrm{width}} \big)} \big] \big\}.">
</p>

<p align="center">
    <img src="./readme_pics/test_plots_statDistros.png" alt="readme_pics/test_plots_statDistros.png" width="500" height="375">
</p>

* The approximate half-width of the multiple Coulomb scattering (MCS) angular distribution &mdash; `fMCS(E, x, X0, z, bLogTerm)`, where `E` is the projectile energy in GeV, `x` is the thickness of the crossed medium, `X0` (optional, 1 by default) is the medium radiation length, `z` (optional, 1 by default) is the projectile charge in units of electron charge and `bLogTerm` (default, `True` by default) is a boolean determining whether to include the logarithmic term in the formula below. Note that, to compute the MCS contribution using the medium thickness in units of radiation length directly, it is sufficient to leave `X0 = 1`.

<p align="center">    
    <img src="https://render.githubusercontent.com/render/math?math=\large f(x) = {13.6 \mathrm{MeV}} \over E z \big( x \over {X_0} \big)^{1 \over 2} \big[1 %2B 0.038 \mathrm{ln}\big( x \over {X_0} \big) \big].">
</p>

##### Profile plot (compatible with [matplotlib](https://matplotlib.org/))

Inspired by the [ROOT TProfile object](https://root.cern.ch/doc/master/classTProfile.html), the function `hist2dToProfile(hist2d, errType)` computes the profile plot *y(x)* associated to the 2-dimensional histogram representing the *(x, y)* space. Its arguments are
* `hist2d`, the object returned by the [matplotlib.pyplot.hist2d](https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist2d.html) call that draws the histogram, and
* `errType`, a string for the selection of the error type to be associated to the output *y* values &mdash; &sigma;*(y)*; in particular
    * if `errType = "std"` the standard deviations of the distributions along *y* are used,
    * if `errType = "mean"` the errors on the distribution mean values are used,
    * in any other case, all the errors are set to zero.

Note: the error associated to single-entry *x*-slices is automatically set to zero. Moreover, in case of empty *x*-slices, no profile plot entry is created.

The function returns 3 numpy.array objects, corresponding to the *x*, *y* and &sigma;*(y)* arrays respectively.

<p align="center">
    <img src="./readme_pics/test_plots_profile.png" alt="readme_pics/test_plots_profile.png" width="500" height="375">
</p>

##### Ratio between 2-dimensional histograms

The function

```python
hist2dRatio(
    xNum,
    yNum,
    xDen, 
    yDen,
    bins = None,
    range = None,
    bPlot = True,
    ax = None,
    norm = None,
    cmap = None
)
```

computes the ratio between the 2-dimensional histograms created with the (array-like) input values
* `yNum` versus `xNum` &mdash; at the numerator, and
* `yDen` versus `xDen` &mdash; at the denominator,

and with the common parameters `bins` and `range` (optional) with the same format as in [matplotlib.pyplot.hist2d](https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist2d.html); note that, if such arguments are set to None, they are determined automatically from the denominator histogram. The function always returns a tuple with the same format of the one returned by matplotlib.pyplot.hist2d &mdash; elements 0 to 2, i.e. the bin value matrix, the abscissas bin array and the ordinates bin array respectively. In case of empty bins in the denominator histogram, all the corresponding zeros are replaced with NaNs (`numpy.nan`), which in turn correspond to NaNs in the returned ratio histogram.

The ratio histogram is drawn only if `bPlot = True` (optional). The plot is drawn into `ax` (a [matplotlib.axes.Axes](https://matplotlib.org/3.3.0/api/axes_api.html#matplotlib.axes.Axes) object, optional) if the latter is given, otherwise (`ax = None`, default) the current figure is exploited. Moreover, some (optional) graphical settings are available, with the same format and default values as in [matplotlib.pyplot.imshow](https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.imshow.html).

<p align="center">
    <img src="./readme_pics/test_plots_hist2dRatio.png" alt="readme_pics/test_plots_hist2dRatio.png" width="700" height="525">
</p>

##### Event-by-event Gaussian smearing

The function

```python
def eventSmear(
    dfIn,
    lsVar,
    lsSigma,
    nIter,
    bSmearSingleIter = False,
    bKeepOld = False,
    bVerbose = False
)
```

applies a Gaussian smearing to the variables of the `dfIn` DataFrame whose name are listed in the list-like object `lsVar` on an event-by-event basis. For each DataFrame row, a set of `nIter` (integer >= 1) different events is created, with randomly distributed values for the selected variables according to Gaussian distributions with the original event values as centres and corresponding error values, which must be defined in `dfIn` with the names listed in the list-like object `lsSigma`, as sigmas. For each element of `lsVar` there must be a corresponding element in `lsSigma`, so that the two elements of each variable-pair appear in the two objects in the same order; if `len(lsVar)` differs from `len(lsSigma)` or if any of the elements in the two objects does not correspond to a `dfIn` column, an empty dictionary is returned, otherwise a dictionary with the variable names (lists of smeared values) as keys (values) is returned &mdash; the length of each value of the latter being `nIter` times the number of rows in `dfIn`. The elapsed time in seconds is always returned as the second output.

In the limit case `nIter = 1`, the Gaussian smearing is only applied if `bSmearSingleIter = True` (optional, uneffective for other values of `nIter`). Furthermore, if `bKeepOld = True` (optional), the original values of the `lsVar` variables, as well as the input DataFrame index values of the original events, are also written into the output dictionary with the prefix "old_" to the names. 

For instance, some examples of the application of `eventSmear` to the DataFrame

```python
dfIn = pd.DataFrame(data={
    "A" : [1, 2, 5, 10, 20, 35],
    "B" : [1, 3, 5, 5, 3, 1],
    "eA" : [1, 1, 1, 0.8, 1.5, 3],  # errors to A values
    "eB" : [1, 1, 1, 0.8, 1.2, 1.4],  # errors to B values
})
```

are shown in the figure below.

<p align="center">
    <img src="./readme_pics/test_plots_eventSmear.png" alt="readme_pics/test_plots_eventSmearing.png" width="700" height="525">
</p>
