import os
from PIL import Image
    
wnid = 'n03082979'
image_dir = './downloaded_images/{}/{}_urlimages'.format(wnid, wnid)

for filename in os.listdir(image_dir):
  # if filename.endswith('.png'):
	try:
		filepath = os.path.join(image_dir, filename)
		img = Image.open(filepath) # open the image file
		img.verify() # verify that it is, in fact an image
	except (IOError, SyntaxError) as e:
		print('Bad file, removing: {}'.format(filename)) # print out the names of corrupt files
		os.remove(filepath)