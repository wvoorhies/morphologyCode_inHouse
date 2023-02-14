


# import required library
import torch
import torchvision
from torchvision.io import read_image
from torchvision.utils import make_grid
from torchvision.utils import save_image
import os

## read in all images in a directory
data_dir = '../figures/supp_f1/'

files = os.listdir(data_dir)
# sort all files alphabetically
files.sort()

# load into list
filenames = [name for name in files if os.path.splitext(name)[-1] == '.png']

## create an empty batch to laod files into

# ARGS: 
# batch_size = number of files 
# color = 3 (RGB) can change if you want black and white or other color settings
# width and height will change with images content.
	#This can be calculated or if its incorrect the error output will suggest the correct

batch_size = len(filenames)
batch = torch.zeros(batch_size, 3, 1294, 2464, dtype=torch.uint8)


# ## read in all images
for i, filename in enumerate(filenames):
 	batch[i] = torchvision.io.read_image(os.path.join(data_dir, filename))

#print(batch)

## make a grid
# set your number of columns, rows (nrow), and any space between images. 
Grid = make_grid(batch, nrow=4, padding=1)
  
## display result
img = torchvision.transforms.ToPILImage()(Grid)

## save image
img.save("../figures/supp_f1/supp1.png","PNG")
print('done')