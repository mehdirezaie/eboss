#!/usr/bin/env python
'''
    Update
    jan 03, switch back to v7_1
    dec 14, switch to 512
'''
import os
import logging
import pandas as pd

import sys
sys.path.append('/home/mehdi/github/LSSutils')

from LSSutils.catalogs.combinefits import EbossCatalog, RegressionCatalog
from LSSutils.catalogs.datarelease import zcuts, cols_eboss_mocks_qso as columns
from LSSutils import setup_logging



def main(ns):

    # ---- prepare data for regression
    # step 1. read data, randoms, and imaging maps

    data = EbossCatalog(ns.data_name, kind='galaxy', zmin=0.8, zmax=3.5)
    random = EbossCatalog(ns.random_name, kind='random', zmin=0.8, zmax=3.5)
    dataframe = pd.read_hdf(ns.systematics_name, key='templates')  
    
    # step 2. apply a z cut, project to HEALPIX, make a df
    # split into 5-fold, save as .npy
    RCat = RegressionCatalog(data, random, dataframe)
    RCat(ns.slices, zcuts, ns.output_dir, cap=ns.cap, efficient=True, columns=columns)
    
    
    
    
    
if __name__ == '__main__':
    
    
    from argparse import ArgumentParser
    
    ap = ArgumentParser(description='PREPARE EBOSS DATA FOR NN REGRESSION')
    ap.add_argument('-d','--data_name', type=str, required=True)
    ap.add_argument('-r', '--random_name', type=str, required=True)
    ap.add_argument('-s', '--systematics_name', type=str, required=True)
    ap.add_argument('-o', '--output_dir', type=str, required=True)    
    ap.add_argument('-n', '--nside',  type=int, default=512)
    ap.add_argument('-c', '--cap',    type=str, default='NGC')
    ap.add_argument('-sl', '--slices', type=str, nargs='*',
                    default=['low', 'high', 'all', 'zhigh', 'z1','z2', 'z3'])
    ap.add_argument('--log',       default='none')    
    ns = ap.parse_args()    
    
    # output directory
    if not os.path.exists(ns.output_dir):
        os.makedirs(ns.output_dir)
        
    # logger    
    logfile = '/'.join([ns.output_dir, ns.log]) if ns.log!='none' else None    
    setup_logging('info', logfile=logfile)
    
    
    # call the main function
    main(ns)