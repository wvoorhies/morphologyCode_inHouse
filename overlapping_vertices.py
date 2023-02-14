'''
Remove overlapping vertices from two freesurfer labels


This script identifies shared vertices between two freesurfer labels (label_A and label_B). 
It removes the shared vertices from label_A and saves a new version of label_A to the fs directory without label_B's vertices

Output: A new freesurfer label with overlapping vertices removed. See functions below for specifics. 
Note: if you attempt to remove a large number of vertices from label A the system will prompt you for explicit permission.
In this case it is strongly recommended that you visually inspect the labels in freesurfer before proceeding.  


REQUIREMENTS: 
1. A freesurfer directory for each subject (run recon-all)
2. A list of subjects
3.  Labels  of interest in the format:
		.../<subject>/<label>/<hemi>.<sulcus>.label.
		eg. .../sub_1/label/rh.MFS.label. 
4. nibable and nilearn must be installed and operational


TO CALL: 
To call this script from the command line: 

python overlapping_vertices.py '<subject_dir>' <sub_list.txt> '<label_A>' '<label_B>'
	
	- subjects dir = path to freesurfer subjects directory
	- sub list = path to subjects list text file
	- label_A: label with vertices overlapping to remove
	- label_B = label with overlapping vertices.  
'''
############################################################################################################################
#### import packages ####

import numpy as np
import nibabel as nib

from nilearn import image, plotting, surface

import os 
import itertools
import sys
import pandas as pd

#### load data from command line input ####

# set freesurfer directory
SUBJECTS_DIR = sys.argv[1]

# read in subs list
file = open(sys.argv[2], 'r')
subs = file.read().splitlines()
file.close

# define hemispheres 
hemis = ['lh', 'rh']

# labels
label_A = sys.argv[3]

label_B = sys.argv[4]

# combine hemis and subjects
sub_hemi_combos = list(itertools.product(subs, hemis))



## read label in freesurfer format and returns vertices and RAS coordinates ##
def read_label(label_name):
    """
    Reads a freesurfer-style .label file (5 columns)
    Parameters
    ----------
    label_name: str
    Returns
    -------
    vertices: index of the vertex in the label np.array [n_vertices]
    RAS_coords: columns are the X,Y,Z RAS coords associated with vertex number in the label, np.array [n_vertices, 3]
    """

    # read label file, excluding first two lines of descriptor
    df_label = pd.read_csv(label_name,skiprows=[0,1],header=None,names=['vertex','x_ras','y_ras','z_ras','stat'],delimiter='\s+')

    vertices = np.array(df_label.vertex)
    RAS_coords = np.empty(shape = (vertices.shape[0], 3))
    RAS_coords[:,0] = df_label.x_ras
    RAS_coords[:,1] = df_label.y_ras
    RAS_coords[:,2] = df_label.z_ras

    return vertices, RAS_coords



#### find overlapping vertices and remove shared vertices ####
    
def rm_overlapping_vertices(SUBJECTS_DIR,sub, hemi, label_A, label_B):

    # Identifies overlapping vertices and removes labe_B vertices from label_A
    # returns: an array of values for the new label_A vertices

    # load surface data for label A 
    label_A_filename = SUBJECTS_DIR + '/{}/label/{}.{}.label'.format(sub,hemi,label_A)
    label_A_data = surface.load_surf_data(label_A_filename)
    #check to see how many vertices you are starting out with; later check new vertice number
    print(label_A_data.shape)
    
    # load surface data for label B 
    label_B_filename = SUBJECTS_DIR + '/{}/label/{}.{}.label'.format(sub,hemi, label_B)
    label_B_data = surface.load_surf_data(label_B_filename)
           
    # find overlapping vertices 
    values, B_ind, A_ind = np.intersect1d(label_B_data, label_A_data, return_indices=True)

    ## remove intersecting vertices from label A so that label B is unique. ##

    while True:
    	# if the number of vertices is small, go ahead and remove from label A.
    	# (Note: if the number of overlapping vertices are 0, then the values will logically remain unchanged)

        if len(values) < 50:       # Adjust this to redefine a "small number of vertices" for your needs

        	# remove overlapping vertices
            label_A_new = label_A_data[~np.isin(label_A_data,values)]

            # return new label A with label B vertices removed
            return(label_A_new)

        # for larger replacements require overwrite permission from user. 
        else: 
            print("WARNING: You are replacing a very large number of vertices. Are you sure you want to proceed?")
            overwrite = input("yes/no:")
            print(overwrite)

            # if user gives permission:
            if overwrite == 'yes':

            	# remove overlapping vertices from label A
                label_A_new = label_A_data[~np.isin(label_A_data,values)]

                # return new label A with label B vertices removed
                return(label_A_new)

            # if user does not give permission:
            elif overwrite =='no':

            	# Exit and return error message. 
                return "cannot overwrite vertices for {}".format(sub)

            # If invalid input is provided:
            else:
                print('invalid input')
                # ask again
                continue



##### save an array to a freesufer label ####

def array_to_label(SUBJECTS_DIR, sub, hemi, label_array, label_name):
	# saves a numpy array as values in a freesurfer label file 
	# returns: path to saved label file.
	# check to see if new label has the correct number of vertices
	print(label_array.shape[0])
    
    # creates empty space for RAS labels
	for i, new_label in enumerate(label_name):
		new_label_RAS = np.empty(shape=(0,3),dtype=int)
    
	## a new label file in the fs directory ##
	new_label_path = SUBJECTS_DIR + '/{}/label/{}.{}_new.label'.format(sub,hemi,label_name)
	## the old label file in the fs directory ##
	old_label_path = SUBJECTS_DIR + '/{}/label/{}.{}.label'.format(sub,hemi,label_name)
	## read original label file in the fs directory ##
	old_vertices, RAS = read_label(old_label_path)
    
    ##add RAS coordinates that correspond to vertices ##
	for vertex in label_array:
        # find index of vertex in label_A old_vertices
		vertexindex = np.where(old_vertices==vertex)
        # copy RAS coordinates into label_A_new
		new_label_RAS = np.append(new_label_RAS, RAS[vertexindex,:][0], axis=0)
		# print(RAS[vertexindex,:].shape)
        
	## create array to put into new label ##
	new_label_array = np.zeros(shape=(label_array.shape[0],5),dtype=float)
	new_label_array[:,0] = label_array
	new_label_array[:,1:4] = new_label_RAS
	np.savetxt(new_label_path, new_label_array, fmt='%-2d  %2.3f  %2.3f  %2.3f %1.10f')
	
	## open new label##
	f = open(label_path, 'r')
	edit_f = f.read()
	f.close()

	## edit this new new label ##
	f = open(label_path, 'w')

	# set up the freesurfer header. Below the header add the values from the array
	f.write('#ascii label  , from subject {} vox2ras=TkReg coords=white\n{}\n'.format(sub, label_array.shape[0]))
		# save your changes
	f.write(edit_f)
	f.close()
	return ("label saved as {}". format(label_path))



####  remove overlapping vertices and save out new labels  #####

# for each subject in sub list and each hemisphere: 
for sub_hemi in sub_hemi_combos:
	sub = sub_hemi[0]
	hemi = sub_hemi[-1]

	# remove label_B vertices from label A 
	new_label_A = rm_overlapping_vertices(SUBJECTS_DIR, sub,  hemi, label_A, label_B) 

	# save out label_A to freesurfer as <label_A>_new.label
	array_to_label(SUBJECTS_DIR, sub, hemi, new_label_A, label_A)
