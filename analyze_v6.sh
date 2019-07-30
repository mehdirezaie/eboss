#!/bin/bash
source activate py3p6

# codes
ablation=/Users/rezaie/github/SYSNet/src/ablation.py
multfit=/Users/rezaie/github/SYSNet/src/mult_fit.py
nnfit=/Users/rezaie/github/SYSNet/src/nn_fit.py
split=/Users/rezaie/github/SYSNet/src/add_features-split.py
docl=/Users/rezaie/github/eboss/run_pipeline.py
docont=/Users/rezaie/github/SYSNet/src/contaminate.py



# ================ RUNS ====================
# DATA SGC+NGC
# DATA
# output dirs & labels
glmp=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_all_v6.dat.hp.512.fits
glmpwsys=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_all_v6_wsys.dat.hp.512.fits
glmp5=/Volumes/TimeMachine/data/eboss/v6/qso.all.hp.512.r.npy
drfeat=/Volumes/TimeMachine/data/eboss/v6/ngal_features.fits
rnmp=/Volumes/TimeMachine/data/eboss/v6/fracgood.hp.512.fits
oudr_ab=/Volumes/TimeMachine/data/eboss/v6/results/ablation/
oudr_r=/Volumes/TimeMachine/data/eboss/v6/results/regression/
oudr_c=/Volumes/TimeMachine/data/eboss/v6/results/clustering/
maskc=/Volumes/TimeMachine/data/eboss/v6/mask.cut.hp.512.fits    # remove pixels with extreme weights
mult1=mult_all
mult2=mult_depz
mult3=mult_ab
mult4=mult_f
log_ab=v6.log
nn1=nn_ab
nn3=nn_p
nn4=nn_f

# REGRESSION

# Jul 16: Ablation on v6
# took 34 min
# for rk in 0 1 2 3 4
# do
#  time mpirun --oversubscribe -np 5 python $ablation --data $glmp5 --output $oudr_ab --log $log_ab --rank $rk --axfit 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17
# done


# Jun 9: Linear/quadratic multivariate fit on DR7 
#         NN fit on v6 with ablation
#         Run DR7 NN fit w/o ablation
# python $multfit --input $glmp5 --output ${oudr_r}${mult1}/ --split --nside 512
# took around 20 secs
# ablation picks up [0, 1, 2, 7, 10, 11, 12, 14, 16, 17]
# mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn1}/ --ablog ${oudr_ab}${log_ab} --nside 512
# mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn3}/ --nside 512
# took 16 min


# run the weight footprint cut
# python make_common_mask-data.py
# took 1 min
#
# July 17
# took 550 m
#for wname in uni lin quad
#do
#  wmap=${oudr_r}${mult1}/${wname}-weights.hp512.fits
#  mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --clfile cl_$wname --nnbar nnbar_$wname --corfile xi_$wname --nside 512 --lmax 1024 
#done

#for nni in $nn1 $nn3
#do
#  wmap=${oudr_r}${nni}/nn-weights.hp512.fits
#  mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --nnbar nnbar_$nni --clfile cl_$nni  --corfile xi_$nni --nside 512 --lmax 1024
#done

#
# auto C_l for systematics
#mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap none --clsys cl_sys --corsys xi_sys --nside 512 --lmax 1024

# default w_sys correction
# 99 min
# wname=uni_wsys
# wmap=${oudr_r}${mult1}/${wname}-weights.hp512.fits
# mpirun --oversubscribe -np 4 python $docl --galmap $glmpwsys --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --clfile cl_$wname --nnbar nnbar_$wname --corfile xi_$wname --nside 512 --lmax 1024


#
#
# DATA NGC, SGC, NGC+SGC
# 111 min for ablation and regression
# 1010 min for clustering
# output dirs & labels
# for cap in all ngc sgc
# do
#     glmp=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_${cap}_v6.dat.hp.512.fits
#     glmpwsys=/Volumes/TimeMachine/data/eboss/v6/eBOSS_QSO_clustering_${cap}_wsys_v6.dat.hp.512.fits
#     glmp5=/Volumes/TimeMachine/data/eboss/v6/qso.${cap}.hp.512.r.npy
#     drfeat=/Volumes/TimeMachine/data/eboss/v6/ngal_features_${cap}.fits
#     rnmp=/Volumes/TimeMachine/data/eboss/v6/fracgood.${cap}.hp.512.fits
#     oudr_ab=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/ablation/
#     oudr_r=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/regression/
#     oudr_c=/Volumes/TimeMachine/data/eboss/v6/results_${cap}/clustering/
#     maskc=/Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.hp.512.fits    # remove pixels with extreme weights
#     mult1=mult_all
#     mult2=mult_depz
#     mult3=mult_ab
#     mult4=mult_f
#     log_ab=v6.log
#     nn1=nn_ab
#     nn3=nn_p
#     axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16'
    
    # REGRESSION
    #echo 'ablation on ' $cap 'with ' $axfit 
    #for rk in 0 1 2 3 4
    #do
    # echo $rk 'on ' $glmp5
    # mpirun --oversubscribe -np 5 python $ablation --data $glmp5 --output $oudr_ab --log $log_ab --rank $rk --axfit $axfit
    #done
    #echo 'regression on ' $cap
    #python $multfit --input $glmp5 --output ${oudr_r}${mult1}/ --split --nside 512 --axfit $axfit
    #mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn1}/ --ablog ${oudr_ab}${log_ab} --nside 512
    #mpirun --oversubscribe -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn3}/ --nside 512 --axfit $axfit

    # remove the extreme weight pixels
    #python make_common_mask-data.py
    #python make_common_mask-data.py /Volumes/TimeMachine/data/eboss/v6/mask.${cap}.hp.512.fits /Volumes/TimeMachine/data/eboss/v6/mask.${cap}.cut.hp.512.fits /Volumes/TimeMachine/data/eboss/v6/results_${cap}/regression/*/*-weights.hp512.fits

    # Clustering
    # no correction, linear, quadratic
#     for wname in uni lin quad
#     do
#       wmap=${oudr_r}${mult1}/${wname}-weights.hp512.fits
#       mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --clfile cl_$wname --nnbar nnbar_$wname --corfile xi_$wname --nside 512 --lmax 1024 --axfit $axfit 
#     done

#     # nn w ablation, nn plain
#     for nni in $nn1 $nn3
#     do
#       wmap=${oudr_r}${nni}/nn-weights.hp512.fits
#       mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --nnbar nnbar_$nni --clfile cl_$nni  --corfile xi_$nni --nside 512 --lmax 1024 --axfit $axfit
#     done
#     #
#     # auto C_l for systematics
#     mpirun --oversubscribe -np 4 python $docl --galmap $glmp --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap none --clsys cl_sys --corsys xi_sys --nside 512 --lmax 1024 --axfit $axfit

#     # default w_sys correction
#     wname=uni_wsys
#     wmap=${oudr_r}${mult1}/${wname}-weights.hp512.fits
#     mpirun --oversubscribe -np 4 python $docl --galmap $glmpwsys --ranmap $rnmp --photattrs $drfeat --mask $maskc --oudir $oudr_c --verbose --wmap $wmap --clfile cl_$wname --nnbar nnbar_$wname --corfile xi_$wname --nside 512 --lmax 1024 --axfit $axfit
# done





#   
#   3D
catlab=eBOSS_QSO_clustering
indir=/Volumes/TimeMachine/data/eboss/v6/

# NGC
cap=NGC
wdir=/Volumes/TimeMachine/data/eboss/v6/results_ngc/regression/
oudir=/Volumes/TimeMachine/data/eboss/v6/results_ngc/clustering/
random=${indir}${catlab}_${cap}_v6.ran.fits


python subtitute_wnn_systot.py  --input_path ${indir}${catlab}_${cap}_v6.dat.fits --input_wnn ${wdir}nn_p/nn-weights.hp512.fits --output_path ${indir}${catlab}_${cap}_v6_wnnp.dat.fits --overwrite
python subtitute_wnn_systot.py  --input_path ${indir}${catlab}_${cap}_v6.dat.fits --input_wnn ${wdir}nn_ab/nn-weights.hp512.fits --output_path ${indir}${catlab}_${cap}_v6_wnn.dat.fits --overwrite

# mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wosystot
# mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystot --sys_tot
mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6_wnn.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystotnn --sys_tot
mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6_wnnp.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystotnnp --sys_tot

# SGC
cap=SGC
wdir=/Volumes/TimeMachine/data/eboss/v6/results_sgc/regression/
oudir=/Volumes/TimeMachine/data/eboss/v6/results_sgc/clustering/
random=${indir}eBOSS_QSO_clustering_${cap}_v6.ran.fits


python subtitute_wnn_systot.py  --input_path ${indir}${catlab}_${cap}_v6.dat.fits --input_wnn ${wdir}nn_p/nn-weights.hp512.fits --output_path ${indir}${catlab}_${cap}_v6_wnnp.dat.fits --overwrite
python subtitute_wnn_systot.py  --input_path ${indir}${catlab}_${cap}_v6.dat.fits --input_wnn ${wdir}nn_ab/nn-weights.hp512.fits --output_path ${indir}${catlab}_${cap}_v6_wnn.dat.fits --overwrite

# mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wosystot
# mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystot --sys_tot
mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6_wnn.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystotnn --sys_tot
mpirun -np 2 python run_pk.py --galaxy_path ${indir}${catlab}_${cap}_v6_wnnp.dat.fits --random_path $random --output_path ${oudir}pk_256_p8_2p2_wsystotnnp --sys_tot