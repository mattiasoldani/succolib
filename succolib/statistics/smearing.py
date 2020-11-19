import numpy as np
import time

########################################################################################################################

def eventSmear(
    dfIn,
    lsVar,
    lsSigma,
    nIter,
    bSmearSingleIter=False,
    bKeepOld=False,
    bVerbose=False
):
    
    t0 = time.time()  # chronometer start
    
    # check whether the input arguments make sense --> if not, returns empty dictionary
    if len(lsVar) != len(lsSigma):  # lsVar must have the same length as lsSigma
        if bVerbose:
            print ("list of variables and list of corresponding errors have different length --> operation not performed")
        t1 = time.time()  # chronometer stop
        dt = t1 - t0
        return {}, dt
    
    for s in lsVar+lsSigma:  # all the variables in lsVar+lsSigma must be available in the input dataframe
        if not (s in dfIn.columns):
            if bVerbose:
                print("variable %s not in input dataframe --> operation not performed")
            t1 = time.time()  # chronometer stop
            dt = t1 - t0
            return {}, dt
    
    # setting up input dataframe properly
    # events in which at least 1 of the variables to be studied are NaN are excluded
    dfIn = dfIn[lsVar+lsSigma].dropna()
    
    ind = list(dfIn.index)
    var = {}
    for iVar in lsVar+lsSigma:  # each dfIn variable into a list; lsVar-then-lsSigma; both elements of lsVar & lsSigma are included here
        var.update({iVar: list(dfIn[iVar])})
    
    # preparing the output dictionary (original index & values included only if bKeepOld is True)
    dictOut = {"old_index": np.ndarray(shape=nIter*dfIn.count()[0])} if bKeepOld else {}
    for iVar in lsVar:
        dictOut.update({iVar: np.ndarray(shape=nIter*dfIn.count()[0])})
        if bKeepOld:
            dictOut.update({"old_"+iVar: np.ndarray(shape=nIter*dfIn.count()[0])})

    for i in range(len(ind)):  # loop over original events
        
        # retrieving the event central value & sigma for each variable
        means, stds = [], []     
        for iVar in lsVar+lsSigma:
            if iVar in lsVar:
                means.append(var[iVar][i])
            elif iVar in lsSigma:
                stds.append(var[iVar][i])
    
        # gaussian doping
        covMatr = np.zeros((len(lsVar), len(lsVar)), float)   
        if (nIter > 1) | ((nIter == 1) & bSmearSingleIter):
        # note: if nIter < 1 or =1 in case bSmearSingleIter=True, null covariance matrix is used --> output data equal the input ones
            np.fill_diagonal(covMatr, np.array(stds)**2)
        outStat = np.random.multivariate_normal(means, covMatr, nIter).T
        
        # filling the output dictionary
        for k, iVar in enumerate(lsVar):
            dictOut[iVar][i*nIter:(i+1)*nIter] = outStat[k]
            if bKeepOld:
                dictOut["old_"+iVar][i*nIter:(i+1)*nIter] = np.array([means[k] for j in range(nIter)])
                dictOut["old_index"][i*nIter:(i+1)*nIter] = np.array([ind[i] for j in range(nIter)])

    t1 = time.time()  # chronometer stop
    dt = t1 - t0
    return dictOut, dt