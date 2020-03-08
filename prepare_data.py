#!/usr/bin/env python
'''
    Update
    jan 03, switch back to v7_1
    dec 14, switch to 512
'''
import numpy as np
import pandas as pd
import logging
import os

import sys
sys.path.append('/home/mehdi/github/LSSutils')
from LSSutils import setup_logging
from LSSutils.catalogs.combinefits import EbossCatalog, hd5_2_fits
#from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as my_cols
from LSSutils.catalogs.datarelease import cols_eboss_mocks_qso as my_cols


setup_logging("info")


from argparse import ArgumentParser
ap = ArgumentParser(description='PREPARE EBOSS DATA FOR NN REGRESSION')
ap.add_argument('--nside',  type=int, default=512)
ap.add_argument('--cap',    type=str, default='NGC')
ap.add_argument('--target', type=str, default='QSO')
ap.add_argument('--slices', type=str, default=['low', 'high', 'all', 'zhigh', 'z1','z2', 'z3'], nargs='*')

ns = ap.parse_args()    

## --- input parameters
nside  = ns.nside
cap    = ns.cap
target = ns.target
slices = ns.slices

## --- z-cuts --- 
#zcuts     = {'0.8': [0.80, 1.14],
#             '1.1': [1.14, 1.39],
#             '1.4': [1.39, 1.63],
#             '1.6': [1.63, 1.88],
#             '1.9': [1.88, 2.20]}

#zcuts = {'all':[0.80, 2.20]}

#zcuts = {'low':[0.80, 1.50],
#        'high':[1.50, 2.20]}

zcuts = {'low':[0.8, 1.5],
         'high':[1.5, 2.2],
         'all':[0.8, 2.2],
         'zhigh':[2.2, 3.5],
         'z1':[0.8, 1.3],
         'z2':[1.3, 1.6],
         'z3':[1.6, 2.2]}


output_dir    = '/home/mehdi/data/eboss/v7_2/0.1'    
data_name_in = f'/home/mehdi/data/eboss/v7_2/eBOSS_{target}_full_{cap}_v7_2.dat.fits'
rand_name_in = f'/home/mehdi/data/eboss/v7_2/eBOSS_{target}_full_{cap}_v7_2.ran.fits'

#--- logger
# logging.basicConfig(
#     #filename=output_dir + '/test.log',
#     level=logging.INFO,
#     format="%(asctime)s:%(levelname)s:%(message)s"
#     )
logger = logging.getLogger("Logger 1")

# --- check if the output directory exists
if not os.path.isdir(output_dir):
    logger.info('create {}'.format(output_dir))
    os.makedirs(output_dir)
logger.info('results will be written under {}'.format(output_dir))    

# --- input files
logger.info('prepare the files for NN regression ')
logger.info('read {}'.format(data_name_in))
logger.info('read {}'.format(rand_name_in))

# --- imaging templates
systematics_dir  = '/home/mehdi/data/eboss/sysmaps'
systematics_name = systematics_dir + '/SDSS_WISE_HI_imageprop_nside512.h5'
dataframe = pd.read_hdf(systematics_name, key='templates')
logger.info('read {}'.format(systematics_name))

for i, key_i in enumerate(slices):
    
    if key_i not in slices:
         raise RuntimeError(f'{key_i} not in {slices}')

    logger.info('split based on {}'.format(zcuts[key_i]))

    #--- read galaxy and random 
    if key_i=='zhigh':
        zmin = 2.2
        zmax = 3.5
    else:
        zmin=0.8
        zmax=2.2

    mock   = EbossCatalog(data_name_in, 'galaxy', zmin=zmin, zmax=zmax)
    random = EbossCatalog(rand_name_in, 'random', zmin=zmin, zmax=zmax)    


    # --- prepare the names for the output files
    hpcat     = output_dir + f'/galmap_{cap}_{key_i}_{nside}.hp.fits'
    hpmask    = output_dir + f'/mask_{cap}_{key_i}_{nside}.hp.fits'
    fracgood  = output_dir + f'/frac_{cap}_{key_i}_{nside}.hp.fits'
    fitname   = output_dir + f'/ngal_features_{cap}_{key_i}_{nside}.fits'    
    fitkfold  = output_dir + f'/ngal_features_{cap}_{key_i}_{nside}.5r.npy'

    mock.cutz(zcuts[key_i])
    mock.tohp(nside)
    mock.writehp(hpcat)    
    
    ##random.apply_zcut(zcuts[key_i]) ## -- we don't cut randoms
    ##random.cutz([0.8, 2.2])
    random.tohp(nside)
    
    # --- append the galaxy and random density
    dataframe_i = dataframe.copy()
    dataframe_i['ngal'] = mock.hpmap
    dataframe_i['nran'] = random.hpmap    
    dataframe_i['nran'][random.hpmap == 0] = np.nan
    
    dataframe_i.dropna(inplace=True)
    logger.info('df shape : {}'.format(dataframe_i.shape))
    logger.info('columns  : {}'.format(my_cols))
    
    # --- write 
    hd5_2_fits(dataframe_i, 
                  my_cols, 
                  fitname, 
                  hpmask, 
                  fracgood, 
                  fitkfold,
                  res=nside, 
                  k=5)
