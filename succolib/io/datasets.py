import awkward as ak
import numpy as np
from copy import deepcopy

from .root import rootToAkMulti
from .ascii import asciiToAkMulti

########################################################################################################################

class cAkDataset:
    def __init__(
        self,
        dataType,
        nameFormat,
        fileIndex,
        treeName = "t",
        varlist = [],
        treeMap = {},
        asciiMap = [],
        chunksize = 100,
        nLinesEv = 1,
        fileIndexName = "iIndex",
        descFrac = {},
        nEvMax = 10000000000,
        mirrorMap = {},
        bVerbose = False,
        bProgress = False,
    ):
        
        # attributes set via input:

        self.dataType = dataType
        self.nameFormat = nameFormat
        self.fileIndex = fileIndex
        
        self.treeName = treeName
        self.varlist = varlist
        self.treeMap = treeMap
        self.treeMap = treeMap
        self.asciiMap = asciiMap
        self.chunksize = int(chunksize)
        self.nLinesEv = nLinesEv
        self.fileIndexName = fileIndexName
        self.descFrac = descFrac
        self.nEvMax = int(nEvMax)
        self.bVerbose = bVerbose
        self.mirrorMap = mirrorMap
        self.bProgress = bProgress

        # calculated attributes:

        self.data = ak.Array([])
        
        self.loadtime = 0
        self.nvars = 0
        self.nevs = 0
        self.shape = [self.nevs, self.nvars]
        
    # compute nr. of events and variables, private
    def __compute_size(self):
        self.nvars = len(self.data.fields)
        self.nevs = len(self.data)
        self.shape = [self.nevs, self.nvars]
        
    # open data --> return the instance
    def open(self):
        
        if self.dataType == "ROOT":
            self.data, self.loadtime = rootToAkMulti(
                self.nameFormat, self.fileIndex, self.treeName, self.varlist, self.treeMap,
                self.chunksize, self.fileIndexName, self.descFrac, self.nEvMax, self.mirrorMap,
                self.bVerbose, self.bProgress
            )
        elif self.dataType == "ASCII":
            self.data, self.loadtime = asciiToAkMulti(
                self.nameFormat, self.fileIndex, self.asciiMap,
                self.nLinesEv, self.fileIndexName, self.descFrac, self.nEvMax, self.mirrorMap,
                self.bVerbose, self.bProgress
            )
                
        self.__compute_size()
        self.add_vars({"index" : ak.Array(range(self.nevs))})
        self.__compute_size()
                
        return self
    
    # add new variable(s)
    # dict_vars = { variable name (string) : actual variable (array) }
    def add_vars(self, dict_vars):
        
        for varname in dict_vars:
            self.data[varname] = dict_vars[varname]
            
        self.__compute_size()
        
    # cut dataset --> return a copy of the instance with the cut applied
    # condition is the array of booleans
    def cut_copy(self, condition):
        dataset_new = deepcopy(self)
        dataset_new.data = self.data if np.isscalar(condition) else self.data[condition]
        dataset_new.__compute_size()
        return dataset_new
