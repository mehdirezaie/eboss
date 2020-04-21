#!/usr/bin/env python
'''
    Code to read a galaxy, random catalog,
    swap weights, subsample randoms, assess the redshift distribution
    export the new catalogs


    get help with $> python swap_mocks.py --help
    run with $> python swap_mocks.py
'''
import os
import logging


import sys
sys.path.append('/home/mehdi/github/LSSutils')
from LSSutils.catalogs.combinefits import SysWeight, EbossCatalog, reassignment

def main(imock=1,
         model='plain',
         cont='null',
         zmin=0.8,
         zmax=2.2,
         nside=512,
         zsplit='lowmidhigh',
         slices=['low', 'high'],
         cap='NGC',
         target='QSO',
         version='v7',
         versiono='0.3'):    

    # 
    if 'zhigh' in slices:
        raise RuntimeError(f'zhigh is not allowed for mocks')

    output_dir = f'/B/Shared/mehdi/eboss/mocks/{versiono}/{cap}_{imock:04d}_{cont}'

    if cont == 'contaminated':
        input_dir = '/B/Shared/eBOSS/contaminated'
        data_name_in = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_{version}_{imock:04d}.dat.fits'
        rand_name_in = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_{version}_{imock:04d}.ran.fits'
    elif cont == 'null':
        input_dir = '/B/Shared/eBOSS/null'
        data_name_in = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_{version}_noweight_{imock:04d}.dat.fits'
        rand_name_in = input_dir+ f'/EZmock_eBOSS_{target}_{cap}_{version}_noweight_{imock:04d}.ran.fits'
    else:
        raise ValueError(f'{cont} should be either cont or null')
    
    tag           = '_'.join((version, versiono, model, zsplit))
    data_name_out = output_dir + f'/EZmock_eBOSS_{target}_{cap}_{tag}_{imock:04d}.dat.fits'
    rand_name_out = output_dir + f'/EZmock_eBOSS_{target}_{cap}_{tag}_{imock:04d}.ran.fits'
    plotname      = output_dir + f'/eBOSS_{target}_{cap}_{tag}_{imock:04d}.pdf'

    weight = lambda zcut, model: output_dir + f'/results/{cap}_{zcut}_{nside}'\
             +f'/regression/nn_{model}/nn-weights.hp{nside}.fits'

    zcuts = {'low':[[0.8, 1.5],   None],
             'high':[[1.5, 2.2],  None],
             'all':[[0.8, 2.2],   None],
             'zhigh':[[2.2, 3.5], None],
             'z1':[[0.8, 1.3], None],
             'z2':[[1.3, 1.6], None],
             'z3':[[1.6, 2.2], None]}




    logger = logging.getLogger("Swapper")
    logger.info('results will be written under {}'.format(output_dir))  
    logger.info('swap the NN-z weights')
    logger.info(f'input data   : {data_name_in}')
    logger.info(f'input random : {rand_name_in}')
    logger.info(f'output data   : {data_name_out}')
    logger.info(f'output random : {rand_name_out}')
    
    # --- check if the output directory exists
    if not os.path.isdir(output_dir):
        logger.info('create {}'.format(output_dir))
        #os.makedirs(output_dir)

    for zcut in slices: #--only read slices that we need
        logger.info(f'zcut : {zcut}')
        zcuts[zcut][1]=SysWeight(weight(zcut, model))

    data = EbossCatalog(data_name_in, zmin=zmin, zmax=zmax, kind='galaxy')
    data.swap(zcuts=zcuts, slices=slices)
    #data.make_plots(zcuts, slices=slices, filename=plotname)
    data.to_fits(data_name_out)


    random    = EbossCatalog(rand_name_in, zmin=zmin, zmax=zmax, kind='random')
    newrandom = reassignment(random.data, data.data, seed=1234567)
    newrandom.write(rand_name_out)    

    
    
if __name__ == '__main__':
        
    from argparse import ArgumentParser
    ap = ArgumentParser(description='Prepare EBOSS Data and Random Catalogs')
    ap.add_argument('--model', type=str, default='plain', help='eg:plain, other options are ablation and known ')
    ap.add_argument('--imock', type=int, default=1, help='eg:1')
    ap.add_argument('--cont', type=str, default='null', help='null or contaminated')
    ap.add_argument('--zmin', type=float, default=0.8, help='eg:0.8')
    ap.add_argument('--zmax', type=float, default=2.2, help='eg:2.2')
    ap.add_argument('--nside', type=int, default=512, help='eg:512')
    ap.add_argument('--zsplit', type=str, default='lowmidhigh', help='eg: lowmidhigh')
    ap.add_argument('--slices', type=str, default=['low', 'high'], nargs='*', help="eg:['low', 'high']")
    ap.add_argument('--cap', type=str, default='NGC', help='eg: NGC or SGC')
    ap.add_argument('--target', type=str, default='QSO', help='eg: QSO')
    ap.add_argument('--version', type=str, default='v7', help='eg: v7')
    ap.add_argument('--versiono',type=str, default='0.3', help='eg: 0.3')
    ns = ap.parse_args()    

    #--- default
    #
    # model='plain',
    # zmin=0.8,
    # zmax=3.5,
    # nside=512,
    # zsplit='lowmidhigh',
    # slices=['low', 'high', 'zhigh'],
    # cap='NGC',
    # target='QSO',
    # version='v7_2',
    # versiono='0.3'
    
    from LSSutils import setup_logging
    setup_logging('info')

    logger = logging.getLogger("Swapper")
    
    kwargs = ns.__dict__
    for (a,b) in zip(kwargs.keys(), kwargs.values()):
        logger.info('{:6s}{:15s} : {}'.format('', a, b))
        
    # -- call the function    
    main(**kwargs)
        
    
