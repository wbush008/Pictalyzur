import numpy as np
import csv
import os
import glob
import json
import argparse
import cPickle as pickle


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
	input: username
	return: None

	Check to see if there is any information already available for the
	user.  if not, scrapes the users images, then sends the images through
	the caffe network resulting in a set of .npy arrays for the user.
	'''

    image_path = '/home/will/code/Instagramalyze/bin/jpgs/users/'
    web_image_path = '/home/will/code/Instagramalyze/website/static/user_images/'
    npy_path = '/home/will/code/Instagramalyze/bin/npys/users/'
    caffe_classify_path = '/home/will/code/caffe/python/classify.py'

    # create list of stored user photos
    stream = os.popen('ls ' + image_path)
    user_folders = stream.read().split()

    # create list of stored user .npys
    stream = os.popen('ls ' + npy_path)
    user_npys = stream.read().split()

    # If we don't have photos, get 'em
    if username not in user_folders:
        os.system(' '.join(
            ['python /home/will/code/Instagramalyze/process_user/ScrapeUser.py', username]))

        os.system(
            ' '.join(['cp -r', image_path + username, web_image_path + username]))

    # if we don't have .npys, make 'em
    if username + '.npy' not in user_npys:
        os.system(' '.join(['python ',
                            caffe_classify_path,
                            '--gpu',
                            image_path + username,
                            npy_path + username]))


def predict_user(username):
	'''
	input: username
	return: None

	Takes a username, makes predictions of image categories, and saves the
	predictions to a dictionary with other users. 
	'''
    image_path = '/home/will/code/Instagramalyze/bin/jpgs/users/'
    npy_path = '/home/will/code/Instagramalyze/bin/npys/users/'
    classifier_path = '/home/will/code/Instagramalyze/classifiers/'

    # Open the stored user data
    if os.path.exists('/home/will/code/Instagramalyze/bin/stats/all_users.pkl'):
        with open('/home/will/code/Instagramalyze/bin/stats/all_users.pkl') as m_un:
            all_users = pickle.load(m_un)
    else:
        all_users = set()


    if username not in all_users:
    	# load .npy outputs from caffe
        X = np.load(npy_path + username + '.npy')

        # make a list of classifiers to run
        stream = os.popen('ls /home/will/code/Instagramalyze/bin/jpgs/categories/')
        label_folders = stream.read().split()

        # dicts to store classifier output
        user_dict = {}
        user_stats = {}

        # save list of images in the order they are classified
        image_lst = sorted([im_f for im_f in glob.glob(''.join([image_path,
                                                                username, '/*.jpg']))])

        user_stats['image_lst'] = image_lst

        # run each of the classifiers we have trained
        for label in label_folders:
        	# unpickle model parts
            with open(classifier_path + label + '_svd.pkl') as m_un:
                mod_svd = pickle.load(m_un)

            with open(classifier_path + label + '_logit.pkl') as m_un:
                mod_logit = pickle.load(m_un)

            with open(classifier_path + label + '_labels.csv', 'r') as myfile:
                csv_reader = csv.reader(myfile)
                categories = list(csv_reader)[0]

            X_s = mod_svd.transform(X)

            # make predictions
            predictions = mod_logit.predict(X_s)
            confidence = mod_logit.predict_proba(X_s).max(axis=1)

            preds_c = [categories[int(pred)] for pred in predictions]
            category_counts = dict(
                [(cat, preds_c.count(cat)) for cat in categories])

            top_count = keywithmaxval(category_counts)

            # save predictions
            user_stats[label + '_predictions'] = preds_c
            user_stats[label + '_confidence'] = confidence.tolist()
            user_stats[label + '_category_counts'] = category_counts
            user_stats[label + '_top_count'] = top_count

        # save all stats as a dict with username as key
        user_dict[username] = user_stats

        # Add the new user to all the saved predictions
        if username not in all_users:
            if os.path.exists('/home/will/code/Instagramalyze/bin/stats/user_stats.json'):
                with open('/home/will/code/Instagramalyze/bin/stats/user_stats.json', 'r') as myfile:
                    old_user_dict = json.load(myfile)

                with open('/home/will/code/Instagramalyze/bin/stats/user_stats.json', 'wb') as myfile:
                    old_user_dict.update(user_dict)
                    json.dump(old_user_dict, myfile)

                print old_user_dict
            else:
                with open('/home/will/code/Instagramalyze/bin/stats/user_stats.json', 'w') as myfile:
                    json.dump(user_dict, myfile)
            all_users.add(username)

            # re-pickle updated user data
            with open('/home/will/code/Instagramalyze/bin/stats/all_users.pkl', 'w') as f:
                pickle.dump(all_users, f)

if __name__ == '__main__':
	"""
    Usage: python PredictUser.py <username>
    """
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('username')
    add_user(parser.parse_args().username)
    predict_user(parser.parse_args().username)
