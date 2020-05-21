########################################################################################################################

def dfMirror(
        df,
        mirrorMap
):

    for iVar in mirrorMap:
        if iVar in df.columns:
            df[iVar] = -df[iVar]
    return df
