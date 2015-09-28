'''
Find new image folders, fun the images through the ANN,
return .npy arrays where columns are the 4096 output
features of layer 6 of the ANN, and rows are individual images.

Every folder in categories will be a classifier (e.g. activity,
scene, composition).
Every folder in these classifiers is a level of the classifier
(e.g. hiking, fitness, pets).

'''

import os

image_path = '../bin/jpgs/categories/'
npy_path = '../bin/npys/categories/'
caffe_classify_path = '../../caffe/python/classify.py'


def update_feature_files(category):

    # List the levels of the classifier
    label_folders = os.listdir(os.path.join(image_path, category))

    # List the .npy files that already exist
    curr_npys = os.listdir(os.path.join(npy_path, category))

    # If the folder has not been run through the ANN, run it
    # through and record the features.
    for folder in label_folders:
        if folder + '.npy' not in curr_npys:
            os.system(' '.join(['python ',
                                caffe_classify_path,
                                '--gpu',
                                image_path + category + '/' + folder,
                                npy_path + category + '/' + folder]))


def update_classifier_files():

    # List the folders that are classifier areas
    cat_folders = os.listdir(image_path)

    # Iterate through classifiers and process new folders
    for category in cat_folders:
        update_feature_files(category)


if __name__ == '__main__':
    """
    Usage: python BuildFeatures.py
    """

    update_classifier_files()
