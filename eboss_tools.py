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
mpl.use('Agg')

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

