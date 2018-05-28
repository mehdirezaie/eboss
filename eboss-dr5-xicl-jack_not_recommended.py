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

class XI_JACK(object):
    def __init__(self, theta, phi, weight, delta):
        self.theta  = theta
        self.phi    = phi
        self.weight = weight
        self.delta  = delta
    def run(self):
        bw = 3.*hp.nside2resol(256)*180./3.1416  # 3x resol.
        bins = np.arange(bw, 10, bw)
        njack = len(self.theta)
        self.result = dict()
        # jackknife samples
        for m in range(njack):
            thetal  = self.theta.copy()
            phil    = self.phi.copy()
            weightl = self.weight.copy()
            deltal  = self.delta.copy()
            thetal.pop(m)
            phil.pop(m)
            weightl.pop(m)
            deltal.pop(m)
            t = np.concatenate(thetal)
            p = np.concatenate(phil)
            w = np.concatenate(weightl)
            d = np.concatenate(deltal)
            t1 = time()
            self.result[m] = XI(t, p, d, d, w, bins)
            print('s{} done in {} s'.format(m, time()-t1))
        # all samples
        thetal  = self.theta.copy()
        phil    = self.phi.copy()
        weightl = self.weight.copy()
        deltal  = self.delta.copy()
        t = np.concatenate(thetal)
        p = np.concatenate(phil)
        w = np.concatenate(weightl)
        d = np.concatenate(deltal)
        t1 = time()
        self.result[-1] = XI(t, p, d, d, w, bins)
        print('sample {} done in {} s'.format('all', time()-t1))



# read map
# read elgmap and ranmap
elgmap = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/eboss/eBOSS.ELGhpmap.fits')
ranmap = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/eboss/eBOSS.ELGRANhpmap.fits')


weight = sys.argv[1]
if weight == 'nn':
    select_fun = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/march22/nn-weights-hpmap256.fits')
elif weight == 'lin':
    select_fun = hp.read_map('/global/cscratch1/sd/mehdi/dr5_anand/march22/lin-weights-hpmap256.fits')
elif weight == 'uni':
    select_fun = np.ones(elgmap.size) # nside = 256
else:
    sys.exit("weight is not provided correctly!")

# find a common mask
mask = ranmap != 0.0



delta = np.zeros(12*256*256)
randc = ranmap * select_fun
sf    = (elgmap[mask].sum() / randc[mask].sum())
delta[mask] = elgmap[mask] / randc[mask] / sf - 1
w = ranmap[mask]

theta, phi = hp.pix2ang(256, np.argwhere(mask).flatten())

thetal, phil, wl, deltal = split_jackknife(theta, phi, w, delta[mask])
dr5jack = XI_JACK(thetal, phil, wl, deltal)
dr5jack.run()

# run

# save
np.save('/global/cscratch1/sd/mehdi/dr5_anand/march22/xi-cl-dr5_jackerr_'+weight, dr5jack.result)


