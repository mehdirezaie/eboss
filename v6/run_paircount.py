#
#
#import matplotlib.pyplot as plt
import numpy as np
import fitsio as ft
import nbodykit.lab as nb
from nbodykit import setup_logging, style
setup_logging() # turn on logging to screen




from mpi4py import MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()   


from argparse import ArgumentParser
ap = ArgumentParser(description='Neural Net regression')
ap.add_argument('--galaxy_path',  default='NONE')
ap.add_argument('--output_path',  default='NONE')
# ap.add_argument('--nmesh',        default=256, type=int)
ap.add_argument('--zlim',         nargs='*',   type=float, default=[0.8, 2.2])
# ap.add_argument('--sys_tot',      action='store_true')
ns = ap.parse_args()

# 
data    = nb.FITSCatalog(ns.galaxy_path)
print(data.columns)
data['Weight'] = data['WEIGHT_FKP']
#data['Weight'] = data['WEIGHT_CP']*data['WEIGHT_NOZ']*data['WEIGHT_SYSTOT']*data['WEIGHT_FKP']

ZMIN = ns.zlim[0]
ZMAX = ns.zlim[1]

# slice the data and randoms
print('before', data.size)  
valid = (data['Z'] > ZMIN) & (data['Z'] < ZMAX)
data = data[valid]
print('after', data.size)

if rank == 0:    
    print('data    columns = ',    data.columns, data.size)

# #
edges = np.logspace(np.log10(0.1), np.log10(5000.0), 100)
# # edges = np.linspace(0.001, 5000.0, 100) # linear
cosmo = nb.cosmology.Planck15
RR    = nb.SurveyDataPairCount('2d', data, edges, Nmu=20, cosmo=cosmo, 
                                ra='RA', dec='DEC', redshift='Z', weight='Weight',
                                show_progress=True)
# save
RR.save(ns.output_path)
