#!/usr/bin/env python
'''

    run it 
    for i in {2..4};do echo ${i};python swap_mocks.py --kind cont --imock ${i} --kind null;done
    for i in {1..4};do echo ${i};python swap_mocks.py --kind cont --imock ${i} --kind cont;done
'''
import numpy as np
import pandas as pd
import logging
import os


from astropy.table import Table


def make_clustering_catalog_random(rand, mock, seed=None):
    
    rand_clust = Table()
    rand_clust['RA'] = rand['RA']*1
    rand_clust['DEC'] = rand['DEC']*1
    rand_clust['Z'] = rand['Z']*1
    rand_clust['NZ'] = rand['NZ']*1
    rand_clust['WEIGHT_FKP'] = rand['WEIGHT_FKP']*1
    rand_clust['COMP_BOSS'] = rand['COMP_BOSS']*1
    rand_clust['sector_SSR'] = rand['sector_SSR']*1

    if not seed is None:
        np.random.seed(seed)
    
    index = np.arange(len(mock))
    ind = np.random.choice(index, size=len(rand), replace=True)
    
    fields = ['WEIGHT_NOZ', 'WEIGHT_CP', 'WEIGHT_SYSTOT'] 
    for f in fields:
        rand_clust[f] = mock[f][ind]

    #-- As in real data:
    rand_clust['WEIGHT_SYSTOT'] *= rand_clust['COMP_BOSS']

    w = (rand_clust['COMP_BOSS'] > 0.5) & (rand_clust['sector_SSR'] > 0.5) 

    return rand_clust[w]

import sys
sys.path.append('/home/mehdi/github/LSSutils')
from LSSutils.catalogs.combinefits import EBOSSCAT, hd5_2_fits, swap_weights
#from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as my_cols
from LSSutils.catalogs.datarelease import cols_eboss_mocks_qso as my_cols

from argparse import ArgumentParser
ap = ArgumentParser(description='PREPARE EBOSS MOCKS FOR NN REGRESSION')
ap.add_argument('--imock', type=int, default=1)
ap.add_argument('--nside', type=int, default=512)
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
#zcuts     = {'0.8': [0.80, 1.14],
#             '1.1': [1.14, 1.39],
#             '1.4': [1.39, 1.63],
#             '1.6': [1.63, 1.88],
#             '1.9': [1.88, 2.20]}
#
#zcuts = {'all':[0.80, 2.20]}
zcuts = {'low':[0.80, 1.50],
        'high':[1.50, 2.20]}


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
    filename=output_dir + '/swap.log',
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )
logger = logging.getLogger("Logger 1")
logger.info('results will be written under {}'.format(output_dir))    


# --- input files
logger.info('swap the NN-z weights {}'.format(kind))
logger.info('read {}'.format(mock_name_out))
logger.info('read {}'.format(rand_name_out))

    

# --- read the data and randoms
# mock   = EBOSSCAT([mock_name_out],
#                 weights=['weight_fkp', 'weight_noz', 'weight_cp'])
# random = EBOSSCAT([rand_name_out],
#                 weights=['weight_fkp', 'weight_noz', 'weight_cp', 'weight_systot'])

# for i, key_i in enumerate(zcuts):
#     logger.info('split based on {}'.format(zcuts[key_i]))

#     # --- prepare the names for the output files
#     hpcat     = output_dir + f'/galmap_{cap}_{key_i}_{nside}.hp.fits'
#     hpmask    = output_dir + f'/mask_{cap}_{key_i}_{nside}.hp.fits'
#     fracgood  = output_dir + f'/frac_{cap}_{key_i}_{nside}.hp.fits'
#     fitname   = output_dir + f'/ngal_features_{cap}_{key_i}_{nside}.fits'    
#     fitkfold  = output_dir + f'/ngal_features_{cap}_{key_i}_{nside}.5r.npy'


#     mock.apply_zcut(zcuts[key_i])
#     mock.project2hp(nside)
#     mock.writehp(hpcat)    
    
#     ##random.apply_zcut(zcuts[key_i]) ## -- we don't cut randoms
#     random.project2hp(nside)
    
    
#     # --- append the galaxy and random density
#     dataframe_i = dataframe.copy()
#     dataframe_i['ngal'] = mock.galm
#     dataframe_i['nran'] = random.galm    
#     dataframe_i['nran'][random.galm == 0] = np.nan
    
#     dataframe_i.dropna(inplace=True)
#     logger.info('df shape : {}'.format(dataframe_i.shape))
#     logger.info('columns  : {}'.format(my_cols))
    
#     # --- write 
#     hd5_2_fits(dataframe_i, 
#                   my_cols, 
#                   fitname, 
#                   hpmask, 
#                   fracgood, 
#                   fitkfold,
#                   res=nside, 
#                   k=5)

random = Table.read(rand_name_out)

for i, model_i in enumerate(['plain', 'ablation', 'known']):       
    # /home/mehdi/data/eboss/mocks/null/0005/results_NGC_1.6_256/regression/nn_plain/    
    weight    = lambda zcut_i, model_i: output_dir + f'/results_{cap}_{zcut_i}_{nside}'\
                                        +f'/regression/nn_{model_i}/nn-weights.hp{nside}.fits'
    #redshifts = ['0.8', '1.1', '1.4', '1.6', '1.9']
    redshifts = ['low', 'high']
    weights   = dict(zip(redshifts, [weight(zcut_i, model_i) for zcut_i in redshifts]))
    #print(weights)
    
    wtag = '_'.join(('v7', 'wnnlowhigh', model_i))
    #print(wtag)
    
    mock_name_wtag   = output_dir + '/' + mock_name_out.split('/')[-1].replace('v7', wtag)
    random_name_wtag = mock_name_wtag.replace('.dat', '.ran')
    #print(mock_name_out)
    #print(mock_name_wtag)
    
    mycat = swap_weights(mock_name_out)
    mycat.run(weights, zcuts)
    mycat.to_fits(mock_name_wtag)
    logger.info('Exporting mocks to {}'.format(mock_name_wtag))
    
    # random
    random_clus = make_clustering_catalog_random(random, mycat.data, seed=1234567)
    logger.info('Exporting randoms to {}'.format(random_name_wtag))
    random_clus.write(random_name_wtag, overwrite=True) 
    print(100*'-', '\n')
