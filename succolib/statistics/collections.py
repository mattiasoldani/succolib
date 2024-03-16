from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import awkward as ak
from copy import deepcopy

########################################################################################################################

class cCollection:
    # note: this is just a dependency for actual event collections
    def __init__(self):
        sl = __import__(__name__)
        self.fGaus = getattr(sl, "fGaus")
        self.fLandau = getattr(sl, "fLandau")
        pass
    
    # tool to turn a (M*N)-dimensional array into (N*M), protected
    # array_mn is the original (M*N) array
    def _array_transpose(self, array_mn):
        array_nm = np.array(array_mn).T
        return array_nm
    
    # create a 1d histogram to instance the histogram collection, with boolean
    # --> return this list: [hist_x, hist_y, nevs]
    def create_histo_1d(
        self,
        var,  # variable to deal with among the loaded one, string or array*
        boolean=True,  # boolean to be applied to the dataset
        bins=100,  # like np.histogram
        range=None,  # like np.histogram
        density=False,  # like np.histogram
        weights=None,  # like np.histogram
    ):
        # * if an entire variable array is given, the loaded dataset is overridden
        
        dataset_temp = self.dataset.cut_copy(boolean)
        nevs = dataset_temp.shape[0]
        hist0 = np.histogram(
            np.array(dataset_temp.data[var]) if\
                np.isscalar(var) else\
                (np.array(var) if np.isscalar(boolean) else np.array(var[boolean])),
            bins=bins, range=range, density=density, weights=weights,
        )
        
        hist = [
            hist0[1][:-1] + 0.5 * (hist0[1][1]-hist0[1][0]),
            hist0[0],
            nevs
        ]
        return hist
    
    # create a 2d histogram to instance the histogram collection, with boolean
    # --> return this list: [hist_x, hist_y, hist_z, nevs]
    def create_histo_2d(
        self,
        varx,  # abscissa variable to deal with among the loaded one, string or array*
        vary,  # ordinate variable to deal with among the loaded one, string or array*
        boolean=True,  # boolean to be applied to the dataset
        bins=100,  # like np.histogram2d
        range=None,  # like np.histogram2d
        density=False,  # like np.histogram2d
        weights=None,  # like np.histogram2d
    ):
        # * if an entire variable array is given, the loaded dataset is overridden
        
        if not (range is None):
            if ((range[0] is None) & (range[1] is None)):
                range=None
        
        dataset_temp = self.dataset.cut_copy(boolean)
        nevs = dataset_temp.shape[0]
        hist0 = np.histogram2d(
            np.array(dataset_temp.data[varx]) if\
                np.isscalar(varx) else\
                (np.array(varx) if np.isscalar(boolean) else np.array(varx[boolean])),
            np.array(dataset_temp.data[vary]) if\
                np.isscalar(vary) else\
                (np.array(vary) if np.isscalar(boolean) else np.array(vary[boolean])),
            bins=bins, range=range, density=density, weights=weights,
        )
        
        hist = [
            hist0[1][:-1] + 0.5 * (hist0[1][1]-hist0[1][0]),
            hist0[2][:-1] + 0.5 * (hist0[2][1]-hist0[2][0]),
            hist0[0],
            nevs
        ]
        return hist
    
    # tweak binning and range info for a histogram if unspecified according to a variable, protected
    # array_var is the array on which to base the tweaking
    # bins, range are the histogram-borne objects to tweak
    # --> return bins, range after tweaking
    def _tweak_bins_range(self, array_var, bins, range):
        if bins is None:
            bins = np.linspace(np.min(array_var), np.max(array_var), 100)
        if range is None:
            range = (np.min(array_var), np.max(array_var))
        return bins, range
    
    # draw a 2d histogram previously stored by create_histo_2d, protected
    # hist2d is the create_histo_2d output
    # ax is the destination axis in a figure
    # bcbar is a boolean: if True, toggle colorbar
    # b is the whole destination figure (needed for the colorbar)
    # blog is a boolean: if True, toggle z log scale
    def _draw_hist2d(self, hist2d, ax, bcbar=False, fig=None, blog=False):
        im = ax.imshow(
            np.flip(hist2d[2].T, axis=0), extent=(hist2d[0][0], hist2d[0][-1], hist2d[1][0], hist2d[1][-1]),
            aspect="auto", norm=LogNorm() if blog else None, interpolation="none",
        )
        if bcbar:
            fig.colorbar(im, ax=ax)
    
    # calculate a box to superimpose on a plot, protected
    # limsx(y) is the horizontal (vertical) range of the box
    # --> return the abscissa and ordinate array to use in plt.plot
    def _superimpose_box(self, limsx, limsy):
        box = (
            (limsx[0], limsx[0], limsx[1], limsx[1], limsx[0]),
            (limsy[0], limsy[1], limsy[1], limsy[0], limsy[0])
        )
        return box[0], box[1]
        
    # fit a 1d histogram with a Landau function and draw it, protected
    # hist is the histogram, created by create_histo_1d
    # ax is the destination axis in a figure
    # bplot is a boolean: if True, draw the fit curve into ax
    # blegend is a boolean: if True, add to the legend in ax
    # apar_fit, upar_fit, spar_fit are the starting points (if None, they are estimated)
    # plot_color is the color of the fit plot
    # --> return the fit parameters, 3-entry array
    # --> also return fit_ok, a boolean that is True (False) if the fit succeeded (failed)
    def _fit_hist1d_landau(
        self, hist,
        bplot=False, ax=None, blegend=True,
        apar_fit=None, upar_fit=None, spar_fit=None,
        plot_color="red",
    ):
        fit_func = self.fLandau
        fit_par0 = (
            max(hist[1]) if apar_fit is None else apar_fit,
            hist[0][hist[1]==max(hist[1])][0] if upar_fit is None else upar_fit,
            hist[0][hist[1]==max(hist[1])][0] if spar_fit is None else spar_fit,
        )
        
        fit_ok = False
        try:
            fit_par, _ = curve_fit(
                fit_func, hist[0], hist[1], p0=fit_par0, bounds=((0, -np.inf, 0), np.inf)
            )
            fit_ok = True
        except:
            fit_par = fit_par0
            fit_ok = False
        
        fit_plot_x = np.linspace(hist[0][0], hist[0][-1], 1000)
        fit_plot_y = fit_func(fit_plot_x, *fit_par)
        if (bplot & fit_ok):
            ax.plot(
                fit_plot_x[fit_plot_y>0.01*np.max(fit_plot_y)],
                fit_plot_y[fit_plot_y>0.01*np.max(fit_plot_y)],
                lw=1, label=\
                    "Landau MPV = %.4e\nLandau sigma = %.4e" % (fit_par[1], fit_par[2])\
                    if blegend else None, color=plot_color,
            )
        return fit_par, fit_ok
    
    # fit a 1d histogram with a Gaussian function and draw it, protected
    # hist is the histogram, created by create_histo_1d
    # ax is the destination axis in a figure
    # bplot is a boolean: if True, draw the fit curve into ax
    # blegend is a boolean: if True, add to the legend in ax
    # apar_fit, upar_fit, spar_fit are the starting points (if None, they are estimated)
    # plot_color is the color of the fit plot
    # --> return the fit parameters, 3-entry array
    # --> also return fit_ok, a boolean that is True (False) if the fit succeeded (failed)
    def _fit_hist1d_gaus(
        self, hist,
        bplot=False, ax=None, blegend=True,
        apar_fit=None, upar_fit=None, spar_fit=None,
        plot_color="red",
    ):
        fit_func = self.fGaus
        fit_par0 = (
            max(hist[1]) if apar_fit is None else apar_fit,
            hist[0][hist[1]==max(hist[1])][0] if upar_fit is None else upar_fit,
            hist[0][hist[1]==max(hist[1])][0] if spar_fit is None else spar_fit,
        )
        
        fit_ok = False
        try:
            fit_par, _ = curve_fit(
                fit_func, hist[0], hist[1], p0=fit_par0
            )
            fit_ok = True
        except:
            fit_par = fit_par0
            fit_ok = False
            
        fit_plot_x = np.linspace(hist[0][0], hist[0][-1], 1000)
        fit_plot_y = fit_func(fit_plot_x, *fit_par)
        if (bplot & fit_ok):
            ax.plot(
                fit_plot_x[fit_plot_y>0.01*np.max(fit_plot_y)],
                fit_plot_y[fit_plot_y>0.01*np.max(fit_plot_y)],
                label=\
                    "Gaussian MPV = %.4e\nGaussian sigma = %.4e" % (fit_par[1], fit_par[2])\
                    if blegend else None, color=plot_color,
            )
        return fit_par, fit_ok
    
    # sum all the histograms of an array of collections into a single output collection, static
    # ls_in_hists_collections is the input array, it should contain at least 1 collection
    # --> returns the output collection
    @staticmethod
    def sum_hists_collections(ls_in_hists_collections):
        if len(ls_in_hists_collections)>0:
            out_hists_collection = deepcopy(ls_in_hists_collections[0])
            for key in ls_in_hists_collections[0].keys():
                if "hist_" in key:
                    ind_y = 1
                    ind_nevs = 2
                elif "hist2d_" in key:
                    ind_y = 2
                    ind_nevs = 3
                out_hists_collection[key][ind_y] =\
                    np.sum([ls_in_hists_collections[bunch][key][ind_y]\
                    for bunch in range(len(ls_in_hists_collections))], axis=0)
                out_hists_collection[key][ind_nevs] = \
                    np.sum([ls_in_hists_collections[bunch][key][ind_nevs]\
                    for bunch in range(len(ls_in_hists_collections))])
            return out_hists_collection
            
########################################################################################################################

class cTracksCollection(cCollection):
    def __init__(
        self,
        dataset,
        x0,
        y0,
        dictTrackParams,
        bVerbose = False,
        outtype = "x4",
    ):
        super().__init__()

        sl = __import__(__name__)
        self.cTrack = getattr(sl, "cTrack")
        
        # attributes set via input:
        
        self.dataset = dataset
        self.x0 = x0
        self.y0 = y0
        
        self.dictTrackParams = dictTrackParams
        self.dictProjections = \
            dictTrackParams["dictProjections"] if ("dictTrackParams" in dictTrackParams.keys()) else {}
        
        self.bVerbose = bVerbose
        self.outtype = outtype
        
        # calculated attributes:
        
        self.__output_collection = {
                "x0" : [],
                "y0" : [],
                "x" : [],
                "y" : [],
                "thx0" : [],
                "thy0" : [],
                "thx" : [],
                "thy" : [],
            }
        for hitproj in self.dictProjections:
            self.__output_collection.update({"x"+hitproj+"0" : []})
            self.__output_collection.update({"y"+hitproj+"0" : []})
            self.__output_collection.update({"x"+hitproj : []})
            self.__output_collection.update({"y"+hitproj : []})
            
        self.__dictTrackParams_before = deepcopy(self.dictTrackParams)
                
        self.__hists_collection_latest = {}
                
        self.__outfig_dpi = 200
    
    # create the 1d beam profile and 2d beam spot histograms at a single long. point of the track
    # name is a string with the two variables in hists_collection to use - replace x/y with *
    # ind is the index in case of multi-entry hit arrays, if the variables are 1d set None
    # hists_collection is the dictionary with all the histograms
    # boolean is the filling condition
    # bins_2d/h/v and range_h/v are the binning and range info for the histograms
    # b2d is a boolean: if True, also create 2-dimensional histograms
    # --> return the updated hists_collection
    def __create_hists_beam(
        self, name, ind, hists_collection,
        bins_h, bins_v, range_h, range_v,
        boolean=True, b2d=False, bins_2d=None
    ):
        hists_collection_temp = hists_collection
        
        names = (name.replace("*", "x"), name.replace("*", "y"))
        
        hvar = self._array_transpose(self.__output_collection[names[0]])
        vvar = self._array_transpose(self.__output_collection[names[1]])
        
        hists_collection_temp[
            "hist_%s%s"%(names[0], "" if ind is None else "_%d"%ind)
        ] = self.create_histo_1d(
            hvar if ind is None else hvar[ind],
            boolean, bins=bins_h, range=range_h
        )
        hists_collection_temp[
            "hist_%s%s"%(names[1], "" if ind is None else "_%d"%ind)
        ] = self.create_histo_1d(
            vvar if ind is None else vvar[ind],
            boolean, bins=bins_v, range=range_v
        )
        if b2d:
            hists_collection_temp[
                "hist2d_%s_%s%s"%(names[0], names[1], "" if ind is None else "_%d"%ind)
            ] = self.create_histo_2d(
                hvar if ind is None else hvar[ind], vvar if ind is None else vvar[ind],
                boolean, bins=bins_2d, range=(range_h, range_v)
            )
        
        return hists_collection_temp
        
    # wrappers for output fiels in the dataset, private - x4
    # outds_var is the output dataset field name, string
    # outcol_var_x is the name of the horizontal component in hists_collection, string
    # outcol_var_y is the name of the vertical component in hists_collection, string
    def __output_dataset_wrapper_x4_4(self, outds_var, outcol_var_x, outcol_var_y):
        self.dataset.add_vars({outds_var : np.array([
                self._array_transpose(self.__output_collection[outcol_var_x])[0],
                self._array_transpose(self.__output_collection[outcol_var_y])[0],
                self._array_transpose(self.__output_collection[outcol_var_x])[1],
                self._array_transpose(self.__output_collection[outcol_var_y])[1]
            ]).T})
    def __output_dataset_wrapper_x4_2(self, outds_var, outcol_var_x, outcol_var_y):
        self.dataset.add_vars({outds_var : np.array([
                self.__output_collection[outcol_var_x],
                self.__output_collection[outcol_var_y],
            ]).T})
        
    # wrappers for output fiels in the dataset, private - x2y2
    # outds_var is the output dataset field name, string
    # outcol_var is the corresponding name in hists_collection, string
    def __output_dataset_wrapper_x2y2_2(self, outds_var, outcol_var):
        self.dataset.add_vars(
            {outds_var : np.array(self.__output_collection[outcol_var])}
        )
    def __output_dataset_wrapper_x2y2_1(self, outds_var, outcol_var):
        self.dataset.add_vars(
            {outds_var : self.__output_collection[outcol_var]}
        )
        
    # wrappers for output fiels in the dataset, private - x1x1y1y1   
    # outds_var is the output dataset field name, string
    # outcol_var is the corresponding name in hists_collection, string
    # outcol_index is the hists_collection entry index, if None use __output_dataset_wrapper_x2y2_1
    def __output_dataset_wrapper_x1x1y1y1(self, outds_var, outcol_var, outcol_index):
        if outcol_index==None:
            self.__output_dataset_wrapper_x2y2_1(outds_var, outcol_var)
        else:
            self.dataset.add_vars(
                {outds_var : np.array(self.__output_collection[outcol_var]).T[outcol_index]}
            )
            
    # compute uncentred angular distribution centres, then rerun full_calculations_output
    # --> return the shift values: (shift_thx, shift_thy) depending on breturn
    def full_alignment_output(
        self,
        bins_thx = 100,  # binning for x angular distributions, 2-entry array or None
        bins_thy = 100,  # binning for y angular distributions, 2-entry array or None
        range_thx = None,  # range for x angular distributions, 2-entry array or None
        range_thy = None,  # range for y angular distributions, 2-entry array or None
        apar_fit_thx = None,  # amplitude start parameter for x ang. distributions (if None, estimated)
        upar_fit_thx = None,  # mean value start parameter for x ang. distributions (if None, estimated)
        spar_fit_thx = None,  # width start parameter for x ang. distributions (if None, estimated)
        apar_fit_thy = None,  # amplitude start parameter for y ang. distributions (if None, estimated)
        upar_fit_thy = None,  # mean value start parameter for y ang. distributions (if None, estimated)
        spar_fit_thy = None,  # width start parameter for y ang. distributions (if None, estimated)
        breturn = False,  # boolean: if True (False), (don't) return the shift values
    ):
        hists_collection = {}
        shifts_total = [0, 0]  
        fit_ok_global = [True, True]
        
        for iside in range(2):
            sside = "x" if iside==0 else "y"
            
            array_temp = np.array(self.__output_collection["th%s0"%sside])
            
            for istep in range(10):
            
                if self.bVerbose:
                    print("aligning side %d, step %d..."%(iside, istep))
                
                self.__output_collection["th%s"%sside] = list(array_temp)
                hists_collection.update(self.__create_hists_beam(
                    "th*", None, hists_collection,
                    bins_thx, bins_thy, range_thx, range_thy,
                    boolean=True, 
                ))            
                hist_temp = hists_collection["hist_th%s"%sside]
                par_temp, fit_ok = self._fit_hist1d_gaus(
                    hist_temp, ax=None, bplot=False,
                    apar_fit=apar_fit_thx if iside==0 else apar_fit_thy,
                    upar_fit=upar_fit_thx if iside==0 else upar_fit_thy,
                    spar_fit=spar_fit_thx if iside==0 else spar_fit_thy,
                )
                
                if not (fit_ok):
                    fit_ok_global[iside] = False
                    if self.bVerbose: print("fit failed, exiting loop...")
                    break
                
                if abs(par_temp[1])<1e-8:
                    if self.bVerbose: print("precision reached, exiting loop...")
                    break
                                    
                shifts_total[iside] += par_temp[1]
                array_temp = np.array(array_temp) - par_temp[1]

            self.dictTrackParams["shiftTh%s"%sside.title()] = shifts_total[iside]
            self.dictTrackParams["mirror%s"%sside.title()] = [False, False]
        
        if (fit_ok_global[0] & fit_ok_global[1]):
            if self.bVerbose: print("after alignment, recomputing all centred tracks...")
            self.full_calculations_output()
            
        self.dictTrackParams = deepcopy(self.__dictTrackParams_before)
                
        if breturn:
            return shifts_total
        else:
            return
        
    # process all the tracks and add results to the dataset
    def full_calculations_output(self):                    
        for iev_data, ev_data in enumerate(self.dataset.data):
            if self.bVerbose:
                if iev_data%1000==0: print("doing event #%d" % (iev_data))

            track_temp = self.cTrack(
                self.x0[iev_data], self.y0[iev_data], **self.dictTrackParams
            )
            track_temp.full_analysis()

            for out_var in self.__output_collection:
                attr_temp = track_temp.__getattribute__(out_var)
                if iev_data==0:
                    self.__output_collection[out_var] = [attr_temp]
                else:
                    self.__output_collection[out_var] += [attr_temp]
                    
        if self.outtype=="x4":
            self.__output_dataset_wrapper_x4_4("xRawMirrored", "x0", "y0")
            self.__output_dataset_wrapper_x4_4("x", "x", "y")
            self.__output_dataset_wrapper_x4_2("thxRaw", "thx0", "thy0")
            self.__output_dataset_wrapper_x4_2("thx", "thx", "thy")
            for hitproj in self.dictProjections:
                self.__output_dataset_wrapper_x4_2("xRaw"+hitproj, "x"+hitproj+"0", "y"+hitproj+"0")
                self.__output_dataset_wrapper_x4_2("x"+hitproj, "x"+hitproj, "y"+hitproj)
                    
        if self.outtype=="x2y2":
            self.__output_dataset_wrapper_x2y2_2("xRawMirrored", "x0")
            self.__output_dataset_wrapper_x2y2_2("yRawMirrored", "y0")
            self.__output_dataset_wrapper_x2y2_2("x", "x")
            self.__output_dataset_wrapper_x2y2_2("y", "y")
            self.__output_dataset_wrapper_x2y2_1("thxRaw", "thx0")
            self.__output_dataset_wrapper_x2y2_1("thyRaw", "thy0")
            self.__output_dataset_wrapper_x2y2_1("thx", "thx")
            self.__output_dataset_wrapper_x2y2_1("thy", "thy")
            for hitproj in self.dictProjections:
                self.__output_dataset_wrapper_x2y2_1("xRaw"+hitproj, "x"+hitproj+"0")
                self.__output_dataset_wrapper_x2y2_1("yRaw"+hitproj, "y"+hitproj+"0")
                self.__output_dataset_wrapper_x2y2_1("x"+hitproj, "x"+hitproj)
                self.__output_dataset_wrapper_x2y2_1("y"+hitproj, "y"+hitproj)
                
        if self.outtype=="x1x1y1y1":
            self.__output_dataset_wrapper_x1x1y1y1("xRawMirrored0", "x0", 0)
            self.__output_dataset_wrapper_x1x1y1y1("xRawMirrored1", "x0", 1)
            self.__output_dataset_wrapper_x1x1y1y1("yRawMirrored0", "y0", 0)
            self.__output_dataset_wrapper_x1x1y1y1("yRawMirrored1", "y0", 1)
            self.__output_dataset_wrapper_x1x1y1y1("x0", "x", 0)
            self.__output_dataset_wrapper_x1x1y1y1("x1", "x", 1)
            self.__output_dataset_wrapper_x1x1y1y1("y0", "y", 0)
            self.__output_dataset_wrapper_x1x1y1y1("y1", "y", 1)
            self.__output_dataset_wrapper_x1x1y1y1("thxRaw", "thx0", None)
            self.__output_dataset_wrapper_x1x1y1y1("thyRaw", "thy0", None)
            self.__output_dataset_wrapper_x1x1y1y1("thx", "thx", None)
            self.__output_dataset_wrapper_x1x1y1y1("thy", "thy", None)
            for hitproj in self.dictProjections:
                self.__output_dataset_wrapper_x1x1y1y1("xRaw"+hitproj, "x"+hitproj+"0", None)
                self.__output_dataset_wrapper_x1x1y1y1("yRaw"+hitproj, "y"+hitproj+"0", None)
                self.__output_dataset_wrapper_x1x1y1y1("x"+hitproj, "x"+hitproj, None)
                self.__output_dataset_wrapper_x1x1y1y1("y"+hitproj, "y"+hitproj, None)
                    
    # create all the main (e.g. beam profiles and angles) histograms
    # --> return a dictionary with the histogram collection
    def analyse_main_distributions(
        self,
        boolean = True,  # boolean to be applied to the dataset
        bins_x = 100,  # binning for x spatial distributions, 2-entry array or None
        bins_y = 100,  # binning for y spatial distributions, 2-entry array or None
        bins_thx = 100,  # binning for x angular distributions, 2-entry array or None
        bins_thy = 100,  # binning for y angular distributions, 2-entry array or None
        bins_xy = 100,  # binning for 2d spatial distributions, 2-entry array or None
        bins_thxy = 100,  # binning for 2d angular distributions, 2-entry array or None
        range_x = None,  # range for x spatial distributions, 2-entry array or None
        range_y = None,  # range for y spatial distributions, 2-entry array or None
        range_thx = None,  # range for x angular distributions, 2-entry array or None
        range_thy = None,  # range for y angular distributions, 2-entry array or None
    ):
        hists_collection = {}
        
        hists_collection.update(self.__create_hists_beam(
            "*0", 0, hists_collection, 
            bins_x, bins_y, range_x, range_y, b2d=True, bins_2d=bins_xy,
            boolean=boolean,
        ))
        hists_collection.update(self.__create_hists_beam(
            "*0", 1, hists_collection, 
            bins_x, bins_y, range_x, range_y, b2d=True, bins_2d=bins_xy,
            boolean=boolean,
        ))
        hists_collection.update(self.__create_hists_beam(
            "*", 0, hists_collection, 
            bins_x, bins_y, range_x, range_y, b2d=True, bins_2d=bins_xy,
            boolean=boolean,
        ))
        hists_collection.update(self.__create_hists_beam(
            "*", 1, hists_collection, 
            bins_x, bins_y, range_x, range_y, b2d=True, bins_2d=bins_xy,
            boolean=boolean,
        ))
        
        hists_collection.update(self.__create_hists_beam(
            "th*0", None, hists_collection, 
            bins_thx, bins_thy, range_thx, range_thy, b2d=True, bins_2d=bins_xy,
            boolean=boolean,
        ))
        hists_collection.update(self.__create_hists_beam(
            "th*", None, hists_collection, 
            bins_thx, bins_thy, range_thx, range_thy, b2d=True, bins_2d=bins_xy,
            boolean=boolean,
        ))
        
        for hitproj in self.dictProjections:
            hists_collection.update(self.__create_hists_beam(
                "*"+hitproj+"0", None, hists_collection, 
                bins_x, bins_y, range_x, range_y, b2d=True, bins_2d=bins_xy,
                boolean=boolean,
            ))
            hists_collection.update(self.__create_hists_beam(
                "*"+hitproj, None, hists_collection, 
                bins_x, bins_y, range_x, range_y, b2d=True, bins_2d=bins_xy,
                boolean=boolean,
            ))
        
        self.__hists_collection_latest = hists_collection
        return hists_collection
    
    # plot (and fit some of the) global distributions, with boolean --> create figure
    def plot_distributions_tracking(
        self,
        boolean = True,  # boolean to be applied to the dataset
        proj_at = None,  # dictProjections key to project the beam to, string or None (upstream tracker)
        bins_x = 100,  # binning for x spatial distributions, 2-entry array or None
        bins_y = 100,  # binning for y spatial distributions, 2-entry array or None
        bins_thx = 100,  # binning for x angular distributions, 2-entry array or None
        bins_thy = 100,  # binning for y angular distributions, 2-entry array or None
        range_x = None,  # range for x spatial distributions, 2-entry array or None
        range_y = None,  # range for y spatial distributions, 2-entry array or None
        range_thx = None,  # range for x angular distributions, 2-entry array or None
        range_thy = None,  # range for y angular distributions, 2-entry array or None
        hists_collection = None,  # a hists_collection can be directly fed in this method*
        bfit_thx0 = False,  # boolean: if True, fit the x (uncentred) angular distribution
        bfit_thy0 = False,  # boolean: if True, fit the y (uncentred) angular distribution
        bfit_thx = False,  # boolean: if True, fit the x (centred) angular distribution
        bfit_thy = False,  # boolean: if True, fit the y (centred) angular distribution
        apar_fit_thx = None,  # amplitude start parameter for x ang. distributions (if None, estimated)
        upar_fit_thx = None,  # mean value start parameter for x ang. distributions (if None, estimated)
        spar_fit_thx = None,  # width start parameter for x ang. distributions (if None, estimated)
        apar_fit_thy = None,  # amplitude start parameter for y ang. distributions (if None, estimated)
        upar_fit_thy = None,  # mean value start parameter for y ang. distributions (if None, estimated)
        spar_fit_thy = None,  # width start parameter for y ang. distributions (if None, estimated)
        figsize = (10, 9),  # figure size, 2-entry array
        figtitle = "",  # string with the figure title
        bsave = False,  # boolean: if True (False), (don't) save the figure
        outname  = "./out.jpg",  # path and name of the figure output file, string
    ):
        # * hists_collection is can be created elsewhere with analyse_main_distributions;
        #   note that some of the other arguments are overwritten
        
        if hists_collection is None:
            hists_collection = self.analyse_main_distributions(
                boolean=boolean,
                bins_x = bins_x, bins_y = bins_y,
                bins_thx = bins_thx, bins_thy = bins_thy,
                range_x = range_x, range_y = range_y,
                range_thx = range_thx, range_thy = range_thy,
            )
            
        fig, axs = plt.subplots(figsize=figsize, nrows=3, ncols=2)
        
        for i in range(2):

            ax = axs[0, i]
            hist_temp = hists_collection["hist_th%s0" % ("x" if i==0 else "y")]
            ax.grid(True)
            ax.set_title("unaligned ang., dir. %d"%i)
            ax.plot(
                hist_temp[0], hist_temp[1], drawstyle="steps-mid", lw=1, color="C0"
            )
            if (((i==0) & bfit_thx0) | ((i==1) & bfit_thy0)):
                _, _ = self._fit_hist1d_gaus(
                    hist_temp, ax=ax, bplot=True,
                    apar_fit=apar_fit_thx if i==0 else apar_fit_thy,
                    upar_fit=upar_fit_thx if i==0 else upar_fit_thy,
                    spar_fit=spar_fit_thx if i==0 else spar_fit_thy,
                    plot_color="C1",
                )    
                ax.legend()
            ax.axvline(0, c="k", ls=":", lw=1) 
            if (((i==0) & (not (range_thx is None))) | ((i==1) & (not (range_thy is None)))):
                ax.set_xlim(range_thx if i==0 else range_thy)
            
            ax = axs[1, i]
            hist_temp = hists_collection["hist_th%s" % ("x" if i==0 else "y")]
            ax.grid(True)
            ax.set_title("aligned ang., dir. %d"%i)
            ax.plot(
                hist_temp[0], hist_temp[1], drawstyle="steps-mid", lw=1, color="C0"
            )
            if (((i==0) & bfit_thx) | ((i==1) & bfit_thy)):
                _, _ = self._fit_hist1d_gaus(
                    hist_temp, ax=ax, bplot=True,
                    apar_fit=apar_fit_thx if i==0 else apar_fit_thy,
                    upar_fit=upar_fit_thx if i==0 else upar_fit_thy,
                    spar_fit=spar_fit_thx if i==0 else spar_fit_thy,
                    plot_color="C1",
                )    
                ax.legend()
            ax.axvline(0, c="k", ls=":", lw=1) 
            if (((i==0) & (not (range_thx is None))) | ((i==1) & (not (range_thy is None)))):
                ax.set_xlim(range_thx if i==0 else range_thy)
            
            ax = axs[2, i]
            ax.grid(True)
            ax.set_title("profile, dir. %d"%i)
            hist_temp = hists_collection["hist_%s_0" % ("x" if i==0 else "y")]
            ax.plot(
                hist_temp[0], hist_temp[1], 
                drawstyle="steps-mid", lw=1, color="C0", label = "at mod. 0"
            )
            hist_temp = hists_collection["hist_%s_1" % ("x" if i==0 else "y")]
            ax.plot(
                hist_temp[0], hist_temp[1], 
                drawstyle="steps-mid", lw=1, color="C1", label = "at mod. 1"
            )
            if not (proj_at is None):
                hist_temp = hists_collection["hist_%s%s" % ("x" if i==0 else "y", proj_at)]
                ax.plot(
                    hist_temp[0], hist_temp[1], 
                    drawstyle="steps-mid", lw=1, color="C2", label = "at %s"%proj_at
                )
            ax.legend()
            if (((i==0) & (not (range_x is None))) | ((i==1) & (not (range_y is None)))):
                ax.set_xlim(range_x if i==0 else range_y)
            
        fig.suptitle(figtitle)
        fig.tight_layout()

        if bsave:
            fig.savefig(outname, dpi=self.__outfig_dpi)
                
    # plot (and fit some of the) global distributions, with boolean --> create figure
    def plot_distributions_spot2d(
        self,
        boolean_d = True,  # condition on the denominator plot, boolean
        boolean_n = True,  # condition on the numerator plot, boolean
        proj_at = None,  # dictProjections key to project the beam to, string or None (upstream tracker)
        bins_xy = 100,  # binning for 2d spatial distributions, 2-entry array or None
        bins_thxy = 100,  # binning for 2d angular distributions, 2-entry array or None
        range_x = None,  # range for x spatial distributions, 2-entry array or None
        range_y = None,  # range for y spatial distributions, 2-entry array or None
        range_thx = None,  # range for x angular distributions, 2-entry array or None
        range_thy = None,  # range for y angular distributions, 2-entry array or None
        hists_collection_n = None,  # a (num.) hists_collection can be directly fed in this method*
        hists_collection_d = None,  # a (den.) hists_collection can be directly fed in this method*
        figsize = (10, 5),  # figure size, 2-entry array
        blog_d = False,  # boolean: if True, toggle z log scale on the full-beam (i.e. denominator) plot
        bcbar_ndr = False,  # boolean: if True, toggle colorbar on the efficiency (i.e. ratio) plot
        figtitle = "",  # string with the figure title
        bsave = False,  # boolean: if True (False), (don't) save the figure
        outname  = "./out.jpg",  # path and name of the figure output file, string
    ):        
        # * hists_collection is can be created elsewhere with analyse_main_distributions;
        #   note that some of the other arguments are overwritten
        
        if hists_collection_d is None:
            hists_collection_d = self.analyse_main_distributions(
                boolean=boolean_d,
                bins_xy = bins_xy, bins_thxy = bins_thxy,
                range_x = range_x, range_y = range_y,
                range_thx = range_thx, range_thy = range_thy,
            )
        if hists_collection_n is None:
            hists_collection_n = self.analyse_main_distributions(
                boolean=boolean_n,
                bins_xy = bins_xy, bins_thxy = bins_thxy,
                range_x = range_x, range_y = range_y,
                range_thx = range_thx, range_thy = range_thy,
            )
            
        fig, axs = plt.subplots(figsize=figsize, nrows=1, ncols=2)
        
        ax = axs[0]
        hist = hists_collection_d["hist2d_%s_%s" % ("x"+proj_at, "y"+proj_at)]
        self._draw_hist2d(hist, ax, blog=blog_d)
        ax.set_title("whole beam spot")
        
        ax = axs[1]
        hist_d = hists_collection_d["hist2d_%s_%s" % ("x"+proj_at, "y"+proj_at)]
        hist_n = hists_collection_n["hist2d_%s_%s" % ("x"+proj_at, "y"+proj_at)]
        with np.errstate(divide="ignore", invalid="ignore"):
            hist = [hist_d[0], hist_d[1], hist_n[2]/hist_d[2]]
        self._draw_hist2d(hist, ax, blog=False, bcbar=bcbar_ndr, fig=fig)
        ax.set_title("cut efficiency map")
        
        fig.suptitle(figtitle)
        fig.tight_layout()

        if bsave:
            fig.savefig(outname, dpi=self.__outfig_dpi)
            
########################################################################################################################

class cWaveFormsCollection(cCollection):
    def __init__(
        self,
        dataset,
        varlist,
        dictWfParams,
        bVerbose = False,
        bOutWfs = False,
    ):
        super().__init__()

        sl = __import__(__name__)
        self.cWaveForm = getattr(sl, "cWaveForm")
        
        # attributes set via input:
        
        self.dataset = dataset
        self.varlist = varlist
        self.dictWfParams = dictWfParams
        self.bVerbose = bVerbose
        self.bOutWfs = bOutWfs
        
        # calculated attributes:
        
        self.__output_collection = {}
        for var in self.varlist:
            self.__output_collection.update({var : {
                "base_mean" : [],
                "base_rms" : [],
                "ph" : [],
                "peak_time" : [],
                "charge" : [],
                "snr" : [],
            }})
            if self.bOutWfs:
                self.__output_collection[var].update({
                    "x" : [],
                    "y" : [],
                })
                
        self.__hists_collection_latest = {}
                
        self.__outfig_dpi = 200
        
    # process all the waveforms and add results to the dataset
    def full_calculations_output(self):                    
            for isch, sch in enumerate(self.varlist):

                for iev_data, ev_data in enumerate(self.dataset.data):
                    if self.bVerbose:
                        if iev_data%1000==0: print("doing channel %s, event #%d" % (sch, iev_data))

                    wf_temp = self.cWaveForm(
                        y0 = ev_data[sch], **self.dictWfParams[sch]
                    )
                    wf_temp.full_analysis()

                    for out_var in self.__output_collection[sch]:
                        attr_temp = wf_temp.__getattribute__(out_var)
                        if iev_data==0:
                            self.__output_collection[sch][out_var] = [attr_temp]
                        else:
                            self.__output_collection[sch][out_var] += [attr_temp]
                            
                self.dataset.add_vars({sch+"_out_"+k : ak.Array(v) for (k, v) in self.__output_collection[sch].items()})
    
    # create all the main (ph, time, charge) histograms --> return a dictionary with the histogram collection
    def analyse_main_distributions(
        self,
        channel,  # (waveform) variable to plot among the loaded one, string
        boolean,  # boolean to be applied to the dataset
        range_time_sig,  # time interval in which to get signal, 2-entry array
        range_time_bkg,  # time interval in which to get pedestal, 2-entry array
        b_pede_internal = True,  # boolean: if True (False), use same-event off-time (externally computed) pedestal values
        pede_ph = 0,  # pedestal value to manually shift the signal PH spectra (only used if not b_pede_internal)
        pede_charge = 0,  # pedestal value to manually shift the signal charge spectra (only used if not b_pede_internal)
        b_pede_subtract = False,  # boolean: if True, the pedestal population is also subtracted from the signal spectra
        time_var = "peak_time",  # time variable to use, string
        bins_ph = None,  # binning for PH distributions, like in hist. functions
        bins_time = None,  # binning for time distributions, like in hist. functions
        bins_charge = None,  # binning for charge distributions, like in hist. functions
        bins_nev = None,  # binning for event nr. distributions, like in hist. functions
        range_ph = None,  # range for PH distributions, 2-entry array or None
        range_time = None,  # range for time distributions, 2-entry array or None
        range_charge = None,  # range for charge distributions, 2-entry array or None
    ):
        
        dataset_temp = self.dataset.cut_copy(boolean)
        x0_base_range = self.dictWfParams[channel]["x0BaseRange"]
        sign_base = 1 if self.dictWfParams[channel]["bPositive"] else -1
        hists_collection = {}
        
        bins_time, range_time = self._tweak_bins_range(
            dataset_temp.data["%s_out_%s"%(channel, time_var)], bins_time, range_time
        )
        bins_ph, range_ph = self._tweak_bins_range(
            dataset_temp.data["%s_out_ph"%(channel)], bins_ph, range_ph
        )
        bins_charge, range_charge = self._tweak_bins_range(
            dataset_temp.data["%s_out_charge"%(channel)], bins_charge, range_charge
        )
        bins_nev, range_nev = self._tweak_bins_range(
            dataset_temp.data["index"], bins_nev, None
        )
        
        hists_collection["hist2d_ph_%s"%(time_var)] = self.create_histo_2d(
            "%s_out_ph"%(channel), "%s_out_%s"%(channel, time_var),
            boolean, bins=(bins_ph, bins_time), range=(range_ph, range_time)
        )
        hists_collection["hist_time"] =\
            self.create_histo_1d("%s_out_%s"%(channel, time_var), boolean, bins=bins_time, range=range_time)
        hists_collection["hist_ph"] =\
            self.create_histo_1d("%s_out_ph"%(channel), boolean, bins=bins_ph, range=range_ph)
        hists_collection["hist_charge"] =\
            self.create_histo_1d("%s_out_charge"%(channel), boolean, bins=bins_charge, range=range_charge)
        
        boolean_bkg = boolean &\
            (self.dataset.data["%s_out_%s"%(channel, time_var)] > range_time_bkg[0]) &\
            (self.dataset.data["%s_out_%s"%(channel, time_var)] < range_time_bkg[1])
        hists_collection["hist_time_bkg"] =\
            self.create_histo_1d("%s_out_%s"%(channel, time_var), boolean_bkg, bins=bins_time, range=range_time)
        hists_collection["hist_ph_bkg0"] =\
            self.create_histo_1d("%s_out_ph"%(channel), boolean_bkg, bins=bins_ph, range=range_ph)
        hists_collection["hist_charge_bkg0"] =\
            self.create_histo_1d("%s_out_charge"%(channel), boolean_bkg, bins=bins_charge, range=range_charge)
        
        boolean_sig = boolean &\
            (self.dataset.data["%s_out_%s"%(channel, time_var)] > range_time_sig[0]) &\
            (self.dataset.data["%s_out_%s"%(channel, time_var)] < range_time_sig[1])
        hists_collection["hist_time_sig"] =\
            self.create_histo_1d("%s_out_%s"%(channel, time_var), boolean_sig, bins=bins_time, range=range_time)
        hists_collection["hist_ph_sig0"] =\
            self.create_histo_1d("%s_out_ph"%(channel), boolean_sig, bins=bins_ph, range=range_ph)
        hists_collection["hist_charge_sig0"] =\
            self.create_histo_1d("%s_out_charge"%(channel), boolean_sig, bins=bins_charge, range=range_charge)
        
        hists_collection["hist_ph_bkg"] = hists_collection["hist_ph_bkg0"]
        hists_collection["hist_charge_bkg"] = hists_collection["hist_charge_bkg0"]
        hists_collection["hist_ph_bkg"][1] = hists_collection["hist_ph_bkg0"][1] *\
            (range_time_sig[1]-range_time_sig[0])/(range_time_bkg[1]-range_time_bkg[0])
        hists_collection["hist_charge_bkg"][1] = hists_collection["hist_charge_bkg0"][1] *\
            (range_time_sig[1]-range_time_sig[0])/(range_time_bkg[1]-range_time_bkg[0])
        
        hists_collection["hist_ph_sig"] = hists_collection["hist_ph_sig0"]
        hists_collection["hist_charge_sig"] = hists_collection["hist_charge_sig0"]
        if b_pede_internal:
            pede_ph_temp, pede_charge_temp = self.compute_pede(hists_collection, bontime=False)
            hists_collection["hist_ph_sig"][0] = hists_collection["hist_ph_sig0"][0] - pede_ph_temp
            hists_collection["hist_charge_sig"][0] = hists_collection["hist_charge_sig0"][0] - pede_charge_temp
        else:
            hists_collection["hist_ph_sig"][0] = hists_collection["hist_ph_sig0"][0] - pede_ph
            hists_collection["hist_charge_sig"][0] = hists_collection["hist_charge_sig0"][0] - pede_charge 
        if b_pede_subtract:
            hists_collection["hist_ph_sig"][1] =\
                hists_collection["hist_ph_sig0"][1] - hists_collection["hist_ph_bkg"][1]
            hists_collection["hist_charge_sig"][1] =\
                hists_collection["hist_charge_sig0"][1] - hists_collection["hist_charge_bkg"][1]
            hists_collection["hist_ph_sig"][1][hists_collection["hist_ph_sig"][1] < 0] = 0
            hists_collection["hist_charge_sig"][1][hists_collection["hist_charge_sig"][1] < 0] = 0
                   
        hists_collection["hist2d_nev_%s"%(time_var)] = self.create_histo_2d(
            "index", "%s_out_%s"%(channel, time_var),
            boolean, bins=(bins_nev, bins_time), range=(range_nev, range_time)
        )
        hists_collection["hist2d_nev_base_mean"] = self.create_histo_2d(
            "index", "%s_out_base_mean"%(channel),
            boolean, bins=(bins_nev, 100),
        )
        hists_collection["hist2d_nev_ph"] = self.create_histo_2d(
            "index", "%s_out_ph"%(channel),
            boolean, bins=(bins_nev, bins_ph), range=(range_nev, range_ph)
        )
        hists_collection["hist2d_nev_charge"] = self.create_histo_2d(
            "index", "%s_out_charge"%(channel),
            boolean, bins=(bins_nev, bins_charge), range=(range_nev, range_charge)
        )
        
        self.__hists_collection_latest = hists_collection
        return hists_collection
    
    # compute pedestal from an existing collection of distributions (created with analyse_main_distributions)
    # note: it should be used on distributions computed with b_pede_internal = False and pede_ph/charge = 0
    # hists_collection is the collection of distributions to use; if None, use the latest created
    # bontime is a boolean: if True (False) on-(off-)time pedestal is computed, i.e. from "sig" ("bkg") distributions
    def compute_pede(self, hists_collection=None, bontime=True):
        if hists_collection is None:
            hists_collection = self.__hists_collection_latest

        pedetype = "sig" if bontime else "bkg"
        
        pede_ph = \
            np.sum(hists_collection["hist_ph_%s0"%pedetype][0]*hists_collection["hist_ph_%s0"%pedetype][1]) /\
            np.sum(hists_collection["hist_ph_%s0"%pedetype][1])
        
        pede_charge = \
            np.sum(hists_collection["hist_charge_%s0"%pedetype][0]*hists_collection["hist_charge_%s0"%pedetype][1]) /\
            np.sum(hists_collection["hist_charge_%s0"%pedetype][1])
        
        return pede_ph, pede_charge
    
    # draw three 1d histograms previously stored by create_histo_1d (total, bkg, sig)
    # hist1d, hist1d_bkg, hist1d_sig are create_histo_1d output
    # ax is the destination axis in a figure
    # b_swap_axes is a boolean: is True, the plot is drawn with the axes swapped
    def __draw_hist1d_bkg_sig(self, hist1d, hist1d_bkg, hist1d_sig, ax, b_swap_axes=False, blegend=True):
        if b_swap_axes:
            ax.fill_betweenx(hist1d[0], hist1d[1], step="mid", lw=0, alpha=0.2, color="C0")
            ax.fill_betweenx(
                hist1d_bkg[0], hist1d_bkg[1], step="mid", lw=1, edgecolor="purple", facecolor="#FF000000",
                label="int. pedestal (selection)" if blegend else None,
            )
            ax.fill_betweenx(
                hist1d_sig[0], hist1d_sig[1], step="mid", lw=1, edgecolor="C1", facecolor="#FF000000",
                label="signal (selection)" if blegend else None,
            )
        else:
            ax.fill_between(hist1d[0], hist1d[1], step="mid", lw=0, alpha=0.2, color="C0")
            ax.plot(
                hist1d_bkg[0], hist1d_bkg[1], drawstyle="steps-mid", lw=1, color="purple",
                label="int. pedestal (selection)" if blegend else None,
            )
            ax.plot(
                hist1d_sig[0], hist1d_sig[1], drawstyle="steps-mid", lw=1, color="C1",
                label="signal (selection)" if blegend else None,
            )
                    
    # plot waveforms as individual curves, with boolean --> create figure
    def plot_wfs_curves(
        self,
        channel,  # (waveform) variable to plot among the loaded one, string
        boolean = True,  # boolean to be applied to the dataset
        plot_lims = None,  # plot limits, (2-entry array, 2-entry array) or None
        bbaseline = False,  # boolean: if True (False), (don't) plot baseline info
        figsize = (8, 6),  # figure size, 2-entry array
        figtitle = "",  # string with the figure title
        bsave = False,  # boolean: if True (False), (don't) save the figure
        outname  = "./out.jpg",  # path and name of the figure output file, string
    ):
        
        dataset_temp = self.dataset.cut_copy(boolean)
        x0_base_range = self.dictWfParams[channel]["x0BaseRange"]
        unit_x = self.dictWfParams[channel]["unitX"]
        unit_y = self.dictWfParams[channel]["unitY"]
        sign_base = 1 if self.dictWfParams[channel]["bPositive"] else -1
        
        plot_lims = np.array(plot_lims, dtype=object)
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.grid(True)
        ax.set_xlabel("time [%.2e s]" % unit_x)
        ax.set_ylabel("voltage [%.2e V]" % unit_y)
        
        for iev_data, ev_data in enumerate(dataset_temp.data):
            ax.plot(
                ev_data["%s_out_x"%channel], 
                ev_data["%s_out_y"%channel],
                color="C0", lw=0.2
            )

        ax.axvline(0, color="k", lw=1, ls=":")
        
        if bbaseline:
            ax.axvline(x0_base_range[0], color="red", lw=1)
            ax.axvline(x0_base_range[1], color="red", lw=1)
            ax.plot(
                x0_base_range, np.mean(dataset_temp.data["%s_out_base_mean"%channel])*np.ones(2) * sign_base,
                color="red", lw=1, label="(mean) baseline calculation"
            )
            ax.plot(
                x0_base_range,
                (
                    np.mean(dataset_temp.data["%s_out_base_mean"%channel]) +\
                    np.mean(dataset_temp.data["%s_out_base_rms"%channel])
                )*np.ones(2) * sign_base,
                color="red", lw=1, ls=":"
            )
            ax.plot(
                x0_base_range,
                (
                    np.mean(dataset_temp.data["%s_out_base_mean"%channel]) -\
                    np.mean(dataset_temp.data["%s_out_base_rms"%channel])
                )*np.ones(2) * sign_base,
                color="red", lw=1, ls=":"
            )
            ax.legend()

        if not (plot_lims is None):
            ax.set_xlim(plot_lims[0])
            ax.set_ylim(plot_lims[1])
            
        fig.suptitle(figtitle)
        fig.tight_layout()
        
        if bsave:
            fig.savefig(outname, dpi=self.__outfig_dpi)
            
    # plot waveforms in a single 2d histogram, with boolean --> create figure
    def plot_wfs_hist2d(
        self,
        channel,  # (waveform) variable to plot among the loaded one, string
        boolean = True,  # boolean to be applied to the dataset
        plot_lims = None,  # plot limits, (2-entry array, 2-entry array) or None
        nbins = (100, 100),  # nr. of bins, integer or (integer, integer) or None
        bbaseline = False,  # boolean: if True (False), (don't) plot baseline info
        figsize = (8, 6),  # figure size, 2-entry array
        figtitle = "",  # string with the figure title
        blog = False,  # blog is a boolean: if True, toggle z log scale
        bsave = False,  # boolean: if True (False), (don't) save the figure
        outname  = "./out.jpg",  # path and name of the figure output file, string
    ):
        
        dataset_temp = self.dataset.cut_copy(boolean)
        x0_base_range = self.dictWfParams[channel]["x0BaseRange"]
        unit_x = self.dictWfParams[channel]["unitX"]
        unit_y = self.dictWfParams[channel]["unitY"]
        sign_base = 1 if self.dictWfParams[channel]["bPositive"] else -1
        
        plot_lims = np.array(plot_lims, dtype=object)
        _, plot_lims[0] = self._tweak_bins_range(
            dataset_temp.data["%s_out_x"%channel], None, plot_lims[0]
        )
        _, plot_lims[1] = self._tweak_bins_range(
            dataset_temp.data["%s_out_y"%channel], None, plot_lims[1]
        )
        
        fig, ax = plt.subplots(figsize=figsize)
        ax.grid(True)
        ax.set_xlabel("time [%.2e s]" % unit_x)
        ax.set_ylabel("voltage [%.2e V]" % unit_y)
        
        hist_temp = self.create_histo_2d(
            ak.flatten(dataset_temp.data["%s_out_x"%channel]),
            ak.flatten(dataset_temp.data["%s_out_y"%channel]),
            bins=nbins, range=plot_lims,
        )
        self._draw_hist2d(hist_temp, ax=ax, blog=blog)

        ax.axvline(0, color="k", lw=1, ls=":")
        
        if bbaseline:
            ax.axvline(x0_base_range[0], color="red", lw=1)
            ax.axvline(x0_base_range[1], color="red", lw=1)
            ax.plot(
                x0_base_range, np.mean(dataset_temp.data["%s_out_base_mean"%channel])*np.ones(2) * sign_base,
                color="red", lw=1, label="(mean) baseline calculation"
            )
            ax.plot(
                x0_base_range,
                (
                    np.mean(dataset_temp.data["%s_out_base_mean"%channel]) +\
                    np.mean(dataset_temp.data["%s_out_base_rms"%channel])
                )*np.ones(2) * sign_base,
                color="red", lw=1, ls=":"
            )
            ax.plot(
                x0_base_range,
                (
                    np.mean(dataset_temp.data["%s_out_base_mean"%channel]) -\
                    np.mean(dataset_temp.data["%s_out_base_rms"%channel])
                )*np.ones(2) * sign_base,
                color="red", lw=1, ls=":"
            )
            ax.legend()

        if not (plot_lims is None):
            ax.set_xlim(plot_lims[0])
            ax.set_ylim(plot_lims[1])
        
        fig.suptitle(figtitle)
        fig.tight_layout()
        
        if bsave:
            fig.savefig(outname, dpi=self.__outfig_dpi)
    
    # plot (and fit some of the) global distributions, with boolean --> create figure
    def plot_distributions_summary(
        self,
        channel,  # (waveform) variable to plot among the loaded one, string
        range_time_sig,  # time interval in which to get signal, 2-entry array
        range_time_bkg,  # time interval in which to get pedestal, 2-entry array
        boolean = True,  # boolean to be applied to the dataset
        time_var = "peak_time",  # time variable to use, string
        range_ph = None,  # range for PH distributions, 2-entry array or None
        range_time = None,  # range for time distributions, 2-entry array or None
        range_charge = None,  # range for charge distributions, 2-entry array or None
        bins_ph = None,  # binning for PH distributions, like in hist. functions
        bins_time = None,  # binning for time distributions, like in hist. functions
        bins_charge = None,  # binning for charge distributions, like in hist. functions
        hists_collection = None,  # a hists_collection can be directly fed in this method*
        b_pede_internal = True,  # boolean: if True (False), use same-event off-time (externally computed) pedestal values
        pede_ph = 0,  # pedestal value to manually shift the signal PH spectra (only used if not b_pede_internal)
        pede_charge = 0,  # pedestal value to manually shift the signal charge spectra (only used if not b_pede_internal)
        b_pede_subtract = False,  # boolean: if True, the pedestal population is also subtracted from the signal spectra
        bfit_ph = False,  # boolean: if True, fit the PH signal distribution
        bfit_charge = False,  # boolean: if True, fit the charge signal distribution
        apar_fit_ph = None,  # PH amplitude start parameter (if None, estimated)
        upar_fit_ph = None,  # PH mean value start parameter (if None, estimated)
        spar_fit_ph = None,  # PH width start parameter (if None, estimated)
        apar_fit_charge = None,  # charge amplitude start parameter (if None, estimated)
        upar_fit_charge = None,  # charge mean value start parameter (if None, estimated)
        spar_fit_charge = None,  # charge width start parameter (if None, estimated)
        figsize = (14, 9),  # figure size, 2-entry array
        blog_ph_charge = True,  # boolean: if True, toggle log scale on PH and charge 1d plots
        blog_time = True,  # boolean: if True, toggle log scale on time 1d plots
        blogz = True,  # boolean: if True, toggle z log scale in 2d plot
        figtitle = "",  # string with the figure title
        bsave = False,  # boolean: if True (False), (don't) save the figure
        outname  = "./out.jpg",  # path and name of the figure output file, string
    ):
        # * hists_collection is can be created elsewhere with analyse_main_distributions;
        #   note that some of the other arguments are overwritten
        
        dataset_temp = self.dataset.cut_copy(boolean)
        x0_base_range = self.dictWfParams[channel]["x0BaseRange"]
        unit_ph = self.dictWfParams[channel]["unitY"]
        unit_time = self.dictWfParams[channel]["unitX"]
        unit_charge = unit_ph * unit_time
        
        bins_time, range_time = self._tweak_bins_range(
            dataset_temp.data["%s_out_%s"%(channel, time_var)], bins_time, range_time
        )
        bins_ph, range_ph = self._tweak_bins_range(
            dataset_temp.data["%s_out_ph"%(channel)], bins_ph, range_ph
        )
        bins_charge, range_charge = self._tweak_bins_range(
            dataset_temp.data["%s_out_charge"%(channel)], bins_charge, range_charge
        )
        
        if hists_collection is None:
            hists_collection = self.analyse_main_distributions(
                channel=channel, boolean=boolean,
                range_time_sig=range_time_sig, range_time_bkg=range_time_bkg, time_var=time_var, 
                range_ph=range_ph, range_time=range_time, range_charge=range_charge,  
                bins_ph=bins_ph, bins_time=bins_time, bins_charge=bins_charge,
                b_pede_internal=b_pede_internal, pede_ph=pede_ph, pede_charge=pede_charge, b_pede_subtract=b_pede_subtract,
            )

        fig, axs = plt.subplots(figsize=figsize, nrows=2, ncols=2)

        ax = axs[0, 0]
        self._draw_hist2d(hists_collection["hist2d_ph_%s"%(time_var)], ax, blog=blogz)
        ax.axhline(range_time_sig[0], color="C1", lw=1, label="signal (selection)")
        ax.axhline(range_time_sig[1], color="C1", lw=1)
        ax.axhline(range_time_bkg[0], color="purple", lw=1, label="ext. pedestal (sel . interval)")
        ax.axhline(range_time_bkg[1], color="purple", lw=1)
        ax.axvline(0, color="k", lw=1, ls=":")
        ax.axhline(0, color="k", lw=1, ls=":")
        ax.axhline(x0_base_range[0], color="red", lw=1, label="baseline (selection)")
        ax.axhline(x0_base_range[1], color="red", lw=1)
        if not (range_ph is None):
            ax.set_xlim((range_ph[0], range_ph[1]))
        if not (range_time is None):
            ax.set_ylim((range_time[0], range_time[1]))
        ax.grid(True)
        ax.set_xlabel("PH [%.2e V]" % unit_ph)
        ax.set_ylabel("time [%.2e s]" % unit_time)
        ax.legend()
        
        ax = axs[0, 1]
        self.__draw_hist1d_bkg_sig(
            hists_collection["hist_time"], 
            hists_collection["hist_time_bkg"], 
            hists_collection["hist_time_sig"], 
            ax, b_swap_axes=True, blegend=False,
        )
        ax.axhline(0, color="k", lw=1, ls=":")
        ax.axhline(x0_base_range[0], color="red", lw=1, label="baseline (selection)")
        ax.axhline(x0_base_range[1], color="red", lw=1)
        if not (range_time is None):
            ax.set_ylim((range_time[0], range_time[1]))
        ax.set_xscale("log" if blog_time else "linear")
        ax.set_ylabel("time [%.2e s]" % unit_time)
        ax.grid(True)
        
        ax = axs[1, 0]
        self.__draw_hist1d_bkg_sig(
            hists_collection["hist_ph"], 
            hists_collection["hist_ph_bkg"], 
            hists_collection["hist_ph_sig"], 
            ax, blegend=False,
        )
        ax.axvline(0, color="k", lw=1, ls=":")
        if not (range_ph is None):
            ax.set_xlim((range_ph[0], range_ph[1]))
        ax.set_yscale("log" if blog_ph_charge else "linear")
        ax.set_xlabel("PH [%.2e V]" % unit_ph)
        ax.grid(True)
        if bfit_ph:
            _, _ = self._fit_hist1d_landau(
                hists_collection["hist_ph_sig"], ax=ax, bplot=True,
                apar_fit=apar_fit_ph, upar_fit=upar_fit_ph, spar_fit=spar_fit_ph,
                plot_color="green",
            )        
            ax.legend()

        ax = axs[1, 1]
        self.__draw_hist1d_bkg_sig(
            hists_collection["hist_charge"], 
            hists_collection["hist_charge_bkg"], 
            hists_collection["hist_charge_sig"], 
            ax, blegend=False,
        )
        ax.axvline(0, color="k", lw=1, ls=":")
        if not (range_charge is None):
            ax.set_xlim((range_charge[0], range_charge[1]))
        ax.set_yscale("log" if blog_ph_charge else "linear")
        ax.set_xlabel("charge [%.2e C]" % unit_charge)
        ax.grid(True)
        if bfit_charge:
            _, _ = self._fit_hist1d_landau(
                hists_collection["hist_charge_sig"], ax=ax, bplot=True,
                apar_fit=apar_fit_charge, upar_fit=upar_fit_charge, spar_fit=spar_fit_charge,
                plot_color="green",
            )        
            ax.legend()
        
        fig.suptitle(figtitle)
        fig.tight_layout()
        
        if bsave:
            fig.savefig(outname, dpi=self.__outfig_dpi)
        
    # plot trends (over the event nr.) of the global distributions, with boolean --> create figure
    def plot_distribution_trends(
        self,
        channel,  # (waveform) variable to plot among the loaded one, string
        range_time_sig,  # time interval in which to get signal, 2-entry array
        range_time_bkg,  # time interval in which to get pedestal, 2-entry array
        boolean = True,  # boolean to be applied to the dataset
        time_var = "peak_time",  # time variable to use, string
        range_ph = None,  # range for PH distributions, 2-entry array or None
        range_time = None,  # range for time distributions, 2-entry array or None
        range_charge = None,  # range for charge distributions, 2-entry array or None
        bins_ph = None,  # binning for PH distributions, like in hist. functions
        bins_time = None,  # binning for time distributions, like in hist. functions
        bins_charge = None,  # binning for charge distributions, like in hist. functions
        bins_nev = None,  # binning for event nr. distributions, like in hist. functions
        hists_collection = None,  # a hists_collection can be directly fed in this method*
        b_pede_internal = True,  # boolean: if True (False), use same-event off-time (externally computed) pedestal values
        pede_ph = 0,  # pedestal value to manually shift the signal PH spectra (only used if not b_pede_internal)
        pede_charge = 0,  # pedestal value to manually shift the signal charge spectra (only used if not b_pede_internal)
        b_pede_subtract = False,  # boolean: if True, the pedestal population is also subtracted from the signal spectra
        figsize = (14, 9),  # figure size, 2-entry array
        blog = False,  # boolean: if True, toggle z log scale
        figtitle = "",  # string with the figure title
        bsave = False,  # boolean: if True (False), (don't) save the figure
        outname  = "./out.jpg",  # path and name of the figure output file, string
    ):
        # * hists_collection is can be created elsewhere with analyse_main_distributions;
        #   note that some of the other arguments are overwritten
        
        dataset_temp = self.dataset.cut_copy(boolean)
        unit_ph = self.dictWfParams[channel]["unitY"]
        unit_time = self.dictWfParams[channel]["unitX"]
        unit_charge = unit_ph * unit_time
        
        bins_time, range_time = self._tweak_bins_range(
            dataset_temp.data["%s_out_%s"%(channel, time_var)], bins_time, range_time
        )
        bins_ph, range_ph = self._tweak_bins_range(
            dataset_temp.data["%s_out_ph"%(channel)], bins_ph, range_ph
        )
        bins_charge, range_charge = self._tweak_bins_range(
            dataset_temp.data["%s_out_charge"%(channel)], bins_charge, range_charge
        )
        bins_nev, _ = self._tweak_bins_range(
            dataset_temp.data["index"], bins_nev, 0
        )
        
        if hists_collection is None:
            hists_collection = self.analyse_main_distributions(
                channel=channel, boolean=boolean,
                range_time_sig=range_time_sig, range_time_bkg=range_time_bkg, time_var=time_var, 
                range_ph=range_ph, range_time=range_time, range_charge=range_charge,  
                bins_ph=bins_ph, bins_time=bins_time, bins_charge=bins_charge, bins_nev=bins_nev,
                b_pede_internal=b_pede_internal, pede_ph=pede_ph, pede_charge=pede_charge, b_pede_subtract=b_pede_subtract,
            )

        fig, axs = plt.subplots(figsize=figsize, nrows=2, ncols=2)
    
        ax = axs[0, 0]
        ax.grid(True)
        self._draw_hist2d(hists_collection["hist2d_nev_%s"%(time_var)], ax, blog=blog)
        ax.set_ylabel("time [%.2e s]" % unit_time)

        ax = axs[0, 1]
        ax.grid(True)
        self._draw_hist2d(hists_collection["hist2d_nev_base_mean"], ax, blog=blog)
        ax.set_ylabel("baseline [%.2e V]" % unit_ph)

        ax = axs[1, 0]
        ax.grid(True)
        self._draw_hist2d(hists_collection["hist2d_nev_ph"], ax, blog=blog)
        ax.set_ylabel("PH [%.2e V]" % unit_ph)

        ax = axs[1, 1]
        ax.grid(True)
        self._draw_hist2d(hists_collection["hist2d_nev_charge"], ax, blog=blog)
        ax.set_ylabel("charge [%.2e C]" % unit_charge)

        fig.supxlabel("event nr.")

        fig.suptitle(figtitle)
        fig.tight_layout()

        if bsave:
            fig.savefig(outname, dpi=self.__outfig_dpi)        