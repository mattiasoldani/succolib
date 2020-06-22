import numpy as np

########################################################################################################################

def fLandau(
        x,
        A,
        mpv,
        width
):

    expo0 = (x-mpv)/width
    expo1 = np.exp(-expo0)
    return A*np.exp(-0.5*(expo0+expo1))


########################################################################################################################

def fLandauMirror(
        x,
        A,
        mpv,
        width
):

    expo0 = (mpv-x)/width
    expo1 = np.exp(-expo0)
    return A*np.exp(-0.5*(expo0+expo1))
