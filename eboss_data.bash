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
#python prepare_data.py


#
# --- perform regression
# 553 min
nside=512
axfit0='0 1'
axfit1='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19'
#for cap in NGC
#do
#    for zcut in all
#    do 
#        output_dir=/home/mehdi/data/eboss/v7_1/0.5
#        ngal_features_5fold=${output_dir}/ngal_features_${cap}_${zcut}_${nside}.5r.npy
#
#        # define output dirs
#        oudir_ab=${output_dir}/results_${cap}_${zcut}_${nside}/ablation/
#        oudir_reg=${output_dir}/results_${cap}_${zcut}_${nside}/regression/            
#
#        # define output names
#        log_ablation=eboss_data.log
#        nn1=nn_ablation
#        nn2=nn_plain           
#        nn3=nn_known
#               
#        du -h ${ngal_features_5fold}
#        echo $oudir_ab
#        echo $oudir_reg
#
#        # ablation
#        for fold in 0 1 2 3 4
#        do
#            echo "feature selection on " $fold ${cap}_${zcut}
#            mpirun -np 16 python $ablation --data $ngal_features_5fold \
#                         --output $oudir_ab --log $log_ablation \
#                         --rank $fold --axfit $axfit1
#        done      
#
#        echo 'regression on ' $fold ${cap}_${zcut}
#         # regression with ablation
#        mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                            --output ${oudir_reg}${nn1}/ \
#                            --ablog ${oudir_ab}${log_ablation} --nside $nside
#
#        # regression with all maps
#        mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                           --output ${oudir_reg}${nn2}/ --nside $nside --axfit $axfit1 
#
#        # regression with known maps
#        mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                           --output ${oudir_reg}${nn3}/ --nside $nside --axfit $axfit0 
#
#   done        
#done 
#
# ---- swap the weights in mock catalogs
# NN's weights
# 4 min
#python swap_data.py

# Julian's code
# 2 min
# python do_systematics_fit.py QSO NGC 1 10 0.8 2.2


#
nmesh=512
ouput_pk=/home/mehdi/data/eboss/v7_1/0.5
input_cat=/home/mehdi/data/eboss/v7_1/0.5

#
for cap in NGC
do
  wtags='v7_1 v7_1_wnnz_known v7_1_wnnz_plain v7_1_wnnz_ablation'
  for wtag in $wtags
  do
    echo $kind $wtag
    ouname=${ouput_pk}/pk_${cap}_${wtag}_${nmesh}.json
    rancat=${input_cat}/eBOSS_QSO_full_${cap}_${wtag}.ran.fits
    galcat=${input_cat}/eBOSS_QSO_full_${cap}_${wtag}.dat.fits
    echo $ouname
    du -h $galcat $rancat               
    # with weights
    mpirun -np 16 python $pk --galaxy_path $galcat \
                             --random_path $rancat \
                             --output_path $ouname \
                             --nmesh $nmesh --sys_tot
    # without weights
    if [ $wtag == "v7_1" ]
    then 
        ouname=${ouput_pk}/pk_${cap}_${wtag}_nosysweight_${nmesh}.json
        echo $ouname
        # with weights
        mpirun -np 16 python $pk --galaxy_path $galcat \
                                 --random_path $rancat \
                                 --output_path $ouname \
                                --nmesh $nmesh                   
    fi                              
    done
done
