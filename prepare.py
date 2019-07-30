#
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

# PATHS to my storage
# mehdi  @ cori
# rezaie @ OU iMac
HOME    = os.getenv('HOME')
USER    = os.getenv('USER')
sys.path.append(HOME + '/github/SYSNet/src')
import utils as ut

dirs    = dict(rezaie='/Volumes/TimeMachine/data/', mehdi='/global/cscratch1/sd/mehdi/')
scratch = dirs[USER]
print('home is {}'.format(HOME))



class CAT(object):
    '''
        Class to facilitate reading eBOSS cats
    '''
    def __init__(self, gals, weights=['weight_noz', 'weight_cp']):
        #
        print('len of gal cats %d'%len(gals))
        gal = []
        for gali in gals:
            gald = ft.read(gali, lower=True)
            gal.append(gald)
            
        #    
        #
        gal  = np.concatenate(gal)
        self.cols = gal.dtype.names
        self.num  = gal['ra'].size
        self.ra   = gal['ra']
        self.dec  = gal['dec']
        self.z    = gal['z']
        self.nz   = gal['nz']
        #
        #
        print('num of gal obj %d'%self.num)
        value     = np.ones(self.num)
        for weight_i in weights:
            if weight_i in self.cols:
                value *= gal[weight_i]
            else:
                print('col %s not in columns'%weight_i)
        #
        self.w = value
        
    def apply_zcut(self, zcuts=[None, None]):
        #
        # if no limits were provided
        zmin = self.z.min()
        zmax = self.z.max()
        if (zcuts[0] is None):
            zcuts[0] = zmin-1.e-7
        if (zcuts[1] is None):
            zcuts[1] = zmax+1.e-7
        print('going to apply z-cuts : {}'.format(zcuts))
        #
        #
        zmask    = (self.z > zcuts[0]) & (self.z < zcuts[1])
        self.z   = self.z[zmask]
        self.ra  = self.ra[zmask]
        self.w   = self.w[zmask]
        self.nz  = self.nz[zmask]
        self.num = self.z.size 
        
    def project2hp(self, nside=512):
        print('projecting into a healpix map with nside of %d'%nside)
        self.galm = ut.hpixsum(nside, self.ra, self.dec, value=self.w)
        
    def writehp(self, filename, overwrite=True):
        if os.path.isfile(filename):
            print('%s already exists'%filename, end=' ')
            if not overwrite:
                print('please change the filename!')
                return
            else:
                print('going to rewrite....')
        hp.write_map(filename, self.galm, overwrite=True, fits_IDL=False)
            
    def plot_hist(self, titles=['galaxy map', 'Ngal distribution']):
        fig, ax = plt.subplots(ncols=2, figsize=(8,3))
        plt.sca(ax[0])
        hp.mollview(self.galm, title=titles[0], hold=True)
        ax[1].hist(self.galm[self.galm!=0.0], histtype='step')
        ax[1].text(0.7, 0.8, r'%.1f $\pm$ %.1f'%(np.mean(self.galm[self.galm!=0.0]),\
                                          np.std(self.galm[self.galm!=0.0], ddof=1)),
                  transform=ax[1].transAxes)
        ax[1].set_yscale('log')
        ax[1].set_title(titles[1])
        plt.show()
        
        
        
class combinemaps(object):
    #
    def __init__(self, galf, ranf, sysmapf):
        self.galm = hp.read_map(galf, verbose=False)
        self.ranm = hp.read_map(ranf, verbose=False)
        self.sysm = ft.read(sysmapf, lower=True)
        self.cols = self.sysm.dtype.names
        print('attributes : {}'.format(self.cols))
        
    def maketable(self, mask=None, cols=None, ran_cut=0):
        if cols is None:
            cols = self.cols
            
        if mask is None:
            mask = self.ranm > ran_cut
        self.table = {'ngal':self.galm.astype('f8'), 
                      'nran':self.ranm.astype('f8'),
                      'mask':mask}
        #
        print('total mask ran > %d : %d'%(ran_cut, mask.sum()))
        for col_i in cols:
            if col_i in self.cols:
                self.table[col_i] = self.sysm[col_i].astype('f8')
                mask &= ~np.isnan(self.sysm[col_i].astype('f8'))
            else:
                print('%s not available'%col_i)

        #
        print('total mask after nan maps : %d'%mask.sum())
        self.table = pd.DataFrame(self.table)
        self.table.replace([np.inf, -np.inf], np.nan, inplace=True)
        print('Info : ', self.table.info())
        
    def to_hdf(self, filename, label, overwrite=True, mode='w', format='fixed', **kwargs):
        if os.path.isfile(filename):
            print('%s already exists'%filename, end=' ')
            if not overwrite:
                print('please change the filename!')
                return
            else:
                print('going to rewrite....')
        print(**kwargs)
        self.table.to_hdf(filename, 'qso_hpsyst', **kwargs)
        
    def plot_corrmax(self, vlim=[-0.3, 0.3]):
        mpl.rcParams.update(mpl.rcParamsDefault)
        params = {
        'axes.spines.right':True,
        'axes.spines.top':True,
        'axes.labelsize': 8,
        #'text.fontsize': 8,
        'legend.fontsize': 8,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'text.usetex': False,
        'figure.figsize': [4, 3.5],
        'font.family':'serif',
        'font.size':8
        }    
        plt.rcParams.update(params)  
        corr = self.table[self.table['mask']].drop(columns=['mask', 'nran']).corr()
        #corr = self.table[self.table['mask']].drop(columns=['nran']).corr()
        mask = np.zeros_like(corr, '?')
        mask[np.triu_indices_from(corr)] = True
        sns.heatmap(corr, cmap=plt.cm.seismic, center=0,
                    mask=mask, vmin=vlim[0], vmax=vlim[1], cbar_kws={'extend':'both'})
        plt.show()
        
    def plot_mollweide(self):
        mpl.rcParams.update(mpl.rcParamsDefault)
        params = {
        'axes.spines.right':True,
        'axes.spines.top':True,
        'axes.labelsize': 8,
        #'text.fontsize': 8,
        'legend.fontsize': 8,
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'text.usetex': False,
        'figure.figsize': [4, 3],
        'font.family':'serif',
        'font.size':8
        }    
        plt.rcParams.update(params)  
        fig, ax = plt.subplots(nrows=7, ncols=3, figsize=(8,15))
        ax=ax.flatten()
        for i,name in enumerate(self.table.columns):
            plt.sca(ax[i])
            hp.mollview(self.table[name], hold=True, title=name)    
        plt.show()        
        
def hd5_2_fits(metaname, fitname, hpmask, hpfrac, cols, mask_in=None, res=512):
    metadata = pd.read_hdf(metaname)
    ngal     = metadata['ngal'].values
    nran     = metadata['nran'].values    
    
    if mask_in is None:
        maskou = metadata['mask'].values
    else:
        maskou = metadata['mask'].values & mask_in
        
    features = metadata[cols][maskou].values    
    hpind    = np.argwhere(maskou).flatten()
    fracgood = nran / nran[maskou].mean()
    
    label    = ut.makedelta(ngal, fracgood, maskou, select_fun=None, is_sys=False) + 1
    label    = label[maskou]
    fracgood = fracgood[maskou]
    
    # for n in metadata.columns:
    #     print('%20s : %d'%(n, np.isnan(metadata[metadata['mask']][n]).sum()))
    outdata = np.zeros(features.shape[0], 
                       dtype=[('label', 'f8'),
                              ('hpind','i8'), 
                              ('features',('f8', features.shape[1])),
                              ('fracgood','f8')])
    outdata['label']    = label
    outdata['hpind']    = hpind
    outdata['features'] = features
    outdata['fracgood'] = fracgood
    #
    #
    ft.write(fitname, outdata, clobber=True)
    print('wrote %s'%fitname)
    #
    # 
    mask = np.zeros(12*res*res, '?')
    mask[hpind] = True
    hp.write_map(hpmask, mask, overwrite=True, fits_IDL=False)
    print('wrote %s'%hpmask)
    #
    #
    frac = np.zeros(12*res*res)
    frac[hpind] = fracgood
    hp.write_map(hpfrac, frac, overwrite=True, fits_IDL=False)
    print('wrote %s'%hpfrac)