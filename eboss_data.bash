#!/bin/bash

# ---  activate the env
eval "$(/home/mehdi/miniconda3/bin/conda shell.bash hook)"
conda activate py3p6

export NUMEXPR_MAX_THREADS=2
export PYTHONPATH=${HOME}/github/LSSutils:${PYTHONPATH}

ablation=${HOME}/github/LSSutils/scripts/analysis/ablation_tf_old.py
multfit=${HOME}/github/LSSutils/scripts/analysis/mult_fit.py
nnfit=${HOME}/github/LSSutils/scripts/analysis/nn_fit_tf_old.py
docl=${HOME}/github/LSSutils/scripts/analysis/run_pipeline.py
elnet=${HOME}/github/LSSutils/scripts/analysis/elnet_fit.py
pk=${HOME}/github/LSSutils/scripts/analysis/run_pk.py
xi=${HOME}/github/LSSutils/scripts/analysis/run_xi.py
pkracut=${HOME}/github/LSSutils/scripts/analysis/run_pk_racut.py



nside=512
nmesh=512
dk=0.002
boxsize=6600
version=v7_2
versiono=0.3
ouput_pk=/B/Shared/mehdi/eboss/data/${version}/${versiono}/
input_catn=/B/Shared/mehdi/eboss/data/${version}/${versiono}/
input_cato=/B/Shared/mehdi/eboss/data/${version}/

# known maps, depth, ebv, psfi skyi
axfit0='0 2 5 13'
# no w1 or depth-g maps 
axfit1='0 1 2 3 4 5 6 8 9 10 11 12 13 14 17 18 19'


# --- prepare for NN regression
# took 2 min
# for cap in NGC SGC
# do
#     data=${input_cato}eBOSS_QSO_full_${cap}_v7_2.dat.fits
#     random=${input_cato}eBOSS_QSO_full_${cap}_v7_2.ran.fits
#     systematics=/B/Shared/mehdi/templates/SDSS_WISE_HI_imageprop_nside${nside}.h5
#     output_dir=${input_catn}
#     nside=$nside
#     cap=$cap
#     slices='low high all zhigh z1 z2 z3'    
#     du -h $data $random $systematics     
#     echo ${cap} ${nside} ${version} ${versiono} ${output_dir} ${slices}
#     python prepare_data.py -d ${data} -r ${random} -s ${systematics} -o ${output_dir} -n ${nside} -c ${cap} -sl ${slices}
# done
#

# --- perform regression
# 553 min
#
#for cap in NGC SGC
#do
#    #for zcut in zhigh_racut all_racut ## only for NGC
##    for zcut in zhigh all low high z1 z2 z3  
#       output_dir=/B/Shared/mehdi/eboss/data/${version}/${versiono}
#       ngal_features_5fold=${output_dir}/ngal_features_${cap}_${zcut}_${nside}.5r.npy
#
#       #-- define output dirs
#       oudir_ab=${output_dir}/results/${cap}_${zcut}_${nside}/ablation/
#       oudir_reg=${output_dir}/results/${cap}_${zcut}_${nside}/regression/            
#
#       #-- define output names
#       log_ablation=eboss_data.log
#       nn1=nn_ablation
#       nn2=nn_plain           
#       nn3=nn_known
#              
#       du -h ${ngal_features_5fold}
#       echo $oudir_ab
#       echo $oudir_reg
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
#       #-- regression with all maps
#       mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                          --output ${oudir_reg}${nn2}/ --nside $nside --axfit $axfit1 
#
#        #-- regression with known maps
#        mpirun -np 5 python $nnfit --input $ngal_features_5fold \
#                           --output ${oudir_reg}${nn3}/ --nside $nside --axfit $axfit0 
#  done        
#done 
#
#
#
## ---- reassignment
## swap the weights in the data catalogs with NN's weights
# reassign the data attributes to randoms
# make clustering-like catalogs with 0.8<=z<=3.5
#
#
# 4 min
# for cap in NGC SGC 
# do
#     echo $cap $versiono
#
#    # standard weights
#    #python full2cosmology.py --cap ${cap} --versiono ${versiono}
#
#    # nn-based weights
#    for model in known ablation plain
#    do
#        #for zsplit in allhighra 
#        for zsplit in lowmidhigh allhigh z3high
#        do
#           if [ $zsplit == "lowmidhigh" ]
#           then
#               slices='low high zhigh'
#           elif [ $zsplit == "allhigh" ]
#           then
#               slices='all zhigh'
#           elif [ $zsplit == "z3high" ]
#           then
#               slices='z1 z2 z3 zhigh'
#           elif [ $zsplit == "allhighra" ]
#           then 
#               slices='all_racut zhigh_racut'
#           else
#               echo $zsplit 'not known'
#               continue
#           fi
#           echo $cap $model $zsplit $slices $versiono $nside
#           python swap_data.py -c ${cap} -m ${model} -zs ${zsplit} -sl ${slices} -vo ${versiono} -n $nside
#           #python swap_data_racut.py --cap ${cap} --model ${model} --zsplit ${zsplit} --slices ${slices} --versiono ${versiono} -n $nside
#       done
#   done
# done

#
#
#
#
#for zlim in standard zhigh combined
#do
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
#  #echo $zrange $zlim
#
#  for cap in NGC SGC
#  do
#      #echo $cap
#      ## --- standard treatment
#      versioni=${version}_${versiono}
#      galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#      rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits
#
#      
#      du -h $galcat $rancat
#
#      # --- power spectrum
#      model=wsystot
#      versioni=${version}_${versiono}_${model}
#      ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#      echo $ouname
#                               
#      mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                               -n $nmesh -z ${zrange} --dk $dk  --use_systot
#
#                               
#      model=wosystot
#      versioni=${version}_${versiono}_${model}
#      ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#      echo $ouname
#      mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                               -n $nmesh -z ${zrange} --dk $dk
#
#
#       ## --- NN-based treatment
#       for model in plain known ablation
#       do
#           for wtag in lowmidhigh allhigh z3high
#           
#           do
#               versioni=${version}_${versiono}_${model}_${wtag}
#               ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#               galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#               rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits
#               echo $cap $zlim $model $wtag $zrange $nmesh $ouname
#               du -h $galcat $rancat
#               echo 
#               echo 
#                mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                       -n $nmesh -z ${zrange} --dk $dk --use_systot
#   
#          done
#       done
#  done
#done
##



## --- clustering of the concatenated catalogs
# --- only testing the full and clustering catalogs
# only test NGC standard
#for zlim in standard #zhigh combined
# do
#     if [ $zlim == "standard" ]
#     then
#         zrange='0.8 2.2'
#     elif [ $zlim == "zhigh" ]
#     then 
#         zrange='2.2 3.5'
#     elif [ $zlim == "combined" ]
#     then
#         zrange='0.8 3.5'
#     fi
#     #echo $zrange $zlim
#
#     for cap in NGC #SGC
#     do
#         #echo $cap
#
#
#         ## --- standard treatment
#         galcat=${input_cato}eBOSS_QSOandhiz_clustering_${cap}_${version}.dat.fits
#         rancat=${input_cato}eBOSS_QSOandhiz_clustering_${cap}_${version}.ran.fits
#         du -h $galcat $rancat
#
#         model=wsystotnhiz
#         versioni=${version}_${versiono}_${model}
#         ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#         echo $ouname
#         mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                -n $nmesh -z ${zrange} --dk $dk  --use_systot      
#         model=wosystotnhiz
#         versioni=${version}_${versiono}_${model}
#         ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#         echo $ouname
#         mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                -n $nmesh -z ${zrange} --dk $dk 
#     done
# done
#

# --- pk with ra cut
#for zlim in standard zhigh combined
#do
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
#  echo $zrange $zlim
#
#  for cap in NGC # ra cut only for NGC
#  do
#      #echo $cap
#
#      # --- standard treatment
#      versioni=${version}_${versiono}
#      galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#      rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits
#
#    
#      du -h $galcat $rancat
#      # --- power spectrum
#      model=wsystot_racut
#      versioni=${version}_${versiono}_${model}
#      ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#      echo $ouname
#      mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                             -n $nmesh -z ${zrange} --dk $dk --use_systot
#
#
#      model=wosystot_racut
#      versioni=${version}_${versiono}_${model}
#      ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#      echo $ouname
#      mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                             -n $nmesh -z ${zrange} --dk $dk
#
#       # --- NN-based treatment
#       for model in plain #known ablation
#       do
#           for wtag in allhighra
#           #for wtag in lowmidhigh allhigh z3high
#           do
#               versioni=${version}_${versiono}_${model}_${wtag}
#               ouname=${ouput_pk}pk_${cap}_${versioni}_racut_${nmesh}_${zlim}.json
#               galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#               rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits
#               echo $cap $zlim $model $wtag $zrange $nmesh $ouname
#               du -h $galcat $rancat
#               echo 
#               echo 
#               mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                       -n $nmesh -z ${zrange} --dk $dk --use_systot  
#          done
#       done
#  done
#done

## extend zmax for high-z
# for zmax in 2.8 3.0 3.2 3.4
# do
#    zrange='2.2 '${zmax}
#    zlim=hizextend$zmax
#    echo $zrange $zlim

#    for cap in NGC SGC
#    do
       #echo $cap
       ## --- standard treatment
#        versioni=${version}_${versiono}
#        galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#        rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits

     
#        du -h $galcat $rancat

#        ## --- power spectrum
#        model=wsystot
#        versioni=${version}_${versiono}_${model}
#        ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#        echo $ouname
#        mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                 -n $nmesh -z ${zrange} --dk $dk  --use_systot

#       model=wosystot
#       versioni=${version}_${versiono}_${model}
#       ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#       echo $ouname
#       mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                -n $nmesh -z ${zrange} --dk $dk
#
#
#       ## --- NN-based treatment
#       for model in plain #known ablation
#       do
#           for wtag in lowmidhigh allhigh z3high
#           do
#               versioni=${version}_${versiono}_${model}_${wtag}
#               ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#               galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#               rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits
#               echo $cap $zlim $model $wtag $zrange $nmesh $ouname
#               du -h $galcat $rancat
#               echo 
#               echo 
#               mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                -n $nmesh -z ${zrange} --dk $dk --use_systot
# 
#          done
#       done
#    done
# done

#
#
##---- extending z-max 
## in hope of getting a better quadrupole
# for zmax in 2.4 2.6 2.8 3.0
# do
#    zrange='0.8 '${zmax}
#    zlim=zextend$zmax
#    echo $zrange $zlim

#    for cap in NGC SGC
#    do
#        #echo $cap


#        ## --- standard treatment
#        versioni=${version}_${versiono}
#        galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#        rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits

       
#        du -h $galcat $rancat

#        ## --- power spectrum
#        model=wsystot
#        versioni=${version}_${versiono}_${model}
#        ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#        echo $ouname
#        mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                 -n $nmesh -z ${zrange} --dk $dk --use_systot

#       model=wosystot
#       versioni=${version}_${versiono}_${model}
#       ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#       echo $ouname
#       mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                -n $nmesh -z ${zrange} --dk $dk
#
#
#        ## --- NN-based treatment
#        for model in plain #known ablation
#        do
#            for wtag in lowmidhigh allhigh z3high
#            do
#                versioni=${version}_${versiono}_${model}_${wtag}
#                ouname=${ouput_pk}pk_${cap}_${versioni}_${nmesh}_${zlim}.json
#                galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#                rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits
#                echo $cap $zlim $model $wtag $zrange $nmesh $ouname
#                du -h $galcat $rancat
#                echo 
#                echo 
#                #mpirun -np 16 python $pk -g $galcat -r $rancat -o $ouname \
#                                -n $nmesh -z ${zrange} --dk $dk --use_systot
#    
#           done
#        done
  done
done



# --- correlation function
# for zlim in zhigh #standard #combined zhigh
# do
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

#    for cap in NGC SGC 
#    do

#        ## --- standard treatment
#        versioni=${version}_${versiono}
#        galcat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.dat.fits
#        rancat=${input_catn}eBOSS_QSO_clustering_${cap}_${versioni}.ran.fits

#        du -h $galcat $rancat

#        ## --- xi
#        model=wsystot
#        versioni=${version}_${versiono}_${model}
#        ouname=${ouput_pk}xi_${cap}_${versioni}_${nmesh}_${zlim}.json
#        echo $ouname
#        mpirun -np 16 python $xi --galaxy_path $galcat \
#                                 --random_path $rancat \
#                                 --output_path $ouname \
#                                 --nmesh $nmesh --zlim ${zrange} --sys_tot

#    done
# done


#for cap in NGC SGC
#do
#    # add default systot
#
#    for model in plain # known ablation
#    do
#        for zsplit in allhigh lowmidhigh z3high
#        do
#            cat=${input_catn}eBOSS_QSO_clustering_${cap}_v7_2_0.3_${model}_${zsplit}.dat.fits
#            #du -h $cat
#            python prepare_data_hp.py ${cat}
#        done
#
#    done
#done


#--- Angular clustering
# data/eboss/v7_2/0.3/eBOSS_QSO_clustering_NGC_v7_2_0.3_ablation_lowmidhigh_zhigh.hp512.dat.fits

# templates=/B/Shared/mehdi/templates/SDSS_WISE_HI_imageprop_nside512.h5
# axfit='21 18 6 1 2 3 4 7 8 9 10 11 12 13 14 15 16 19 20 5' # eboss columns
# oudir=${input_catn}clustering/

# for cap in NGC SGC
# do
#     for zrange in low high zhigh #all z1 z2 z3 tot
#     do
#         # default
#         mask=${input_catn}mask_${cap}.hp512.ran.fits       
#         galmap=${input_catn}eBOSS_QSO_clustering_${cap}_v7_2_0.3_${zrange}.hp512.dat.fits
#         ranmap=${input_catn}eBOSS_QSO_clustering_${cap}_v7_2_0.3_tot.hp512.ran.fits
        
#         clfile=cl_0.3_${cap}_systot_${zrange}.npy
#         nnbar=nnbar_0.3_${cap}_systot_${zrange}.npy
#         logfile=log_0.3_${cap}_systot_${zrange}.txt
        
#         #echo $nnbar #$logfile $oudir
#         #du -h $galmap $ranmap $mask

#         time mpirun -np 16 python $docl --galmap ${galmap} --ranmap ${ranmap} --photattrs ${templates} --mask ${mask} --oudir ${oudir} --axfit ${axfit[@]} --clfile ${clfile} --log ${logfile} --nside $nside
#         # nn
#         for model in plain ablation known
#         do

#             for zsplit in allhigh lowmidhigh z3high
#             do
#                 galmap=${input_catn}eBOSS_QSO_clustering_${cap}_v7_2_0.3_${model}_${zsplit}_${zrange}.hp512.dat.fits
#                 ranmap=${input_catn}eBOSS_QSO_clustering_${cap}_v7_2_0.3_${model}_${zsplit}_tot.hp512.ran.fits
#                 #du -h $galmap $ranmap $mask

#                clfile=cl_0.3_${cap}_${model}_${zsplit}_${zrange}.npy
#                nnbar=nnbar_0.3_${cap}_${model}_${zsplit}_${zrange}.npy
#                logfile=log_0.3_${cap}_${model}_${zsplit}_${zrange}.txt

#                #echo $nnbar
#                 time mpirun -np 16 python $docl --galmap ${galmap} --ranmap ${ranmap} --photattrs ${templates} --mask ${mask} --oudir ${oudir} --axfit ${axfit[@]} --clfile ${clfile} --log ${logfile} --nside $nside
#             done

#         done

#     done

# done
