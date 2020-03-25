"""
succolib

notes (temporary!):
> z is the beam direction, x & y are orthogonal
"""

from math import atan2, sqrt
from numpy import exp, loadtxt
from glob import glob
from pandas import DataFrame
from progressbar import ProgressBar
from os import stat

""" openASCII ###################################################################################################### """
"""
openASCII opens all the ASCII files that have the same name format & creates a single Pandas dataframe

dfOut = openASCII(nameFormat, varMap, nLinesEv, descFrac) is the output dataframe
nameFormat is the name format common to all the ASCII files to be opened
varMap is the list of the variables contained in each column of the ASCII files
nLinesEv is the number of lines per single event
descFrac is the descaling fraction, i.e. fraction of (uniformly distributed along the run) events to be processed

default values:
    nLinesEv = 1
    descFrac = 1

all the ASCII files must have the same event format
formats in which there are multiple lines per event are supported -- nLinesEv>1:
in this case varMap must follow the columns-then-rows order
e.g. (0,0), ..., (0, NCol), (1,0), ..., (1, NCol), ..., (NRow, NCol)

empty ASCII files are automatically skipped

if descFrac = 0, descFrac is set equal to 10^(-100)

dependencies: glob.glob, numpy.loadtxt, pandas.DataFrame, os.stat
"""

def openASCII(nameFormat, varMap, nLinesEv = 1, descFrac = 1):
    nameList = sorted(glob(nameFormat))
    dfOut = DataFrame()
    pb = ProgressBar()
    if descFrac == 0:
        descFrac = 10e-100
    for iFile in pb(nameList):
        if stat(iFile).st_size > 0:
            if nLinesEv == 1:
                tableTemp = loadtxt(iFile, unpack=False, ndmin=2)
            else:
                wholeStr0 = open(iFile,'r').read()
                wholeStr0Spl = wholeStr0.splitlines()
                wholeStr = ""
                for i, iPart in enumerate(wholeStr0Spl):
                    if (i%nLinesEv==nLinesEv-1):
                        wholeStr += iPart + "\n"
                    else:
                        wholeStr += iPart + " "
                wholeStrSpl = wholeStr.splitlines()
                tableTemp = loadtxt(wholeStrSpl)
            dfTemp = DataFrame(tableTemp, columns=varMap)
            dfOut = dfOut.append(dfTemp[dfTemp.index % int(1 / descFrac) == 0], ignore_index=True, sort=False)
            del dfTemp
    return dfOut

""" fGaus ########################################################################################################## """
"""
fGaus is the Gaussian distribution

fGaus(x, A, u, sigma) is the Gaussian distribution
x is the distribution variable
A is the distribution amplitude
u is the distribution mean
sigma is the distribution sigma

function format: A * exp[ - ( (x-u)^2 / (2*(sigma)^2) ) ]

dependencies: numpy.exp
"""

def fGaus(x, A, u, sigma):
    expo = -(x-u)**2/(2*sigma**2)
    return A*exp(expo)

""" fLandau ######################################################################################################## """
"""
fLandau is the Landau's distribution

fLandau(x, A, mpv, width)
x is the distribution variable
A is the distribution amplitude
mpv is the distribution most probable value
width is the distribution width

function format: A * exp[ - (1/2) * ( (x-mpv)/width + exp(-(x-mpv)/width) ) ]

dependencies: numpy.exp
"""

def fLandau(x, A, mpv, width):
    expo0 = (x-mpv)/width
    expo1 = exp(-expo0)
    return A*exp(-0.5*(expo0+expo1))

""" fLandauMirror ################################################################################################## """
"""
fLandauMirror is the mirrored Landau's distribution, i.e. with inverted abscissas

fLandauMirror(x, A, mpv, width)
x is the distribution variable
A is the distribution amplitude
mpv is the distribution most probable value
width is the distribution width

function format: A * exp[ - (1/2) * ( (mpv-x)/width + exp(-(mpv-x)/width) ) ]

dependencies: numpy.exp
"""

def fLandauMirror(x, A, mpv, width):
    expo0 = (mpv-x)/width
    expo1 = exp(-expo0)
    return A*exp(-0.5*(expo0+expo1))

""" dz ############################################################################################################# """
"""
dz finds the difference between the positions along z of 2 setup elements (El1 & El2) this way: z(El2)-z(El1)

dz(zDictionary, zKey2, zKey1) is the z position difference (float)
zDictionary is the z positions dictionary (dict)
zKey1 (zKey2) is the dictionary key of El1 (El2)

the output sign will be + (-) if El2 is placed downstream (upstream) wrt. El1

dependencies: none
"""

def dz(zDictionary, zKey2, zKey1):
    return zDictionary[zKey2]-zDictionary[zKey1]

""" zProjScalar #################################################################################################### """
"""
zProjScalar finds the x coordinate coming from the projection of the line defined by 2 (x,z) points to some new z

x2 = zProjScalar(x1, z1, x0, z0, z2) is the output point x coordinate
x1 & x0 are the 2 input points x coordinates
z1 & z0 are the 2 input points z positions
z2 is the output point z position

dependencies: none
"""

def zProjScalar(x1, z1, x0, z0, z2):
    zRatio = (z2-z1)/(z1-z0)
    x2 = (1+zRatio)*x1 - (zRatio)*x0
    return x2

""" zAngleScalar ################################################################################################### """
"""
zAngleScalar finds the angle between the z axis and the vector identified by 2 (x,z) points

th = zAngleScalar(x1, z1, x0, z0) is the angle
x1 & x0 are the 2 input points x coordinates
z1 & z0 are the 2 input points z positions

dependencies: math.atan2
"""

def zAngleScalar(x1, z1, x0, z0):
    th = atan2(x1-x0, z1-z0)
    return th

""" zProjList ###################################################################################################### """
"""
zProjList applies zProjScalar to the coordinates in a list entry by entry; then creates an output list

x2 = zProjList(x1, z1, x0, z0, z2) is the output point x coordinates list
x1 & x0 are the 2 input points x coordinates list
z1 & z0 are the 2 input points z positions
z2 is the output point z position

dependencies: succolib.zProjScalar
"""

def zProjList(x1, z1, x0, z0, z2):
    x2 = []
    for i in range(len(x0)):
        temp = zProjScalar(x1[i], z1, x0[i], z0, z2)
        x2.append(temp)
    return x2

""" zAngleList ##################################################################################################### """
"""
zAngleList applies zAngleScalar to the coordinates in a list entry by entry; then creates an output list

th = zAngleScalar(x1, z1, x0, z0) is the angles list
x1 & x0 are the 2 input points x coordinates list
z1 & z0 are the 2 input points z positions

dependencies: succolib.zAngleScalar
"""

def zAngleList(x1, z1, x0, z0):
    th = []
    for i in range(len(x0)):
        temp = zAngleScalar(x1[i], z1, x0[i], z0)
        th.append(temp)
    return th

""" profPlotMeans ################################################################################################## """
"""
profPlotMeans produces a profile plot from a 2D histogram

xVal, yVal, yErr = profPlot(hist2DObj, errType) returns several objects:
 xVal is the abscissas list; each element is the centre of one of the histogram bins along x
 yVal is the ordinates list; each element is the weighted average of the bins along y at a certain x -- details below
 yErr is the ordinate errors list -- details below
hist2DObj is the tuple that is output by matplotlib.pyplot.hist2d
errtype is the error type: "std", "mean" or something else -- details below

default values: errType is different from any of the explicit options described below

xVal, yVal and yErr have the same length, which is lower than or equal to the number of bins along x of the histogram
the weighted average that gives each element of yVal is computed on the set of the centres of the histogram bins along y
at the x given by the corresponding entry in xVal; the bin content values are used as weights

empty bins along x are excluded and don't appear in the output lists

the yErr entries are:
 > the standard deviations of the population of the bins along x if errType = "std"
 > the errors on the yVal entries (standard deviation divided by square of population entries) if errType = "mean"
 > null if errType is anything else (default)

in case an element of yVal is computed on a single entry, the corresponding entry in yErr is set to 0

dependencies: math.sqrt
"""

def profPlot(hist2DObj, errType = ""):
    xVal = []
    yVal = []
    yErr = []
    for i in range(len(hist2DObj[1])-1):
        yNum = 0
        yErrNum = 0
        yDenom = 0
        for j in range(len(hist2DObj[2])-1):
            yNum += hist2DObj[0][i][j] * (hist2DObj[2][j] + (hist2DObj[2][j+1] - hist2DObj[2][j])/2)
            yDenom += hist2DObj[0][i][j]
        if yDenom != 0:
            for j in range(len(hist2DObj[2])-1):
                yErrNum += hist2DObj[0][i][j] * \
                           ((hist2DObj[2][j] + (hist2DObj[2][j + 1] - hist2DObj[2][j]) / 2) - yNum/yDenom) ** 2
            yErrDenom = yDenom - 1
            xVal.append(hist2DObj[1][i] + (hist2DObj[1][i+1] - hist2DObj[1][i])/2)
            yVal.append(yNum/yDenom)
            if yDenom > 1:
                if errType == "std":
                    yErr.append(sqrt(yErrNum/yErrDenom))
                elif errType == "mean":
                    yErr.append(sqrt(yErrNum/yErrDenom) / sqrt(yDenom))
                else:
                    yErr.append(0)
            else:
                yErr.append(0)
    return xVal, yVal, yErr
