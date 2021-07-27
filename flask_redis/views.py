from flask import (Flask, g, request, render_template,
                   session, redirect, url_for)
import redis

app = Flask(__name__)
DEBUG = True
SECRET_KEY = 'e7fc1b2cd7dfde6c6e00850a40d7249a2d10103e30baa332'
app.secret_key = SECRET_KEY
# Redis setup
DB_HOST = 'localhost'
DB_PORT = 6379
DB_NO = 0


def init_db():
    db = redis.StrictRedis(host=DB_HOST,port=DB_PORT,db=DB_NO)
    return db


@app.before_request
def before_request():
    g.db = init_db()


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'GET':
        return render_template('signup.html', error=error)
    username = request.form['username']
    password = request.form['password']
    user_id = str(g.db.incrby('next_user_id', 1000))
    g.db.hmset('user:' + user_id, dict(usrnm=username, paswrd=password))
    g.db.hset('users', username, user_id)
    session['username'] = username


    return redirect(url_for('home'))


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'GET':
        return render_template('login.html', error=error)
    username = request.form['username']
    password = request.form['password']
    try:
        user_id = str(g.db.hget('users', username), 'utf-8')
    except:
        error = 'No such user'
        return render_template('login.html', error=error)
    saved_password = str(g.db.hget('user:' + str(user_id), 'paswrd'), 'utf-8')
    if password != saved_password:
        error = 'Incorrect password'
        return render_template('login.html', error=error)
    session['username'] = username
    return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session:
        return redirect(url_for('login'))
    user_id = g.db.hget('users', session['username'])
    if request.method == 'GET':
        return render_template('home.html', username = session['username'])
