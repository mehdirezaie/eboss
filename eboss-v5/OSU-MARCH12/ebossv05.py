"""
    eBOSS ELGs analysis
    Mehdi Rezaie medirz90@icloud.com

    last edit   Dec 21, 2017
    Notes:
    - systematic weights are not available yet
    - FKP weights are calculated within Nbodykit
"""
import sys
sys.path.append('/Users/mthecosmologist/Dropbox/github/DESILSS')
from syslss import powerspectrum, iusp
import numpy as np
import os
import fitsio as ft


"""
 reading catalogs
 lower=True, we force the columns to be lowercase
"""
path2cats = '/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/'
path2nofz = '/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/nofz/'

g  = lambda i: path2cats+'eboss2'+i+'.v5_10_7.latest.fits'
r  = lambda i: path2cats+'eboss2'+i+'.v5_10_7.latest.rands.fits'
cat_i    = sys.argv[1]
version = 'v05'
path4pks = path2cats+'kpks-'+version
if not os.path.exists(path4pks):
    os.makedirs(path4pks)

class cat(object):
    # class to prepare our catalogs for Nbodykit
    def __init__(self, ra, dec, z, w):
        self.RA = ra
        self.DEC = dec
        self.Z = z
        self.Weight = w

def get_pk(cat_i):
    # 
    cosmo_params = {'Om0': 0.31,'H0':69.0,'flat':True} # this has to be the same for n(z) calculation
    nmesh = 256
    tsrc = 0.8
    ssrc = 0.7
    zlim = (0.6, 1.1)
    # reading
    galc = ['ra','dec','z','z_reliable','sector_tsr','sector_ssr','weight_systot','isdupl', 'plate_ssr']
    ranc = ['ra','dec','sector_ssr','sector_tsr','plate_ssr']
    gal = ft.read(g(cat_i), lower=True, columns=galc)
    ran = ft.read(r(cat_i), lower=True, columns=ranc)
    z, nz = np.loadtxt(path2nofz+'nofz_eboss2'+str(cat_i)+'.dat').T
    print("readings are done ... ")
    nofz = iusp(z, nz)
    # galaxy
    # z_reliable
    galmask = (gal['sector_tsr'] > tsrc) & (gal['sector_ssr'] > ssrc)
    galmask &= (gal['z_reliable']) & (~gal['isdupl'])
    gal = gal[galmask]
    galw = np.ones(gal.size) # no sys weight
    maskz = (gal['z'] > zlim[0]) & (gal['z'] < zlim[1])
    #
    #
    ranmask = (ran['sector_tsr'] > tsrc) & (ran['sector_ssr'] > ssrc)
    ran = ran[ranmask]
    ranz = np.random.choice(gal['z'][maskz], size=ran.size)
    ranw = ran['sector_tsr'] * ran['plate_ssr']
    #
    #
    galaxy = cat(gal['ra'], gal['dec'], gal['z'], galw)
    random = cat(ran['ra'], ran['dec'], ranz, ranw)
    #
    # compute pk for a given redshift bin
    eboss = powerspectrum(galaxy, random, nofz, cosmo_params)
    ebosspk = eboss.run(zlim, nmesh)
    np.save(path4pks+'/kpkeboss2'+cat_i+'Y1v5_10_7'+version, ebosspk)
    print('DONE!')





get_pk(cat_i)



