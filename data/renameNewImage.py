import sys

import fnmatch
import os
import re
from shutil import copyfile

image_similar_dir = os.path.abspath('../data/face_image_new/')

image_new_dir = os.path.abspath('../data/face_image/')
similar_image_paths = []
for file in os.listdir(image_similar_dir):
    if fnmatch.fnmatch(file, '*.jpg'):
        similar_image_paths.append(image_similar_dir +'/'+ file)

for imagePath in similar_image_paths:
    imageName = imagePath.split('/')[-1][:-4]

    find = re.findall(r'\d+',imageName)

    if len(find) == 0:
        #os.remove(imagePath)
        print imagePath
    else:
        copyfile(imagePath, image_new_dir+find[0]+'.jpg')

