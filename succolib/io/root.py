import pandas as pd
import awkward as ak
import uproot
import time
import glob
from tqdm.auto import tqdm

from .misc import dfReshape, dfMirror, akReshape, akMirror

########################################################################################################################

def rootToDfMulti(
        nameFormat,
        fileIndex,
        treeName = "t",
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
            with uproot.open(iName)[treeName] as tree:
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
            if not (fileIndexName in dfTemp.columns):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)

        df = df.append(dfTemp, ignore_index=True, sort=False)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt
    
########################################################################################################################

def rootToAkMulti(
        nameFormat,
        fileIndex,
        treeName = "t",
        varlist = [],
        treeMap = {},
        chunksize = 100,
        fileIndexName = "iIndex",
        descFrac = {},
        nEvMax = 10000000000,
        mirrorMap = {},
        bVerbose = False,
        bProgress = False,
):

    t0 = time.time()  # chronometer start
    df = ak.Array([])
    for i, iIndex in enumerate(sorted(fileIndex)):
        names = sorted(glob.glob(nameFormat.replace("XXXXXX", iIndex).replace("YYYYYY", "*")))  # list of all the filenames of the current run
        dictFiles = {name : treeName for name in names}
        if not (iIndex in descFrac.keys()):
            descFrac.update({iIndex: 1})  # all the undefined descaling factors are trivially set to 1
        descFrac[iIndex] = 1e-12 if descFrac[iIndex] <= 0 else (descFrac[iIndex] if descFrac[iIndex] <= 1 else 1)
        
        dfTemp = ak.Array([])
        if bVerbose:
            print("(%d/%d) %s -- descaling fraction: %14.12f" % (i + 1, len(fileIndex), iIndex, descFrac[iIndex]))    
        uprootChain = enumerate(uproot.iterate(dictFiles,
            expressions=varlist, step_size=chunksize, allow_missing=True,
        ))
        for ichunk, chunk in tqdm(uprootChain) if (bVerbose & bProgress) else uprootChain:
            if ichunk==0:
                dfTemp = chunk[0:int(len(chunk) * descFrac[iIndex])]
            else:
                dfTemp = ak.concatenate((dfTemp, chunk[0:int(len(chunk) * descFrac[iIndex])]))

        # data reshaping: removing the square brackets in the names & remapping all the names according to treeMap
        if len(treeMap)>0:
            if bVerbose:
                print("remapping some ROOT tree variables (from tree map given)")
            if len(dfTemp) > 0:
                dfTemp = akReshape(dfTemp, treeMap, True)

        # data mirroring according to mirrorMap, which differs from iLayer to iLayer
        if iIndex in mirrorMap:
            if bVerbose:
                print("mirroring (from mirror map given) "+str(mirrorMap[iIndex]))
            if dfTemp.shape[0] > 0:
                dfTemp = akMirror(dfTemp, mirrorMap[iIndex])
        else:
            if bVerbose:
                print("no variables to mirror")

        # fileIndexName column creation (if requested & not already existing -- after the data reshaping)
        if len(fileIndexName)>0:
            if bVerbose:
                print("%s also added to df" % fileIndexName)
            if not (fileIndexName in dfTemp.fields):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                akTemp = ak.to_list(dfTemp[fileIndexName])
                dfTemp[fileIndexName] = ak.Array([str(ind) for ind in akTemp])

        df = ak.concatenate((df, dfTemp))
        if len(df)>nEvMax:
            df = df[:nEvMax]
            if bVerbose:
                print("event nr. reached nEvMax=%d, breaking" % nEvMax)
            break
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt
