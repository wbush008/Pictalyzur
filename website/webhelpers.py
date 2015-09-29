import os
import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns


def initialize_display(username):
    if os.path.exists('static/images/cat_counts.png'):
        os.remove('static/images/cat_counts.png')

    os.system(' '.join(
        ['python ../model_code/PredictUser.py', username]))

    with open('../bin/stats/user_stats.json') as data_file:
        user_data = json.load(data_file)

    with open('act_labels.json', 'r') as fp:
        label_dict = json.load(fp)

    return user_data, label_dict


def set_example_photos(username, user_data, label_dict):
    user = user_data[username]
    df = pd.DataFrame([user['activity_confidence'],
                       user['activity_predictions'],
                       user['image_lst']]).T

    df.columns = ['activity_confidence', 'activity_predictions', 'image_lst']
    df_top = df[df['activity_predictions'] != 'other'].sort('activity_confidence', ascending=False).head(12)
    top_conf = df_top.activity_confidence.values
    top_preds = df_top.activity_predictions.values
    top_images = df_top.image_lst.values
    top_images = [''.join(['/static/user_images/', username, '/', link.split('/')[-1]]) for link in top_images]
    captions = [''.join([label_dict[pred], ': ', str(top_conf[i])[:4]])
                for i, pred in enumerate(top_preds)]

    return top_images, captions

def sum_group_counts(user_data, classiffier):
    tot_count = {}
    for user in user_data:
        for k, v in user_data[user][classiffier+'_category_counts'].iteritems():
            if k in tot_count:
                tot_count[k] += v
            else:
                tot_count[k] = v

    return tot_count


def make_xy_arrs(cat_dict, classiffier):
    bar_v = []
    bar_k = []
    for k, v in cat_dict.iteritems():
        if k != 'other':
            bar_v.append(v)
            bar_k.append(k)

    x_arr = np.array(bar_v)
    x_arr = x_arr/float(x_arr.sum())
    y_arr = np.array(bar_k)

    return x_arr, y_arr


def save_count_plot(user_data, user, classiffier, fig_name, nice_labels=None):
    user_dct = user_data[user][classiffier+'_category_counts']
    tot_dct = sum_group_counts(user_data, classiffier)

    user_x, user_y = make_xy_arrs(user_dct, classiffier)
    tot_x, tot_y = make_xy_arrs(tot_dct, classiffier)

    msk = user_x.argsort()

    tot_x = np.array([tot_x[np.where(tot_y == i)] for i in user_y[msk]])

    if nice_labels:
        with open('act_labels.json', 'r') as fp:
            label_dict = json.load(fp)
        y_labels = np.array([label_dict[i] for i in user_y])
    else:
        y_labels = user_y

    y_size = .4
    sns.set_context(rc={"figure.figsize": (6, 4)})

    fig, ax = plt.subplots()

    rects1 = ax.barh(np.arange(len(user_x))+y_size, user_x[msk]*100, height=y_size, color='darkgreen', alpha=.8, label=user)
    rects2 = ax.barh(np.arange(len(user_x)), tot_x*100, height=y_size, color='seagreen', alpha=.3, label='Average user')

    ax.set_yticks(np.array(range(len(y_labels)))+(y_size/2))
    ax.set_yticklabels(y_labels[msk])
    ax.set_xlabel('Percentage of photos')
    ax.set_title('Photos in each category')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.savefig(fig_name, bbox_inches='tight', pad_inches=0)
