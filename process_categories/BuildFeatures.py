import numpy as np
import pandas as pd
import csv
import os

image_path = '../bin/jpgs/categories/'
npy_path = '../bin/npys/categories/'
caffe_classify_path = '../../caffe/python/classify.py'

stream = os.popen('ls '+image_path)
cat_folders = stream.read().split()

for category in cat_folders:
	stream = os.popen('ls '+image_path+category+'/')
	label_folders = stream.read().split()

	stream = os.popen('ls '+npy_path+category+'/')
	curr_npys = stream.read().split()
	
	for folder in label_folders:
		if folder+'.npy' not in curr_npys:
			os.system(' '.join(['python ', 
					    caffe_classify_path, 
					    '--gpu', 
		                            image_path+category+'/'+folder, 
		                            npy_path+category+'/'+folder]))
