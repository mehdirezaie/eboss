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
xi=${HOME}/github/LSSutils/scripts/analysis/run_xi.py
pkracut=${HOME}/github/LSSutils/scripts/analysis/run_pk_racut.py


# --- prepare for NN regression
# took 2 min
cap=NGC
path_mocks=/B/Shared/eBOSS
systematics_name=/home/mehdi/data/templates/SDSS_WISE_HI_imageprop_nside512.h5


#--- mock 1 is done separately for debugging purposes
for i in $(seq -f "%04g" 2 9)
do

    for cont in contaminated null
    do
    
        if [ ${cont} == 'contaminated' ]
        then
            data_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_${i}.dat.fits
            random_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_${i}.ran.fits
        else
            data_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_noweight_${i}.dat.fits
            random_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_noweight_${i}.ran.fits            
        fi
    
    
    
        output_dir=/B/Shared/mehdi/eboss/mocks/${cap}_${i}_${cont}
          
        echo ${i} $output_dir
        #du -h $data_name $random_name $systematics_name
        
        # mocks do not have slice zhigh
        python prepare_data.py -d $data_name -r $random_name -s $systematics_name -o $output_dir \
                    -c $cap -sl low high all z1 z2 z3 --log log_${cont}_${i}.txt
    
    
    done
done


#
# --- perform regression
# took 6h with 5 processes ngc, null and cont,
# 5 z bins
# real    8748m25.076s
# user    149188m18.459s
# sys     6889m37.525s
#nside=512
#axfit0='0 1'
#axfit1='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19'
#for cap in NGC
#do
#     for mocki in $(seq -f "%04g" 1 9)
#     do
#         for kind in null cont
#         do
#             for zcut in low high
#             
#             do 
#                 output_dir=/home/mehdi/data/eboss/mocks/${kind}/${mocki}
#                 ngal_features_5fold=${output_dir}/ngal_features_${cap}_${zcut}_${nside}.5r.npy
#               
#                 # define output dirs
#                 oudir_ab=${output_dir}/results_${cap}_${zcut}_${nside}/ablation/
#                 oudir_reg=${output_dir}/results_${cap}_${zcut}_${nside}/regression/            
#
#                 # define output names
#                 log_ablation=eboss_mocks.log
#                 nn1=nn_ablation
#                 nn2=nn_plain           
#                 nn3=nn_known
#               
#              
#                 du -h ${ngal_features_5fold}
#                 echo $oudir_ab
#                 echo $oudir_reg
#                
#                 #
#                 # ablation
#                 for fold in 0 1 2 3 4
#                 do
#                      echo "feature selection on " $fold ${cap}_${zcut}
#                      mpirun -np 16 python $ablation --data $ngal_features_5fold \
#                                   --output $oudir_ab --log $log_ablation \
#                                   --rank $fold --axfit $axfit1
#                 done      
#               
#                  echo 'regression on ' $fold ${cap}_${zcut}
#                  # regression with ablation
#                  mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                                     --output ${oudir_reg}${nn1}/ \
#                                     --ablog ${oudir_ab}${log_ablation} --nside $nside
#                
#                 # regression with all maps
#                 mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                                    --output ${oudir_reg}${nn2}/ --nside $nside --axfit $axfit1 
#                
#                 # regression with known maps
#                 mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                                    --output ${oudir_reg}${nn3}/ --nside $nside --axfit $axfit0 
# 
#             done        
#         done
#     done
#done 
##



# ---- swap the weights in mock catalogs
# NN's weights
# 4 min
#for i in {1..9}
#do 
#    for kind in null cont
#    do
#        echo ${i}  ${kind}
#        python swap_mocks.py --kind ${kind} --imock ${i}
#    done
#done
#
# Julian's code
# 2 min
# python do_systematics_fit.py QSO NGC 1 10 0.8 2.2


# copy all catalogs to their local
# for i in {2..9};do cp /B/Shared/eBOSS/null/EZmock_eBOSS_QSO_NGC_v7_noweight_000${i}.dat.fits /B/Shared/eBOSS/null/EZmock_eBOSS_QSO_NGC_v7_noweight_000${i}.ran.fits /home/mehdi/data/eboss/mocks/null/000${i}/;done

# nmesh=512
# ouput_pk=/home/mehdi/data/eboss/mocks/pks
# input_cat=/home/mehdi/data/eboss/mocks

# for cap in NGC
# do
#     for mocki in $(seq -f "%04g" 1 9)
#     do    

#         for kind in null cont
#         do
#            echo $mocki $kind 
#            # corrected
#            if [ $kind == "cont" ]
#            then
#                #wtags='v7 v7_wnnall_known v7_wnnall_plain v7_wnnall_ablation'
#                wtags='v7_wnnlowhigh_known v7_wnnlowhigh_plain v7_wnnlowhigh_ablation'
#            else
#                #wtags='v7 v7_noweight v7_wnnall_known_noweight v7_wnnall_plain_noweight v7_wnnall_ablation_noweight'
#                wtags='v7_wnnlowhigh_known_noweight v7_wnnlowhigh_plain_noweight v7_wnnlowhigh_ablation_noweight'
#            fi
           
#            for wtag in $wtags
#            do
#                echo $kind $wtag
#                ouname=${ouput_pk}/pk_${cap}_${kind}_${wtag}_${nmesh}_${mocki}.json
#                rancat=${input_cat}/${kind}/${mocki}/EZmock_eBOSS_QSO_NGC_${wtag}_${mocki}.ran.fits
#                galcat=${input_cat}/${kind}/${mocki}/EZmock_eBOSS_QSO_NGC_${wtag}_${mocki}.dat.fits
               
#                echo $ouname
#                du -h $galcat $rancat               
#                # with weights
#                mpirun -np 16 python $pk --galaxy_path $galcat \
#                                        --random_path $rancat \
#                                        --output_path $ouname \
#                                        --nmesh $nmesh --sys_tot

#                # without weights
#                if [[ $wtag == "v7_noweight"  &&  $kind == "null" ]]
#                then 
#                    ouname=${ouput_pk}/pk_${cap}_${kind}_v7_nosysweight_${nmesh}_${mocki}.json
#                    echo $ouname
#                    # with weights
# #                   mpirun -np 16 python $pk --galaxy_path $galcat \
# #                                            --random_path $rancat \
# #                                            --output_path $ouname \
# #                                            --nmesh $nmesh                   
#                fi
               
#                if [[ $wtag == "v7"  &&  $kind == "cont" ]]
#                then 
#                    ouname=${ouput_pk}/pk_${cap}_${kind}_v7_nosysweight_${nmesh}_${mocki}.json
#                    echo $ouname
#                    # with weights
# #                   mpirun -np 16 python $pk --galaxy_path $galcat \
# #                                            --random_path $rancat \
# #                                            --output_path $ouname \
# #                                            --nmesh $nmesh                   
#                fi                              
#            done           
#         done
#     done
# done
