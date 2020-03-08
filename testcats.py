import sys
import fitsio as ft

name = sys.argv[1]
data = ft.read(name)
total = data.size
totalw = (data['WEIGHT_SYSTOT']*data['WEIGHT_CP']*data['WEIGHT_FKP']*data['WEIGHT_NOZ']).sum()

print('{:70s} {:9d} {:9.3f}'.format(name.split('/')[-1], total, totalw))

