import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
import os
import fitsio as ft
import healpy as hp
import numpy as np
from   glob import glob
import pandas as pd
import seaborn as sns


def hyper_params_data(files1=glob('/Volumes/TimeMachine/data/eboss/v6/results/ablation/*.log_*.npy'), tl=['eBOSS QSO V6'], verbose=False):
    mpl.rcParams.update(mpl.rcParamsDefault)
    params = {
    'axes.spines.right':True,
    'axes.spines.top':True,
    'axes.labelsize': 15,
    #'text.fontsize': 8,
    'legend.fontsize': 15,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'text.usetex': False,
    'figure.figsize': [4, 3],
    'font.family':'serif',
    'font.size':12
    }    
    plt.rcParams.update(params)      
    def get_all(ablationlog):
        d = np.load(ablationlog).item()
        indices = None
        for il, l in enumerate(d['validmin']):
            m = (np.array(l) - d['RMSEall']) > 0.0
            #print(np.any(m), np.all(m))
            if np.all(m):
                #print(il, d['indices'][il])
                #print(il, [lbs[m] for m in d['indices'][il]])
                #break
                indices = d['indices'][il]
                break
            if (il == len(d['validmin'])-1) & (np.any(m)):
                indices = [d['indices'][il][-1]]       
        # return either None or indices
        FEAT    = d['importance'] + [i for i in range(17)\
              if i not in d['importance']]
        if indices is not None:
            return FEAT[17-len(indices):]
        else:
            return FEAT[17:]
    
    def get_axes(files, verbose=False):    
        axes = []
        for filei in files:
            axi = get_all(filei)
            if verbose:print(axi)
            if axi is not None:
                axes.append(axi)
            else:
                axes.append(np.nan)
        return axes
    
    if verbose:print(files1)
    axes1 = get_axes(files1, verbose=verbose)
    
    def add_plot(axes, ax, **kw):
        
        m = 0
        for i in range(len(axes)):
            if axes[i] is np.nan:
                continue
            else:
                #print(axes[i])                
                n = len(axes[i])
                colors = np.array([plt.cm.Reds(i/n) for i in range(n)])
                m += n
                for j in range(n):
                    ax.scatter(i, axes[i][j], c=colors[j], marker='o', **kw)    
        

    #labels = ['EBV', 'lnHI', 'nstar']
    #labels += [''.join((s,'-',b)) for s in ['depth', 'seeing', 'skymag', 'exptime', 'mjd']\
    #           for b in 'rgz']
    labels = ['sky_g', 'sky_r', 'sky_i', 'sky_z', 
        'depth_g', 'depth_r', 'depth_i','depth_z',
        'psf_g','psf_r', 'psf_i', 'psf_z',
        'w1_med', 'w1_covmed',
        'star_density', 'ebv', 'airmass']
    fig, ax = plt.subplots(ncols=1, sharey=True, figsize=(6, 4))
    ax = [ax]
    add_plot(axes1, ax[0])
    ax[0].set_yticks(np.arange(17))
    ax[0].set_yticklabels(labels)
    ax[0].set_xticks(np.arange(5))
    ax[0].set_xticklabels(['1', '2', '3', '4', '5'])

    for i,axi in enumerate(ax):
        #axi.set_title(tl[i])
        axi.grid()
        axi.set_xlabel(tl[i]+' Partition-ID')    
    #plt.savefig('./figs/hyper-params_data.pdf', bbox_inches='tight')
    plt.show()