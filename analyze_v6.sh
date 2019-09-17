#!/bin/bash
if [ -f "~/.bash_profile" ]
then
	source ~/.bash_profile
fi

if [ $HOST == "lakme" ]
then 
    eval "$(/home/mehdi/miniconda3/bin/conda shell.bash hook)"
    DATA=${HOME}/data
fi
conda activate py3p6

# codes

ablation=${HOME}/github/LSSutils/scripts/analysis/ablation_tf_old.py
multfit=${HOME}/github/LSSutils/scripts/analysis/mult_fit.py
nnfit=${HOME}/github/LSSutils/scripts/analysis/nn_fit_tf_old.py
docl=${HOME}/github/LSSutils/scripts/analysis/run_pipeline.py
elnet=${HOME}/github/LSSutils/scripts/analysis/elnet_fit.py


# ================ RUNS ====================

if [ $1 == "regression" ]
then
        echo "run regression ... "
        # low and high z
        # qso.sgc.all.hp.256.r.npy
        # 
        # ablation 98 min -- 1000 min (10 chain)
        # regression 35 minm
        for cap in ngc sgc
        do
          for zcut in all low high
          do
            nside=256
            lmax=512  
            mycap=$cap.$zcut
            echo $mycap
            glmp5=${DATA}/eboss/v6/qso.${mycap}.hp.${nside}.r.npy
            #du -h $glmp5
            oudr_ab=${DATA}/eboss/v6/results_${mycap}/ablationv2/
            oudr_r=${DATA}/eboss/v6/results_${mycap}/regression/
            log_ab=v6.log
            nn1=nn_abv2
            nn3=nn_p
            # axfit MUST change depending on the imaging maps # aug 19: with 256, WISE maps dropped
            axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16'
            # REGRESSION
            echo 'ablation on ' $mycap 'with ' $axfit 
            for rk in 0 1 2 3 4
            do
                echo $rk 'on ' $glmp5 $mycap
                mpirun -np 5 python $ablation --data $glmp5 --output $oudr_ab --log $log_ab --rank $rk --axfit $axfit
            done
            echo 'regression on ' $mycap
            mpirun -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn1}/ --ablog ${oudr_ab}${log_ab} --nside $nside
            mpirun -np 5 python $nnfit --input $glmp5 --output ${oudr_r}${nn3}/ --nside $nside --axfit $axfit      
          done
        done
elif [ $1 == "elnet" ]
then
    for cap in NGC SGC
    do
        echo $1 on $cap
        python $elnet $cap
    done
elif [ $1 == "clustering" ]
then 
        echo "run clustering ... "
        # 28 min
        for cap in NGC SGC
        do
             nmesh=512
             nside=256
             lmax=512
             axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16'
             capl=$(echo "$cap" | tr '[:upper:]' '[:lower:]')
             catlab=eBOSS_QSO_clustering
             indir=${DATA}/eboss/v6/    
             wdir=${DATA}/eboss/v6/results_${capl}.all/regression/
             oudir=${DATA}/eboss/v6/results_${capl}.all/clustering/
             random=${indir}${catlab}_${cap}_v6.ran.fits
             if [ -d $oudir ]
             then
                 echo $oudir exists
             else
                 echo creating ... $oudir
                 mkdir -p $oudir
             fi
             # compute the p(k)
             for wtag in v6 v6_wnn_abv2 v6_wnnz_abv2 v6_wnn_p v6_wnnz_p v6_zelnet v6_wosys
             do 
                 echo $wtag  $cap    
                 # 3D stuff
                 galcat=${indir}${catlab}_${cap}_${wtag}.dat.fits
                 ouname1=${oudir}pk_${wtag}_${nmesh}.json       
                 
                 # 2D stuff
                 galmap=${indir}${catlab}_${cap}_${wtag}.dat.hp256.fits
                 ranmap=${indir}fracgood.${capl}.all.hp.256.fits
                 drfeat=${indir}ngal_features_${capl}.all.fits
                 maskc=${indir}mask.${capl}.all.hp.256.fits
                 if [ $wtag = 'v6' ] 
                 then 
                     du -h $galcat             
                     #ouname2=${oudir}pk_${wtag}_wsystot_${nmesh}.json             
                     #echo $galcat $ouname1 $ouname2
                     #mpirun -np 2 python run_pk.py --galaxy_path $galcat --random_path $random --output_path $ouname2 --nmesh $nmesh
                 fi
                 # 3D st
                 #echo $galcat $ouname1
                 #mpirun -np 2 python run_pk.py --galaxy_path $galcat --random_path $random --output_path $ouname1 --nmesh $nmesh --sys_tot
                 # 2D aug 30:  
                 # mpirun -np 16 python $docl --galmap $galmap --ranmap $ranmap --photattrs $drfeat --mask $maskc --oudir $oudir --verbose --clfile cl_${cap}_${wtag} --nnbar nnbar_${cap}_${wtag} --nside $nside --lmax $lmax --axfit $axfit --corfile xi_${cap}_${wtag}
                python $docl --galmap $galmap --ranmap $ranmap --photattrs $drfeat --mask $maskc --oudir $oudir --nnbar nnbar_${cap}_${wtag} --nbin 6 --axfit $axfit
             done
             #mpirun -np 16 python $docl --galmap $galmap --ranmap $ranmap --photattrs $drfeat --mask $maskc --oudir $oudir --verbose --wmap none --clsys cl_sys --corsys xi_sys --nside ${nside} --lmax $lmax --axfit $axfit
        done
elif [ $1 == "zclustering" ]
then 
        echo "run 2D z-clustering ... "
        # 101 min
        for cap in NGC SGC
        do
             nmesh=512
             nside=256
             lmax=512
             axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16'
             capl=$(echo "$cap" | tr '[:upper:]' '[:lower:]')
             catlab=eBOSS_QSO_clustering
             indir=${DATA}/eboss/v6/    
             wdir=${DATA}/eboss/v6/results_${capl}.all/regression/
             oudir=${DATA}/eboss/v6/results_${capl}.all/clustering/
             random=${indir}${catlab}_${cap}_v6.ran.fits
             if [ -d $oudir ]
             then
                 echo $oudir exists
             else
                 echo creating ... $oudir
                 mkdir -p $oudir
             fi
             for wtag in v6 v6_wnn_abv2 v6_wnnz_abv2 v6_wnn_p v6_wnnz_p v6_zelnet v6_wosys
             do 
                 for zi in 0.8 1.1 1.3 1.5 1.7 1.9 
                 do
                     echo $wtag  $cap $zi
                     # 2D stuff
                     wtag2=${wtag}_z${zi}
                     galmap=${indir}${catlab}_${cap}_${wtag2}.dat.hp256.fits
                     ranmap=${indir}fracgood.${capl}.all.hp.256.fits
                     drfeat=${indir}ngal_features_${capl}.all.fits
                     maskc=${indir}mask.${capl}.all.hp.256.fits
                     
                     du -h $galmap
                     # 2D aug 30:  
                     #mpirun -np 16 python $docl --galmap $galmap --ranmap $ranmap --photattrs $drfeat --mask $maskc --oudir $oudir --verbose --clfile cl_${cap}_${wtag2} --nnbar nnbar_${cap}_${wtag2} --corfile xi_${cap}_${wtag2} --nside $nside --lmax $lmax --axfit $axfit 
                     python $docl --galmap $galmap --ranmap $ranmap --photattrs $drfeat --mask $maskc --oudir $oudir --nnbar nnbar_${cap}_${wtag2} --nbin 5 --axfit $axfit                     
                 done
             done
        done
else
    echo "nothing ...."
fi


# Z elnet
#   886  mpirun -np 4 python run_pk.py --galaxy_path /home/mehdi/data/eboss/v6_elnet/eBOSS_QSO_clustering_NGC_v6_zelnet.dat.fits --random_path /home/mehdi/data/eboss/v6_elnet/eBOSS_QSO_clustering_NGC_v6.ran.fits --output_path /home/mehdi/data/eboss/v6_elnet/pk_zelnet_512.json --systot
#   887  mpirun -np 4 python run_pk.py --galaxy_path /home/mehdi/data/eboss/v6_elnet/eBOSS_QSO_clustering_NGC_v6_zelnet.dat.fits --random_path /home/mehdi/data/eboss/v6_elnet/eBOSS_QSO_clustering_NGC_v6.ran.fits --output_path /home/mehdi/data/eboss/v6_elnet/pk_zelnet_512.json --sys_tot
#   888  mpirun -np 4 python run_pk.py --galaxy_path /home/mehdi/data/eboss/v6_elnet/eBOSS_QSO_clustering_SGC_v6_zelnet.dat.fits --random_path /home/mehdi/data/eboss/v6_elnet/eBOSS_QSO_clustering_SGC_v6.ran.fits --output_path /home/mehdi/data/eboss/v6_elnet/pk_SGC_zelnet_512.json --sys_tot


#
#       OLD RUNS
#
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
