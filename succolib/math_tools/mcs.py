import numpy as np

########################################################################################################################

def fMCS(
        E,  # in GeV
        x,
        x0 = 1,
        z = 1,
        bLogTerm = True  # if True (False) logarithmic term is (not) included
):

    eRatio = 13.6e-3 / E
    linTerm = eRatio * z * np.sqrt(x/x0) * 1
    logTerm = eRatio * z * np.sqrt(x/x0) * 0.038*np.log(x/x0)
    return (linTerm + logTerm) if bLogTerm else linTerm