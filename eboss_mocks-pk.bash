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
## took 2 min
# for i in {2..9}
# do
#     echo ${i}
#     python prepare_mocks.py --imock ${i} --kind null
#     python prepare_mocks.py --imock ${i} --kind cont
# done


#
# --- perform regression
nside=256
axfit='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16'
# for cap in NGC
# do
#     for mocki in $(seq -f "%04g" 1 9)
#     do
#         for kind in null cont
#         do
#             for zcut in 0.8 1.1 1.4 1.6 1.9
#             do 
#                 output_dir=/home/mehdi/data/eboss/mocks/${kind}/${mocki}
#                 ngal_features_5fold=${output_dir}/ngal_features_${cap}_${zcut}_${nside}.5r.npy
                
#                 # define output dirs
#                 oudir_ab=${output_dir}/results_${cap}_${zcut}_${nside}/ablation/
#                 oudir_reg=${output_dir}/results_${cap}_${zcut}_${nside}/regression/            

#                 # define output names
#                 log_ablation=eboss_mocks.log
#                 nn1=nn_ablation
#                 nn2=nn_plain                
                
                
#                 #du -h ${ngal_features_5fold}
#                 #echo $oudir_ab
#                 #echo $oudir_reg
                
#                 #
#                 # ablation
#                 for fold in 0 1 2 3 4
#                 do
#                     echo "feature selection on " $fold ${cap}_${zcut}
#                     mpirun -np 16 python $ablation --data $ngal_features_5fold \
#                                  --output $oudir_ab --log $log_ablation \
#                                  --rank $fold --axfit $axfit
#                 done      
                
#                 echo 'regression on ' $fold ${cap}_${zcut}
#                 mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                                    --output ${oudir_reg}${nn1}/ \
#                                    --ablog ${oudir_ab}${log_ablation} --nside $nside
                                   
#                 mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                                    --output ${oudir_reg}${nn2}/ --nside $nside --axfit $axfit 
                
#             done        
#         done
#     done
# done          






nmesh=512
ouput_pk=/home/mehdi/data/eboss/mocks/pks


for cap in NGC
do
    for mocki in $(seq -f "%04g" 1 4)
    do
        for kind in null cont
        do          
            #
            # ---- corrected
            
            input_dir=/home/mehdi/data/eboss/mocks/${kind}/${mocki}            
            for wtag in v7_wnnz_plain v7_wnnz_ablation
            do
                if [ $kind == "null" ]
                then 
                    rancat=/B/Shared/eBOSS/null/EZmock_eBOSS_QSO_NGC_v7_noweight_${mocki}.ran.fits
                    galcat=${input_dir}/EZmock_eBOSS_QSO_NGC_${wtag}_noweight_${mocki}.dat.fits
                elif [ $kind == "cont" ]
                then
                    rancat=/B/Shared/eBOSS/contaminated/EZmock_eBOSS_QSO_NGC_v7_${mocki}.ran.fits
                    galcat=${input_dir}/EZmock_eBOSS_QSO_NGC_${wtag}_${mocki}.dat.fits
                fi
                
                ouname=${ouput_pk}/pk_${cap}_${kind}_${wtag}_${nmesh}_${mocki}.json
                du -h $galcat
                du -h $rancat
                echo $ouname
                echo =======================================================
                mpirun -np 8 python $pk --galaxy_path $galcat \
                                         --random_path $rancat \
                                         --output_path $ouname \
                                         --nmesh $nmesh --sys_tot      
                                                                              
            done
            
            
            #
            # --- default weights
            wtag=v7
            if [ $kind == "null" ]
            then 
                rancat=/B/Shared/eBOSS/null/EZmock_eBOSS_QSO_NGC_v7_noweight_${mocki}.ran.fits
                galcat=/B/Shared/eBOSS/null/EZmock_eBOSS_QSO_NGC_${wtag}_noweight_${mocki}.dat.fits
            elif [ $kind == "cont" ]
            then
                rancat=/B/Shared/eBOSS/contaminated/EZmock_eBOSS_QSO_NGC_v7_${mocki}.ran.fits
                galcat=/B/Shared/eBOSS/contaminated/EZmock_eBOSS_QSO_NGC_${wtag}_${mocki}.dat.fits
            fi

            ouname=${ouput_pk}/pk_${cap}_${kind}_${wtag}_${nmesh}_${mocki}.json
            du -h $galcat
            du -h $rancat
            echo $ouname
            echo =======================================================
            mpirun -np 8 python $pk --galaxy_path $galcat \
                                   --random_path $rancat \
                                   --output_path $ouname \
                                   --nmesh $nmesh --sys_tot       
            
            # ---  no weight
            ouname=${ouput_pk}/pk_${cap}_${kind}_${wtag}_nowsys_${nmesh}_${mocki}.json
            du -h $galcat
            du -h $rancat
            echo $ouname
            echo =======================================================
            mpirun -np 8 python $pk --galaxy_path $galcat \
                                   --random_path $rancat \
                                   --output_path $ouname \
                                   --nmesh $nmesh
            
        done
    done
done
