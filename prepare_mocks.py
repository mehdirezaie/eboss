#!/usr/bin/env python
'''

    run it 
    > for i in {2..9};
    do
            python mock.py --imock ${i} --kind null &&
            python mock.py --imock ${i} --kind cont &&
    done
'''
import numpy as np
import pandas as pd
import logging
import os

import sys
sys.path.append('/home/mehdi/github/LSSutils')
from LSSutils.catalogs.combinefits import EBOSSCAT, hd5_2_fits
from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as my_cols

from argparse import ArgumentParser
ap = ArgumentParser(description='PREPARE EBOSS MOCKS FOR NN REGRESSION')
ap.add_argument('--imock', type=int, default=1)
ap.add_argument('--nside', type=int, default=256)
ap.add_argument('--kind',    default='null')
ap.add_argument('--cap',    default='NGC')
ap.add_argument('--target', default='QSO')
ns = ap.parse_args()    

## --- input parameters
imock = ns.imock
nside = ns.nside
cap   = ns.cap
target= ns.target
kind  = ns.kind

## --- z-cuts --- 
zcuts     = {'0.8': [0.80, 1.14],
             '1.1': [1.14, 1.39],
             '1.4': [1.39, 1.63],
             '1.6': [1.63, 1.88],
             '1.9': [1.88, 2.20]}

if kind == 'cont':
    input_dir = '/B/Shared/eBOSS/contaminated'
    mock_name_out = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_v7_{imock:04d}.dat.fits'
    rand_name_out = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_v7_{imock:04d}.ran.fits'
    output_dir    = '/home/mehdi/data/eboss/mocks/cont' + f'/{imock:04d}'
elif kind == 'null':
    input_dir = '/B/Shared/eBOSS/null'
    mock_name_out = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_v7_noweight_{imock:04d}.dat.fits'
    rand_name_out = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_v7_noweight_{imock:04d}.ran.fits'
    output_dir    = '/home/mehdi/data/eboss/mocks/null' + f'/{imock:04d}'
else:
    raise ValueError(f'{kind} should be either cont or null')

# --- check if the output directory exists
if not os.path.isdir(output_dir):
    #logger.info('create {}'.format(output_dir))
    os.makedirs(output_dir)
    

logging.basicConfig(
    filename=output_dir + '/test.log',
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )
logger = logging.getLogger("Logger 1")
logger.info('results will be written under {}'.format(output_dir))    


# --- input files
logger.info('prepare the files for NN regression for {}'.format(kind))
logger.info('read {}'.format(mock_name_out))
logger.info('read {}'.format(rand_name_out))

# --- imaging templates
systematics_dir  = '/home/mehdi/data/eboss/sysmaps'
systematics_name = systematics_dir + '/SDSS_HI_imageprop_nside256.h5'
dataframe = pd.read_hdf(systematics_name)
logger.info('read {}'.format(systematics_name))



    

# --- read the data and randoms
mock   = EBOSSCAT([mock_name_out],
                weights=['weight_fkp', 'weight_noz', 'weight_cp'])
random = EBOSSCAT([rand_name_out],
                weights=['weight_fkp', 'weight_noz', 'weight_cp', 'weight_systot'])

for i, key_i in enumerate(zcuts):
    logger.info('split based on {}'.format(zcuts[key_i]))

    # --- prepare the names for the output files
    hpcat     = output_dir + f'/galmap_{cap}_{key_i}_{nside}.hp.fits'
    hpmask    = output_dir + f'/mask_{cap}_{key_i}_{nside}.hp.fits'
    fracgood  = output_dir + f'/frac_{cap}_{key_i}_{nside}.hp.fits'
    fitname   = output_dir + f'/ngal_features_{cap}_{key_i}_{nside}.fits'    
    fitkfold  = output_dir + f'/ngal_features_{cap}_{key_i}_{nside}.5r.npy'


    mock.apply_zcut(zcuts[key_i])
    mock.project2hp(nside)
    mock.writehp(hpcat)    
    
    ##random.apply_zcut(zcuts[key_i]) ## -- we don't cut randoms
    random.project2hp(nside)
    
    
    # --- append the galaxy and random density
    dataframe_i = dataframe.copy()
    dataframe_i['ngal'] = mock.galm
    dataframe_i['nran'] = random.galm    
    dataframe_i['nran'][random.galm == 0] = np.nan
    
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