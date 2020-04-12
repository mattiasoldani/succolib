import pandas as pd
import uproot


########################################################################################################################
# dfFromRootReshape ####################################################################################################
"""
dfFromRootReshape reshapes the variable names in a Pandas dataframe, solving the typical issues of dataframes coming from ROOT files, i.e.
    > removing the square brackets in the variable names
    > remapping all the variable names according to an old-to-new name map
    
df1 = dfFromRootReshape(...) is the output (reshaped) dataframe
df0 is the input (raw) dataframe
treeMap is a dictionary containing the old-to-new name map (new/old names in keys/values)

default values for the optional variables:
    treeMap = {}
    
note: treeMap can be not given at all -- in this case, all the variable names are unchanged, only the square brackets being removed

dependencies: none
"""

def dfFromRootReshape(df0, treeMap):
    df1 = df0

    # remove square brackets from the variable names
    df1 = df1.rename(columns = dict(zip(
        [s for s in df1.columns if ("[" in s) & ("]" in s)], 
        [s.replace("[", "").replace("]", "") for s in df1.columns if ("[" in s) & ("]" in s)]
    )))

    # rename variables according to treeMap
    df1 = df1.rename(columns = dict(zip(
        [treeMap[s] for s in treeMap if treeMap[s] in df1.columns], 
        [s for s in treeMap if treeMap[s] in df1.columns]
    )))

    return df1


########################################################################################################################
# rootToDfMulti ########################################################################################################
"""
rootToDfMulti opens all the ROOT files that have the same name format apart from one part & creates a single Pandas dataframe with minor data reshaping (see dfFromRootReshape)

df = rootToDfMulti(...) is the output dataframe
nameFormat is the name format common to all the ROOT files to be opened (with a XXXXXX in place of the changing part)
fileIndex is the list of string values the filename changing part has to assume
treeName is the name of the tree inside the ROOT files, common to all the files
fileIndexName is the name of the newly created (if not already existing) dataframe column that contains the changing part values -- if "", no new column is created
descFrac is the dictionary of descaling fractions, i.e. fraction of (uniformly distributed along the run) events to be processed -- one per fileIndex entry
treeMap is a dictionary containing the old-to-new name map (new/old names in keys/values)
bVerbose is a boolean for the verbose (True) or quiet (False) mode

default values for the optional variables:
    fileIndexName = "iIndex"
    descFrac = {}
    treeMap = {}
    bVerbose = False

note: descFrac can be not given at all -- in this case, 1 is taken for all the fileIndex values

note: treeMap can be not given at all -- in this case, all the variable names are unchanged, only the square brackets being removed (see dfFromRootReshape)

if descFrac = 0 for , descFrac is set equal to 10^(-12)

dependencies: pd.DataFrame, uproot.open, succolib.dfFromRootReshape
"""

def rootToDfMulti(nameFormat, fileIndex, treeName, fileIndexName = "iIndex", descFrac = {}, treeMap = {}, bVerbose = False):
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
    return df
