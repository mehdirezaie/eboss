import numpy as np
import sys
import os
sys.path.append('/Users/rezaie/github/SYSNet/src')
from utils import radec2hpix


import fitsio as ft
import healpy as hp

from argparse import ArgumentParser
ap = ArgumentParser(description='Neural Net regression')
ap.add_argument('--input_path',  default='/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_NGC_v6.dat.fits')
ap.add_argument('--output_path', default='/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_NGC_v6_wnn.dat.fits')
ap.add_argument('--input_wnn',   default='/Volumes/TimeMachine/data/eboss/v6/results_ngc/regression/nn_ab/nn-weights.hp512.fits')
ap.add_argument('--overwrite',   action='store_true')
ns = ap.parse_args()


# read input
data = ft.read(ns.input_path)


wmap = hp.read_map(ns.input_wnn, verbose=False)
nside = hp.get_nside(wmap)

# find data healpix indices
data_hpix = radec2hpix(nside, data['RA'], data['DEC'])
wmap_data = wmap[data_hpix]

#low = wmap_data <= 0.001
#wmap_data[low] = 0.001
wmap_data = wmap_data.clip(0.5, 2.0)
assert np.all(wmap_data > 0.0)
data['WEIGHT_SYSTOT'] = 1./wmap_data
    
    
if os.path.isfile(ns.output_path):
    if ns.overwrite:
        print('file exists, but will be rewritten!')
        ft.write(ns.output_path, data, clobber=True)
    else:
        print('file exists!')        
else:
    ft.write(ns.output_path, data)





