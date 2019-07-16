import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import healpy as hp
import sys
import fitsio as ft
import numpy as np


key = sys.argv[2]
d = ft.read(sys.argv[1], lower=True)

if key == 'dr3':
   PIXEL = d['hpind']
   mjd = d['mjd_min_g']
elif key == 'dr7':
   PIXEL = d['hpix']
   mjd   = d['features'][:,19]
elif key == 'map':
   PIXEL = d['pixel']
   mjd   = d['signal']

thph = hp.pix2ang(256, PIXEL)
ra0,dec = np.degrees(thph[1]), 90-np.degrees(thph[0])
ra = ra0.copy()
#ra[ra0> 180] -= 180




#
# plot
plt.title(sys.argv[1].split('/')[-1])
mjdc = [56216, 56590, 56221, 56239, 56245]
for mjdc_i in mjdc:
    mask = (mjd >= mjdc_i) & (mjd < mjdc_i + 6) # binsize ~ 5.4-5.7
    m = plt.scatter(ra[mask], dec[mask],
        c=mjd[mask], vmin=56200, vmax=56700, marker='s', alpha=0.5)
plt.axis([-5, 50, -6, 6])
plt.xlabel('RA')
plt.ylabel('DEC')
cb = plt.colorbar()
cb.set_label('min MJD g-band')
plt.show()
