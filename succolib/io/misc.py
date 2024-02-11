########################################################################################################################

def dfMirror(
        df,
        map
):

    for iVar in map:
        if iVar in df.columns:
            df[iVar] = -df[iVar]
    return df

########################################################################################################################

def dfReshape(
        df,
        map,
        bBrackets = True,
):

    # remove square brackets from the variable names (if required)
    if bBrackets:
        df = df.rename(columns = dict(zip(
            [s for s in df.columns if ("[" in s) & ("]" in s)],
            [s.replace("[", "").replace("]", "") for s in df.columns if ("[" in s) & ("]" in s)]
        )))

    # rename variables according to map
    df = df.rename(columns = dict(zip(
        [map[s] for s in map if map[s] in df.columns],
        [s for s in map if map[s] in df.columns]
    )))

    return df
    
########################################################################################################################

def akMirror(
        df,
        map
):

    for iVar in map:
        if iVar in df.fields:
            df[iVar] = -df[iVar]
    return df
    
########################################################################################################################

def akReshape(
        df,
        map,
        bBrackets = True,
):

    # remove square brackets from the variable names (if required)
    if bBrackets:
        fieldsToChange = dict(zip(
            [s for s in df.columns if ("[" in s) & ("]" in s)],
            [s.replace("[", "").replace("]", "") for s in df.columns if ("[" in s) & ("]" in s)]
        ))
        for fieldOld in fieldsToChange:
            fieldNew = fieldsToChange[fieldOld]
            df[fieldNew] = df[fieldOld]
            df = df[[field for field in ak.fields(df) if field!=fieldOld]]

    # rename variables according to map
    if bBrackets:
        fieldsToChange = dict(zip(
            [map[s] for s in map if map[s] in df.columns],
            [s for s in map if map[s] in df.columns]
        ))
        for fieldOld in fieldsToChange:
            fieldNew = fieldsToChange[fieldOld]
            df[fieldNew] = df[fieldOld]
            df = df[[field for field in ak.fields(df) if field!=fieldOld]]

    return df