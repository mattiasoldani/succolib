from pandas import DataFrame
from uproot import open as uproot_open


########################################################################################################################
# dfFromRoot_reshape ###################################################################################################
"""
dfFromRoot_reshape reshapes the variable names in a Pandas dataframe, solving the typical issues of dataframes coming from ROOT files, i.e.
    > removing the square brackets in the variable names
    > remapping all the variable names according to an old-to-new name map
    
dfOut = dfFromRoot_reshape(...) is the output (reshaped) dataframe
dfIn is the input (raw) dataframe
treeMap is a dictionary containing the old-to-new name map (new/old names in keys/values)

default values for the optional variables:
    treeMap = {}
    
note: treeMap can be not given at all -- in this case, all the variable names are unchanged, only the square brackets being removed

dependencies: none
"""

def dfFromRoot_reshape(dfIn, treeMap):
    dfOut = dfIn
    # remove square brackets from the variable names
    dfOut = dfOut.rename(columns = dict(zip(
        [s for s in dfOut.columns if ("[" in s) & ("]" in s)], 
        [s.replace("[", "").replace("]", "") for s in dfOut.columns if ("[" in s) & ("]" in s)]
    )))

    # rename variables according to treeMap
    dfOut = dfOut.rename(columns = dict(zip(
        [treeMap[s] for s in treeMap if treeMap[s] in dfOut.columns], 
        [s for s in treeMap if treeMap[s] in dfOut.columns]
    )))

    return dfOut


########################################################################################################################
# rootToDfMulti ########################################################################################################
"""
rootToDfMulti opens all the ROOT files that have the same name format apart from one part & creates a single Pandas dataframe with minor data reshaping (see dfFromRoot_reshape)

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

note: treeMap can be not given at all -- in this case, all the variable names are unchanged, only the square brackets being removed (see dfFromRoot_reshape)

if descFrac = 0 for , descFrac is set equal to 10^(-12)

dependencies: pandas.DataFrame as DataFrame, uproot.open as uproot_open, succolib.dfFromRoot_reshape
"""

def rootToDfMulti(nameFormat, fileIndex, treeName, fileIndexName = "iIndex", descFrac = {}, treeMap = {}, bVerbose = False):
    df = DataFrame()
    for i, iIndex in enumerate(sorted(fileIndex)):
        if not (iIndex in descFrac.keys()):
            descFrac.update({iIndex: 1})  # all the undefined descaling factors are trivially set to 1
        if bVerbose:
            print("(%d/%d) %s -- descaling fraction: %f" % (i+1, len(fileIndex), iIndex, descFrac[iIndex]))
        tree = uproot_open(nameFormat.replace("XXXXXX", iIndex))[treeName]
        dfTemp = tree.pandas.df()
        dfTemp = dfFromRoot_reshape(dfTemp, treeMap)  # data reshaping: removing the square brackets in the names & remapping all the names according to treeMap
        if len(fileIndexName)>0:  # fileIndexName column creation (if requested & not already existing -- after the data reshaping)
            if not (fileIndexName in dfTemp.columns):
                dfTemp[fileIndexName] = str(iIndex)
            else:
                dfTemp[fileIndexName] = dfTemp[fileIndexName].astype(str)
        df = df.append(dfTemp, ignore_index=True, sort=False)
    return df
