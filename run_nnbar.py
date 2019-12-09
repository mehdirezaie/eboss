#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import fitsio as ft
import pandas as pd

import sys
sys.path.append('/home/mehdi/github/LSSutils')
from LSSutils.stats import nnbar 
from LSSutils.utils import flux_to_mag
from LSSutils.catalogs.combinefits import EBOSSCAT


plt.rc('axes.spines', right=False, top=False)


def chi2(*arrays):
    _,y,ye = arrays
    res = (y-1)/ye
    return np.sum(res*res)





nside  = 256
ixcols = {'u':0, 'g':1, 'r':2, 'i':3 ,'z':4}



    
from argparse import ArgumentParser
ap = ArgumentParser(description='NNbar')
ap.add_argument('--hemi',    default='NGC')
ap.add_argument('--version', default='7_1')
ap.add_argument('--branch',  default='')
ap.add_argument('--cut',     default='z')
ap.add_argument('--cache', action='store_true')
ns = ap.parse_args()    
    
sample      = 'QSO'
hemi        = ns.hemi
version     = ns.version
branch      = ns.branch
column      = ns.cut
run_nnbar   = ns.cache # once
    
    
if column == 'z':
    zcuts  = {'low':[0.8, 1.3],
              'middle':[1.3, 1.7],
              'high':[1.7, 2.2],
              'all':[0.8, 2.2]}
elif column == 'imag':
    zcuts  = {'low':[10, 19.9],
              'middle0':[19.9, 20.6],
              'middle1':[20.6, 21.1],
              'high':[21.1, 30],
              'all':[10, 30]}
else:
    raise ValueError('column not defined')
    
path        ='/home/mehdi/data/eboss/v' + version + '/' + branch
data_name   = path + 'eBOSS_'+sample+'_clustering_'+hemi+'_v'+version+'.dat.fits'
random_name = path + 'eBOSS_'+sample+'_clustering_'+hemi+'_v'+version+'.ran.fits'
nnbar_name  = path + 'NNBAR_'+sample+'_'+hemi+'_'+column+'.npy'
plot_name   = path + 'NNBAR_'+sample+'_'+hemi+'_'+column+'.pdf'

if run_nnbar:
    sysmaps = pd.read_hdf('/home/mehdi/data/eboss/sysmaps/SDSS_HI_imageprop_nside256.h5')
    print('Systematics :', sysmaps.columns)


    data   = EBOSSCAT([data_name],
                   weights=['weight_noz', 'weight_cp', 'weight_fkp', 'weight_systot'])
    random = EBOSSCAT([random_name],
                   weights=['weight_noz', 'weight_cp', 'weight_fkp', 'weight_systot'])

    results = {}
    for sysmap_name in sysmaps.columns:
        print(sysmap_name, end=' ')

        results[sysmap_name] = {}
        # read and prepare the map
        if 'depth' in sysmap_name:
            #print(sysmap_name.split('_'))
            band = sysmap_name.split('_')[-1]
            #print(ixcols[band])        
            #print('apply ext. coorection')
            sysmap_i = flux_to_mag(sysmaps[sysmap_name], ixcols[band], sysmaps['ebv']) # ugriz
        else:
            sysmap_i = sysmaps[sysmap_name]

        # read data and random
        for zcut_i in zcuts.keys():
            print(zcut_i)

            data.apply_zcut(zcuts=zcuts[zcut_i], column=column)
            data.project2hp(nside=nside)

            random.apply_zcut(zcuts=zcuts[zcut_i], column=column)
            random.project2hp(nside=nside)

            mask = (random.galm>0) & np.isfinite(sysmap_i)
            nnbar_i = nnbar.NNBAR(data.galm, random.galm, 
                                  mask, sysmap_i,
                                  nbins=6)
                                  #binning='simple')
            nnbar_i.run(njack=10)
            results[sysmap_name][zcut_i] = (0.5*(nnbar_i.output['bin_edges'][1:]\
                                                 +nnbar_i.output['bin_edges'][:-1]),
                                            nnbar_i.output['nnbar'],
                                            nnbar_i.output['nnbar_err'])        

    np.save(nnbar_name, results)
else:
    results = np.load(nnbar_name, allow_pickle=True).item()



nrows = len(results)//4 if len(results)%4==0 else len(results)//4+1
color = ['k', 'b', 'r', 'purple', 'g', 'orange']
marker= ['o', '^', '*', 's', '+', '.']
chi2l = {}
fig, ax = plt.subplots(ncols=4, nrows=nrows, figsize=(16, 3*nrows),
                      sharey=True)
fig.subplots_adjust(hspace=0.5)
ax = ax.flatten()
ax[0].set_ylim(0.95, 1.05)

sysmaps_columns = list(results.keys())
splits = list(results[sysmaps_columns[0]].keys())
for j, key_j in enumerate(splits):
    chi2t = 0
    for i, key_i in enumerate(sysmaps_columns):
        chi2_i = chi2(*results[key_i][key_j])
        chi2t += chi2_i
        ax[i].text(0.1+j*0.2, 0.9, '{:.1f}'.format(chi2_i),
                  color=color[j],
                 transform=ax[i].transAxes)        
        ax[i].errorbar(*results[key_i][key_j], color=color[j], marker=marker[j])
        if j==0:ax[i].set(xlabel=key_i) 
    chi2l[key_j] = chi2t
    

iend = len(results)
for c,key_c in enumerate(chi2l.keys()):
    ax[iend].text(0.1, 0.9-c*0.1, '{} : {:.1f}'.format(key_c, chi2l[key_c]),
                  color=color[c],
                 transform=ax[iend].transAxes)
plt.savefig(plot_name)

print('done!')
