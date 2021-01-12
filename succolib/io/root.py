import pandas as pd
import uproot
import time
import glob
from tqdm.auto import tqdm

from .misc import dfReshape, dfMirror

########################################################################################################################

def rootToDfMulti(
        nameFormat,
        fileIndex,
        treeName,
        fileIndexName = "iIndex",
        descFrac = {},
        treeMap = {},
        mirrorMap = {},
        bVerbose = False,
        bProgress = False,
):

    t0 = time.time()  # chronometer start
    df = pd.DataFrame()
    for i, iIndex in enumerate(sorted(fileIndex)):
        names = sorted(glob.glob(nameFormat.replace("XXXXXX", iIndex).replace("YYYYYY", "*")))  # list of all the filenames of the current run
        if not (iIndex in descFrac.keys()):
            descFrac.update({iIndex: 1})  # all the undefined descaling factors are trivially set to 1
        descFrac[iIndex] = 1e-12 if descFrac[iIndex] <= 0 else (descFrac[iIndex] if descFrac[iIndex] <= 1 else 1)

        dfTemp = pd.DataFrame()
        if bVerbose:
            print("(%d/%d) %s -- descaling fraction: %14.12f" % (i + 1, len(fileIndex), iIndex, descFrac[iIndex]))
        for iName in tqdm((names)) if (bVerbose & bProgress) else names:  # for each value of iIndex, look for all the corresponding files
            tree = uproot.open(iName)[treeName]
            dfTemp0 = tree.arrays(library="pd")
            dfTemp = dfTemp.append(dfTemp0[dfTemp0.index % int(1 / descFrac[iIndex]) == 0], ignore_index=True, sort=False)

        # data reshaping: removing the square brackets in the names & remapping all the names according to treeMap
        if len(treeMap)>0:
            if bVerbose:
                print("remapping some ROOT tree variables (from tree map given)")
            if dfTemp.shape[0] > 0:
                dfTemp = dfReshape(dfTemp, treeMap, True)

        # data mirroring according to mirrorMap, which differs from iLayer to iLayer
        if iIndex in mirrorMap:
            if bVerbose:
                print("mirroring (from mirror map given) "+str(mirrorMap[iIndex]))
            if dfTemp.shape[0] > 0:
                dfTemp = dfMirror(dfTemp, mirrorMap[iIndex])
        else:
            if bVerbose:
                print("no variables to mirror")

        # fileIndexName column creation (if requested & not already existing -- after the data reshaping)
        if len(fileIndexName)>0:
            if bVerbose:
                print("%s also added to df" % fileIndexName)
            if dfTemp.shape[0] > 0:
                if not (fileIndexName in dfTemp.columns):
                    dfTemp[fileIndexName] = str(iIndex)
                else:
                    dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)

        df = df.append(dfTemp, ignore_index=True, sort=False)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt
