'''
                          Sulcal Depth and Morphology script -- most recent version

OUTPUT: a CSV saved to project folder with minimum/maximum sulcal depth for each sulcal label (normalized to deepest point in hemisphere)
Also includes formatted morphological stats from freesurfer command 'mris_anatomicals' (eg. cortical thickness, GM-volumen, surface area, curvature).

REQUIREMENTS: 
	1) Run the following freesurfer commands on all subjects:

		a) recon-all
		b) mris_anatomicals for all labels of interest
			output should be nested in freesurfer label directory in the following format:
			.../<subject>/<label>/label_stats/<hemi>.<label>.label.stats.txt
			eg. sub_1/label/label_stats/lh.MFS.label.stats.txt

	3) A subjects list in a .txt file. 

	4) Labels created for sulcus of interest in the format
		.../<subject>/<label>/<hemi>.<sulcus>.label.
		eg. .../sub_1/label/rh.MFS.label. 

		All labels should have output from mris_anatomicals.
		Split annotation files with annot2label command

	5) nibabel and nilearn must be installed and operational

TO CALL: 
python sulc_morphology.py '<subject_dir>' <sub_list.txt> <sulcal_list.txt> '<out_dir>'
	
	- subjects dir = path to freesurfer subjects directory (string)
	- sub list = path to subjects list text file
	- labels of interest as a comma-(and-space)-separated string: "MFS, CoS, OTS"
	- path to output directory (string)
'''
###################### Load modules and data ####################################

import numpy as np
import pandas as pd
import nilearn
from nilearn import surface
import nibabel as nib
import scipy
import os
import sys
import itertools

### Load data ###
subjects_dir = sys.argv[1]

# read in subs list
file = open(sys.argv[2], "r")
subs = file.read().splitlines()
file.close

# read in subs list
file = open(sys.argv[3], "r")
labels = file.read().splitlines()
file.close


hemis = ['lh', 'rh']


# combine subject list and hemi list
sub_hemi_combos = list(itertools.product(subs,hemis))


############# pull metrics from mris_anatomicals output ################################

def anatomicals_output (sub, hemi, label):
	''' 
	reads in output from mris_anatomicals and organizes into a df

	Parameters
	-----------
	label: str

	Returns
	-------
	outputs from mris_anatomicals as an array
	'''
    # Pull metrics from label txt file for each label for every subject and append to df. 

    # label stats directory
	label_dir = subjects_dir + '/{}/label/'.format(sub)
	labels_stats = label_dir + 'label_stats/'

    # extract cortical thickness, volume, surface area and curvature for each label
	label_filename = label_dir + '{}.{}.label'.format(hemi,label)
	label_stats_filename = labels_stats + '{}.{}.stats.txt'.format(hemi,label)
	###label_data = surface.load_surf_data(label_filename)
    # open label stats text file and pull the stats from the bottom line of the file. 
	try:
		with open(label_stats_filename) as f: 
			lastN = list(f)[-1:]
			label_stats = np.array(lastN[0].split()[:-1], dtype=float)
	except:
		label_stats = ["NA"]*9

	return label_stats

################################## compute mean/max sulcal depth from surface file #####################################################
def calc_depth(sub, hemi, label):
	''''
	computes total mean, max sulcal depth and also mean/max depth as percentage of maximum depth in hemi

	Parameters
	----------
	label: str

	Returns
	--------
	depth values as an array
	'''
	if sub == 'fsaverage':
		sulc_path = subjects_dir + '/fsaverage/surf/{}.smoothsulc'.format(hemi)
	else:
		sulc_path = subjects_dir + '/{}/surf/{}.sulc'.format(sub, hemi)
		sulc_data = surface.load_surf_data(sulc_path)

	
	# Load .sulc file for label vertices
	label_dir = subjects_dir + '/{}/label/'.format(sub)
	label_filename = label_dir + '{}.{}.label'.format(hemi,label)
	try:
		label_data = surface.load_surf_data(label_filename)

	# calculate sulcal depth by mean label value in .sulc file
		label_mean_depth = np.mean(sulc_data[label_data])
		label_max_depth = np.amax(sulc_data[label_data])

	# calculate mean sulcal depth as a percentage of max depth in subject
		sulc_data_pct_max = sulc_data/np.amax(sulc_data)
		label_mean_depth_pct_max = np.mean(sulc_data_pct_max[label_data])
	except:
		label_mean_depth = 'NA'
		label_max_depth = 'NA'
		label_mean_depth_pct_max = 'NA'
	
	return np.array([label_mean_depth, label_max_depth, label_mean_depth_pct_max])

######################## Compute and organize sulcal morphology data into a CSV ###################################### 
# set up CSV

columns =  ['sub', 'hemi', 'label', 'vertices', 'total_surface_area_(mm^2)',
                                       'total_gray_matter_volume_(mm^3)', 'cortical_thickness_mean', 
                                        'cortical_thickness_std',
                                       'rectified_mean_curvature', 'rectified_Gaussian_curvature',
                                       'folding_index', 'intrinsic_curvature_index', 'sulcal_depth_mean', 'sulcal_depth_max',
                                        'sulcal_depth_mean_pct']
df_anatomical = pd.DataFrame(columns = columns)

# Compute morphological metrics for each subject

for sub_hemi in sub_hemi_combos:
	sub = sub_hemi[0]
	hemi = sub_hemi[-1]
	for label in labels:
		anatomicals = anatomicals_output(sub, hemi, label)
		depth = calc_depth(sub, hemi, label)

	  #       	# append metrics to dataframe
		label_stats = np.append(anatomicals, depth)
		descriptives = [sub, hemi, label]
		df_row = pd.DataFrame([descriptives + list(label_stats)], columns = columns)
		df_anatomical = pd.concat([df_anatomical, df_row], axis=0)
		#except: # if label does not exist for this subject (i.e. if subject doesn't have the labeled sulcus)
			##print('whoops') #pass

# write to csv
out_dir = sys.argv[4]
df_anatomical.to_csv('/home/weiner/NH_Primates/projects/LPFC/data/morphological_metrics.csv')
