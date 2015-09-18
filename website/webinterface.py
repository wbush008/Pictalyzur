from collections import Counter
import cPickle as pickle
import os
import pandas as pd
import json
import matplotlib.pyplot as plt
import csv
import numpy as np
from flask import Flask, request, render_template

plt.style.use('ggplot')
app = Flask(__name__)


def dict_to_html(d):
    return '<br>'.join('{0}: {1}'.format(k, d[k]) for k in sorted(d))

# home page
@app.route('/')
def index():

    return render_template('index.html')
#     return '''
# <!DOCTYPE html>
# <html>
#   <head>
#     <title>ttci</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#   </head>
#   <body>
#     <div class="container">
#       <h1>Taking text to class...ification.</h2>
#       <br>
#       <p>Click <a href="/submit_page">submission</a> to go add some text.</p>
#     </div>
#   </body>
# </html>
# '''


# Form page to submit text
@app.route('/submit_page')
def submit_page():
    return '''
        <form action="/word_classifier" method='POST' >
            <input type="text" name="user_input" />
            <input type="submit" />
        </form>
        '''


# My word counter app
@app.route('/word_classifier', methods=['POST'] )
def word_class():
    text = str(request.form['user_input'])

    if os.path.exists('static/images/cat_counts.png'):
        os.remove('static/images/cat_counts.png')
    image_path = '/home/will/code/Instagramalyze/bin/jpgs/users/'

    os.system(' '.join(['python /home/will/code/Instagramalyze/process_user/PredictUser.py', text]))

    with open('../bin/stats/user_stats.json') as data_file: 
        user_data = json.load(data_file)
    
    bar_v = []
    bar_k = []
    for k, v in user_data[text]['category_counts'].iteritems():
        bar_v.append(v)
        bar_k.append(k)
        
    y_size = .8

    fig, ax = plt.subplots()
    # rects1 = ax.barh(x, user_data['senabrew']['category_counts'].values(), height=y_size, color='b')
    rects1 = ax.barh(range(12), bar_v, height=y_size, color='b')
    ax.set_yticks(np.array(range(12))+(y_size/2))
    # ax.set_yticklabels(user_data['senabrew']['category_counts'].keys())
    ax.set_yticklabels(bar_k)
    ax.set_title('Photos in each category')

    plt.savefig('static/images/cat_counts.png')

    adverts = '../static/images/'+user_data[text]['top_count']+'.jpg'

    confidence = np.array(user_data[text]['confidence'])
    msk = confidence.argsort()[-4:][::-1]
    top_conf = confidence[msk]
    top_preds = np.array(user_data[text]['predictions'])[msk]
    top_images = np.array(user_data[text]['image_lst'])[msk]
    top_images = [''.join(['/static/user_images/', text, '/', link.split('/')[-1]]) for link in top_images]
    captions = [''.join([pred, ': ', str(top_conf[i])]) for i, pred in enumerate(top_preds)]


    return render_template('display.html', 
                            ad=adverts, 
                            image_set=top_images, 
                            caption_set=captions)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

