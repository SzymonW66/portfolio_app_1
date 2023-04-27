from flask import Flask
from flask import request
from flask import render_template
from flask import abort, redirect, url_for, make_response
from prometheus_client import start_http_server, Counter
from flask import Flask, flash, abort
from flask_mail import Mail, Message
import sqlite3
from flask_dance.contrib.github import make_github_blueprint, github
import secrets
import os
import requests

app = Flask(__name__)
start_http_server(8000)
mail = Mail(app)

HTTP_REQUESTS = Counter('http_requests_total', 'Total HTTP Requests')

app.secret_key = secrets.token_hex(16)  # generujemy sekretny klucz aplikacji
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

github_blueprint = make_github_blueprint(
    client_id="072cb12cb5ea91611253",  # tu wklej swoj wygenerowany id z github
    client_secret="fb3842b64dfe3fef2572dea8ceeb4d0093c94cea",  # tu wklej swoj
    # wygenerowany client secret z github
)
app.register_blueprint(github_blueprint, url_prefix='/login')

app.config['SECRET_KEY'] = '1234'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'szymekwajs@gmail.com'
app.config['MAIL_PASSWORD'] = '*****'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


@app.route('/')
def home():
    HTTP_REQUESTS.inc()
    return render_template('index.html')


@app.route('/index2')
def index2():
    HTTP_REQUESTS.inc()
    return render_template('index2.html')


@app.route('/about')
def about():
    HTTP_REQUESTS.inc()
    return render_template('about.html')


@app.route('/gallery')
def gallery():
    HTTP_REQUESTS.inc()
    return render_template('gallery.html')


@app.route('/contact')
def contact():
    HTTP_REQUESTS.inc()
    return render_template('contact.html')


@app.route('/rock')
def rock():
    HTTP_REQUESTS.inc()
    return render_template('rock.html')


@app.route('/gallery2')
def gallery2():
    HTTP_REQUESTS.inc()
    return render_template('gallery2.html')


@app.route('/sendmail')
def sendmail():
    HTTP_REQUESTS.inc()
    msg = Message('Hello', sender='yourId@gmail.com', recipients=['someone1@gmail.com'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)
    return render_template('send_mail.html')


@app.route('/create/', methods=('GET', 'POST'))
def create():
    HTTP_REQUESTS.inc()
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']

        if not name:
            flash('Name is required!')
        elif not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (name, title, content) VALUES (?, ?, ?)',
                         (name, title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('guestbook'))

    return render_template('create.html')


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    HTTP_REQUESTS.inc()
    post = get_post(id)

    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        content = request.form['content']

        if not name:
            flash('Name is required!')

        elif not title:
            flash('Title is required!')

        elif not content:
            flash('Content is required!')

        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET name = ?, title = ?, content = ?'
                         ' WHERE id = ?',
                         (name, title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('guestbook'))

    return render_template('edit.html', post=post)


@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    HTTP_REQUESTS.inc()
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('guestbook'))


@app.route('/guestbook', methods=('GET', 'POST'))
def guestbook():
    HTTP_REQUESTS.inc()
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('guestbook.html', posts=posts)


@app.route('/guestbook-admin', methods=('GET', 'POST'))
def guestbookAdmin():
    HTTP_REQUESTS.inc()
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('guestbook-admin.html', posts=posts)


@app.route("/login")
def github_login():
    HTTP_REQUESTS.inc()
    if not github.authorized:
        return redirect(url_for('github.login'))
    else:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            return '<h1>Your Github name is {}'.format(account_info_json['login'])
    return '<h1>Request failed!</h1>'


def format_response(city):
    HTTP_REQUESTS.inc()
    weather_key = "6a2d34ead1a8f0627c3933eb6dd85d07"  # tu wklej swój KLUCZ API
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"APPID": weather_key, "q": city, "units": "Metric"}
    response = requests.get(url, params=params)
    weather = response.json()
    name = weather['name']
    desc = weather['weather'][0]['description']
    temp = weather['main']['temp']
    hum = weather['main']['humidity']
    wind = weather['wind']['speed']
    clouds = weather['clouds']['all']
    pres = weather['main']['pressure']
    return "City %s Condition: %s Temperature : %s  Wind : %s Clouds : %s Pressure : %s (C) Humadity : %s word" % (
    name, desc, temp, wind, clouds, pres, hum)


@app.route('/weather', methods=['POST', 'GET'])
def weather():
    HTTP_REQUESTS.inc()
    if request.method == 'GET':
        return render_template('weather.html')
    if request.method == 'POST':
        city = request.form['city']
        weather_data = format_response(city)
        return render_template('weather.html', data=weather_data)
    return render_template('weather.html')


@app.errorhandler(404)
def not_found_error(error):
    HTTP_REQUESTS.inc()
    return render_template('404.html'), 404


@app.route('/error_not_found')
def error_not_found():
    HTTP_REQUESTS.inc()
    response = make_response(render_template('404.html', name='ERROR 404'), 404)
    response.headers['X-Something'] = 'A value'
    return response


if __name__ == '__main__':
    app.run()
