

### An in-house function to save an array in python to a freesurfer label file ###

def array_to_label(subjects_dir, sub, hemi, label_array, label_name):
'''
saves an array to a label file formatted for freesurfer. 
INPUT: 
	- subjects_dir: freesurfer subjects_dir
	- sub: freesurfer subject
	- hemi = hemisphere (lh/rh)
	- label_array = array of values for new label
	- label_name = label to create (will have _new appended to label name by default)
OUTPUT: 
	- a freesurfer label in subjects label dir with "_new" appended 
'''
	## a new label file in the fs directory ##
	label_path = subjects_dir + '/{}/label/{}.{}_new.label'.format(sub,hemi,label_name)
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
