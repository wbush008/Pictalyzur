import os
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, request, render_template

plt.style.use('ggplot')
app = Flask(__name__)


def dict_to_html(d):
    return '<br>'.join('{0}: {1}'.format(k, d[k]) for k in sorted(d))
# home page


@app.route('/')
def index():

    return render_template('index.html')



@app.route('/user_data', methods=['POST'])
def word_class():
    text = str(request.form['user_input'])

    if os.path.exists('static/images/cat_counts.png'):
        os.remove('static/images/cat_counts.png')

    os.system(' '.join(
        ['python /home/will/code/Instagramalyze/process_user/PredictUser.py', text]))

    with open('../bin/stats/user_stats.json') as data_file:
        user_data = json.load(data_file)

    tot_count = {}
    for user in user_data:
        for k, v in user_data[user]['activity_category_counts'].iteritems():
            if k != 'other':
                if k in tot_count:
                    tot_count[k] += v
                else:
                    tot_count[k] = v   
                
    bar_vt = []
    bar_kt = []
    for k, v in tot_count.iteritems():
            bar_vt.append(v)
            bar_kt.append(k)
            
    xt_arr = np.array(bar_vt)
    yt_arr = np.array(bar_kt)

    total = xt_arr.sum()
    xt_arr = xt_arr/float(total)
    sor_msk_t = xt_arr.argsort()

    bar_v = []
    bar_k = []
    for k, v in user_data[text]['activity_category_counts'].iteritems():
        if k != 'other':
            bar_v.append(v)
            bar_k.append(k)
            
    x_arr = np.array(bar_v)
    y_arr = np.array(bar_k)

    total = x_arr.sum()
    x_arr = x_arr/float(total)
    sor_msk = x_arr.argsort()

    y_size = .4

    fig, ax = plt.subplots()

    rects1 = ax.barh(np.arange(12), x_arr[sor_msk], height=y_size, color='blue', alpha=.6, label='user')
    x_tt = [xt_arr[np.where(yt_arr== i )] for i in y_arr[sor_msk]]

    rects2 = ax.barh(np.arange(12)+y_size, x_tt, height=y_size, color='blue', alpha=.2, label='group')

    ax.set_yticks(np.array(range(12))+(y_size/2))
    ax.set_yticklabels(y_arr[sor_msk])
    plt.legend()
    plt.savefig('static/images/cat_counts.png')


    tot_count = {}
    for user in user_data:
        for k, v in user_data[user]['scene_category_counts'].iteritems():
            if k != 'other':
                if k in tot_count:
                    tot_count[k] += v
                else:
                    tot_count[k] = v   
                
    bar_vt = []
    bar_kt = []
    for k, v in tot_count.iteritems():
            bar_vt.append(v)
            bar_kt.append(k)
            
    xt_arr = np.array(bar_vt)
    yt_arr = np.array(bar_kt)

    total = xt_arr.sum()
    xt_arr = xt_arr/float(total)
    sor_msk_t = xt_arr.argsort()

    bar_v = []
    bar_k = []
    for k, v in user_data[text]['scene_category_counts'].iteritems():
        if k != 'other':
            bar_v.append(v)
            bar_k.append(k)
            
    x_arr = np.array(bar_v)
    y_arr = np.array(bar_k)

    total = x_arr.sum()
    x_arr = x_arr/float(total)
    sor_msk = x_arr.argsort()

    y_size = .4

    fig, ax = plt.subplots()

    rects1 = ax.barh(np.arange(3), x_arr[sor_msk], height=y_size, color='blue', alpha=.6, label='user')
    x_tt = [xt_arr[np.where(yt_arr== i )] for i in y_arr[sor_msk]]

    rects2 = ax.barh(np.arange(3)+y_size, x_tt, height=y_size, color='blue', alpha=.2, label='group')

    ax.set_yticks(np.array(range(3))+(y_size/2))
    ax.set_yticklabels(y_arr[sor_msk])
    plt.legend()
    plt.savefig('static/images/scene_counts.png')

    adverts = '../static/images/' + \
        user_data[text]['activity_top_count'] + '.jpg'

    user = user_data[text]
    df = pd.DataFrame([user['activity_confidence'], 
                       user['activity_predictions'], 
                       user['image_lst']]).T
    df.columns = ['activity_confidence', 'activity_predictions', 'image_lst']
    df_top = df[df['activity_predictions']!='other'].sort('activity_confidence', ascending=False).head(4)
    top_conf = df_top.activity_confidence.values
    top_preds = df_top.activity_predictions.values
    top_images = df_top.image_lst.values
    top_images = [''.join(['/static/user_images/', text, '/', link.split('/')[-1]]) for link in top_images]
    captions = [''.join([pred, ': ', str(top_conf[i])])
                for i, pred in enumerate(top_preds)]

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
