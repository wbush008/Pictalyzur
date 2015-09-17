from sklearn.linear_model import LogisticRegression
import numpy as np
import cPickle as pickle
import pandas as pd
from sklearn.decomposition import TruncatedSVD
import csv

# Model variables
n_features = 175

# read in a list of .npy file to use to build the model
np_path = '../bin/npys/categories/'
np_lst = pd.read_csv('np_lst.txt', header=None)[0].values

# load the .npy files from the list.
feat_array = []
categories = []

for i, feats in enumerate(np_lst):
    if '_a' in feats:
        feat_array.append(np.load(np_path+feats))
        categories.append(feats[:-6])
    else:
        feat_array[-1] = np.vstack([feat_array[-1], np.load(np_path+feats)])

X = np.vstack(feat_array)

# Create a list of labels based on the .npy files
label_lst = []
for i, feats in enumerate(feat_array):
    label_lst.append(i*np.ones(len(feats)))

y = np.hstack(label_lst)

# Feature reduction
X_svd = TruncatedSVD(n_components=n_features)
X_red = X_svd.fit_transform(X)

# Train logistic regression
mod_logit = LogisticRegression()
mod_logit.fit(X_red, y)

# Pickle the model
with  open("mod_logit.pkl", 'w') as f:
    pickle.dump(mod_logit, f)

# Write the category labels to a .csv
with open('labels_logit.csv', 'wb') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(categories)