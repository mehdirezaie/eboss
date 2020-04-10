import sys
sys.path.append('/home/mehdi/github/eboss_clustering/python')
sys.path.append('/home/mehdi/github/eboss_clustering/bin')

sys.path.append('/home/mehdi/github/LSSutils')
from LSSutils.catalogs.combinefits import reassignment

import numpy as np
import matplotlib 
import matplotlib.pylab as plt
import healpy as hp
#import pymangle
import sys
import os
import logging

from nbodykit.algorithms.fibercollisions import FiberCollisions
from astropy.table import Table, vstack, unique
from astropy.coordinates import SkyCoord
from astropy import units

#-- This is from github.com/julianbautista/eboss_clustering.git
#-- The equivalent in mkAllsamples is zfail_JB.py
from cosmo import CosmoSimple
import redshift_failures
import systematic_fitter 

logging.basicConfig(format='%(asctime)s %(message)s')
logger=logging.getLogger('systematics') 
#Setting the threshold of logger to DEBUG 
logger.setLevel(logging.INFO) 


def get_systematic_weights(mock, rand, 
    target='LRG', zmin=0.6, zmax=1.0, 
    random_fraction=1, seed=None, nbins=20, plotit=False):

    wd = (mock['Z'] >= zmin)&(mock['Z'] <= zmax)
    if 'IMATCH' in mock.colnames:
        logger.info('apply IMATCH cut mock')
        wd &= ((mock['IMATCH']==1)|(mock['IMATCH']==2))
    if 'COMP_BOSS' in mock.colnames:
        logger.info('apply COMP_BOSS cut mock')        
        wd &= (mock['COMP_BOSS'] > 0.5)
    if 'sector_SSR' in mock.colnames:
        logger.info('apply sector_SSR cut mock')        
        wd &= (mock['sector_SSR'] > 0.5) 

    wr = (rand['Z'] >= zmin) & (rand['Z'] <= zmax)
    if 'COMP_BOSS' in rand.colnames:
        logger.info('apply COMP_BOSS cut random')        
        wr &= (rand['COMP_BOSS'] > 0.5)
    if 'sector_SSR' in rand.colnames:
        logger.info('apply sector_SSR cut random')                
        wr &= (rand['sector_SSR'] > 0.5)
    if random_fraction != 1:
        logger.info('apply subsampling on randoms')                        
        wr &= (np.random.rand(len(rand))<random_fraction)

    logger.info(f'{np.mean(wr)}')
    logger.info(f'{np.mean(wd)}')
    #-- Defining RA, DEC and weights
    data_ra, data_dec = mock['RA'].data[wd], mock['DEC'].data[wd]
    rand_ra, rand_dec = rand['RA'].data[wr], rand['DEC'].data[wr]
    
    #-- weights
    data_we = mock['WEIGHT_FKP'][wd]
    logger.info('apply WEIGHT_FKP on mocks')                                
    if 'WEIGHT_CP' in mock.colnames:
        logger.info('apply WEIGHT_CP on mocks')                                
        data_we *= mock['WEIGHT_CP'][wd]
    if 'sector_SSR' in mock.colnames:
        logger.info('apply sector_SSR on mocks')                                
        data_we /= mock['sector_SSR'][wd]
    elif 'WEIGHT_NOZ' in mock.colnames:
        logger.info('apply WEIGHT_NOZ on mocks')                                
        data_we *= mock['WEIGHT_NOZ'][wd]

        
    logger.info('apply WEIGHT_FKP on randoms')                                    
    rand_we = rand['WEIGHT_FKP'][wr]
    if 'COMP_BOSS' in rand.colnames:
        logger.info('apply COMP_BOSS on randoms')                                
        rand_we *= rand['COMP_BOSS'][wr]

    #-- Read systematic values for data and randoms
    data_syst = systematic_fitter.get_systematic_maps(data_ra, data_dec)
    rand_syst = systematic_fitter.get_systematic_maps(rand_ra, rand_dec)
    map_syst = systematic_fitter.get_systematic_maps(nside=256)

    #-- Create fitter object
    s = systematic_fitter.Syst(data_we, rand_we)

    if target == 'LRG':
        use_maps = ['STAR_DENSITY', 'EBV', 'PSF_I', 'DEPTH_I_MINUS_EBV', 'AIRMASS']
        fit_maps = ['STAR_DENSITY', 'EBV']
    if target == 'QSO':
        use_maps = ['STAR_DENSITY', 'EBV', 'PSF_G', 'SKY_G', 'DEPTH_G_MINUS_EBV', 'AIRMASS']
        fit_maps = ['STAR_DENSITY', 'DEPTH_G_MINUS_EBV']

    #-- Add the systematic maps we want 
    for syst_name in use_maps:
        s.add_syst(syst_name, data_syst[syst_name], rand_syst[syst_name])
    #-- Cut galaxies and randoms with some extreme values
    s.cut_outliers(p=0.5, verbose=1)
    #-- Perform global fit
    s.prepare(nbins=nbins)
    s.fit_minuit(fit_maps=fit_maps)
    if plotit:
        s.plot_overdensity(pars=[None, s.best_pars], ylim=[0.5, 1.5],
                           title='global fit')

    #-- Get weights for global fit
    weight_systot = 1/s.get_model(s.best_pars, data_syst)

    logger.info(f'# zero `weight_systot` : {np.sum(weight_systot==0)}')
    mock_weight_systot     = np.zeros(len(mock))
    rand_weight_systot     = np.zeros(len(rand))
    mock_weight_systot[wd] = weight_systot
    rand_weight_systot[wr] = np.random.choice(weight_systot, 
                                              size=np.sum(wr), replace=True)

    mock['WEIGHT_SYSTOT'] = mock_weight_systot
    rand['WEIGHT_SYSTOT'] = rand_weight_systot
    
    #-- Compute a map with the best-fit density model that will be used to sub-sample mocks
    #dens_model = s.get_model(s.best_pars, map_syst)
    #w = np.isnan(dens_model) | (dens_model < 0.01) | (dens_model > 2)
    #dens_model[w] = hp.UNSEEN 
    #norm = np.percentile(dens_model[~w], 99.9)
    #dens_model[~w] /= norm
    #return s, dens_model 
    return 0




def null_mocks(target, cap, ifirst, ilast, zmin, zmax): 
    logger.info(f'Target: {target}')
    logger.info(f'cap:    {cap}')
    logger.info(f'zmin:   {zmin}')
    logger.info(f'zmax:   {zmax}')
    
    #-- Optional systematics

    input_dir = '/B/Shared/eBOSS/null'
    for imock in range(ifirst, ilast+1):

        output_dir = f'/B/Shared/mehdi/eboss/mocks/{cap}_{imock:04d}_null'
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        logger.info(f'Mocks will be written at: {output_dir}')
        
        #-- Read mock
        mock_name_in  = input_dir + f'/EZmock_eBOSS_{target}_{cap}_v7_noweight_{imock:04d}.dat.fits'
        random_name_in= input_dir + f'/EZmock_eBOSS_{target}_{cap}_v7_noweight_{imock:04d}.ran.fits'
        logger.info(f'Reading mock from {mock_name_in}')
        logger.info(f'Reading random from {random_name_in}')  
        
        mock   = Table.read(mock_name_in)
        random = Table.read(random_name_in)
        
     
        #-- Correct photometric systematics
        logger.info('Getting photo-systematic weights...')
        _ = get_systematic_weights(mock, random,
                                   target=target, zmin=zmin, zmax=zmax,
                                   random_fraction=1, seed=imock, nbins=20, 
                                   plotit=False)


        #-- Make clustering catalog
        #mock_clust = make_clustering_catalog(mock_full, zmin, zmax)
        mock_clust = mock
        rand_clust = reassignment(random, mock_clust, seed=1234567)
                                                    
        #-- Export  
        mock_name_out = output_dir+ f'/EZmock_eBOSS_{target}_{cap}_v7_{imock:04d}.dat.fits'
        rand_name_out = output_dir+ f'/EZmock_eBOSS_{target}_{cap}_v7_{imock:04d}.ran.fits'

        #print('')
        logger.info(f'Exporting mock to {mock_name_out}')
        mock_clust.write(mock_name_out, overwrite=True) 
        
        logger.info(f'Exporting random to {rand_name_out}')
        rand_clust.write(rand_name_out, overwrite=True) 


        #print('Exporting random to', rand_name_out)
        #rand_clust.write(rand_name_out, overwrite=True) 
        #print('Exporting nbar to', nbar_name_out)
        #export_nbar(nbar_mock, nbar_name_out)        
        
        
if __name__ == '__main__':
    # (target, cap, ifirst, ilast, zmin, zmax)
    null_mocks(sys.argv[1], sys.argv[2], int(sys.argv[3]), 
               int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]))
