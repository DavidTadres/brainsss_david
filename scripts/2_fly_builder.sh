#!/bin/bash
#SBATCH --job-name=2_fly_builder
#SBATCH --partition=trc
#SBATCH --time=2-00:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --output=./logs/2_fly_builder.out
#SBATCH --open-mode=append
#SBATCH --mail-type=ALL

flagged_dir = os.path.join(imports_path, dir_to_build)
        args = {'logfile': logfile, 'flagged_dir': flagged_dir, 'dataset_path': dataset_path, 'fly_dirs': fly_dirs, 'user': user}
        script = '2_fly_builder.py'
        job_id = brainsss.sbatch(jobname='bldfly',
                             script=os.path.join(scripts_path, script),
                             modules=modules,
                             args=args,
                             logfile=logfile, time=3, mem=1, nice=nice, nodes=nodes)
        func_and_anats = brainsss.wait_for_job(job_id, logfile, com_path)
        func_and_anats = func_and_anats.split('\n')[:-1]
        funcs = [x.split(':')[1] for x in func_and_anats if 'func:' in x] # will be full paths to fly/expt
        anats = [x.split(':')[1] for x in func_and_anats if 'anat:' in x]

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
