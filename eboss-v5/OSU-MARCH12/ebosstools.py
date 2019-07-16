import sys
import os
import fitsio as ft
import numpy as np
sys.path.append('/Users/mthecosmologist/Dropbox/github/DESILSS')
from tools import nzhist, write # for nz
from syslss import powerspectrum, iusp, radec2hpix # for pk
from syslss import hpixsum, ngalsys # for systematic fit

path2cats = '/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/'
g  = lambda i: path2cats+'eboss2'+i+'.v5_10_7.latest.fits'
r  = lambda i: path2cats+'eboss2'+i+'.v5_10_7.latest.rands.fits'
analysis  = 'woSSR'
kwargs = dict(ran_per_sqdeg=10000, 
              cosmo_params={'Om0': 0.31,'H0':69.0,'flat':True},
              tsrmin=0.8,
              ssrmin=0.7,
              galcolnames=['ra','dec','z','z_reliable','sector_tsr',
                      'sector_ssr','weight_systot','isdupl', 'plate_ssr'],
              rancolnames=['ra','dec','sector_ssr','sector_tsr'],
              zbins=np.arange(0.5, 1.2, 0.005),
              path4nofz=path2cats+analysis,
              nofzname='nofz_ebossY1v5_10_7',
              zlim=(0.6,1.1),
              nmesh=256,
              kpkname='kpk_ebossY1v5_10_7',
              path4kpks=path2cats+analysis,
              sysweight=None
             )

"""
    N(z) calculation
    last update: Jan 9, 2018
    
    steps:
    # 21, 22, 23 separate
    1. allsep = makeNz(['1','2','3'], **kwargs)
    2. allsep.run(save=True, combined=False, **kwargs)
    3. print(allsep.log)
"""
class makeNz(object):
    #
    def __init__(self, catlist, galcolnames=None,rancolnames=None, **kwargs):
        gal = []
        ran = []
        for cat_i in catlist:
            gal.append(ft.read(g(cat_i), lower=True, columns=galcolnames))
            ran.append(ft.read(r(cat_i), lower=True, columns=rancolnames))
        self.gal = gal
        self.ran = ran
        self.log     = '# pipeline to get n(z) for catalogs {}\n'.format(catlist) 
        
    def helper(self, gal, ran, tsrmin=None, ssrmin=None,
               ran_per_sqdeg=None, cosmo_params=None,
               zbins=None, **kwargs):
        #
        # process

        ranmask = (ran['sector_tsr'] > tsrmin) & (ran['sector_ssr'] > ssrmin)
        area = ran['sector_tsr'][ranmask].sum() / ran_per_sqdeg
        fsky = area / 41253
        galmask = (gal['sector_tsr'] > tsrmin) & (gal['sector_ssr'] > ssrmin)
        galmask &= (gal['z_reliable']) & (~gal['isdupl'])
        #
        # out
        self.log += "# both galaxy&random sector_tsr > {} sector_ssr > {} \n".format(tsrmin, ssrmin)
        self.log += "# z_reliable == True   isdupl == False \n"
        self.log += "# area {}deg2 fsky {}\n".format(area, fsky)
        return nzhist(gal['z'][galmask], fsky, cosmo_params, bins=zbins) # weight=1./gal['plate_ssr'][galmask]
        
    def run(self, combined=False, save=False, nofzname='nofz', path4nofz='./',**kwargs):
        self.log += '# going to make n(z) while combined:{}\n'.format(combined)
        if combined:
            gal = np.concatenate(self.gal)
            ran = np.concatenate(self.ran)
            z,nz = self.helper(gal, ran, **kwargs)
            z = z[:-1]
        else:
            z=[]
            nz=[]
            for gal_i, ran_i in zip(self.gal, self.ran):
                z_i,nz_i = self.helper(gal_i, ran_i, **kwargs)
                z.append(z_i[:-1])
                nz.append(nz_i)
        self.output = {}
        self.output['znz'] = (z, nz)
        self.output['combined'] = combined
        self.output['kwargs'] = kwargs
        if save:
            ouname = nofzname+'_combined'+str(combined)[0]
            self.log += '# {} is written under {}\n'.format(ouname, path4nofz)
            self.output['log'] = self.log
            write(path4nofz, ouname, self.output, fmt='npy')
def plot_nz(nzall, nzcomb):
    import matplotlib.pyplot as plt
    plt.rc('font', size=25, family='sans-serif')
    plt.rc('axes.spines', right=False, top=False)
    plt.rc('figure', figsize=(12,8))
    ax = plt.subplot(111)
    c  = ['k','r','b']
    lt = ['-',':','--']
    for i in range(len(nzall['znz'][0])):
        z, nz = nzall['znz'][0][i], nzall['znz'][1][i]
        ax.step(z, 1e4*nz, linestyle=lt[i], color=c[i], alpha=1.0-0.2*i)
        ax.text(0.7,0.90-i*0.05, 'eboss2'+str(i+1), transform=ax.transAxes, color=c[i])
        if i ==0:ax.text(0.01, 0.9, 'eff. area from randoms weighted by sector_TSR\n'
                                     +'sector_TSR >0.8, sector_SSR >0.7\n'
                                     +'doubles are removed & Z_reliable=TRUE',
                        transform=ax.transAxes, fontsize=10)

    z, nz = nzcomb['znz'][0], nzcomb['znz'][1]
    ax.step(z, 1e4*nz, linestyle='-', color='violet', alpha=1.0)
    ax.text(0.7, 0.9-.15, 'eboss21+22', transform=ax.transAxes, color='violet')
    ax.set_xlabel('z')
    ax.set_ylabel(r'n(z) [10$^{4}(h/Mpc)^{3}$]')
#
#
"""
    computing P_l(k) l = 0, 2, 4
    1. path2nofz = '/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/'\
            +'woSSR/nofz_ebossY1v5_10_7_combinedF.npy'
    2. pksep = computePk(['1','2','3'], **kwargs)
    3. pksep.run(save=True, combined=False, path2nofz=path2nofz, **kwargs)
    4. print(pksep.log)
"""        
        
        
class computePk(object):
    def __init__(self, catlist, galcolnames=None,rancolnames=None, **kwargs):
        gal = []
        ran = []
        for cat_i in catlist:
            gal.append(ft.read(g(cat_i), lower=True, columns=galcolnames))
            ran.append(ft.read(r(cat_i), lower=True, columns=rancolnames))
        self.gal = gal
        self.ran = ran
        self.log     = '# pipeline to get P(k) for catalogs {}\n'.format(catlist)
        
    def helper(self, gal, ran, nofz, sysweight=None, 
               tsrmin=None, ssrmin=None, zlim=None, 
               cosmo_params=None, nmesh=None, **kwargs):
        galmask = (gal['sector_tsr'] > tsrmin) & (gal['sector_ssr'] > ssrmin)
        galmask &= (gal['z_reliable']) & (~gal['isdupl'])
        gal = gal[galmask]
        #
        maskz = (gal['z'] > zlim[0]) & (gal['z'] < zlim[1])
        #
        #
        ranmask = (ran['sector_tsr'] > tsrmin) & (ran['sector_ssr'] > ssrmin)
        ran = ran[ranmask]
        ranz = np.random.choice(gal['z'][maskz], size=ran.size)
        ranw = ran['sector_tsr'] #* ran['plate_ssr'] # AJR thinks plate_SSR is not right
        if sysweight is not None:
            ranw *= sysweight.mapit(ran['ra'], ran['dec'])
            galw = np.ones(gal.size) # no sys weight        
            #raise RuntimeError('sys weight not implemented yet!')
        else:    
            galw = np.ones(gal.size) # no sys weight        
        #
        #
        galaxy = cat(gal['ra'], gal['dec'], gal['z'], galw)
        random = cat(ran['ra'], ran['dec'], ranz, ranw)
        #
        # compute pk for a given redshift bin
        eboss = powerspectrum(galaxy, random, nofz, cosmo_params)
        self.log += "# both galaxy&random sector_tsr > {} sector_ssr > {} \n".format(tsrmin, ssrmin)
        self.log += "# z_reliable == True   isdupl == False \n"
        self.log += "# computing p(k) for {0} < z < {1} with nmesh of {2} \n".format(*zlim, nmesh)
        return eboss.run(zlim, nmesh)
    
    def run(self, combined=False, save=False, 
            kpkname='kpk', path4kpks='./', path2nofz=None, **kwargs):
        self.log += '# going to make P(k) while combined:{}\n'.format(combined)
        nofzb = np.load(path2nofz).item()
        if combined:
            gal = np.concatenate(self.gal)
            ran = np.concatenate(self.ran)
            nofz  = iusp(nofzb['znz'][0], nofzb['znz'][1])
            kpk = self.helper(gal, ran, nofz, **kwargs)
        else:
            kpk=[]
            for i,(gal_i, ran_i) in enumerate(zip(self.gal, self.ran)):
                nofz  = iusp(nofzb['znz'][0][i], nofzb['znz'][1][i])
                kpk_i = self.helper(gal_i, ran_i, nofz, **kwargs)
                kpk.append(kpk_i)
        self.output = {}
        self.output['combined'] = combined
        self.output['kpk'] = kpk
        self.output['kwargs'] = kwargs
        if save:
            ouname = kpkname+'_combined'+str(combined)[0]
            self.log += '# {} is written under {}\n'.format(ouname, path4kpks)
            self.output['log'] = self.log
            write(path4kpks, ouname, self.output, fmt='npy')


"""
    Systematic fit (R-band bright stars R<21) correction
    1. make_footprint_mask
    2. get_delta_rbs
    3. make_correction_map
    
    selection_rbs = ft.read('/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/selection_rbsfit.fits')
    run power spectrum code with sysweight=sysweight_rbs
    where sysweight_rbs = SYSweight(selection_rbs)
    
"""            
class cat(object):
    # class to prepare our catalogs for Nbodykit
    def __init__(self, ra, dec, z, w):
        self.RA = ra
        self.DEC = dec
        self.Z = z
        self.Weight = w
        
class systematic(object):
    def __init__(self, sysname, mask):
        df = sysname #ft.read(sysname, lower=True)
        self.HPIX = np.argwhere(~np.logical_not(mask)).flatten()
        self.SIGNAL = df[~np.logical_not(mask)]
        
class SYSweight(object):
    #
    def __init__(self, selection, nside=256):
        self.selection = selection
        self.nside     = nside
    def mapit(self, ra, dec):
        return self.selection[radec2hpix(self.nside, ra, dec)]

def make_footprint_mask(cats=[1,2], **kwargs):
    ran = []
    for i in cats:
        ran.append(ft.read(r(str(i)), lower=True, columns=kwargs['rancolnames']))
    ran = np.concatenate(ran)
    ranmask = (ran['sector_tsr'] > kwargs['tsrmin']) & (ran['sector_ssr'] > kwargs['ssrmin'])
    ran = ran[ranmask]
    ranmap = hpixsum(256, ran['ra'], ran['dec'], value=ran['sector_tsr'])
    ft.write('/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/sector_tsr_ssr_mask_p8_p7.fits', ranmap)

def get_delta_rbs(cats=[1,2], **kwargs):
    ranmap = ft.read('/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/sector_tsr_ssr_mask_p8_p7.fits')
    irs = ft.read('/Volumes/Mehdi_Passport/NERSC_archive/other_files/dr3.1/heal_rbs_256.fits')
    gal = []
    for i in cats:
        gal.append(ft.read(g(str(i)), lower=True, columns=kwargs['galcolnames']))
    gal = np.concatenate(gal)
    galmask = (gal['sector_tsr'] > kwargs['tsrmin']) & (gal['sector_ssr'] > kwargs['ssrmin'])
    galmask &= (gal['z'] > kwargs['zlim'][0]) & (gal['z'] < kwargs['zlim'][1])
    galmask &= (gal['z_reliable']) & (~gal['isdupl'])
    gal = gal[galmask]
    galm = cat(gal['ra'], gal['dec'], gal['z'], np.ones(gal['ra'].size))
    irs256 = systematic(irs, ranmap)
    ebossrbs = ngalsys(galm, 256)
    ebossrbs.prepare_inputs(irs256, selection_function=ranmap)
    ebossrbs.digitize_ngalsys(np.logspace(1.8, 3, 16))
    ebossrbs.processjack()
    write('/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/', 'delta_rbs', ebossrbs.output, fmt='npy')
    

def make_correction_map():
    from scipy.optimize import minimize
    drbs = np.load('/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/delta_rbs.npy').item()
    rbsfit = sysfit(drbs['bin_edges'][:-1], drbs['delta'], drbs['delta_err'], mask=(drbs['bin_edges'][:-1]<550))
    rbsfit.Minimize([.0,0.0])
    irs = ft.read('/Volumes/Mehdi_Passport/NERSC_archive/other_files/dr3.1/heal_rbs_256.fits')
    selection_rbs = rbsfit.makeSF(irs)
    ft.write('/Users/mthecosmologist/analyses/eboss/ebossY1v5_10_7/selection_rbsfit.fits', selection_rbs)
    
def model(theta, x, *args):
    return theta[0] + theta[1] * x

def cf(theta, x, xrange, empty=0.0):
    xmin = xrange[0]
    xmax = xrange[1]
    y    = np.zeros(x.size)
    low = x<= xmin
    high = x>= xmax
    middle = ~(low | high)
    y[low] = model(theta, xmin)
    y[high] = model(theta, xmax)
    y[middle] = model(theta, x[middle])
    y[x==empty] = 0.0
    return y
class sysfit(object):
    def __init__(self,x,y,ye, mask=None):
        if mask is None:
            mask = np.ones(x.size, '?')
        self.org = (x,y,ye)
        self.x  = x[mask]
        self.y  = y[mask]
        self.ye = ye[mask]
        self.mask = mask
        
    def chi2(self, theta,  *args):
        return np.mean( ((model(theta, self.x) - self.y)/(self.ye))**2)
        
    def Minimize(self, theta0):
        self.res = minimize(self.chi2, theta0)
        self.theta = self.res.x
    def plot(self, ylim=(0.7, 1.2)):
        xgrid = np.linspace(self.x.min(), self.x.max())
        xt  = np.linspace(10, 600, 100)
        ax = plt.subplot(111)
        ax.errorbar(*self.org, linestyle='None', marker='o')
        ax.plot(xt, 0.005+cf(self.theta, xt, (self.x.min(), self.x.max())), color='violet')
        ax.plot(xgrid, model(self.theta, xgrid), color='r')
        ax.plot(xgrid, model([1.,0], xgrid), 'k--' )
        ax.text(0.1,0.2, r'$\chi^{}_{}$={:.2f}'.format(2,"{lin}",self.chi2(self.theta)), transform=ax.transAxes, color='r')
        ax.text(0.1,0.1, r'$\chi^{}_{}$={:.2f}'.format(2,"{null}",self.chi2([1.,0])), transform=ax.transAxes, color='k')
        ax.set_ylim(ylim)
        ax.set_xlabel('# R-band BS')
        ax.set_ylabel(r'$N_{gal}/N_{ran, normed}$')
    def makeSF(self, sysmap, empty=0.0):
        return cf(self.theta, sysmap, (self.x.min(), self.x.max()), empty=empty)