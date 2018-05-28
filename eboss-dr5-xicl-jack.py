#
import sys
sys.path.append('/global/homes/m/mehdi/github/DESILSS')

#
import healpy as hp
import numpy as np
from xi import XI
from time import time

def split_jackknife(theta, phi, weight, delta, njack=20):
    f = weight.sum() // njack
    theta_L = []
    theta_l = []
    phi_L = []
    phi_l = [] 
    frac_L = []
    frac    = 0
    delta_L = []
    delta_l = []
    w_L = []
    w_l = []

    for i in range(theta.size):
        frac += weight[i]            
        theta_l.append(theta[i])
        phi_l.append(phi[i])
        delta_l.append(delta[i])
        w_l.append(weight[i])
        if frac >= f:
            theta_L.append(theta_l)
            phi_L.append(phi_l)
            frac_L.append(frac)
            delta_L.append(delta_l)
            w_L.append(w_l)
            frac    = 0
            w_l     = []
            theta_l = []
            phi_l   = []
            delta_l = []
#         elif i == theta.size-1:
#             theta_L.append(theta_l)
#             phi_L.append(phi_l)
#             frac_L.append(frac)
#             delta_L.append(delta_l)
#             w_L.append(w_l)
    return theta_L, phi_L, w_L, delta_L #, frac_L

def hpupgrade(mapin, res_o, res_i):
    ipix       = np.arange(12*res_o**2)  # 1, 2, .... 12*nside**2 
    theta, phi = hp.pix2ang(res_o, ipix) # radian
    ipix_o     = hp.ang2pix(res_i, theta, phi)
    return mapin[ipix_o]

class XI_JACK(object):
    def __init__(self, elgmap, ranmap, select_fun, mask):
#         mask = ranmap > 0.2  # min fracgood = 0.25
        delta = np.zeros(12*1024*1024)
        randc = ranmap * select_fun
        sf    = (elgmap[mask].sum() / randc[mask].sum())
        delta[mask] = elgmap[mask] / randc[mask] / sf - 1
        w = ranmap[mask]
        theta, phi = hp.pix2ang(1024, np.argwhere(mask).flatten())
        thetal, phil, wl, deltal = split_jackknife(theta, phi, w, delta[mask])
        self.theta  = thetal
        self.phi    = phil
        self.weight = wl
        self.delta  = deltal
    def run(self):
        bw = 3.*hp.nside2resol(1024)*180./3.1416  # 3x resol.
        bins = np.arange(bw, 10, bw)
        njack = len(self.theta)
        print('njack ', njack)
        self.result = dict()
        for m in range(njack):
            t  = self.theta[m].copy()
            p  = self.phi[m].copy()
            w  = self.weight[m].copy()
            d  = self.delta[m].copy()
            t1 = time()
            self.result[m] = XI(t, p, d, d, w, bins)
            print('sample{} done in {} s'.format(m, time()-t1))
        #
        #
        xijackl = []
        for i in range(njack): # jackknife
            wa = np.zeros(len(bins)-1)
            wb = np.zeros(len(bins)-1)
            for j in range(njack): 
                if j!=i:
                    wa += self.result[j][1]
                    wb += self.result[j][2]
            xijackl.append(wa/wb)

        wa = np.zeros(len(bins)-1)
        wb = np.zeros(len(bins)-1)
        for j in range(njack): 
            wa += self.result[j][1]
            wb += self.result[j][2]
        xiall  = wa/wb
        var = np.zeros(len(bins)-1)
        for i in range(njack):
            var += (xiall - xijackl[i])**2
        var *= (njack-1)/njack
        self.output = dict(alls=self.result, t=0.5*(bins[:-1]+bins[1:]),
                           njack=njack, w=xiall, werr=np.sqrt(var), wjacks=xijackl)


# read map
# read elgmap and ranmap
#elgmap = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/eboss/eBOSS.ELGhpmap.fits')
# read elgmap and ranmap
elgmap = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/eboss/eBOSS.ELGhpmap1024.fits')
ranmap256 = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/eboss/eBOSS.ELGRANhpmap.fits')
ranmap    = hpupgrade(ranmap256, 1024, 256)


weight = sys.argv[1]
if weight == 'nn':
    select_256 = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/march22/nn-weights-hpmap256.fits')
    select_fun = hpupgrade(select_256, 1024, 256)
elif weight == 'lin':
    select_256 = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/march22/lin-weights-hpmap256.fits')
    select_fun = hpupgrade(select_256, 1024, 256)
elif weight == 'uni':
    select_fun = np.ones(elgmap.size) # nside = 1024
else:
    sys.exit("weight is not provided correctly!")

# find a common mask
mask = ranmap != 0.0




xijack = XI_JACK(elgmap, ranmap, select_fun, mask)
xijack.run()
np.save('/global/cscratch1/sd/mehdi/dr5_anand/march22/xi-dr5-jack1024-'+weight, xijack.output)

