import time
import sys
import os
import re
import json
import datetime
import pyfiglet
import textwrap
import brainsss

modules = 'gcc/6.3.0 python/3.6.1 py-numpy/1.14.3_py36 py-pandas/0.23.0_py36 viz py-scikit-learn/0.19.1_py36 antspy/0.2.2'

#########################
### Setup preferences ###
#########################

width = 120 # width of print log
flies = ['fly_001', 'fly_002'] # set to None, or a list of fly dirs in dataset_path
nodes = 2 # 1 or 2
nice = True # true to lower priority of jobs. ie, other users jobs go first

#####################
### Setup logging ###
#####################

logfile = './logs/' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
printlog = getattr(brainsss.Printlog(logfile=logfile), 'print_to_log')
sys.stderr = brainsss.Logger_stderr_sherlock(logfile)

###################
### Setup paths ###
###################

#CHANGE THESE PATHS
scripts_path = "/home/users/brezovec/projects/brainsss/scripts"
com_path = "/home/users/brezovec/projects/brainsss/scripts/com"

#change this path to your oak directory, something like /oak/stanford/groups/trc/data/Brezovec/data
dataset_path = "/oak/stanford/groups/trc/data/Brezovec/2P_Imaging/20210220_alex_anat_test"

###################
### Print Title ###
###################

title = pyfiglet.figlet_format("Brainsss", font="cyberlarge" ) #28 #shimrod
title_shifted = ('\n').join([' '*28+line for line in title.split('\n')][:-2])
printlog(title_shifted)
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog(F"{day_now+' | '+time_now:^{width}}")
printlog("")

for fly in flies:
    ##########################
    ### Create mean brains ###
    ##########################
    printlog(f"\n{'   MEAN BRAINS   ':=^{width}}")
    job_ids = []
    directory = os.path.join(dataset_path, fly)
    files = ['anatomy_channel_1', 'anatomy_channel_2']
    args = {'logfile': logfile, 'directory': directory, 'files': files}
    script = '5_make_mean_brain.py'
    job_id = brainsss.sbatch(jobname='meanbrn',
                         script=os.path.join(scripts_path, script),
                         modules=modules,
                         args=args,
                         logfile=logfile, time=1, mem=4, nice=nice, nodes=nodes)
    job_ids.append(job_id)

    for job_id in job_ids:
        brainsss.wait_for_job(job_id, logfile, com_path)

    ##################
    ### Start MOCO ###
    ##################
    timepoints = 100 #number of volumes
    step = 10 #how many volumes one job will handle
    mem = 7
    time_moco = 6
    begin='21:00'#'now'

    printlog(f"\n{'   MOTION CORRECTION   ':=^{width}}")
    # This will immediately launch all partial mocos and their corresponding dependent moco stitchers
    stitcher_job_ids = []
    progress_tracker = {}

    directory = os.path.join(dataset_path, fly)
    fly_print = directory.split('/')[-1]

    moco_dir = os.path.join(directory, 'moco')
    if not os.path.exists(moco_dir):
        os.makedirs(moco_dir)

    starts = list(range(0,timepoints,step))
    stops = starts[1:] + [timepoints]

    #######################
    ### Launch partials ###
    #######################
    job_ids = []
    for start, stop in zip (starts, stops):
        args = {'logfile': logfile, 'directory': directory, 'start': start, 'stop': stop}
        script = 'moco_partial.py'
        job_id = brainsss.sbatch(jobname='moco',
                             script=os.path.join(scripts_path, script),
                             modules=modules,
                             args=args,
                             logfile=logfile, time=time_moco, mem=mem, nice=nice, silence_print=True, nodes=nodes, begin=begin)
        job_ids.append(job_id)

    printlog(F"| moco_partials | SUBMITTED | {fly_print} | {len(job_ids)} jobs, {step} vols each |")
    job_ids_colons = ':'.join(job_ids)
    for_tracker = '/'.join(directory.split('/')[-2:])
    progress_tracker[for_tracker] = {'job_ids': job_ids, 'total_vol': timepoints}

    #################################
    ### Create dependent stitcher ###
    #################################
    args = {'logfile': logfile, 'directory': moco_dir}
    script = 'moco_stitcher.py'
    job_id = brainsss.sbatch(jobname='stitch',
                         script=os.path.join(scripts_path, script),
                         modules=modules,
                         args=args,
                         logfile=logfile, time=2, mem=12, dep=job_ids_colons, nice=nice, nodes=nodes)
    stitcher_job_ids.append(job_id)

    if bool(progress_tracker): #if not empty
        brainsss.moco_progress(progress_tracker, logfile, com_path)

    for job_id in stitcher_job_ids:
        brainsss.wait_for_job(job_id, logfile, com_path)

    ##############################
    ### Average stiched brains ###
    ##############################
    printlog(f"\n{'   MEAN BRAINS   ':=^{width}}")
    job_ids = []
    directory = moco_dir
    files = ['stitched_brain_green', 'stitched_brain_red']
    args = {'logfile': logfile, 'directory': directory, 'files': files}
    script = '5_make_mean_brain.py'
    job_id = brainsss.sbatch(jobname='meanbrn',
                         script=os.path.join(scripts_path, script),
                         modules=modules,
                         args=args,
                         logfile=logfile, time=1, mem=4, nice=nice, nodes=nodes)
    job_ids.append(job_id)

    for job_id in job_ids:
        brainsss.wait_for_job(job_id, logfile, com_path)

############
### Done ###
############

time.sleep(30) # to allow any final printing
day_now = datetime.datetime.now().strftime("%B %d, %Y")
time_now = datetime.datetime.now().strftime("%I:%M:%S %p")
printlog("="*width)
printlog(F"{day_now+' | '+time_now:^{width}}")