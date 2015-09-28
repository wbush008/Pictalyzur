import numpy as np
import csv
import os
import glob
import json
import argparse
import cPickle as pickle

caffe_classify_path = '/home/will/code/caffe/python/classify.py'
image_path = '../bin/jpgs/users/'
web_image_path = '../website/static/user_images/'
npy_path = '../bin/npys/users/'
stats_path = '../bin/stats/'
category_path = '../bin/jpgs/categories/'
classifier_path = '../model_data/'


def keywithmaxval(d):
    '''
    input: dictionary
    return: key with the maximum value

    Remove item if key == 'other'.
    '''

    r = dict(d)
    if 'other' in r:
        del r['other']
    v = list(r.values())
    k = list(r.keys())

    return k[v.index(max(v))]


def add_user(username):
    '''
    input: string
    return: None

    Check to see if there is any information already available for the
    user.  If not, scrapes the users images, then sends the images through
    the caffe network and save the resulting set of .npy arrays.
    '''

    # create list of stored user photos
    user_folders = os.listdir(image_path)

    # create list of stored user .npys
    user_npys = os.listdir(npy_path)

    # If we don't have photos, get 'em
    if username not in user_folders:
        os.system(' '.join(['python ../model_code/ScrapeUser.py', username]))
        os.system(' '.join(['cp -r', image_path + username, web_image_path + username]))

    # if we don't have .npys, make 'em
    if username + '.npy' not in user_npys:
        os.system(' '.join(['python ',
                            caffe_classify_path,
                            '--gpu',
                            image_path + username,
                            npy_path + username]))


def unpickle_model(label):
    # unpickle model parts
    with open(classifier_path + label + '_svd.pkl') as fl:
        mod_svd = pickle.load(fl)

    with open(classifier_path + label + '_logit.pkl') as fl:
        mod_logit = pickle.load(fl)

    with open(classifier_path + label + '_labels.csv', 'r') as fl:
        csv_reader = csv.reader(fl)
        categories = list(csv_reader)[0]

    return mod_svd, mod_logit, categories


def run_classifier(label, X):
    '''
    input: string, npy
    return: dict

    Takes a classifier name and an array of image features.
    Returns a dict with the predictions for each image based
    on the specified classifier.
    '''

    # unpickle model parts
    mod_svd, mod_logit, categories = unpickle_model(label)

    # reduce features with SVD
    X_s = mod_svd.transform(X)

    # make predictions with logit
    predictions = mod_logit.predict(X_s)

    # format predictions
    confidence = mod_logit.predict_proba(X_s).max(axis=1)
    preds_c = [categories[int(pred)] for pred in predictions]
    category_counts = dict([(cat, preds_c.count(cat)) for cat in categories])
    top_count = keywithmaxval(category_counts)

    # record predictions in a dict
    label_stats = {}
    label_stats[label + '_predictions'] = preds_c
    label_stats[label + '_confidence'] = confidence.tolist()
    label_stats[label + '_category_counts'] = category_counts
    label_stats[label + '_top_count'] = top_count

    return label_stats


def save_user_stats(username, user_dict, all_users):
    '''
    input: string, dict, dict
    return: None

    Combines a new users stats with the dict of all users stats,
    and saves the result as a json.
    '''
    if os.path.exists(stats_path + 'user_stats.json'):
        with open(stats_path + 'user_stats.json', 'r') as fr:
            old_user_dict = json.load(fr)

        with open(stats_path + 'user_stats.json', 'wb') as fw:
            old_user_dict.update(user_dict)
            json.dump(old_user_dict, fw)

    else:
        with open(stats_path + 'user_stats.json', 'w') as fw:
            json.dump(user_dict, fw)

    # re-pickle updated user data
    all_users.add(username)
    with open(stats_path + 'all_users.pkl', 'w') as fw:
        pickle.dump(all_users, fw)


def predict_user(username):
    '''
    input: username
    return: None

    Takes a username, makes predictions of image categories, and saves the
    predictions to a dictionary with other users.
    '''

    # Scrape user images
    add_user(username)

    # Open the stored user data
    if os.path.exists(stats_path + 'all_users.pkl'):
        with open(stats_path + 'all_users.pkl') as fl:
            all_users = pickle.load(fl)
    else:
        all_users = set()

    # exit if we already have this users predictions
    if username in all_users:
        return

    # load .npy outputs from caffe
    X = np.load(npy_path + username + '.npy')

    # make a list of classifiers to run
    label_folders = os.listdir(category_path)

    # save list of images in the order they are classified
    image_lst = sorted([im_f for im_f in glob.glob(''.join([image_path, username, '/*.jpg']))])

    # run each of the classifiers we have trained
    user_stats = {}
    user_stats['image_lst'] = image_lst

    for label in label_folders:
        user_stats.update(run_classifier(label, X))

    # record stats as a dict with username as key
    user_dict = {}
    user_dict[username] = user_stats

    # Add the new user to the dict of all saved predictions
    save_user_stats(username, user_dict, all_users)


if __name__ == '__main__':
    """
    Usage: python PredictUser.py <username>
    """
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('username')

    predict_user(parser.parse_args().username)
