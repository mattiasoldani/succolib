from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np

from ..succolib import fLandau, fGaus

########################################################################################################################

class cCollection:
    # note: this is just a dependency for actual event collections
    def __init__(self):
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
        fit_func = fLandau
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
        fit_func = fGaus
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