import matplotlib
matplotlib.use('Agg') # png/pdf backend
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
labels = ['debv_lenz_sfd','loghii',
              'hpgaiastardens', 'hpebv',
              'hppsfdepth_r', 'hppsfdepth_g',
              'hppsfdepth_z', 'hpgaldepth_r',
              'hpgaldepth_g', 'hpgaldepth_z',
              'hppsfsize_r', 'hppsfsize_g',
              'hppsfsize_z']


def ablation_plot(filename):    
    ab1 = np.load(filename).item()
    #
    INDICES = ab1['indices']
    VALUES  = ab1['validmin']
    FEAT    = ab1['importance'] + [i for i in range(13) if i not in ab1['importance']]

    matric_dict = {}
    for i in range(len(INDICES)):
        for j in range(len(VALUES[i])):
            matric_dict[str(i)+'-'+str(INDICES[i][j])] = VALUES[i][j]

    matric = np.zeros(shape=(13, 13))
    for i in range(12):
        for j, sys_i in enumerate(FEAT):
            if str(i)+'-'+str(sys_i) in matric_dict.keys():
                matric[i,j] = (matric_dict['%d-%d'%(i,sys_i)][0]/ab1['RMSEall'])-1.#-ab1['baselineRMSE']
    #bands = ['r','g','z']
    #labels = ['ebv','nstar']
    #labels += ['depth-'+b for b in bands]
    #labels += ['seeing-'+b for b in bands]
    #labels += ['airmass-'+b for b in bands]
    #labels += ['skymag-'+b for b in bands]
    #labels += ['exptime-'+b for b in bands]
    #labels += ['mjd-'+b for b in bands]
    xlabels = [labels[j] for j in FEAT]
    mask = ~np.zeros_like(matric, dtype=np.bool)
    #mask[np.triu_indices_from(mask)] = False
    mask[matric==0.0] = False
    vmin = np.minimum(np.abs(np.min(matric)), np.abs(np.max(matric))) * 0.1
    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))
    #plt.title('Correlation Matrix of DR5')
    # Generate a custom diverging colormap
    kw = dict(mask=~mask, cmap=plt.cm.seismic_r, xticklabels=xlabels,
               yticklabels=xlabels[::-1], center=0.0, vmin=-1.*vmin, vmax=vmin, 
                square=True, linewidths=.5, cbar_kws={"shrink": .5, "label":r'$\delta$RMSE'})
    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(matric, **kw)
    ax.set_xticklabels(xlabels, rotation=80)
    ax.set_yticks([])
    ax.xaxis.tick_top()
    ou = ''.join([filename, '.png'])
    print('save ... ', ou)
    plt.savefig(ou, bbox_inches='tight')


import sys


ablation_plot(sys.argv[1])

