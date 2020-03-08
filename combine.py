import sys
import fitsio as ft
import numpy as np




def main(files, output):
    data = []
    for ifile in files:
        data.append(ft.read(ifile))
    data = np.concatenate(data)

    ft.write(output, data)
    print('done')



output = sys.argv[1]
files  = sys.argv[2:]
main(files, output)
