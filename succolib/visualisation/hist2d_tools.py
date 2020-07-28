import numpy as np
import matplotlib.pyplot as plt

########################################################################################################################

def hist2dRatio(
        xNum, yNum,
        xDen, yDen,
        bins=None,
        range=None,
        bPlot=True,
        ax=None,
        norm=None,
        cmap=None,
):

    histNum = np.histogram2d(xNum, yNum, bins=bins, range=range)
    histDen = np.histogram2d(xDen, yDen, bins=bins, range=range)
    histDen[0][histDen[0] == 0] = np.nan  # replace all zeros in the denominator with NaNs
    histRatio = np.transpose(histNum[0]/histDen[0])

    if bPlot:  # output plot only if requested (default)
        if ax!=None:
            ax.imshow(histRatio, origin="lower", extent=[min(histDen[1]), max(histDen[1]), min(histDen[2]), max(histDen[2])], norm=norm, cmap=cmap, aspect="auto")
        else:
            plt.imshow(histRatio, origin="lower", extent=[min(histDen[1]), max(histDen[1]), min(histDen[2]), max(histDen[2])], norm=norm, cmap=cmap, aspect="auto")

    return (histRatio, histDen[1], histDen[2])  # output matrix is always computed and returned
