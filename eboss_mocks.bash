#!/bin/bash

# ---  activate the env
eval "$(/home/mehdi/miniconda3/bin/conda shell.bash hook)"
conda activate py3p6

export NUMEXPR_MAX_THREADS=2

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
versiono=0.3
nside=512
cap=NGC
path_mocks=/B/Shared/eBOSS
systematics_name=/home/mehdi/data/templates/SDSS_WISE_HI_imageprop_nside512.h5

axfit0='0 1'
axfit1='0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19'


# for i in $(seq -f "%04g" 1 9)
# do

#     for cont in contaminated null
#     do
    
#         if [ ${cont} == 'contaminated' ]
#         then
#             data_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_${i}.dat.fits
#             random_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_${i}.ran.fits
#         else
#             data_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_noweight_${i}.dat.fits
#             random_name=${path_mocks}/${cont}/EZmock_eBOSS_QSO_${cap}_v7_noweight_${i}.ran.fits            
#         fi
    
    
    
#         output_dir=/B/Shared/mehdi/eboss/mocks/${cap}_${i}_${cont}
          
#         echo ${i} $output_dir
#         #du -h $data_name $random_name $systematics_name
        
#         # mocks do not have slice zhigh
#         python prepare_data.py -d $data_name -r $random_name -s $systematics_name -o $output_dir \
#                     -c $cap -sl low high all z1 z2 z3 --log log_${cont}_${i}.txt
    
    
#     done
# done


# --- perform regression
# for i in $(seq -f "%04g" 1 9)
# do

#     for cont in contaminated null
#     do
       
#         for zcut in low high all z1 z2 z3
#         do

#             output_dir=/B/Shared/mehdi/eboss/mocks/${cap}_${i}_${cont}

#             ngal_features_5fold=${output_dir}/ngal_features_${cap}_${zcut}_${nside}.5r.npy

#             echo ${i} $output_dir
#             #du -h $data_name $random_name $systematics_name $ngal_features_5fold

#             #-- define output dirs
#             oudir_ab=${output_dir}/results/${cap}_${zcut}_${nside}/ablation/
#             oudir_reg=${output_dir}/results/${cap}_${zcut}_${nside}/regression/            

#             #-- define output names
#             log_ablation=eboss_mocks.log
#             nn1=nn_ablation
#             nn2=nn_plain           
#             nn3=nn_known

#             #du -h ${ngal_features_5fold}
#             #echo $oudir_ab
#             #echo $oudir_reg
            

#            #-- ablation
#            for fold in 0 1 2 3 4
#            do
#                echo "feature selection on " $fold ${cap}_${zcut}
#                mpirun -np 16 python $ablation --data $ngal_features_5fold \
#                             --output $oudir_ab --log $log_ablation \
#                             --rank $fold --axfit $axfit1
#            done      

#            echo 'regression on ' $fold ${cap}_${zcut}

#            #-- regression with ablation
#            mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                                --output ${oudir_reg}${nn1}/ \
#                                --ablog ${oudir_ab}${log_ablation} --nside $nside

#            #-- regression with all maps
#            mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                               --output ${oudir_reg}${nn2}/ --nside $nside --axfit $axfit1 

#            #-- regression with known maps
#            mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                               --output ${oudir_reg}${nn3}/ --nside $nside --axfit $axfit0 


#         done        
#     done
# done





# ---- swap the weights in mock catalogs
# NN's weights
# 4 min
for imock in {1..9}
do 
   for cont in null contaminated
   do
       for model in plain known ablation
       do
           for zsplit in lowmid all z3
           do
               if [ $zsplit == "lowmid" ]
               then
                   slices='low high'
               elif [ $zsplit == "all" ]
               then
                   slices='all'
               elif [ $zsplit == "z3" ]
               then
                   slices='z1 z2 z3'
               else
                   echo $zsplit 'not known'
                   continue
               fi
               echo $imock $cont $model $zsplit $slices
               python swap_mocks.py --cont ${cont} --imock ${imock} --model ${model} --zsplit ${zsplit} --slices ${slices}
          done
      done
   done
done
#
# Julian's code
# 2 min
#python do_systematics_fit.py QSO NGC 1 9 0.8 2.2



#--- clustering
#version=v7
#nmesh=512
#zlim=standard
#
#
#for imock in $(seq -f "%04g" 8 9)
#do 
#
#  if [ $zlim == "standard" ]
#  then
#      zrange='0.8 2.2'
#  elif [ $zlim == "zhigh" ]
#  then 
#      zrange='2.2 3.5'
#  elif [ $zlim == "combined" ]
#  then
#      zrange='0.8 3.5'
#  fi
#  
#  for cont in null contaminated
#  do
#
#
#      #=================================
#      # null and cont. with default correction
#      echo "default method w "${cont}
#      # default
#      if [ ${cont} == "null" ]
#      then
#          galcat=/B/Shared/mehdi/eboss/mocks/NGC_${imock}_${cont}/EZmock_eBOSS_QSO_NGC_${version}_${imock}.dat.fits
#          rancat=${galcat/.dat./.ran.}
#
#      elif [ ${cont} == "contaminated" ]
#      then
#          galcat=/B/Shared/eBOSS/contaminated/EZmock_eBOSS_QSO_NGC_${version}_${imock}.dat.fits
#          rancat=${galcat/.dat./.ran.}
#      fi
#      du -h $galcat $rancat
#      tag=QSO_NGC_${version}_${versiono}_systot_all_${imock}
#      ouname=/B/Shared/mehdi/eboss/mocks/NGC_${imock}_${cont}/pk_${tag}_${cont}_${nmesh}_${zlim}.json
#      echo $ouname
#      mpirun -np 16 python $pk --galaxy_path $galcat \
#                               --random_path $rancat \
#                               --output_path $ouname \
#                               --nmesh $nmesh --zlim ${zrange} --sys_tot
#
#      echo
#      echo
#      echo
#
#
#
#
#      #=================================
#      # cont without correction 
#      if [ ${cont} == "contaminated" ]
#      then
#          galcat=/B/Shared/eBOSS/contaminated/EZmock_eBOSS_QSO_NGC_${version}_${imock}.dat.fits
#          rancat=${galcat/.dat./.ran.}
#          du -h $galcat $rancat
#          tag=QSO_NGC_${version}_${versiono}_nowsys_all_${imock}
#          ouname=/B/Shared/mehdi/eboss/mocks/NGC_${imock}_${cont}/pk_${tag}_${cont}_${nmesh}_${zlim}.json
#          echo ${ouname}
#
#          mpirun -np 16 python $pk --galaxy_path $galcat \
#                                   --random_path $rancat \
#                                   --output_path $ouname \
#                                   --nmesh $nmesh --zlim ${zrange}
#      fi
#      echo 
#      echo
#      echo
#
#
#
#
#      #=================================
#      # null without correction (truth)
#      if [ ${cont} == "null" ]
#      then
#          galcat=/B/Shared/eBOSS/null/EZmock_eBOSS_QSO_NGC_${version}_noweight_${imock}.dat.fits
#          rancat=${galcat/.dat./.ran.}
#          du -h $galcat $rancat
#          tag=QSO_NGC_${version}_${versiono}_truth_all_${imock}
#          ouname=/B/Shared/mehdi/eboss/mocks/NGC_${imock}_${cont}/pk_${tag}_${cont}_${nmesh}_${zlim}.json
#          echo ${ouname}
#
#          mpirun -np 16 python $pk --galaxy_path $galcat \
#                                   --random_path $rancat \
#                                   --output_path $ouname \
#                                   --nmesh $nmesh --zlim ${zrange}
#      fi
#      echo 
#      echo
#      echo
#      
#      
#
#      #=================================
#      echo "NN method w "${cont}
#      # NN-based
#      for model in plain known ablation
#      do
#           for zsplit in lowmid all z3
#           do
#               #echo $imock $cont $model $zsplit
#               tag=QSO_NGC_${version}_${versiono}_${model}_${zsplit}_${imock}
#               galcat=/B/Shared/mehdi/eboss/mocks/NGC_${imock}_${cont}/EZmock_eBOSS_${tag}.dat.fits
#               rancat=${galcat/.dat./.ran.}
#               ouname=/B/Shared/mehdi/eboss/mocks/NGC_${imock}_${cont}/pk_${tag}_${cont}_${nmesh}_${zlim}.json
#
#               du -h $galcat $rancat
#               echo ${ouname}
#
#               mpirun -np 16 python $pk --galaxy_path $galcat \
#                                       --random_path $rancat \
#                                       --output_path $ouname \
#                                       --nmesh $nmesh --zlim ${zrange} --sys_tot
#            done
#      done
#      echo 
#      echo
#      echo
#
#
#  done
#done
#
##
#
#
