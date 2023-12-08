import numpy as np
import sys
import os
import json
import matplotlib.pyplot as plt
from skimage.filters import threshold_triangle
import psutil
import brainsss
import nibabel as nib

def main(args):
    # args = {'logfile': logfile, 'directory': directory, 'dirtype': dirtype}

    standalone = True  # I'll add if statements to be able to go back to Bella's script easliy

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

        dirtype = 'func' # 'func' or 'anat'

    if args['FLIES'] == '':
        #printlog('no flies specified')
        fly_dirs = None
    else:
        fly_dirs = args['FLIES'].split(',')

    funcs = []
    anats = []
    print(fly_dirs)
    for fly_dir in fly_dirs:
        fly_directory = os.path.join(dataset_path, fly_dir)
        if dirtype == 'func' or dirtype == None:
            funcs.extend([os.path.join(fly_directory, x) for x in os.listdir(fly_directory) if 'func' in x])
        if dirtype == 'anat' or dirtype == None:
            anats.extend([os.path.join(fly_directory, x) for x in os.listdir(fly_directory) if 'anat' in x])

    brainsss.sort_nicely(funcs)
    brainsss.sort_nicely(anats)
    funcanats = funcs + anats # ? what's that thing doing here?
    dirtypes = ['func']*len(funcs) + ['anat']*len(anats)

    #logfile = args['logfile']
    if standalone:
        directory = '/Volumes/groups/trc/data/David/Bruker/preprocessed/fly_001/func1/imaging'
    else:
        directory = args['directory'] # directory will be a full path to either an anat/imaging folder or a func/imaging folder
    #dirtype = args['dirtype']
    width = 120
    printlog = getattr(brainsss.Printlog(logfile=logfile), 'print_to_log')

    #################
    ### Load Data ###
    #################

    if dirtype == 'func':
        files = ['functional_channel_1', 'functional_channel_2']
    elif dirtype == 'anat':
        files = ['anatomy_channel_1', 'anatomy_channel_2']
    data_mean = {}
    for file in files:
        full_file = os.path.join(directory, file + '.nii')
        if os.path.exists(full_file):
            brain = np.asarray(nib.load(full_file).get_fdata(), dtype='uint16')
            data_mean[file] = np.mean(brain,axis=(0,1,2))
        else:
            printlog(F"Not found (skipping){file:.>{width-20}}")

    ##############################
    ### Output Bleaching Curve ###
    ##############################

    plt.rcParams.update({'font.size': 24})
    fig = plt.figure(figsize=(10,10))
    signal_loss = {}
    for file in data_mean:
        xs = np.arange(len(data_mean[file]))
        color='k'
        if file[-1] == '1': color='red'
        if file[-1] == '2': color='green'
        plt.plot(data_mean[file],color=color,label=file)
        linear_fit = np.polyfit(xs, data_mean[file], 1)
        plt.plot(np.poly1d(linear_fit)(xs),color='k',linewidth=3,linestyle='--')
        signal_loss[file] = linear_fit[0]*len(data_mean[file])/linear_fit[1]*-100
    plt.xlabel('Frame Num')
    plt.ylabel('Avg signal')
    loss_string = ''
    for file in data_mean:
        loss_string = loss_string + file + ' lost' + F'{int(signal_loss[file])}' +'%\n'
    plt.title(loss_string, ha='center', va='bottom')
    # plt.text(0.5,0.9,
    #          loss_string,
    #          horizontalalignment='center',
    #          verticalalignment='center',
    #          transform=plt.gca().transAxes)

    save_file = os.path.join(directory, 'bleaching.png')
    plt.savefig(save_file,dpi=300,bbox_inches='tight')

#if __name__ == '__main__':
#    main(json.loads(sys.argv[1]))