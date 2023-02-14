
# load packages 
import os 

# produce an annotation file for each subject from an atlas file. 
def atlas2annot(subjects_dir, data_dir, colortable, input_, output_, hemi, sub):
	'''
	implements the freesurfer command mris_ca_label to produce an annotation file, 
	in which each cortical surface vertex is assigned a neuroanatomical label.
	for options and support see: https://surfer.nmr.mgh.harvard.edu/fswiki/mris_ca_label

	Requirements:
	- freesurfer subjects directory (recon-all)
	- sphere.reg surface file for each subject (should be created by recon-all)
	- colortable.txt a colortable file. can use default with atlas or create your own. 
	- an atlas in the data_dir as a .gcs file. See freesurfer wiki to create a file in this format. 

	Input:
		- subjects_dir = freesurfer subjects directory
		- data_dir = directory with anatomical atlas
		- color table = colortable.txt file. 
		- input_ = atals file (.gcs extension)
		- output_ = name of annotation file
		- hemi = hemisphere
		- sub = sub
	Output:
	saves out an annotation file in subject's label directory. 

	'''

	# set freesurfer environment
	os.environ["FREESURFER_HOME"] = '/usr/local/freesurfer_x86_64-6.0.0' # change to local freesurfer if not on the neurocluster

	# set freesurfer subjects dir
   
	os.environ['SUBJECTS_DIR'] = subjects_dir

					
	# Formation of annotation files from command line		
	!mris_ca_label -t ${colortable} ${sub} $hemi ${SUBJECTS_DIR}/${sub}/surf/${hemi}.sphere.reg ${data_dir}/${hemi}.${input_} ${SUBJECTS_DIR}/${sub}/label/${hemi}.${output_}.annot

	return ("annotation created for {}.{}"). format(hemi, sub)
