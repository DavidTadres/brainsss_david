#!/bin/bash
#SBATCH --job-name=6_motion_correction
#SBATCH --partition=trc
#SBATCH --time=2-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --output=./logs/6_motion_correction.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL


ARGS="{\"PWD\":\"$PWD\"}"

ml python/3.9.0
source /home/users/dtadres/.env_brainsss_david/bin/activate
# ml antspy/0.2.2
date
python3 -u ./6_motion_correction.py $ARGS
