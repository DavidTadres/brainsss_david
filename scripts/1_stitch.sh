#!/bin/bash
#SBATCH --job-name=stitch_nii
#SBATCH --partition=trc
#SBATCH --time=2-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --output=./logs/stitchlog3.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL

ml python/3.9.0
source /home/users/dtadres/.env_brainsss_david/bin/activate
# ml antspy/0.2.2
date
python3 -u /home/users/dtadres/brainsss_david/scripts/1_stitch_split_nii.py
