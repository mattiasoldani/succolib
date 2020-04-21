import pandas as pd
import uproot
import time


########################################################################################################################
# dfFromRootReshape

def dfFromRootReshape(df, treeMap):
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
# rootToDfMulti

def rootToDfMulti(nameFormat, fileIndex, treeName, fileIndexName = "iIndex", descFrac = {}, treeMap = {}, bVerbose = False):
    t0 = time.time()  # chronometer start
    df = pd.DataFrame()
    for i, iIndex in enumerate(sorted(fileIndex)):
        if not (iIndex in descFrac.keys()):
            descFrac.update({iIndex: 1})  # all the undefined descaling factors are trivially set to 1
        if bVerbose:
            print("(%d/%d) %s -- descaling fraction: %f" % (i+1, len(fileIndex), iIndex, descFrac[iIndex]))
        tree = uproot.open(nameFormat.replace("XXXXXX", iIndex))[treeName]
        dfTemp = tree.pandas.df()
        dfTemp = dfFromRootReshape(dfTemp, treeMap)  # data reshaping: removing the square brackets in the names & remapping all the names according to treeMap
        if len(fileIndexName)>0:  # fileIndexName column creation (if requested & not already existing -- after the data reshaping)
            if not (fileIndexName in dfTemp.columns):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)
        df = df.append(dfTemp, ignore_index=True, sort=False)
    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return df, dt
