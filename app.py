from flask import Flask, render_template, url_for, make_response

app = Flask(__name__)


@app.route('/')
def home():  # put application's code here
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.errorhandler(404)
def not_found_error(error):
     return render_template('404.html'), 404

@app.route('/error_not_found')
def error_not_found():
    response = make_response(render_template('404.html', name='ERROR 404'), 404)
    response.headers['X-Something'] = 'A value'
    return response


if __name__ == '__main__':
    app.run(debug=True)
