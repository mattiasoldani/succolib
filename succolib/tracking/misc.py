########################################################################################################################
# dz

def dz(zDict, zKey2, zKey1):
    return zDict[zKey2]-zDict[zKey1]


########################################################################################################################
# xMirror

def xMirror(df, lsMirror):
    for iLayer in lsMirror:
        if lsMirror in df.columns:
            df[iLayer] = -df[iLayer]
            print("%s mirrored" % iLayer)
        else:
            print("%s not found in df --> not mirrored" % iLayer)
    return df
