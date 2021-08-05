import numpy as np
import glob
import pandas as pd
import os
import time
from tqdm.auto import tqdm

from .misc import dfMirror

########################################################################################################################

# it's best to use npzToDfMulti() (which exploits this npzToDf()) also for single file opening
def npzToDf(
        nameFormat,
        npzMap,
        arrayName,
        nLinesEv = 1,
        descFrac = 1,
        mirrorMap = (),  # this is a tuple here, but a dictionary in npzToDfMulti() (i.e. the "main" function)
        bVerbose = False,
        bProgress = False,
):

    t0 = time.time()  # chronometer start
    names = sorted(glob.glob(nameFormat.replace("YYYYYY", "*")))  # list of all the filenames of the current run
    df = pd.DataFrame()
    descFrac = 1e-12 if descFrac <= 0 else (descFrac if descFrac <= 1 else 1)
    for iName in tqdm((names)) if (bVerbose & bProgress) else names:
        if os.stat(iName).st_size > 0:
            with np.load(iName) as data0:
                dataTableTemp0 = data0[arrayName]
            if nLinesEv == 1:
                dataTableTemp = dataTableTemp0
            else:
                dataTableTemp = np.hstack([dataTableTemp0[i::nLinesEv] for i in range(nLinesEv)])
            dfTemp = pd.DataFrame(dataTableTemp, columns=npzMap)
            df = df.append(dfTemp[dfTemp.index % int(1 / descFrac) == 0], ignore_index=True, sort=False)
            df = dfMirror(df, mirrorMap)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt

########################################################################################################################

def npzToDfMulti(
        nameFormat,
        fileIndex,
        npzMap,
        arrayName,
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
        dfTemp, _ = npzToDf(nameFormat.replace("XXXXXX", iIndex), npzMap, arrayName, nLinesEv, descFrac[iIndex], bVerbose=bVerbose, bProgress=bProgress)

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
            if bVerbose:
                print("%s also added to df" % fileIndexName)
            if not (fileIndexName in dfTemp.columns):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)

        df = df.append(dfTemp, ignore_index=True, sort=False)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt
