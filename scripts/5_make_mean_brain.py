import os
import sys
import json
from time import sleep
import datetime
import brainsss
import numpy as np
import nibabel as nib
import h5py
import pathlib

def main(args):

    standalone = True  # I'll add if statements to be able to go back to Bella's script easliy
    # args = {'logfile': logfile, 'directory': directory, 'files': files}

    if standalone:
        #new logfile
        import time
        width = 120  # width of print log
        logfile = './logs/' + time.strftime("%Y%m%d-%H%M%S") + '.txt'
        printlog = getattr(brainsss.Printlog(logfile=logfile), 'print_to_log')
        sys.stderr = brainsss.Logger_stderr_sherlock(logfile)
        brainsss.print_title(logfile, width)

        # get path!
        scripts_path = args['PWD']
        com_path = os.path.join(scripts_path, 'com')
        user = scripts_path.split('/')[3]
        settings = brainsss.load_user_settings(user, scripts_path)

        ### Parse user settings
        imports_path = settings['imports_path']
        dataset_path = settings['dataset_path']

        directory = '/oak/stanford/groups/trc/data/David/Bruker/preprocessed/fly_001/func1/imaging'

        files = []
        for current_file in pathlib.Path(directory).iterdir():
            if 'anatomy_channel' in current_file.name or 'functional_channel' in current_file.name:
                files.append(current_file.name)

        """
        # Copy from preprocess.py
        for funcanat, dirtype in zip(funcanats, dirtypes):
            directory = os.path.join(funcanat, 'imaging')

            if dirtype == 'func':
                files = ['functional_channel_1.nii', 'functional_channel_2.nii']
            if dirtype == 'anat':
                files = ['anatomy_channel_1.nii', 'anatomy_channel_2.nii']
            """
    else:
        logfile = args['logfile']
        directory = args['directory'] # directory will be a full path to either an anat/imaging folder or a func/imaging folder
        files = args['files']


    meanbrain_n_frames = args.get('meanbrain_n_frames', None)  # First n frames to average over when computing mean/fixed brain | Default None (average over all frames)
    width = 120
    printlog = getattr(brainsss.Printlog(logfile=logfile), 'print_to_log')

    # Check if files is just a single file path string
    if type(files) is str:
        files = [files]

    for file in files:
        try:
            ### make mean ###
            full_path = os.path.join(directory, file)
            if full_path.endswith('.nii'):
                brain = np.asarray(nib.load(full_path).get_fdata(), dtype='uint16')
            elif full_path.endswith('.h5'):
                with h5py.File(full_path, 'r') as hf:
                    brain = np.asarray(hf['data'][:], dtype='uint16')

            if meanbrain_n_frames is not None:
                # average over first meanbrain_n_frames frames
                meanbrain = np.mean(brain[...,:int(meanbrain_n_frames)], axis=-1)
            else: # average over all frames
                meanbrain = np.mean(brain, axis=-1)

            ### Save ###
            save_file = os.path.join(directory, file[:-4] + '_mean.nii')
            aff = np.eye(4)
            img = nib.Nifti1Image(meanbrain, aff)
            img.to_filename(save_file)

            fly_func_str = ('|').join(directory.split('/')[-3:-1])
            fly_print = directory.split('/')[-3]
            func_print = directory.split('/')[-2]
            #printlog(f"COMPLETE | {fly_func_str} | {file} | {brain.shape} --> {meanbrain.shape}")
            printlog(F"meanbrn | COMPLETED | {fly_print} | {func_print} | {file} | {brain.shape} ===> {meanbrain.shape}")
            if not standalone:
                print(brain.shape[-1]) ### IMPORTANT: for communication to main
            brain = None
        except FileNotFoundError:
            printlog(F"Not found (skipping){file:.>{width-20}}")
            #printlog(f'{file} not found.')

if __name__ == '__main__':
    main(json.loads(sys.argv[1]))