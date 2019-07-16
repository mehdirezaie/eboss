import sys
import os
import fitsio as ft
import numpy as np
sys.path.append('/Users/mthecosmologist/Dropbox/github/DESILSS')
from tools import nzhist, write



#
#   make N(z)
#




path2cats = '/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/'
g  = lambda i: path2cats+'eboss2'+i+'.v5_10_7.latest.fits'
r  = lambda i: path2cats+'eboss2'+i+'.v5_10_7.latest.rands.fits'

#path4nofz = path2cats+'nofz'
#path4nofz = path2cats+'nofz_woSSR'
#path4nofz = path2cats+'nofz_21and22'
analysis  = 'test'


kwargs = dict(ran_per_sqdeg=10000, 
              cosmo_params={'Om0': 0.31,'H0':69.0,'flat':True},
              tsrmin=0.8,
              ssrmin=0.7,
              galcolnames=['ra','dec','z','z_reliable','sector_tsr',
                      'sector_ssr','weight_systot','isdupl', 'plate_ssr'],
              rancolnames=['ra','dec','sector_ssr','sector_tsr'],
              zbins=np.arange(0.5, 1.2, 0.005),
              path4nofz=path2cats+analysis,
              nofzname='nofz_ebossY1v5_10_7'
             )


class makeNz(object):
    #
    def __init__(self, catlist, **kwargs):
        gal = []
        ran = []
        for cat_i in catlist:
            gal.append(ft.read(g(cat_i), lower=True, columns=galcolnames))
            ran.append(ft.read(r(cat_i), lower=True, columns=rancolnames))
        self.gal = gal
        self.ran = ran
        self.log     = '# pipeline to get n(z) for catalogs {}\n'.format(catlist) 
        
    def helper(self, gal, ran, **kwargs):
        #
        # process
        ranmask = (ran['sector_tsr'] > tsrmin) & (ran['sector_ssr'] > ssrmin)
        area = ran['sector_tsr'][ranmask].sum() / ran_per_sqdeg
        fsky = area / 41253
        galmask = (gal['sector_tsr'] > tsrmin) & (gal['sector_ssr'] > ssrmin)
        galmask &= (gal['z_reliable']) & (~gal['isdupl'])
        #
        # out
        self.log += "# area {}deg2 fsky {}\n".format(area, fsky)
        return nzhist(gal['z'][galmask], fsky, kwargs['cosmo_params'],
                       bins=kwargs['nzbins']) # weight=1./gal['plate_ssr'][galmask]
        
    def run(self, combined=False, save=False, **kwargs):
        self.log += '# going to make n(z) while combined:{}\n'.format(combined)
        if combined:
            gal = np.concatenate(self.gal)
            ran = np.concatenate(self.ran)
            z,nz = self.helper(gal, ran, **kwargs)
        else:
            z=[]
            nz=[]
            for gal_i, ran_i in zip(self.gal, self.ran):
                z_i,nz_i = self.helper(gal_i, ran_i, **kwargs)
                z.append(z_i)
                nz.append(nz_i)
        self.output = {}
        self.output['znz'] = (z, nz)
        self.output['combined'] = combined
        self.output['kwargs'] = **kwargs
        if save:
            write(path4nofz, nofzname+'_combined'+str(combined)[0], self.output, fmt='npy')
            
        
    
"""
def makeNz_21and22(catlist=['1','2'], ):
    gal = []
    ran = []
    for cat_i in catlist:
        gal.append(ft.read(g(cat_i), lower=True, columns=galc))
        ran.append(ft.read(r(cat_i), lower=True, columns=ranc))
    gal = np.concatenate(gal)
    ran = np.concatenate(ran)
    #
    # random
    # reject areas with sector_tsr > tsrc to get area
    #
    ranmask = (ran['sector_tsr'] > tsrc) & (ran['sector_ssr'] > ssrc)
    area = ran['sector_tsr'][ranmask].sum() / ran_in
    fsky = area / 41253
    print("area {}deg2 fsky {}".format(area, fsky))
    #
    # galaxy
    # z_reliable
    galmask = (gal['sector_tsr'] > tsrc) & (gal['sector_ssr'] > ssrc)
    galmask &= (gal['z_reliable']) & (~gal['isdupl'])
#    z, nz = nzhist(gal['z'][galmask], fsky, cosmo_params,
#                   bins=np.arange(0.5, 1.2, 0.005), weight=1./gal['plate_ssr'][galmask])
    z, nz = nzhist(gal['z'][galmask], fsky, cosmo_params,
                   bins=np.arange(0.5, 1.2, 0.005))
    return z, nz



if analysis == 'v05':
    z1, nz1 = makeNz('1')
    z2, nz2 = makeNz('2')
    z3, nz3 = makeNz('3')
    for i,(a,b) in enumerate([(z1,nz1),(z2,nz2),(z3,nz3)]):
        ouname = path4nofz+'/nofz_eboss2'+str(i+1)+'.dat'
        print("output {} is written on {}".format(i, ouname))
        np.savetxt(ouname, np.column_stack([a[:-1], b]))
        print("Done!")

if analysis == 'v06':
    z12, nz12 = makeNz_21and22()
    ouname = path4nofz+'/nofz_eboss21and22.dat'
    print("output is written on {}".format(ouname))
    np.savetxt(ouname, np.column_stack([z12[:-1], nz12]))
    print("Done!")
"""

# output for v05
"""    
(nbodykit) aerimus:scripts mthecosmologist$ python make_nofz.py 
area 145.8878deg2 fsky 0.0035364167454488156
area 319.43395deg2 fsky 0.0077432901849562455
area 165.56625deg2 fsky 0.004013435386517344
output 0 is written on /Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/nofz/nofz_eboss21.dat
output 1 is written on /Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/nofz/nofz_eboss22.dat
output 2 is written on /Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/nofz/nofz_eboss23.dat
Done!
"""
# output for v06
"""
(nbodykit) aerimus:scripts mthecosmologist$ python ebossv05_make_nofz.py v06
area 465.32185deg2 fsky 0.011279709354471189
output is written on /Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/nofz_21and22/nofz_eboss21and22.dat
Done!
"""
