from copy import copy, deepcopy
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

########################################################################################################################

class cTrack:
    def __init__(
        self,
        x0,
        y0,
        z,
        mirrorX = [False, False],
        mirrorY = [False, False],
        shiftMirrorX = [0, 0],
        shiftMirrorY = [0, 0],
        shiftThX = 0,
        shiftThY = 0,
        dictProjections = {},
    ):
        
        # attributes set via input:
        
        self.x0 = np.array(x0)
        self.y0 = np.array(y0)
        self.z = np.array(z)
        
        self.shiftMirrorX = np.array(shiftMirrorX)
        self.shiftMirrorY = np.array(shiftMirrorY)
        
        self.mirrorX = np.array(mirrorX)
        self.mirrorY = np.array(mirrorY)
        
        self.shiftThX = shiftThX
        self.shiftThY = shiftThY
        
        self.dictProjections = dictProjections
        
        # calculated attributes:
        
        self.thx0 = -9999
        self.thy0 = -9999
        self.thx = -9999
        self.thy = -9999
        
        self.x = self.x0
        self.y = self.y0
        
        self.__mirrorX_after = deepcopy(self.mirrorX)
        self.__mirrorY_after = deepcopy(self.mirrorY)
        
        for proj in self.dictProjections:
            setattr(self, "x"+proj+"0", -9999)
            setattr(self, "y"+proj+"0", -9999)
            setattr(self, "x"+proj, -9999)
            setattr(self, "y"+proj, -9999)
        
    # mirror all the swapped tracking planes
    def mirror_modules(self):
        for imod in (0, 1):
            self.x0[imod] = (self.shiftMirrorX[imod] - self.x0[imod]) if self.__mirrorX_after[imod] else self.x0[imod]
            self.y0[imod] = (self.shiftMirrorY[imod] - self.y0[imod]) if self.__mirrorY_after[imod] else self.y0[imod]
            self.__mirrorX_after[imod] = False
            self.__mirrorY_after[imod] = False
    
    # compute uncentred track angles
    def compute_angles_0(self):
        self.thx0 = zAngle(self.x0[1], self.z[1], self.x0[0], self.z[0])
        self.thy0 = zAngle(self.y0[1], self.z[1], self.y0[0], self.z[0]) 
    
    # centre track angles, private
    # shiftThX(y) is the hor (ver.) uncentred track angle distribution centre
    def __shift_angles(self):
        self.thx = self.thx0 - self.shiftThX
        self.thy = self.thy0 - self.shiftThY
        
    # compute aligned transverse positions, private
    def __shift_hits(self):
        self.x = self.x0 - (self.z - self.z[0]) * np.tan(self.shiftThX)
        self.y = self.y0 - (self.z - self.z[0]) * np.tan(self.shiftThY)
        
    # compute centred track angles and aligned transverse positions
    # shiftThX(y) is the hor (ver.) uncentred track angle distribution centre
    def align(self):
        self.__shift_angles()
        self.__shift_hits()
        
    # project the uncentred tracks to the chosen longitudinal position
    # zproj: destination longitudinal position, float
    # --> return the projected coordinates: np.array([x, y, z])
    def project_0(self, z_proj):
        x_proj = zProj(self.x0[1], self.z[1], self.x0[0], self.z[0], z_proj)
        y_proj = zProj(self.y0[1], self.z[1], self.y0[0], self.z[0], z_proj)
        return np.array([x_proj, y_proj, z_proj])
        
    # project the centred tracks to the chosen longitudinal position
    # zproj: destination longitudinal position, float
    # --> return the projected coordinates: np.array([x, y, z])
    def project(self, z_proj):
        x_proj = zProj(self.x[1], self.z[1], self.x[0], self.z[0], z_proj)
        y_proj = zProj(self.y[1], self.z[1], self.y[0], self.z[0], z_proj)
        return np.array([x_proj, y_proj, z_proj])
    
    # compute all projections requested in dictProjections (both with uncentred and centred tracks)
    def compute_all_projections(self):
        for proj in self.dictProjections:
            setattr(self, "x"+proj+"0", self.project_0(self.dictProjections[proj])[0])
            setattr(self, "y"+proj+"0", self.project_0(self.dictProjections[proj])[1])
            setattr(self, "x"+proj, self.project(self.dictProjections[proj])[0])
            setattr(self, "y"+proj, self.project(self.dictProjections[proj])[1])
            
    # perform the track full analysis:
    def full_analysis(self):
        self.mirror_modules()
        self.compute_angles_0()
        self.align()
        self.compute_all_projections()