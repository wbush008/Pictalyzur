import os

'''
Find new image folders, fun the images through the ANN,
return .npy arrays where columns are the 4096 output
features of layer 6 of the ANN, and rows are individual images.

Every folder in categories will be a classifier (e.g. activity,
scene, composition).
Every folder in these classifiers is a level of the classifier
(e.g. hiking, fitness, pets).

'''


image_path = '../bin/jpgs/categories/'
npy_path = '../bin/npys/categories/'
caffe_classify_path = '../../caffe/python/classify.py'


# List the folders that are our classifier areas
stream = os.popen('ls ' + image_path)
cat_folders = stream.read().split()

# Iterate through classifier
for category in cat_folders:

    # List the levels of the classifier
    stream = os.popen('ls ' + image_path + category + '/')
    label_folders = stream.read().split()

    # List the .npy files that already exist
    stream = os.popen('ls ' + npy_path + category + '/')
    curr_npys = stream.read().split()

    # If the folder has not been run through the ANN, run it
    # through and record the features.
    for folder in label_folders:
        if folder + '.npy' not in curr_npys:
            os.system(' '.join(['python ',
                caffe_classify_path,
                '--gpu',
                image_path + category + '/' + folder,
                npy_path + category + '/' + folder]))
