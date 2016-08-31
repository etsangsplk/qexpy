import scipy.optimize as sp
import numpy as np
import qexpy.error as qe
import qexpy.utils as qu
import qexpy.fitting as qf

from math import pi
import bokeh.plotting as bp
import bokeh.io as bi
import bokeh.models as mo

CONSTANT = qu.number_types
ARRAY = qu.array_types

def plot_dataset(figure, dataset, residual=False, data_color='black'):
    '''Given a bokeh figure, this will add data points with errors from the dataset'''
  
    xdata = dataset.xdata
    xerr = dataset.xerr
    data_name = dataset.name
    
    if residual is True and dataset.nfits>0:
        ydata = dataset.yres[-1].get_means()
        yerr = dataset.yres[-1].get_stds()
        data_name=None
    else:
        ydata = dataset.ydata
        yerr = dataset.yerr
     
    add_points_with_error_bars(figure, xdata, ydata, xerr, yerr, data_color, data_name)
    
def add_points_with_error_bars(figure, xdata, ydata, xerr=None, yerr=None, data_color='black', data_name='dataset'):
    '''Add data points to a bokeh plot. If the errors are given as numbers, 
    the same error bar is assume for all data points'''
    
    
    _xdata, _ydata, _xerr, _yerr = make_np_arrays(xdata,ydata,xerr,yerr)  
    
    if _xdata.size != _ydata.size:
        print("Error: x and y data must have the same number of points")
        return None 
    
    #Draw points:    
    figure.circle(_xdata, _ydata, color=data_color, size=2, legend=data_name)

    if isinstance(_xerr,np.ndarray) or isinstance(_yerr,np.ndarray):
        #Add error bars
        for i in range(_xdata.size):
            
            xcentral = [_xdata[i], _xdata[i]]
            ycentral = [_ydata[i], _ydata[i]]
            
            #x error bar, if the xerr argument was not none
            if xerr is not None:
                xends = []
                if _xerr.size == _xdata.size and _xerr[i]>0:
                    xends = [_xdata[i]-_xerr[i], _xdata[i]+_xerr[i]]
                elif _xerr.size == 1 and _xerr[0]>0:
                    xends = [_xdata[i]-_xerr[0], _xdata[i]+_xerr[0]]
                else:                    
                    pass
                
                if len(xends)>0:                    
                    figure.line(xends,ycentral, color=data_color)
                    #winglets on x error bar:
                    figure.rect(x=xends, y=ycentral, height=5, width=0.2,
                        height_units='screen', width_units='screen',
                        color=data_color)
                
            #y error bar    
            if yerr is not None:
                yends=[]
                if _yerr.size == _ydata.size and _yerr[i]>0:
                    yends = [_ydata[i]-_yerr[i], _ydata[i]+_yerr[i]]
                elif _yerr.size == 1 and _yerr[i]>0:
                    yends = [_ydata[i]-_yerr[0], _ydata[i]+_yerr[0]]
                else:
                    pass
                if len(yends)>0:          
                    figure.line(xcentral, yends, color=data_color)
                    #winglets on y error bar:
                    figure.rect(x=xcentral, y=yends, height=0.2, width=5,
                        height_units='screen', width_units='screen',
                        color=data_color)
                
def make_np_arrays(*args):
    '''Return a tuple where all of the arguments have been converted into 
    numpy arrays'''
    np_tuple=()
    for arg in args:
        if isinstance(arg,np.ndarray):
            np_tuple = np_tuple +(arg,)
        elif isinstance(arg, list):
            np_tuple = np_tuple +(np.array(arg),)
        elif isinstance(arg, qu.number_types):
            np_tuple = np_tuple +(np.array([arg]),)
        else:
            np_tuple = np_tuple +(np.array([None]),)
    return np_tuple
    
def plot_function(figure, function, xdata, fpars=None, n=100, legend_name=None, color='black', errorbandfactor=1.0):
    '''Plot a function evaluated over the range of xdata'''
    xvals = np.linspace(min(xdata), max(xdata), n)
    
    if fpars is None:
        fvals = function(xvals)
    elif isinstance(fpars, qe.Measurement_Array):
        recall = qe.Measurement.minmax_n
        qe.Measurement.minmax_n=1
        fmes = function(xvals, *(fpars))
        fvals = fmes.get_means()
        qe.Measurement.minmax_n=recall
    elif isinstance(fpars,(list, np.ndarray)):
        fvals = function(xvals, *fpars)
    else:
        print("Error: unrecognized parameters for function")
        pass
    figure.line(xvals, fvals, legend=legend_name, line_color=color)
    
    #Add error band
    if isinstance(fpars, qe.Measurement_Array):
        ymax = fmes.get_means()+errorbandfactor*fmes.get_stds()
        ymin = fmes.get_means()-errorbandfactor*fmes.get_stds()

        figure.patch(x=np.append(xvals,xvals[::-1]),y=np.append(ymax,ymin[::-1]),
                     fill_alpha=0.3,
                     fill_color=color,
                     line_alpha=0.0,
                     legend=legend_name)
       
        

