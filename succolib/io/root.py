import pandas as pd
import uproot
import time

from .misc import dfMirror

########################################################################################################################

def dfFromRootReshape(
        df,
        treeMap
):

    # remove square brackets from the variable names
    df = df.rename(columns = dict(zip(
        [s for s in df.columns if ("[" in s) & ("]" in s)],
        [s.replace("[", "").replace("]", "") for s in df.columns if ("[" in s) & ("]" in s)]
    )))

    # rename variables according to treeMap
    df = df.rename(columns = dict(zip(
        [treeMap[s] for s in treeMap if treeMap[s] in df.columns],
        [s for s in treeMap if treeMap[s] in df.columns]
    )))
    return df

########################################################################################################################

def rootToDfMulti(
        nameFormat,
        fileIndex,
        treeName,
        fileIndexName = "iIndex",
        descFrac = {},
        treeMap = {},
        mirrorMap = {},
        bVerbose = False
):

    t0 = time.time()  # chronometer start
    df = pd.DataFrame()
    for i, iIndex in enumerate(sorted(fileIndex)):
        if not (iIndex in descFrac.keys()):
            descFrac.update({iIndex: 1})  # all the undefined descaling factors are trivially set to 1
        descFrac[iIndex] = 1e-12 if descFrac[iIndex] <= 0 else (descFrac[iIndex] if descFrac[iIndex] <= 1 else 1)
        if bVerbose:
            print("(%d/%d) %s -- descaling fraction: %14.12f" % (i+1, len(fileIndex), iIndex, descFrac[iIndex]))
        tree = uproot.open(nameFormat.replace("XXXXXX", iIndex))[treeName]
        dfTemp = tree.pandas.df()

        # data reshaping: removing the square brackets in the names & remapping all the names according to treeMap
        if len(treeMap)>0:
            if bVerbose:
                print("remapping some ROOT tree variables (from tree map given)")
            dfTemp = dfFromRootReshape(dfTemp, treeMap)

        # data mirroring according to mirrorMap, which differs from iLayer to iLayer
        if iIndex in mirrorMap:
            if bVerbose:
                print("mirroring (from mirror map given) "+str(mirrorMap[iIndex]))
            dfTemp = dfMirror(dfTemp, mirrorMap[iIndex])
        else:
            if bVerbose:
                print("no variables to mirror")

        # fileIndexName column creation (if requested & not already existing -- after the data reshaping)
        if len(fileIndexName)>0:
            if not (fileIndexName in dfTemp.columns):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)
        if bVerbose:
            print("%s also added to df" % fileIndexName)

        df = df.append(dfTemp[dfTemp.index % int(1 / min(1, abs(descFrac[iIndex]))) == 0], ignore_index=True, sort=False)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt
