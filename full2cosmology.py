#!/usr/bin/env python
'''
    code to make clustering catalogs from full catalogs

'''
import os
import logging


import sys
sys.path.append('/home/mehdi/github/LSSutils')
from LSSutils.catalogs.combinefits import SysWeight, EbossCatalog, make_clustering_catalog_random



def main(zmin=0.8,
         zmax=3.5,
         cap='NGC',
         target='QSO',
         version='v7_2',
         versiono='0.1'):    

    output_dir    = f'/home/mehdi/data/eboss/{version}/{versiono}/'    
    data_name_in  = f'/home/mehdi/data/eboss/{version}/eBOSS_{target}_full_{cap}_{version}.dat.fits'
    rand_name_in  = f'/home/mehdi/data/eboss/{version}/eBOSS_{target}_full_{cap}_{version}.ran.fits'

    tag           = '_'.join((version, versiono))
    data_name_out = output_dir + f'eBOSS_{target}_clustering_{cap}_{tag}.dat.fits'
    rand_name_out = output_dir + f'eBOSS_{target}_clustering_{cap}_{tag}.ran.fits'



    logger = logging.getLogger("Full to Cosmology")
    logger.info('results will be written under {}'.format(output_dir))  
    logger.info(f'input data   : {data_name_in}')
    logger.info(f'input random : {rand_name_in}')
    logger.info(f'output data   : {data_name_out}')
    logger.info(f'output random : {rand_name_out}')
    
    # --- check if the output directory exists
    if not os.path.isdir(output_dir):
        logger.info('create {}'.format(output_dir))
        #os.makedirs(output_dir)

    data = EbossCatalog(data_name_in, zmin=zmin, zmax=zmax, kind='galaxy')
    data.to_fits(data_name_out)


    random = EbossCatalog(rand_name_in, zmin=zmin, zmax=zmax, kind='random')
    newrandom = make_clustering_catalog_random(random.data, data.data)
    newrandom.write(rand_name_out)    
    
    
if __name__ == '__main__':
        
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Prepare EBOSS Data and Random Catalogs')
    ap.add_argument('--zmin',    type=float, default=0.8, help='eg:0.8')
    ap.add_argument('--zmax',    type=float, default=3.5, help='eg:3.5')
    ap.add_argument('--cap',     type=str,   default='NGC', help='eg: NGC or SGC')
    ap.add_argument('--target',  type=str,   default='QSO', help='eg: QSO')
    ap.add_argument('--version', type=str,   default='v7_2', help='eg: v7_2')
    ap.add_argument('--versiono',type=str,   default='0.1', help='eg: 0.1')
    ns = ap.parse_args()    

    #--- default
    #
    # zmin=0.8,
    # zmax=3.5,
    # cap='NGC',
    # target='QSO',
    # version='v7_2',
    # versiono='0.1'
    
    from LSSutils import setup_logging
    setup_logging('info')

    logger = logging.getLogger("Full2Cosmology")
    
    kwargs = ns.__dict__
    for (a,b) in zip(kwargs.keys(), kwargs.values()):
        logger.info('{:6s}{:15s} : {}'.format('', a, b))
        
    # -- call the function    
    main(**kwargs)
    
