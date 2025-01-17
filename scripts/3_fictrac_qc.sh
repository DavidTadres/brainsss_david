#!/bin/bash
#SBATCH --job-name=2_fly_builder
#SBATCH --partition=trc
#SBATCH --time=2-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --output=./logs/2_fly_builder.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL

while [[ $# -gt 0 ]]; do
  case $1 in
    -b|--build_flies)
      BUILDFLIES="$2"
      shift
      shift
      ;;
    -f|--flies)
      FLIES="$2"
      shift
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

ARGS="{\"PWD\":\"$PWD\",\"BUILDFLIES\":\"$BUILDFLIES\",\"FLIES\":\"$FLIES\"}"

ml python/3.9.0
source /home/users/dtadres/.env_brainsss_david/bin/activate
# ml antspy/0.2.2
date
python3 -u ./2_fly_builder.py $ARGS
