#!/bin/bash
source ~/.bash_profile
conda activate py3p6

# codes
ablation=/Users/rezaie/github/LSSutils/scripts/analysis/ablation_tf_old.py
multfit=/Users/rezaie/github/LSSutils/scripts/analysis/mult_fit.py
nnfit=/Users/rezaie/github/LSSutils/scripts/analysis/nn_fit_tf_old.py
docl=/Users/rezaie/github/LSSutils/scripts/analysis/run_pipeline.py

# ================ RUNS ====================
#
# C_ell and Xi
#
# DATA NGC, SGC, NGC+SGC
# 111 min for ablation and regression
# 1010 min for clustering
# output dirs & labels
#for cap in all ngc sgc
#do
#     glmp=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_${cap}_v6.dat.hp.512.fits
#     glmpwsys=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_${cap}_wsys_v6.dat.hp.512.fits
#     glmp5=/Volumes/TimeMachine/data/eboss/v6/qso.${cap}.hp.512.r.npy
#     drfeat=/Volumes/TimeMachine/data/eboss/v6/ngal_features_${cap}.fits
#     rnmp=/Volumes/TimeMachine/data/eboss/v6/fracgood.${cap}.hp.512.fits
#     oudr_ab=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/ablation/
#     oudr_r=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/regression/
#     oudr_c=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/clustering/
#     maskc=/Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.hp.512.fits    # remove pixels with extreme weights
#     maskclog=/Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.log
#     mult1=mult_all
#     mult2=mult_depz
#     mult3=mult_ab
#     mult4=mult_f
#     log_ab=v6.log
#     nn1=nn_ab
#     nn3=nn_p
#     nside=512
#     lmax=1024
#     axfit MUST change depending on the imaging maps
#     axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18'
    
#     REGRESSION
#     echo 'ablation on ' $cap 'with ' $axfit 
#     for rk in 0 1 2 3 4
#     do
#      echo $rk 'on ' $glmp5
#      mpirun --oversubscribe -np 5 python $ablation --data $glmp5 --output $oudr_ab --log $log_ab --rank $rk --axfit $axfit
#     done
#     echo 'regression on ' $cap
#     python $multfit --input $glmp5 --output ${oudr_r}${mult1}/ --split --nside 512 --axfit $axfit # we don't do lin regression
#     mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn1}/ --ablog ${oudr_ab}${log_ab} --nside $nside
#     mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn3}/ --nside $nside --axfit $axfit

#     remove the extreme weight pixels
#     python make_common_mask-data.py /Volumes/TimeMachine/data/eboss/v6/mask.${cap}.hp.${nside}.fits /Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.hp.${nside}.fits /Volumes/TimeMachine/data/eboss/v6/results_${cap}/regression/*/*-weights.hp${nside}.fits > $maskclog

#     Clustering
#     no correction, linear, quadratic
#     for wname in uni lin quad
#     for wname in uni
#     do
#       wmap=${oudr_r}${mult1}/${wname}-weights.hp${nside}.fits
#       mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --clfile cl_$wname --nnbar nnbar_$wname --corfile xi_$wname --nside $nside --lmax $lmax --axfit $axfit 
#     done

#     # nn w ablation, nn plain
#     for nni in $nn1 $nn3
#     do
#       wmap=${oudr_r}${nni}/nn-weights.hp${nside}.fits
#       mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --nnbar nnbar_$nni --clfile cl_$nni  --corfile xi_$nni --nside $nside --lmax $lmax --axfit $axfit
#     done
#     #
#     # auto C_l for systematics
#     mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap none --clsys cl_sys --corsys xi_sys --nside ${nside} --lmax $lmax --axfit $axfit

#     # default w_sys correction
#     wname=uni_wsys
#     wmap=${oudr_r}${mult1}/${wname}-weights.hp${nside}.fits
#     mpirun --oversubscribe -np 4 python $docl --galmap $glmpwsys --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --clfile cl_$wname --nnbar nnbar_$wname --corfile xi_$wname --nside $nside --lmax $lmax --axfit $axfit
# done


#   
#   P(k)
# aug 2: no extrem weight (except for all), so run P(k)
# for cap in NGC SGC
# do
#     nside=512    
#     capl=$(echo "$cap" | tr '[:upper:]' '[:lower:]')
#     catlab=eBOSS_QSO_clustering
#     indir=/Volumes/TimeMachine/data/eboss/v6/    
#     wdir=/Volumes/TimeMachine/data/eboss/v6/results_${capl}/regression/
#     oudir=/Volumes/TimeMachine/data/eboss/v6/results_${capl}/clustering/
#     random=${indir}${catlab}_${cap}_v6.ran.fits

#     # subtitute the weights
#     python subtitute_wnn_systot.py  --input_path ${indir}${catlab}_${cap}_v6.dat.fits --input_wnn ${wdir}nn_p/nn-weights.hp${nside}.fits --output_path ${indir}${catlab}_${cap}_v6_wnnp.dat.fits --overwrite
#     python subtitute_wnn_systot.py  --input_path ${indir}${catlab}_${cap}_v6.dat.fits --input_wnn ${wdir}nn_ab/nn-weights.hp${nside}.fits --output_path ${indir}${catlab}_${cap}_v6_wnn.dat.fits --overwrite
#     # compute the 
#     mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wosystot
#     mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystot --sys_tot
#     mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6_wnn.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystotnn --sys_tot
#     mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6_wnnp.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystotnnp --sys_tot
# done


# low and high z
# qso.ngc.low.hp.512.r.npy

for cap in ngc sgc
do
  for zcut in low high
  do
    nside=512
    lmax=1024  
    mycap=$cap.$zcut
    echo $mycap
    glmp5=/Volumes/TimeMachine/data/eboss/v6/qso.${mycap}.hp.${nside}.r.npy
    #du -h $glmp5
    oudr_ab=/Volumes/TimeMachine/data/eboss/v6/results_${mycap}/ablation/
    oudr_r=/Volumes/TimeMachine/data/eboss/v6/results_${mycap}/regression/
    log_ab=v6.log
    nn1=nn_ab
    nn3=nn_p
    ## axfit MUST change depending on the imaging maps
    axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18'
    ## REGRESSION
    echo 'ablation on ' $mycap 'with ' $axfit 
    for rk in 0 1 2 3 4
    do
     echo $rk 'on ' $glmp5 $mycap
     mpirun --oversubscribe -np 5 python $ablation --data $glmp5 --output $oudr_ab --log $log_ab --rank $rk --axfit $axfit
    done
    echo 'regression on ' $mycap
    mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn1}/ --ablog ${oudr_ab}${log_ab} --nside $nside
    mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn3}/ --nside $nside --axfit $axfit      
  done
done
#     glmp=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_${cap}_v6.dat.hp.512.fits
#     glmpwsys=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_${cap}_wsys_v6.dat.hp.512.fits
#     glmp5=/Volumes/TimeMachine/data/eboss/v6/qso.${cap}.hp.512.r.npy
#     drfeat=/Volumes/TimeMachine/data/eboss/v6/ngal_features_${cap}.fits
#     rnmp=/Volumes/TimeMachine/data/eboss/v6/fracgood.${cap}.hp.512.fits
#     oudr_ab=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/ablation/
#     oudr_r=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/regression/
#     oudr_c=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/clustering/
#     maskc=/Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.hp.512.fits    # remove pixels with extreme weights
#     maskclog=/Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.log
#     mult1=mult_all
#     mult2=mult_depz
#     mult3=mult_ab
#     mult4=mult_f
#     log_ab=v6.log
#     nn1=nn_ab
#     nn3=nn_p
#     nside=512
#     lmax=1024
#     axfit MUST change depending on the imaging maps
#     axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18'
    
#     REGRESSION
#     echo 'ablation on ' $cap 'with ' $axfit 
#     for rk in 0 1 2 3 4
#     do
#      echo $rk 'on ' $glmp5
#      mpirun --oversubscribe -np 5 python $ablation --data $glmp5 --output $oudr_ab --log $log_ab --rank $rk --axfit $axfit
#     done
#     echo 'regression on ' $cap
#     python $multfit --input $glmp5 --output ${oudr_r}${mult1}/ --split --nside 512 --axfit $axfit # we don't do lin regression
#     mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn1}/ --ablog ${oudr_ab}${log_ab} --nside $nside
#     mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn3}/ --nside $nside --axfit $axfit

#     remove the extreme weight pixels
#     python make_common_mask-data.py /Volumes/TimeMachine/data/eboss/v6/mask.${cap}.hp.${nside}.fits /Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.hp.${nside}.fits /Volumes/TimeMachine/data/eboss/v6/results_${cap}/regression/*/*-weights.hp${nside}.fits > $maskclog
# done



