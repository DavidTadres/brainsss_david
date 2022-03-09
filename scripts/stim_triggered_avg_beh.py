import brainsss
import numpy as np
import matplotlib.pyplot as plt
import os
import json

def main(args):
	
	logfile = args['logfile']
	func_path = args['func_path']
	printlog = getattr(brainsss.Printlog(logfile=logfile), 'print_to_log')

	###########################
	### PREP VISUAL STIMULI ###
	###########################

	vision_path = os.path.join(func_path, 'visual')

	### Load Photodiode ###
	t, ft_triggers, pd1, pd2 = brainsss.load_photodiode(vision_path)

	stimulus_start_times = brainsss.extract_stim_times_from_pd(photodiode_trace, time_vector)

	### Get Metadata ###
	fname = [x for x in os.listdir(vision_path) if '.hdf5' in x][0]
	visprotocol_file = os.path.join(vision_path, fname)

	stim_ids, angles = brainsss.get_metadata_from_visprotocol(visprotocol_file, 'series_001')
	printlog(F"Found {len(stim_ids)} presented stimuli.")
	if len(stim_ids) < 100:
		printlog("fewer than expected stimuli, trying series_002")
		# this is wrong series, for now just try grabbing series 2
		stim_ids, angles = brainsss.get_metadata_from_visprotocol(visprotocol_file, 'series_002')
		printlog(F"Found {len(stim_ids)} presented stimuli.")

	# *100 puts in units of 10ms, which will match fictrac
	starts_angle_0 = [int(stimulus_start_times[i]*100) for i in range(len(stimulus_start_times)) if angles[i] == 0]
	starts_angle_180 = [int(stimulus_start_times[i]*100) for i in range(len(stimulus_start_times)) if angles[i] == 180]
	printlog(F"starts_angle_0: {len(starts_angle_0)}. starts_angle_180: {len(starts_angle_180)}")

	####################
	### PREP FICTRAC ###
	####################

	fictrac_path = os.path.join(func_path, 'fictrac')
	fictrac_raw = brainsss.load_fictrac(fictrac_path)

	fps = 100
	resolution = 10 #desired resolution in ms
	expt_len = fictrac_raw.shape[0]/fps*1000
	behaviors = ['dRotLabY', 'dRotLabZ']
	fictrac = {}
	for behavior in behaviors:
		if behavior == 'dRotLabY': short = 'Y'
		elif behavior == 'dRotLabZ': short = 'Z'
		fictrac[short] = smooth_and_interp_fictrac(fictrac_raw, fps, resolution, expt_len, behavior)
	xnew = np.arange(0,expt_len,resolution)

	##################
	### MAKE PLOTS ###
	##################
	plot_avg_trace(fictrac, starts_angle_0, starts_angle_180, vision_path)


def plot_avg_trace(fictrac, starts_angle_0, starts_angle_180, vision_path):
	pre_window = 200 # in units of 10ms
	post_window = 300

	traces = []
	for i in range(len(starts_angle_0)):
		trace = fictrac['Z'][starts_angle_0[i]-pre_window:starts_angle_0[i]+post_window]
		traces.append(trace)
	mean_trace_0 = np.mean(np.asarray(traces),axis=0)

	traces = []
	for i in range(len(starts_angle_180)):
		trace = fictrac['Z'][starts_angle_180[i]-pre_window:starts_angle_180[i]+post_window]
		traces.append(trace)
	mean_trace_180 = np.mean(np.asarray(traces),axis=0)

	plt.figure(figsize=(10,10))
	xs = np.arange(-pre_window,post_window)*10
	plt.plot(xs, mean_trace_0,color='r',linewidth=5)
	plt.plot(xs, mean_trace_180,color='cyan',linewidth=5)
	plt.axvline(0,color='grey',lw=3,linestyle='--') # stim appears
	plt.axvline(1000,color='k',lw=3,linestyle='--') # stim moves
	plt.axvline(1500,color='grey',lw=3,linestyle='--') # grey
	plt.ylim(-50,50)
	plt.xlabel('Time, ms')
	plt.ylabel('Angular Velocity')

	name = 'stim_triggered_turning.png'
	fname = os.path.join(fictrac_folder, name)
	plt.savefig(fname,dpi=100,bbox_inches='tight')

if __name__ == '__main__':
	main(json.loads(sys.argv[1]))