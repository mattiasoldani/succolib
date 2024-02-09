import awkward as ak
import numpy as np

from .root import rootToAkMultiEssential

########################################################################################################################

class cAkDataset:
    def __init__(
        self,
        nameFormat,
        fileIndex,
        treeName = "t",
        varlist = [],
        chunksize = 100,
        fileIndexName = "iIndex",
        descFrac = {},
        nEvMax = int(1e10),
        bVerbose = False,
    ):
        
        # attributes set via input:

        self.nameFormat = nameFormat
        self.fileIndex = fileIndex
        
        self.treeName = treeName
        self.varlist = varlist
        self.chunksize = int(chunksize)
        self.fileIndexName = fileIndexName
        self.descFrac = descFrac
        self.nEvMax = int(nEvMax)
        self.bVerbose = bVerbose

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
        
        self.data, self.loadtime = rootToAkMultiEssential(
            self.nameFormat, self.fileIndex, self.treeName, self.varlist,
            self.chunksize, self.fileIndexName, self.descFrac, self.nEvMax,
            self.bVerbose
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