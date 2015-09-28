from sklearn.linear_model import LogisticRegression
import numpy as np
import cPickle as pickle
from sklearn.decomposition import TruncatedSVD
import csv
import os

np_path = '../bin/npys/categories/'

# Model variables
n_features = 150


def load_npys(label_folders, category):
    feat_array = []
    categories = []
    for i, feats in enumerate(label_folders):

        if '_a' in feats:
            feat_array.append(np.load(np_path + category + '/' + feats))
            categories.append(feats[:-6])
        else:
            feat_array[-1] = np.vstack([feat_array[-1],
                                        np.load(np_path + category + '/' + feats)])

    return feat_array, categories


def create_labels(feat_array):
    label_lst = []
    for i, feats in enumerate(feat_array):
        label_lst.append(i * np.ones(len(feats)))

    return label_lst


def train_model(X, y):
    # feature reduction with SVD
    X_svd = TruncatedSVD(n_components=n_features)
    X_red = X_svd.fit_transform(X)

    # train logistic regression
    mod_logit = LogisticRegression()
    mod_logit.fit(X_red, y)

    return X_svd, mod_logit


def pickle_model(category, X_svd, mod_logit, categories):
    with open(category + '_logit.pkl', 'w') as f:
        pickle.dump(mod_logit, f)

    with open(category + '_svd.pkl', 'w') as f:
        pickle.dump(X_svd, f)

    # write the category labels to a .csv
    with open(category + '_labels.csv', 'wb') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow(categories)


def build_model():
    # read in a list of .npy files to use to build the models
    cat_folders = os.listdir(np_path)

    for category in cat_folders:
        # create list of categories in a classifier
        label_folders = os.listdir(os.path.join(np_path, category))

        # load the .npy files from the list.
        feat_array, categories = load_npys(label_folders, category)

        # create a list of labels based on the .npy files
        label_lst = create_labels(feat_array)

        # concatenate data and labels
        X = np.vstack(feat_array)
        y = np.hstack(label_lst)

        # train the models
        X_svd, mod_logit = train_model(X, y)

        # pickle the model
        pickle_model(category, X_svd, mod_logit, categories)


if __name__ == '__main__':
    """
    Usage: python BuildFeatures.py
    """

    build_model()
