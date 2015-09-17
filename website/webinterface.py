from collections import Counter
import cPickle as pickle
from flask import Flask, request, render_template
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



    with open('data/vectorizer.pkl') as f:
        vectorizer = pickle.load(f)
    with open('data/model.pkl') as f:
        model = pickle.load(f)

    x = vectorizer.transform([text])

    page = 'Predictions: {0}'
    return page.format(model.predict(x)[0])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)