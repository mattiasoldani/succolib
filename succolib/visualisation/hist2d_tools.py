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

    bins = bins if not (bins is None) else 10

    # denominator
    histDen = np.histogram2d(xDen, yDen, bins=bins, range=range)

    # if range is None, it is set from histDen
    if range is None:
        range = [[histDen[1][0], histDen[1][len(histDen[1])-1]], [histDen[2][0], histDen[2][len(histDen[2])-1]]]

    # numerator
    histNum = np.histogram2d(xNum, yNum, bins=bins, range=range)

    # ratio
    histDen[0][histDen[0] == 0] = np.nan  # replace all zeros in the denominator with NaNs
    histRatio = np.transpose(histNum[0] / histDen[0])

    if bPlot:  # output plot only if requested (default)
        histRatioPlot = np.nan_to_num(histRatio, nan=0.0)  # replace all the NaNs in the ratio with zeros, just for plot drawing
        if ax!=None:
            ax.imshow(histRatioPlot, origin="lower", extent=[min(histDen[1]), max(histDen[1]), min(histDen[2]), max(histDen[2])], norm=norm, cmap=cmap, aspect="auto")
        else:
            plt.imshow(histRatioPlot, origin="lower", extent=[min(histDen[1]), max(histDen[1]), min(histDen[2]), max(histDen[2])], norm=norm, cmap=cmap, aspect="auto")

    return histRatio, histDen[1], histDen[2]  # output matrix is always computed and returned
