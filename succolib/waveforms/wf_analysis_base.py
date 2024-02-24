import numpy as np
from random import randint

########################################################################################################################

class cWaveForm:
    # deals with single waveforms
    
    def __init__(
        self,
        y0,
        x0BaseRange,
        bPositive,
        samplingRate = 1,
        nbit = 12,
        rangeVpp = 4096,
        unitX = 1,
        unitY = 1,
        resistor = 50,
    ):
    
        # attributes set via input:
        
        self.y0 = np.array(y0)
        
        self.x0BaseRange = x0BaseRange
        
        self.samplingRate = samplingRate
        self.unitX = unitX
        
        self.bPositive = bPositive
        self.nbit = nbit
        self.rangeVpp = rangeVpp
        self.unitY = unitY
        
        self.resistor = resistor
        
        # calculated attributes:
        
        self.x0 = np.array(range(len(self.y0)))
        self.x = self.x0
        self.y = self.y0
        
        self.y_base = np.array([-1])
        self.base_mean = -1
        self.base_rms = 0
        
        self.ph = -1
        self.peak_time = -1
        self.charge = -1
        self.snr = 0
        
        self.__bPositive_after = self.bPositive
        self.__peak_times = np.array([-1])
        
    # turn the sampling ticks into physical time
    def calibrate_x(self):
        self.x = self.x0 / (self.samplingRate * self.unitX)
        
    # turn the ADCs into physical voltage
    def calibrate_y(self):
        self.y = self.y0 * self.rangeVpp / (2**int(self.nbit) * self.unitY)
        
    # if a wf is originally negative, it is turned positive
    def make_positive(self):
        self.y = self.y if self.__bPositive_after else -self.y
        self.__bPositive_after = True
        
    # compute the baseline (and relative quantities) and subtract it from the wf
    def subtract_base(self):
        self.y_base = self.y[(self.x0>=self.x0BaseRange[0]) & (self.x0<=self.x0BaseRange[1])]
        self.base_mean = np.mean(self.y_base)
        self.base_rms = np.sqrt(np.mean((self.y_base - self.base_mean)**2))
        self.y = self.y - self.base_mean
        
    # compute all the wf parametres
    def analyse(self):
        self.ph = np.max(self.y)
        self.__peak_times = self.x[self.y==self.ph]
        self.peak_time = self.__peak_times[randint(0, len(self.__peak_times)-1)]
        self.charge = np.sum(self.y) / (self.resistor * self.samplingRate * self.unitX)
        self.snr = self.ph / self.base_rms
        
    # perform the waveform full analysis
    def full_analysis(self):
        self.calibrate_x()
        self.calibrate_y()
        self.make_positive()
        self.subtract_base()
        self.analyse()