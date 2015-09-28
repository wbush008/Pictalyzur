from webhelpers import initialize_display, set_example_photos, save_count_plot
from flask import Flask, request, render_template

app = Flask(__name__)


def dict_to_html(d):
    return '<br>'.join('{0}: {1}'.format(k, d[k]) for k in sorted(d))
# home page


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/user_data', methods=['POST'])
def word_class():
    username = str(request.form['user_input'])

    user_data, label_dict = initialize_display(username)

    save_count_plot(user_data, username, 'activity',
                    'static/images/cat_counts.png',
                    nice_labels=label_dict)

    save_count_plot(user_data, username, 'scene',
                    'static/images/scene_counts.png')

    adverts = '../static/images/' + user_data[username]['activity_top_count'] + '.jpg'

    top_images, captions = set_example_photos(username, user_data, label_dict)

    return render_template('display.html',
                           ad=adverts,
                           image_set=top_images,
                           caption_set=captions)


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
