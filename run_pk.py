#
#
#import matplotlib.pyplot as plt
from nbodykit.transform import SkyToCartesian
from nbodykit.cosmology import Cosmology
import nbodykit.lab as nb
from nbodykit import setup_logging, style
setup_logging() # turn on logging to screen




from mpi4py import MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()   


from argparse import ArgumentParser
ap = ArgumentParser(description='Neural Net regression')
ap.add_argument('--galaxy_path',  default='/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_NGC_v6.dat.fits')
ap.add_argument('--random_path',  default='/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_NGC_v6.ran.fits')
ap.add_argument('--output_path',  default='/Volumes/TimeMachine/data/eboss/v6/results_ngc/clustering/pk_256_p8_2p2')
ap.add_argument('--nmesh',        default=256, type=int)
ap.add_argument('--zlim',         nargs='*',   type=float, default=[0.8, 2.2])
ap.add_argument('--sys_tot',      action='store_true')
ns = ap.parse_args()

# 
data    = nb.FITSCatalog(ns.galaxy_path)
randoms = nb.FITSCatalog(ns.random_path)

if rank == 0:    
    print('data    columns = ',    data.columns, data.size)
    print('randoms columns = ', randoms.columns, randoms.size)
    
ZMIN = ns.zlim[0]
ZMAX = ns.zlim[1]

# slice the data and randoms
for source in [data, randoms]:
    valid = (source['Z'] > ZMIN) & (source['Z'] < ZMAX)
    source = source[valid]

# the fiducial BOSS DR12 cosmology
cosmo = Cosmology(h=0.676).match(Omega0_m=0.31)

# add Cartesian position column
data['Position']    = SkyToCartesian(data['RA'],    data['DEC'],    data['Z'],    cosmo=cosmo)
randoms['Position'] = SkyToCartesian(randoms['RA'], randoms['DEC'], randoms['Z'], cosmo=cosmo)

# apply the Completeness weights to both data and randoms
if ns.sys_tot:
    if rank ==0:print('including sys_tot')
    data['WEIGHT']      = data['WEIGHT_SYSTOT']    * data['WEIGHT_NOZ']    * data['WEIGHT_CP']
else:
    if rank ==0:print('excluding sys_tot')    
    data['WEIGHT']      = data['WEIGHT_NOZ']    * data['WEIGHT_CP'] # data['WEIGHT_SYSTOT'] 
    
randoms['WEIGHT']   = randoms['WEIGHT_SYSTOT'] * randoms['WEIGHT_NOZ'] * randoms['WEIGHT_CP']

# combine the data and randoms into a single catalog
fkp  = nb.FKPCatalog(data, randoms)
mesh = fkp.to_mesh(Nmesh=ns.nmesh, nbar='NZ', fkp_weight='WEIGHT_FKP', comp_weight='WEIGHT', window='tsc')

# compute 
r = nb.ConvolvedFFTPower(mesh, poles=[0,2,4], dk=0.005, kmin=0.0)

# save
r.save(ns.output_path)