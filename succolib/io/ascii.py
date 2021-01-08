import numpy as np
import glob
import pandas as pd
import os
import time
from tqdm.auto import tqdm

from .misc import dfMirror

########################################################################################################################

# it's best to use asciiToDfMulti() (which exploits this asciiToDf()) also for single file opening
def asciiToDf(
        nameFormat,
        asciiMap,
        nLinesEv = 1,
        descFrac = 1,
        mirrorMap = (),  # this is a tuple here, but a dictionary in asciiToDfMulti() (i.e. the "main" function)
        bVerbose = False,
        bProgress = False,
):

    t0 = time.time()  # chronometer start
    names = sorted(glob.glob(nameFormat.replace("YYYYYY", "*")))  # list of all the filenames of the current run
    df = pd.DataFrame()
    descFrac = 1e-12 if descFrac <= 0 else (descFrac if descFrac <= 1 else 1)
    for iName in tqdm((names)) if (bVerbose & bProgress) else names:
        if os.stat(iName).st_size > 0:
            if nLinesEv == 1:
                dataTableTemp = np.loadtxt(iName, unpack=False, ndmin=2)
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
                dataTableTemp = np.loadtxt(fileToStringSplitted)
            dfTemp = pd.DataFrame(dataTableTemp, columns=asciiMap)
            df = df.append(dfTemp[dfTemp.index % int(1 / descFrac) == 0], ignore_index=True, sort=False)
            df = dfMirror(df, mirrorMap)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt

########################################################################################################################

def asciiToDfMulti(
        nameFormat,
        fileIndex,
        asciiMap,
        fileIndexName = "iIndex",
        nLinesEv = 1,
        descFrac = {},
        mirrorMap = {},
        bVerbose = False,
        bProgress = False,
):

    t0 = time.time()  # chronometer start
    df = pd.DataFrame()
    for i, iIndex in enumerate(sorted(fileIndex)):
        if not (iIndex in descFrac.keys()):
            descFrac.update({iIndex: 1})  # all the undefined descaling factors are trivially set to 1
        if bVerbose:
            print("(%d/%d) %s -- descaling fraction: %14.12f" % (i+1, len(fileIndex), iIndex, descFrac[iIndex]))
        dfTemp, _ = asciiToDf(nameFormat.replace("XXXXXX", iIndex), asciiMap, nLinesEv, descFrac[iIndex], bVerbose=bVerbose, bProgress=bProgress)

        # data mirroring according to mirrorMap, which differs from iLayer to iLayer
        if iIndex in mirrorMap:
            if bVerbose:
                print("mirroring (from mirror map given) "+str(mirrorMap[iIndex]))
            dfTemp = dfMirror(dfTemp, mirrorMap[iIndex])
        else:
            if bVerbose:
                print("no variables to mirror")

        # fileIndexName column creation (if requested & not already existing)
        if len(fileIndexName)>0:
            if not (fileIndexName in dfTemp.columns):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)
            if bVerbose:
                print("%s also added to df" % fileIndexName)

        df = df.append(dfTemp, ignore_index=True, sort=False)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt
