from flask import Flask
from flask import request
from flask import render_template
from flask import abort, redirect, url_for, make_response
from flask import Flask, flash, abort
from flask_mail import Mail, Message
import sqlite3
from flask_dance.contrib.github import make_github_blueprint, github
import secrets
import os
import requests

app = Flask(__name__)
mail = Mail(app)

app.secret_key = secrets.token_hex(16)  # generujemy sekretny klucz aplikacji
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

github_blueprint = make_github_blueprint(
    client_id="072cb12cb5ea91611253",  # tu wklej swoj wygenerowany id z github
    client_secret="fb3842b64dfe3fef2572dea8ceeb4d0093c94cea",  # tu wklej swoj
    # wygenerowany client secret z github
)

app.config['SECRET_KEY'] = '1234'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'szymekwajs@gmail.com'
app.config['MAIL_PASSWORD'] = '*****'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/rock')
def rock():
    return render_template('rock.html')

@app.route('/gallery2')
def gallery2():
    return render_template('gallery2.html')


@app.route('/sendmail')
def sendmail():
    msg = Message('Hello', sender='yourId@gmail.com', recipients=['someone1@gmail.com'])
    msg.body = "Hello Flask message sent from Flask-Mail"
    mail.send(msg)
    return render_template('send_mail.html')


@app.route('/create/', methods=('GET', 'POST'))
def create():
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
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('guestbook'))


@app.route('/guestbook', methods=('GET', 'POST'))
def guestbook():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('guestbook.html', posts=posts)

@app.route('/guestbook-admin', methods=('GET', 'POST'))
def guestbookAdmin():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('guestbook-admin.html', posts=posts)


@app.route("/login")
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    else:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            return '<h1>Your Github name is {}'.format(account_info_json['login'])
    return '<h1>Request failed!</h1>'


@app.errorhandler(404)
def not_found_error(error):
     return render_template('404.html'), 404

@app.route('/error_not_found')
def error_not_found():
    response = make_response(render_template('404.html', name='ERROR 404'), 404)
    response.headers['X-Something'] = 'A value'
    return response

if __name__ == '__main__':
    app.run(port=8080)
