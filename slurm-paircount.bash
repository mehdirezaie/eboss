#!/bin/bash
#SBATCH -q regular
#SBATCH -t 00:15:00
#SBATCH -N 1
#SBATCH -J paircount
#SBATCH -o pc-%j.out 
#SBATCH -C haswell
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=mehdirezaie1990@gmail.com


# run it with
# sbatch slurm-paircount.bash
# to compute the paircount
# 
# load craympi envirnment
# installed with
# conda create -n craympi -c http://portal.nersc.gov/project/m3035/channels/bccp/nbodykit
#
module load python/3.6-anaconda-4.4
source activate craympi

DATA=/Volumes/TimeMachine/data/random0_DR12v5_CMASSLOWZTOT_North.fits
RROUTPUT=/Volumes/TimeMachine/data/random0_DR12v5_CMASSLOWZTOT_North_RR 
srun -n 16 python run_paircount.py --galaxy_path $DATA --output_path $RROUTPUT --zlim 0.2 0.5

