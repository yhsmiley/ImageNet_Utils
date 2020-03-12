import os
from PIL import Image

wnid_path = '/home/yinghui/Projects/AICCC/od_testing_images/n12597798_thatch_palm'

wnid_class = wnid_path.split('/')[-1]
wnid = wnid_class.split('_')[0]

for dirs in os.listdir(wnid_path):
	if dirs.startswith(wnid) and dirs.endswith('images'):
			img_dir = dirs

img_path = os.path.join(wnid_path, img_dir)
anno_path = os.path.join(wnid_path, 'Annotation')

image_filenames = []
for root, dirs, files in os.walk(img_path):
	for file in files:
		image_filenames.append(file.split('.JPEG')[0])

anno_filenames = []
for root, dirs, files in os.walk(anno_path):
	for file in files:
		anno_filename = file.split('.xml')[0]
		anno_filenames.append(anno_filename)

## save in folder if annotation not found (to be annotated)
for root, dirs, files in os.walk(img_path):
	for file in files:
		image_filename = file.split('.JPEG')[0]

		if image_filename not in anno_filenames:
			curr_dir = os.getcwd()
			img = Image.open(os.path.join(img_path, file))
			class_dir = os.path.join(curr_dir, 'to_be_annotated', wnid_class)
			if not os.path.exists(class_dir):
				os.makedirs(class_dir)
				print("made dir")
			save_path = os.path.join(class_dir, file)
			img.save(save_path)
			print("{} saved".format(file))