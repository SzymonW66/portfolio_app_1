from flask import Flask, render_template, url_for, make_response
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)

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
    return "Sent"
    return render_template('send_mail.html')

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
#TODO- Zrobić kolejną galerie w oparciu o booststrap 3 rzędy 3 kolumny z zdjęciami