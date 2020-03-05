#!/bin/bash

# ---  activate the env
eval "$(/home/mehdi/miniconda3/bin/conda shell.bash hook)"
conda activate py3p6

ablation=${HOME}/github/LSSutils/scripts/analysis/ablation_tf_old.py
multfit=${HOME}/github/LSSutils/scripts/analysis/mult_fit.py
nnfit=${HOME}/github/LSSutils/scripts/analysis/nn_fit_tf_old.py
docl=${HOME}/github/LSSutils/scripts/analysis/run_pipeline.py
elnet=${HOME}/github/LSSutils/scripts/analysis/elnet_fit.py
pk=${HOME}/github/LSSutils/scripts/analysis/run_pk.py


# --- prepare for NN regression
# took 2 min
#for cap in NGC SGC
#do
#    echo ${cap}
#    python prepare_data.py --cap ${cap} --slices low high all zhigh z1 z2 z3
#done
#

#
# --- perform regression
# 553 min
#nside=512
###axfit0='0 1'
#axfit0='0 2 5 13'
#axfit1='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19'
#
#for cap in NGC SGC
#do
#    for zcut in zhigh all low high z1 z2 z3 
#    do 
#        output_dir=/home/mehdi/data/eboss/v7_2/0.1
#        ngal_features_5fold=${output_dir}/ngal_features_${cap}_${zcut}_${nside}.5r.npy
#
#        #-- define output dirs
#        oudir_ab=${output_dir}/results/${cap}_${zcut}_${nside}/ablation/
#        oudir_reg=${output_dir}/results/${cap}_${zcut}_${nside}/regression/            
#
#        #-- define output names
#        log_ablation=eboss_data.log
#        nn1=nn_ablation
#        nn2=nn_plain           
#        nn3=nn_known
#               
#        du -h ${ngal_features_5fold}
#        echo $oudir_ab
#        echo $oudir_reg
#
#        #-- ablation
#        for fold in 0 1 2 3 4
#        do
#            echo "feature selection on " $fold ${cap}_${zcut}
#            mpirun -np 16 python $ablation --data $ngal_features_5fold \
#                         --output $oudir_ab --log $log_ablation \
#                         --rank $fold --axfit $axfit1
#        done      
#
#        echo 'regression on ' $fold ${cap}_${zcut}
#        
#        #-- regression with ablation
#        mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                            --output ${oudir_reg}${nn1}/ \
#                            --ablog ${oudir_ab}${log_ablation} --nside $nside
#
#        #-- regression with all maps
#        mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                           --output ${oudir_reg}${nn2}/ --nside $nside --axfit $axfit1 
#
#        #-- regression with known maps
#        mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                           --output ${oudir_reg}${nn3}/ --nside $nside --axfit $axfit0 
#   done        
#done 
#
#
#
# ---- swap the weights in mock catalogs
# NN's weights
# 4 min
for cap in NGC
do
    for model in known ablation
    do
        #for zsplit in lowmidhigh allhigh z123high
        for zsplit in z3high
        do
            if [ $zsplit == "lowmidhigh" ]
            then
                slices='low high zhigh'
            elif [ $zsplit == "allhigh" ]
            then
                slices='all zhigh'
            elif [ $zsplit == "z3high" ]
            then
                slices='z1 z2 z3 zhigh'
            else
                echo $zsplit 'not known'
                continue
            fi
            echo $cap $model $zsplit $slices
            python swap_data.py --cap ${cap} --model ${model} --zsplit ${zsplit} --slices ${slices} 
        done
    done
done


# Julian's code
# 2 min
# python do_systematics_fit.py QSO NGC 1 10 0.8 2.2


#nmesh=512
#version=v7_2
#versiono=0.1
#ouput_pk=/home/mehdi/data/eboss/${version}/${versiono}/
#input_catn=/home/mehdi/data/eboss/${version}/${versiono}/
#input_cato=/home/mehdi/data/eboss/${version}/
#
#for zlim in standard zhigh combined
#do
#    if [ $zlim == "standard" ]
#    then
#        zrange='0.8 2.2'
#    elif [ $zlim == "zhigh" ]
#    then 
#        zrange='2.2 3.5'
#    elif [ $zlim == "combined" ]
#    then
#        zrange='0.8 3.5'
#    fi
#    #echo $zrange $zlim
#
#    for cap in NGC SGC
#    do
#        #echo $cap
#        galcat=${input_cato}eBOSS_QSO_full_${cap}_${version}.dat.fits
#        rancat=${input_cato}eBOSS_QSO_full_${cap}_${version}.ran.fits
#        #du -h $galcat $rancat
#
#        model=wsystot
#        versioni=${version}_${versiono}_${model}
#        ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#        echo $ouname
#        mpirun -np 16 python $pk --galaxy_path $galcat \
#                                 --random_path $rancat \
#                                 --output_path $ouname \
#                                 --nmesh $nmesh --zlim ${zrange} --sys_tot
#       
#        model=wosystot
#        versioni=${version}_${versiono}_${model}
#        ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#        echo $ouname
#        mpirun -np 16 python $pk --galaxy_path $galcat \
#                                 --random_path $rancat \
#                                 --output_path $ouname \
#                                 --nmesh $nmesh --zlim ${zrange} 
#
#
#        for model in plain known ablation
#        do
#            #echo $model 
#            wtag=lowmidhigh
#            versioni=${version}_${versiono}_${model}_${wtag}
#            ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#            galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#            rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits
#            #du -h $galcat $rancat
#            echo $ouname
#            mpirun -np 16 python $pk --galaxy_path $galcat \
#                                 --random_path $rancat \
#                                 --output_path $ouname \
#                                 --nmesh $nmesh --zlim ${zrange} --sys_tot
#
#        done
#    done
#done
