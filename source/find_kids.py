# -*- coding:utf-8 -*-

import sys

sys.path.append('../facepy/feature_extraction/')

from image import extract_features
import fnmatch
import os
import numpy as np

from sklearn.neighbors import LSHForest

image_similar_dir = os.path.abspath('../data/kids_imgs_large/')

similar_image_paths = []
for file in os.listdir(image_similar_dir):
    if fnmatch.fnmatch(file, '*.jpg'):
        similar_image_paths.append(image_similar_dir +'/'+ file)


similar_image_paths.sort()

"""
for image in similar_image_paths:
    a = open(image,'rb')
    b = a.read()
    if b[:2] !="\xff\xd8" or b[-2:] != "\xff\xd9":
        a.close()
        os.remove(image)
        print "remove image: "+ image
    else:
        a.close()
"""
# extract features
#similar_image_features = extract_features(similar_image_paths)
#np.save('../data/model/kids_image_large.pickle',similar_image_features)

# load features

similar_image_features = np.load('../data/model/kids_image_large.pickle.npy')

lshf = LSHForest(random_state=42)
lshf.fit(similar_image_features)
def find_lost_kids(image_path):
    image_feature = extract_features([image_path])
    distances, indices = lshf.kneighbors(image_feature, n_neighbors=3)
    return [similar_image_paths[i] for i in indices[0]][1:]


if __name__ == '__main__':
    
    image_path = image_similar_dir + '/s_184172.jpg'
    similar_images = find_lost_kids(image_path)

    for image in similar_images:
        print image
    
