
import sys
sys.path.append('/home/mehdi/github/LSSutils')

from LSSutils.catalogs.combinefits import EbossCatalog, RegressionCatalog
from LSSutils.catalogs.datarelease import zcuts
from LSSutils import setup_logging

nside = 512
cats = sys.argv[1:]
for cat in cats:
    ran = cat.replace('.dat.', '.ran.')
    print(cat)
    
    data = EbossCatalog(cat, kind='galaxy', zmin=0.8, zmax=3.5)
    random = EbossCatalog(ran, kind='random', zmin=0.8, zmax=3.5)    
    
    for key_i in zcuts:
        cat_i = cat.replace('.dat.', f'_{key_i}.hp{nside}.dat.')
        ran_i = ran.replace('.ran.', f'_{key_i}.hp{nside}.ran.')
        #print(key_i, zcuts[key_i], cat_i, ran_i)
        
        # cut data
        data.cutz(zcuts[key_i])
        data.tohp(nside, raw=False)
        data.writehp(cat_i)    

        # cut randoms
        
        #self.random.cutz(zcuts[key_i])
        if key_i == 'tot':            
            random.tohp(nside, raw=False)
            random.writehp(ran_i)    
        print(key_i, zcuts[key_i])