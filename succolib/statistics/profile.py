import numpy as np

########################################################################################################################

def hist2dToProfile(
        hist2d,
        errType = ""
):

    xVal = []
    yVal = []
    yErr = []
    for i in range(len(hist2d[1])-1):
        yNum = 0
        yErrNum = 0
        yDenom = 0
        for j in range(len(hist2d[2])-1):
            yNum += hist2d[0][i][j] * (hist2d[2][j] + (hist2d[2][j+1] - hist2d[2][j])/2)
            yDenom += hist2d[0][i][j]
        if yDenom != 0:
            for j in range(len(hist2d[2])-1):
                yErrNum += hist2d[0][i][j] * \
                           ((hist2d[2][j] + (hist2d[2][j + 1] - hist2d[2][j]) / 2) - yNum/yDenom) ** 2
            yErrDenom = yDenom - 1
            xVal.append(hist2d[1][i] + (hist2d[1][i+1] - hist2d[1][i])/2)
            yVal.append(yNum/yDenom)
            if yDenom > 1:
                if errType == "std":
                    yErr.append(np.sqrt(yErrNum/yErrDenom))
                elif errType == "mean":
                    yErr.append(np.sqrt(yErrNum/yErrDenom) / np.sqrt(yDenom))
                else:
                    yErr.append(0)
            else:
                yErr.append(0)
    return np.array(xVal), np.array(yVal), np.array(yErr)
