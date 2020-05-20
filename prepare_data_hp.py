
import sys
sys.path.append('/home/mehdi/github/LSSutils')

from LSSutils.catalogs.combinefits import EbossCatalog, RegressionCatalog
from LSSutils.catalogs.datarelease import zcuts
from LSSutils import setup_logging



# single file
cat = sys.argv[1]
nside = int(sys.argv[2])



zslices = ['low', 'high', 'zhigh']
ran = cat.replace('.dat.', '.ran.')
print(cat, nside)

data = EbossCatalog(cat, kind='galaxy', zmin=0.8, zmax=3.5)
random = EbossCatalog(ran, kind='random', zmin=0.8, zmax=3.5)    


# no cut on randoms
key_i = 'tot'
ran_i = ran.replace('.ran.', f'_{key_i}.hp{nside}.ran.')
random.tohp(nside, raw=False)
random.writehp(ran_i)    
print(key_i, zcuts[key_i])

# data
for key_i in zslices:
    cat_i = cat.replace('.dat.', f'_{key_i}.hp{nside}.dat.')    
    #print(key_i, zcuts[key_i], cat_i, ran_i)
    
    # cut data
    data.cutz(zcuts[key_i])
    data.tohp(nside, raw=False)
    data.writehp(cat_i)    


