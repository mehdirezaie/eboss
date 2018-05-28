#
import sys
sys.path.append('/global/homes/m/mehdi/github/DESILSS')

#
import healpy as hp
import numpy as np
import syslss as sl


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
mask1 = ranmap != 0.0


# run
dr5 = sl.AngularClustering2D(elgmap, ranmap, selection_function=select_fun, hpmap=True, mask=mask1)
results = dr5.run_paircount()

# save
np.save('/global/cscratch1/sd/mehdi/dr5_anand/march22/xi-cl-dr5_'+weight, results)


