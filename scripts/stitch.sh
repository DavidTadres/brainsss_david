#!/bin/bash
#SBATCH --job-name=stitch_nii
#SBATCH --partition=trc
#SBATCH --time=2-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --output=./logs/stitchlog3.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL

ml python/3.6.1
# ml antspy/0.2.2
date
python3 -u /home/users/david/brainsss_david/scripts/stitch_nii_only_Ashley.py
