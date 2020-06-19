#!/usr/bin/env python
'''
    Update
    jan 03, switch back to v7_1
    dec 14, switch to 512
'''
import os
import logging
import pandas as pd
import numpy as np

from LSSutils.catalogs.combinefits import EbossCatalog, HEALPixDataset
from LSSutils.catalogs.datarelease import zcuts, cols_eboss_mocks_qso as columns
from LSSutils.utils import split2Kfolds
from LSSutils import setup_logging



def main(ns):

    # ---- prepare data for regression
    # step 1. read data, randoms, and imaging maps
    templates = pd.read_hdf(ns.systematics_name, key='templates')  
    data = EbossCatalog(ns.data_name, kind='galaxy', zmin=0.8, zmax=3.5)
    randoms = EbossCatalog(ns.random_name, kind='random', zmin=0.8, zmax=3.5)
        
        
        
    # step 2. apply a z cut, project to HEALPIX, make a df
    # split into 5-fold, save as .npy
    dataset = HEALPixDataset(data, randoms, templates, columns)
    
    for i, key_i in enumerate(ns.slices):
            if key_i not in zcuts:
                 raise RuntimeError(f'{key_i} not in {zcuts.keys()}')
                    
            zlim = zcuts[key_i]
            fitkfold = ns.output_dir + f'ngal_features_{ns.cap}_{key_i}_{ns.nside}.5r.npy'
            
            nnbarall = dataset.prepare(ns.nside, zlim[0], zlim[1], label='nnbar')
            nnbar5f = split2Kfolds(nnbarall)
            np.save(fitkfold, nnbar5f)
            print(f'wrote {fitkfold}')    
    
    
    
    
if __name__ == '__main__':
    
    
    from argparse import ArgumentParser
    
    ap = ArgumentParser(description='PREPARE EBOSS DATA FOR NN REGRESSION')
    ap.add_argument('-d', '--data_name', type=str, required=True)
    ap.add_argument('-r', '--random_name', type=str, required=True)
    ap.add_argument('-s', '--systematics_name', type=str, required=True)
    ap.add_argument('-o', '--output_dir', type=str, required=True)    
    ap.add_argument('-n', '--nside',  type=int, default=512)
    ap.add_argument('-c', '--cap',    type=str, default='NGC')
    ap.add_argument('-sl', '--slices', type=str, nargs='*',
                    default=['low', 'high', 'all', 'zhigh', 'z1','z2', 'z3'])
    ap.add_argument('--log',       default='none')    
    ns = ap.parse_args()    
    
    for (a,b) in ns.__dict__.items():
        print(f'{a:20s}: {b}')
    

    # output directory
    if not os.path.exists(ns.output_dir):
        os.makedirs(ns.output_dir)
        
    # logger    
    logfile = ''.join([ns.output_dir, ns.log]) if ns.log!='none' else None    
    setup_logging('info', logfile=logfile)
    
    
    # call the main function
    main(ns)