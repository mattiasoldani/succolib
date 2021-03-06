import numpy as np

########################################################################################################################

def zProj(
        x1,
        z1,
        x0,
        z0,
        z2
):

    zRatio = (z2-z1)/(z1-z0)
    x2 = (1+zRatio)*x1 - (zRatio)*x0
    return x2


########################################################################################################################

def zAngle(
        x1,
        z1,
        x0,
        z0
):

    th = np.arctan2(x1-x0, z1-z0)
    return th
