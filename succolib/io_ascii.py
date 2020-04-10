from numpy import loadtxt
from glob import glob
from pandas import DataFrame
from progressbar import ProgressBar
from os import stat


########################################################################################################################
# asciiToDf ############################################################################################################
"""
asciiToDf opens all the ASCII files that have the same name format apart from one part & creates a single Pandas dataframe

df = asciiToDf(...) is the output dataframe
nameFormat is the name format common to all the ASCII files to be opened (with a YYYYYY in place of the changing part)
asciiMap is the list of the variables contained in each column of the ASCII files
nLinesEv is the number of lines per single event
descFrac is the descaling fraction, i.e. fraction of (uniformly distributed along the run) events to be processed
bVerbose is a boolean for the verbose (True) or quiet (False) mode

default values for the optional variables:
    nLinesEv = 1
    descFrac = 1
    bVerbose = False

all the ASCII files must have the same event format
formats in which there are multiple lines per event are supported -- nLinesEv>1:
in this case asciiMap must follow the columns-then-rows order
e.g. (0,0), ..., (0, NCol), (1,0), ..., (1, NCol), ..., (NRow, NCol)

empty ASCII files are automatically skipped

if descFrac = 0, descFrac is set equal to 10^(-12)

dependencies: glob.glob, pandas.DataFrame, progressbar.ProgressBar, os.stat, numpy.loadtxt
"""

def asciiToDf(nameFormat, asciiMap, nLinesEv = 1, descFrac = 1, bVerbose = False):
    names = sorted(glob(nameFormat.replace("YYYYYY", "*")))  # list of all the filenames of the current run
    df = DataFrame()
    descFrac = 10e-12 if descFrac == 0 else descFrac
    for iName in ProgressBar()(names) if bVerbose else names:
        if stat(iName).st_size > 0:
            if nLinesEv == 1:
                dataTableTemp = loadtxt(iName, unpack=False, ndmin=2)
            else:
                fileToString0 = open(iName,'r').read()
                fileToStringSplitted0 = fileToString0.splitlines()
                fileToString = ""
                for i, iLine in enumerate(fileToStringSplitted0):
                    if (i%nLinesEv==nLinesEv-1):
                        fileToString += iLine + "\n"
                    else:
                        fileToString += iLine + " "
                fileToStringSplitted = fileToString.splitlines()
                dataTableTemp = loadtxt(fileToStringSplitted)
            dfTemp = DataFrame(dataTableTemp, columns=asciiMap)
            df = df.append(dfTemp[dfTemp.index % int(1 / descFrac) == 0], ignore_index=True, sort=False)
    return df


########################################################################################################################
# asciiToDfMulti #######################################################################################################
"""
asciiToDfMulti opens all the ASCII files that have the same name format apart from two hierarchically different parts & creates a single Pandas dataframe

df = asciiToDfMulti(...) is the output dataframe
nameFormat is the name format common to all the ASCII files to be opened (with a XXXXXX/YYYYYY in place of the higher-/lower-priority changing part)
fileIndex is the list of string values the filename higher-priority changing part has to assume (all the lower-priority part values available are always taken)
asciiMap is the list of the variables contained in each column of the ASCII files
fileIndexName is the name of the newly created (if not already existing) dataframe column that contains the higher-priority changing part values -- if "", no new column is created
nLinesEv is the number of lines per single event
descFrac is the dictionary of descaling fractions, i.e. fraction of (uniformly distributed along the run) events to be processed -- one per fileIndex entry
bVerbose is a boolean for the verbose (True) or quiet (False) mode

default values for the optional variables:
    fileIndexName = "iIndex"
    nLinesEv = 1
    descFrac = {}
    bVerbose = False
    
note: descFrac can be not given at all -- in this case, 1 is taken for all the fileIndex values

relies on succolib.asciiToDf for each of the filename higher-priority changing part values

dependencies: pandas.DataFrame, succolib.asciiToDf
"""

def asciiToDfMulti(nameFormat, fileIndex, asciiMap, fileIndexName = "iIndex", nLinesEv = 1, descFrac = {}, bVerbose = False):
    df = DataFrame()
    for i, iIndex in enumerate(sorted(fileIndex)):
        if not (iIndex in descFrac.keys()):
            descFrac.update({iIndex: 1})  # all the undefined descaling factors are trivially set to 1
        if bVerbose:
            print("(%d/%d) %s -- descaling fraction: %f" % (i+1, len(fileIndex), iIndex, descFrac[iIndex]))
        dfTemp = asciiToDf(nameFormat.replace("XXXXXX", iIndex), asciiMap, nLinesEv, descFrac[iIndex], bVerbose)
        if len(fileIndexName)>0:  # fileIndexName column creation (if requested & not already existing)
            if not (fileIndexName in dfTemp.columns):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)
        df = df.append(dfTemp, ignore_index=True, sort=False)
    return df
