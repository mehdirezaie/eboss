'''
    Function to carry out analysis on eBOSS Catalogs
    (c) Mehdi Rezaie
    last edit : Sep 18, 2019


'''
path2LSSutils = '/home/mehdi/github/LSSutils'
path2sysmaps  = '/home/mehdi/data/eboss/sysmaps/SDSS_HI_imageprop_nside256.h5'


import sys
sys.path.append(path2LSSutils)
import matplotlib as mpl
#mpl.use('Agg')

import numpy as np
from glob import glob
import matplotlib.pyplot as plt
try:
    import fitsio as ft
    import LSSutils.catalogs.combinefits as cf
    import LSSutils.utils as ut
    from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as mycols
    import pandas as pd
    import healpy as hp
except:
    print('Modules not loaded')
    

def shuffle():
    d   = np.load('/home/mehdi/data/eboss/v7/ngal_features_NGC_0.8.hp256.5r.npy', allow_pickle=True).item()
    out = lambda i:'/home/mehdi/data/eboss/v7/ngal_features_NGC_0.8_sh_'+str(i)+'.hp256.5r.npy'
    for j in range(100):
        for partition in ['validation', 'train']:
            for fold_i in d[partition].keys():
                myfold   = d[partition][fold_i]
                label_sh = np.random.permutation(myfold['label'])
                d[partition][fold_i]['label'] = label_sh
        #print(j, d['validation']['fold0']['label'][:5])
        np.save(out(j), d)
        if j%20==0:print('saved', out(j))
    
    
    
def swap_weights_plain():
    path = '/home/mehdi/data/eboss/v7/'
    weight = lambda x, y: path + 'results_'+x+'_'+y+'/regression/nn_plain/nn-weights.hp512.fits'
    def get_weights(CAP):
        redshifts = ['0.8', '1.1', '1.4', '1.6', '1.9']
        return dict(zip(redshifts, [weight(CAP,y) for y in redshifts]))

    for ab in ['plain']:    
        for CAP in ['NGC', 'SGC']:
            zcuts = {'0.8': [0.8000000000000000, 1.1423845339193297],
                     '1.1': [1.1423845339193297, 1.3862779004064971],
                     '1.4': [1.3862779004064971, 1.6322502623999630],
                     '1.6': [1.6322502623999630, 1.8829689752636356],
                     '1.9': [1.8829689752636356, 2.2000000000000000]}
            # z-dependent
            wtag    = '_'.join(('wnnz', ab))
            incat   = path + 'eBOSS_QSO_clustering_'+CAP+'_v7.dat.fits'
            outcat  = path + 'eBOSS_QSO_clustering_'+CAP+'_v7_'+wtag+'.dat.fits'
            weights = get_weights(CAP)

            print('writing %s'%outcat)
            mycat   = cf.swap_weights(incat)
            mycat.run(weights, zcuts)
            mycat.to_fits(outcat)
            print(100*'=','\n')        
            
def swap_weights256more(model='plain'):
    path = '/home/mehdi/data/eboss/v7/'
    weight = lambda x, y: path + 'results_'+x+'_'+y+'_256/regression/nn_'+model+'/nn-weights.hp256.fits'
    def get_weights(CAP):
        redshifts = ['0.8', '1.1', '1.4', '1.6', '1.9']
        return dict(zip(redshifts, [weight(CAP,y) for y in redshifts]))

    for ab in [model+'256more']:    
        for CAP in ['NGC', 'SGC']:
            zcuts = {'0.8': [0.80, 1.14],
                     '1.1': [1.14, 1.39],
                     '1.4': [1.39, 1.63],
                     '1.6': [1.63, 1.88],
                     '1.9': [1.88, 2.20]}
            # z-dependent
            wtag    = '_'.join(('wnnz', ab))
            incat   = path + 'eBOSS_QSO_clustering_'+CAP+'_v7.dat.fits'
            outcat  = path + 'eBOSS_QSO_clustering_'+CAP+'_v7_'+wtag+'.dat.fits'
            weights = get_weights(CAP)

            print('writing %s'%outcat)
            mycat   = cf.swap_weights(incat)
            mycat.run(weights, zcuts)
            mycat.to_fits(outcat)
            print(100*'=','\n')   
            
def swap_weights256():
    path = '/home/mehdi/data/eboss/v7/'
    weight = lambda x, y: path + 'results_'+x+'_'+y+'_256/regression/nn_plain/nn-weights.hp256.fits'
    def get_weights(CAP):
        redshifts = ['low', 'high']
        return dict(zip(redshifts, [weight(CAP,y) for y in redshifts]))

    for ab in ['plain256']:    
        for CAP in ['NGC', 'SGC']:
            zcuts     = {'low':[0.8, 1.508088732762684], 
                         'high':[1.508088732762684, 2.2]}
            # z-dependent
            wtag    = '_'.join(('wnnz', ab))
            incat   = path + 'eBOSS_QSO_clustering_'+CAP+'_v7.dat.fits'
            outcat  = path + 'eBOSS_QSO_clustering_'+CAP+'_v7_'+wtag+'.dat.fits'
            weights = get_weights(CAP)

            print('writing %s'%outcat)
            mycat   = cf.swap_weights(incat)
            mycat.run(weights, zcuts)
            mycat.to_fits(outcat)
            print(100*'=','\n')    


            
def swap_weights():
    path = '/home/mehdi/data/eboss/v7/'
    weight = lambda x, y: path + 'results_'+x+'_'+y+'/regression/nn_ablation/nn-weights.hp512.fits'
    def get_weights(CAP):
        redshifts = ['0.8', '1.1', '1.4', '1.6', '1.9']
        return dict(zip(redshifts, [weight(CAP,y) for y in redshifts]))

    for ab in ['ab']:    
        for CAP in ['NGC', 'SGC']:
            zcuts = {'0.8': [0.8000000000000000, 1.1423845339193297],
                     '1.1': [1.1423845339193297, 1.3862779004064971],
                     '1.4': [1.3862779004064971, 1.6322502623999630],
                     '1.6': [1.6322502623999630, 1.8829689752636356],
                     '1.9': [1.8829689752636356, 2.2000000000000000]}
            # z-dependent
            wtag    = '_'.join(('wnnz', ab))
            incat   = path + 'eBOSS_QSO_clustering_'+CAP+'_v7.dat.fits'
            outcat  = path + 'eBOSS_QSO_clustering_'+CAP+'_v7_'+wtag+'.dat.fits'
            weights = get_weights(CAP)

            print('writing %s'%outcat)
            mycat   = cf.swap_weights(incat)
            mycat.run(weights, zcuts)
            mycat.to_fits(outcat)
            print(100*'=','\n')    

            
def plot_ablation_selected256more():
    from LSSutils.dataviz import ablation_plot_all, get_selected_maps
    from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as labels
    fig, ax = plt.subplots(ncols=5, nrows=2, figsize=(30, 12), sharey=True)
    ax = ax.flatten()

    i = 0
    for cap in [ 'NGC', 'SGC']: # ngc.all
        for key in ['0.8', '1.1', '1.4', '1.6', '1.9']:
            mycap = cap+'_'+key+'_'+'256' # NGC_0.8
            get_selected_maps(glob('/home/mehdi/data/eboss/v7/results_'+mycap+'/ablation/v7.log_fold*.npy'),
                              ['eBOSS '+mycap], labels=labels, ax=ax[i], hold=True)
            i += 1
    #plt.savefig('./maps_selected_eboss.pdf', bbox_inches='tight')
    plt.show()   
    
def plot_ablation_selected256():
    from LSSutils.dataviz import ablation_plot_all, get_selected_maps
    from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as labels
    fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(12, 12), sharey=True)
    ax = ax.flatten()

    i = 0
    for cap in [ 'NGC', 'SGC']: # ngc.all
        for key in ['low', 'high']:
            mycap = cap+'_'+key+'_'+'256' # NGC_0.8
            get_selected_maps(glob('/home/mehdi/data/eboss/v7/results_'+mycap+'/ablation/v7.log_fold*.npy'),
                              ['eBOSS '+mycap], labels=labels, ax=ax[i], hold=True)
            i += 1
    #plt.savefig('./maps_selected_eboss.pdf', bbox_inches='tight')
    plt.show()    
    
def plot_ablation_selected():
    from LSSutils.dataviz import ablation_plot_all, get_selected_maps
    from LSSutils.catalogs.datarelease import cols_eboss_v7_qso as labels
    fig, ax = plt.subplots(ncols=5, nrows=2, figsize=(30, 12), sharey=True)
    ax = ax.flatten()

    i = 0
    for cap in [ 'NGC', 'SGC']: # ngc.all
        for key in ['0.8', '1.1', '1.4', '1.6', '1.9']:
            mycap = cap+'_'+key # NGC_0.8
            get_selected_maps(glob('/home/mehdi/data/eboss/v7/results_'+mycap+'/ablation/v6.log_fold*.npy'),
                              ['eBOSS '+mycap], labels=labels, ax=ax[i], hold=True)
            i += 1
    #plt.savefig('./maps_selected_eboss.pdf', bbox_inches='tight')
    plt.show()    

    
def preparev7more(dataname='/home/mehdi/data/eboss/sysmaps/SDSS_WISE_imageprop_HI_transformed_nside512.h5',
              nside=512, transformed=True):
    if transformed:
        from LSSutils.catalogs.datarelease import cols_eboss_v7_qso as my_cols
    else:
        from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as my_cols
    snside    = str(nside)
    dataframe = pd.read_hdf(dataname)


    zcuts = {'0.8': [0.80, 1.14],
             '1.1': [1.14, 1.39],
             '1.4': [1.39, 1.63],
             '1.6': [1.63, 1.88],
             '1.9': [1.88, 2.20]}
        
    path      = '/home/mehdi/data/eboss/v7/'

    fitname   = lambda x:path + 'ngal_features_'+x+'.hp'+snside+'.fits'
    hpmask    = lambda x:path + 'mask_'+x+'.hp'+snside+'.fits'
    fracgood  = lambda x:path + 'frac_'+x+'.hp'+snside+'.fits'
    fitkfold  = lambda x:path + 'ngal_features_'+x+'.hp'+snside+'.5r.npy'
    catname   = lambda x:path + 'eBOSS_QSO_clustering_'+x+'_v7.dat.fits'
    ranname   = lambda x:path + 'eBOSS_QSO_clustering_'+x+'_v7.ran.fits'


    hpcatname   = lambda x:path + 'eBOSS_QSO_clustering_'+x+'_v7.hp'+snside+'.dat.fits'


    #
    for cap in ['NGC', 'SGC']:
        catalogs = []
        for i,key_i in enumerate(zcuts.keys()):
            myframe  = dataframe.copy()        
            mytag     = cap+'_'+key_i     
            fitname_i = fitname(mytag)
            catname_i = catname(cap)
            ranname_i = ranname(cap)        
            hpcat_i   = hpcatname(mytag)
            hpmsk_i   = hpmask(mytag)
            hpfrac_i  = fracgood(mytag)
            fitkfld_i = fitkfold(mytag)

            #print(mytag, fitname_i, catname_i, ranname_i, hpcat_i,
            #     hpmsk_i, hpfrac_i, fitkfld_i)        
            mycat    = cf.EBOSSCAT([catname_i])    
            mycat.apply_zcut(zcuts[key_i])
            mycat.project2hp(nside=nside)
            mycat.writehp(hpcat_i)

            myframe['ngal'] = mycat.galm.astype('f8')

            myran    = cf.EBOSSCAT([ranname_i])    
            #myran.apply_zcut(zcuts[key_i]) ## do not cut randoms
            myran.project2hp(nside=nside)
            myranhp = myran.galm.astype('f8')
            myranhp[myranhp==0.] = np.nan
            myframe['nran'] = myranhp

            myfit    = myframe.dropna()
            #print('shape myfit {} {} {}'.format(cap, key_i, myfit.shape))
            cf.hd5_2_fits(myfit, my_cols, fitname_i, hpmsk_i, hpfrac_i, fitkfld_i, res=nside, k=5)    
    
    
def preparev7(dataname='/home/mehdi/data/eboss/sysmaps/SDSS_WISE_imageprop_HI_transformed_nside512.h5',
              nside=512, transformed=True):
    if transformed:
        from LSSutils.catalogs.datarelease import cols_eboss_v7_qso as my_cols
    else:
        from LSSutils.catalogs.datarelease import cols_eboss_v6_qso_simp as my_cols
    snside    = str(nside)
    dataframe = pd.read_hdf(dataname)
    #dataframe = pd.read_hdf('/home/mehdi/data/eboss/sysmaps/'\
    #                        +'SDSS_WISE_imageprop_HI_transformed_nside'+snside+'.h5')


    #nside     = 512


    # zcuts = {'0.8': [0.8000000000000000, 1.1423845339193297],
    #          '1.1': [1.1423845339193297, 1.3862779004064971],
    #          '1.4': [1.3862779004064971, 1.6322502623999630],
    #          '1.6': [1.6322502623999630, 1.8829689752636356],
    #          '1.9': [1.8829689752636356, 2.2000000000000000]}
    
    zcuts     = {'low':[0.8, 1.508088732762684], 
                 'high':[1.508088732762684, 2.2]}
    
    path      = '/home/mehdi/data/eboss/v7/'

    fitname   = lambda x:path + 'ngal_features_'+x+'.hp'+snside+'.fits'
    hpmask    = lambda x:path + 'mask_'+x+'.hp'+snside+'.fits'
    fracgood  = lambda x:path + 'frac_'+x+'.hp'+snside+'.fits'
    fitkfold  = lambda x:path + 'ngal_features_'+x+'.hp'+snside+'.5r.npy'
    catname   = lambda x:path + 'eBOSS_QSO_clustering_'+x+'_v7.dat.fits'
    ranname   = lambda x:path + 'eBOSS_QSO_clustering_'+x+'_v7.ran.fits'


    hpcatname   = lambda x:path + 'eBOSS_QSO_clustering_'+x+'_v7.hp'+snside+'.dat.fits'


    #
    for cap in ['NGC', 'SGC']:
        catalogs = []
        for i,key_i in enumerate(zcuts.keys()):
            myframe  = dataframe.copy()        
            mytag     = cap+'_'+key_i     
            fitname_i = fitname(mytag)
            catname_i = catname(cap)
            ranname_i = ranname(cap)        
            hpcat_i   = hpcatname(mytag)
            hpmsk_i   = hpmask(mytag)
            hpfrac_i  = fracgood(mytag)
            fitkfld_i = fitkfold(mytag)

            #print(mytag, fitname_i, catname_i, ranname_i, hpcat_i,
            #     hpmsk_i, hpfrac_i, fitkfld_i)        
            mycat    = cf.EBOSSCAT([catname_i])    
            mycat.apply_zcut(zcuts[key_i])
            mycat.project2hp(nside=nside)
            mycat.writehp(hpcat_i)

            myframe['ngal'] = mycat.galm.astype('f8')

            myran    = cf.EBOSSCAT([ranname_i])    
            #myran.apply_zcut(zcuts[key_i]) ## do not cut randoms
            myran.project2hp(nside=nside)
            myranhp = myran.galm.astype('f8')
            myranhp[myranhp==0.] = np.nan
            myframe['nran'] = myranhp

            myfit    = myframe.dropna()
            #print('shape myfit {} {} {}'.format(cap, key_i, myfit.shape))
            cf.hd5_2_fits(myfit, my_cols, fitname_i, hpmsk_i, hpfrac_i, fitkfld_i, res=nside, k=5)    

def add_run_HI():
    import numpy.lib.recfunctions as rfn
    from LSSutils.extrn.GalacticForegrounds.hpmaps import logHI

    loghi    = logHI(name='/home/mehdi/data/NHI_HPX.fits', nside=512)
    sdssrun  = hp.read_map('/home/mehdi/data/eboss/sysmaps/sdss_run_mean_512.fits')
    maps     = ft.read('/home/mehdi/data/eboss/sysmaps/SDSS_WISE_imageprop_nside512.fits')
    newmaps  = rfn.append_fields(maps, ['LOGHI', 'RUN'], 
                                   data=[loghi.loghi, sdssrun], 
                                   dtypes=['>f8', '>f8'], usemask=False)
    ft.write('/home/mehdi/data/eboss/sysmaps/SDSS_WISE_imageprop_HI_nside512.fits', 
             newmaps, 
             clobber=True)    

def plot_systematics(sysmap='/home/mehdi/data/eboss/sysmaps/SDSS_WISE_imageprop_HI_nside512.fits',
                     mask=None, return_pd=False):    
    from scipy.stats import skew
    if sysmap.endswith('.fits'):
        systematics = ft.read(sysmap)
        names = systematics.dtype.names        
    elif sysmap.endswith('.h5'):
        systematics = pd.read_hdf(sysmap)
        names = systematics.columns
        
    if (mask is None) & ('NRAN' in names):
        mask = systematics['NRAN'] > 0.0
    if (mask is None) & ('depth_g' in names):
        mask = np.isfinite(systematics['depth_g'])
    else:
        raise ValueError('mask required')
        
    #
    nsys  = len(names)
    nrows = nsys // 3
    if nsys%3!=0:nrows+=1
    fig, ax = plt.subplots(ncols=3, nrows=nrows, figsize=(3*6, nrows*5))
    ax = ax.flatten()
    dic = {}
    for i, name_i in enumerate(names):
        myarray = systematics[name_i]
        skwness = skew(myarray[mask])
        if skwness > 1.:
            if myarray[mask].min() <= 0.0: 
                myarray += 1.0
                name_i  = '(1+%s)'%name_i
            myarray = np.log10(myarray)
            name_i  = 'log'+name_i
            
        if return_pd:dic[name_i] = myarray # return
        ax[i].hist(myarray[mask], alpha=0.5, histtype='step')
        print('{0:20s} : {2:5.3e}: {1:}'\
              .format(name_i, 
                      np.percentile(myarray[mask], [0, 25, 50, 100]),
                      skew(myarray[mask])))
        ax[i].set_xlabel(name_i)    
    if return_pd:return pd.DataFrame(dic)

def prepare_perdata(metadat, metadat5f, path2sysmaps, mycols, CAP, nside, band, index_b, index_e, field):
    sysmaps = pd.read_hdf(path2sysmaps)
    sysmaps = sysmaps[mycols]
    cfull = ft.read('/home/mehdi/data/eboss/v6/eBOSS_QSO_full_'+CAP+'_v6.dat.fits')
    ran   = ft.read('/home/mehdi/data/eboss/v6/eBOSS_QSO_clustering_'+CAP+'_v6.ran.fits')
    cat   = ft.read('/home/mehdi/data/eboss/v6/eBOSS_QSO_clustering_'+CAP+'_v6.dat.fits')
    inc   = np.in1d(cfull['QSO_ID'], cat['QSO_ID'])
    mycat = cfull[inc]

    assert np.array_equal(mycat['QSO_ID'], cat['QSO_ID'])
    hpix   = ut.radec2hpix(nside, cat['RA'], cat['DEC'])
    imag   = mycat[field][:, index_b[band]].astype('float64')
    imagc  = imag - index_e[band]*sysmaps['ebv'][hpix]

    galaxy = pd.DataFrame(dict(imagc=imagc,
                               index=np.arange(hpix.size),
                               z=cat['Z'].astype('float64')))


    ranmap = ut.hpixsum(nside, ran['RA'], ran['DEC'], value=ran['WEIGHT_SYSTOT']*ran['WEIGHT_CP']*ran['WEIGHT_NOZ']) 
    galmap = ut.hpixsum(nside, cat['RA'], cat['DEC'], value=cat['WEIGHT_CP']*cat['WEIGHT_NOZ']) 
    mask   = ranmap > 0.0
    nnbar  = ut.makedelta(galmap, ranmap, mask) # it returns delta
    nnbar[mask] += 1.0
    fracgood = ranmap / np.mean(ranmap[mask])

    galaxy['label']    = nnbar[hpix]
    galaxy['fracgood'] = fracgood[hpix]

    sysmaps = sysmaps.iloc[hpix]
    stack = pd.concat([galaxy, sysmaps], axis=1)


    print('going to write', metadat)
    stack.to_hdf(metadat, 'data')

    features = stack[mycols + ['imagc', 'z']].values
    label    = stack['label'].values
    index    = stack['index'].values
    fracgood = stack['fracgood'].values

    mydata = np.zeros(label.size, dtype=[('hpind', 'f8'), 
                                         ('features', ('f8', features.shape[1])),
                                         ('label', 'f8'),
                                         ('fracgood', 'f8')])
    mydata['hpind'] = index
    mydata['label'] = label
    mydata['features'] = features
    mydata['fracgood'] = fracgood

    #print(cat.size)
    mydata_5f = ut.split2Kfolds(mydata)
    #print(mydata_5f.keys())
    print('going to write ', metadat5f)
    np.save(metadat5f, mydata_5f)


def read_NN(output, files):
    # needs TF
    print('reading ...', files)
    print('saving...', output)
    import LSSutils.nn.nn_tf_old as nn_tf_old
    P, _,_,Y, _, _ = nn_tf_old.read_NNfolds(files)
    P = P.astype('i8')
    W = np.empty(Y.size)
    W[P] = Y
    np.save(output, W)

def update_cat(incat, oucat, weight):
    weights = np.load(weight)
    #print(weights)
    cat = ft.read(incat)
    cat['WEIGHT_SYSTOT'] = 1./weights
    ft.write(oucat, cat) # write
    print('read %s\nwrite %s'%(incat, oucat))

def project2hp(incat, ouhpmap, nside=256):
    mycat  = cf.EBOSSCAT([incat], weights=['weight_systot','weight_noz', 'weight_cp'])
    mycat.project2hp(nside=nside)
    mycat.writehp(ouhpmap)
    print('read %s wrote %s'%(incat, ouhpmap))


def split_to_imag(path2sysmaps, mycols, CAP, nside, band, index_b, index_e, field):
    sysmaps = pd.read_hdf(path2sysmaps)
    sysmaps = sysmaps[mycols]
    snside  = str(nside)
    print(index_b[band], field, nside, band, CAP)
    cfull = ft.read('/home/mehdi/data/eboss/v6/eBOSS_QSO_full_'+CAP+'_v6.dat.fits')
    cat   = ft.read('/home/mehdi/data/eboss/v6/eBOSS_QSO_clustering_'+CAP+'_v6.dat.fits')
    inc   = np.in1d(cfull['QSO_ID'], cat['QSO_ID'])
    mycat = cfull[inc]    
    hpix  = ut.radec2hpix(nside, cat['RA'], cat['DEC'])
    imag  = mycat[field][:, index_b[band]] - index_e[band]*sysmaps['ebv'][hpix]
    imag_percentiles = np.percentile(imag, [0, 25, 50, 75,  100])
    print('percentiles : \n{}'.format(imag_percentiles))
    
    ranname  = '/home/mehdi/data/eboss/v6/eBOSS_QSO_clustering_NGC_v6.ran.fits'.replace('NGC', CAP)
    myran    = cf.EBOSSCAT([ranname])    
    myran.project2hp(nside=nside)
    myranhp = myran.galm.astype('f8')
    myranhp[myranhp==0.] = np.nan
 


    tot = 0
    for i in range(len(imag_percentiles)-1):
        le = imag_percentiles[i]
        ue = imag_percentiles[i+1]
        if i==3:
            mask = (imag>=le) & (imag<=ue)
        else:
            mask = (imag>=le) & (imag<ue)
        #tot += mask.sum()
        #print(tot)
        mycat = cat[mask]
        output_cat = '/home/mehdi/data/eboss/v6/imag_splits/'\
                   + 'eBOSS_QSO_clustering_'+CAP+'_v6_'+str(i)+'.dat.fits'
        ft.write(output_cat, mycat, clobber=True)
        
        #
        #
        myframe  = sysmaps.copy()
        cap      = CAP.lower()
        key_i    = str(i)
        mytag    = cap+'.'+key_i
        fitname  = '/home/mehdi/data/eboss/v6/imag_splits/ngal_features_ngc.fits'.replace('ngc',   mytag)
        fitkfld  = '/home/mehdi/data/eboss/v6/imag_splits/qso.ngc.hp.'+snside+'.r.npy'
        fitkfld  = fitkfld.replace('ngc', mytag)
        hpfrac   = '/home/mehdi/data/eboss/v6/imag_splits/fracgood.ngc.hp.'+snside+'.fits'
        hpfrac   = hpfrac.replace('ngc', mytag)
        hpmask   = '/home/mehdi/data/eboss/v6/imag_splits/mask.ngc.hp.'+snside+'.fits'
        hpmask   = hpmask.replace('ngc', mytag)        
        myngalhp   =  ut.hpixsum(nside, mycat['RA'], 
                                    mycat['DEC'], 
                                    value=mycat['WEIGHT_NOZ']*mycat['WEIGHT_CP']).astype('f8')


        output_hpngal = output_cat.replace('.dat.fits', '.dat.hp256.fits')

        hp.write_map(output_hpngal, myngalhp, overwrite=True, fits_IDL=False)
        
        myframe['ngal'] = myngalhp
        myframe['nran'] = myranhp
        myfit    = myframe.dropna()
        #print('shape myfit {} {} {}'.format(cap, key_i, myfit.shape))
        #print(fitname, fitkfld, hpfrac, hpmask, end=3*'\n')
        cf.hd5_2_fits(myfit, mycols, fitname, hpmask, hpfrac, fitkfld, res=nside, k=5)
        print(10*'=', end=3*'\n')

if __name__ == '__main__':
    #
    #  NGC
    #
    CAP       = 'NGC'
    band      = 'i'
    field     = 'MODELMAG'
    index_b   = dict(zip(['u', 'g', 'r', 'i', 'z'], np.arange(5)))
    index_e   = dict(zip(['u', 'g', 'r', 'i', 'z'], [4.239,3.303,2.285,1.698,1.263]))
    nside     = 256
    metadat   = '/home/mehdi/data/eboss/v6/eBOSS_QSO_perdata'+CAP+'.h5'
    metadat5f = '/home/mehdi/data/eboss/v6/eBOSS_QSO_perdata'+CAP+'.5r.npy'

    #prepare_perdata(metadat, metadat5f, path2sysmaps, mycols, CAP, nside, band, index_b, index_e, field)

    files  = glob('/home/mehdi/data/eboss/v6/results_ngc.all/regression/nn_perdata/fold*/reg-nepoch200-nchain5-batchsize1024units2020-Lrate0.001-l2scale0.0.npz')
    output = '/home/mehdi/data/eboss/v6/results_ngc.all/regression/nn_perdata/weights.npy'
    #read_NN(output, files)


    incat = '/home/mehdi/data/eboss/v6/eBOSS_QSO_clustering_'+CAP+'_v6.dat.fits'
    oucat = '/home/mehdi/data/eboss/v6/eBOSS_QSO_clustering_'+CAP+'_v6_perdata.dat.fits'
    weight = output
    #update_cat(incat, oucat, weight)

    incat   = oucat
    #ouhpmap = incat.replace('.fits', '.hp256.fits')
    #project2hp(incat, ouhpmap)


    split_to_imag(path2sysmaps, mycols, CAP, nside, band, index_b, index_e, field)

