import os
import json
import matplotlib.pyplot as plt
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



@app.route('/user_data', methods=['POST'])
def word_class():
    text = str(request.form['user_input'])

    if os.path.exists('static/images/cat_counts.png'):
        os.remove('static/images/cat_counts.png')

    os.system(' '.join(
        ['python /home/will/code/Instagramalyze/process_user/PredictUser.py', text]))

    with open('../bin/stats/user_stats.json') as data_file:
        user_data = json.load(data_file)

    bar_v = []
    bar_k = []
    for k, v in user_data[text]['activity_category_counts'].iteritems():
        bar_v.append(v)
        bar_k.append(k)

    y_size = .8

    fig, ax = plt.subplots()
    rects1 = ax.barh(range(13), bar_v, height=y_size, color='b')
    ax.set_yticks(np.array(range(13)) + (y_size / 2))
    ax.set_yticklabels(bar_k)
    ax.set_title('Photos in each category')

    plt.savefig('static/images/cat_counts.png')

    adverts = '../static/images/' + \
        user_data[text]['activity_top_count'] + '.jpg'

    confidence = np.array(user_data[text]['activity_confidence'])
    msk = confidence.argsort()[-4:][::-1]
    top_conf = confidence[msk]
    top_preds = np.array(user_data[text]['activity_predictions'])[msk]
    top_images = np.array(user_data[text]['image_lst'])[msk]
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
