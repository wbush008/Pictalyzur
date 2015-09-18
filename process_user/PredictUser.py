import numpy as np
import pandas as pd
import csv
import os
import glob
import json
import argparse
import cPickle as pickle



def keywithmaxval(d):
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]


def add_user(username):

	image_path = '/home/will/code/Instagramalyze/bin/jpgs/users/'
	web_image_path = '/home/will/code/Instagramalyze/website/static/user_images/'
	npy_path = '/home/will/code/Instagramalyze/bin/npys/users/'
	caffe_classify_path = '/home/will/code/caffe/python/classify.py'

	stream = os.popen('ls '+image_path)
	user_folders = stream.read().split()

	stream = os.popen('ls '+npy_path)
	user_npys = stream.read().split()

	if username not in user_folders:
		os.system(' '.join(['python /home/will/code/Instagramalyze/process_user/ScrapeUser.py', username]))

		os.system(' '.join(['cp -r', image_path+username, web_image_path+username]))


	if username+'.npy' not in user_npys:
		os.system(' '.join(['python ', 
				    caffe_classify_path, 
				    '--gpu', 
                    image_path+username, 
                    npy_path+username]))


def predict_user(username):
	image_path = '/home/will/code/Instagramalyze/bin/jpgs/users/'
	npy_path = '/home/will/code/Instagramalyze/bin/npys/users/'
	classifier_path = '/home/will/code/Instagramalyze/classifiers/'

	if os.path.exists('/home/will/code/Instagramalyze/bin/stats/all_users.pkl'):
		with open('/home/will/code/Instagramalyze/bin/stats/all_users.pkl') as m_un:
			all_users = pickle.load(m_un)    	
	else:
		all_users = set()


	if username not in all_users:
		with open(classifier_path+'mod_logit.pkl') as m_un:
		    mod_logit = pickle.load(m_un)

		with open(classifier_path+'labels_logit.csv', 'r') as myfile:
		    csv_reader = csv.reader(myfile)
		    categories = list(csv_reader)[0]

		predictions = mod_logit.predict(np.load(npy_path+username+'.npy'))
		
		confidence = mod_logit.predict_proba(np.load(npy_path+username+'.npy')).max(axis=1)

		preds_c = [categories[int(pred)] for pred in predictions]
		category_counts = dict([(cat, preds_c.count(cat)) for cat in categories]) 
		
		image_lst = sorted([im_f for im_f in glob.glob(''.join([image_path, 
																username,'/*.jpg']))])
		
		top_count = keywithmaxval(category_counts)


		user_dict = {}
		user_stats = {}
		
		user_stats['predictions'] = preds_c
		user_stats['confidence'] = confidence.tolist()
		user_stats['category_counts'] = category_counts
		user_stats['image_lst'] = image_lst
		user_stats['top_count'] = top_count
		user_dict[username] = user_stats



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
			print 'hello?'
			all_users.add(username)

			with  open('/home/will/code/Instagramalyze/bin/stats/all_users.pkl', 'w') as f:
				pickle.dump(all_users, f)



if __name__ == '__main__':
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument('username')
	add_user(parser.parse_args().username) 
	predict_user(parser.parse_args().username)
