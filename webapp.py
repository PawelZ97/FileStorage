from flask import Flask, session, request, redirect, render_template, send_from_directory, jsonify, url_for
from werkzeug.utils import secure_filename
import json, uuid, redis, jwt, os, datetime, hashlib

from functools import wraps
from os import environ as env
from werkzeug.exceptions import HTTPException
#from dotenv import load_dotenv, find_dotenv
from authlib.flask.client import OAuth
from six.moves.urllib.parse import urlencode


app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_PATH'] = "/zychp/webapp"

secret_jwt = open('NoSecretThere.cfg', 'rb').read().decode('utf-8')
secret_auth0 = open('NoSecondSecretThere.cfg', 'rb').read().decode('utf-8')

red = redis.Redis()

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='sPkHamObJWj65rG__BOkn9g9hLhdJ5Bc',
    client_secret=secret_auth0,
    api_base_url='https://zychp.eu.auth0.com',
    access_token_url='https://zychp.eu.auth0.com/oauth/token',
    authorize_url='https://zychp.eu.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile',
    },
)

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/zychp/webapp/login')
    return f(*args, **kwargs)

  return decorated

@app.route('/zychp/webapp/base') 
def baseTest():
    return render_template("base.html")


@app.route('/zychp/webapp/register')
def registerTest():
    return render_template("register.html")
  

@app.route('/zychp/webapp/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        return auth0.authorize_redirect(redirect_uri='https://edi.iem.pw.edu.pl/zychp/webapp/callback', audience='https://zychp.eu.auth0.com/userinfo')
    else:
        return render_template("login.html")

@app.route('/zychp/webapp/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('login', _external=True), 'client_id': 'sPkHamObJWj65rG__BOkn9g9hLhdJ5Bc'}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/zychp/webapp/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/zychp/webapp/fileslist')


@app.route('/zychp/webapp/fileslist')
@requires_auth
def filesList():
    username = checkUserLogin()
    if (username):
        redis_filelist = red.hget('zychp:webapp:userfiles'+ getHash(username), 'fileslist')
        if (redis_filelist != None):
            filelist = json.loads(redis_filelist)
        else:
            filelist = emptyLocalList()
        jwt_value = getToken(username)
        return render_template("fileslist.html", username=username, sec_username=secure_filename(username), jwt_value=jwt_value, fileslist=filelist)
    else:                  
        return redirect('/zychp/webapp/login')
    
@app.route('/zychp/webapp/sharelink', methods=['POST'])
@requires_auth
def share():
    username = checkUserLogin()
    if (username):
        filename = request.form['filename']
        if(filename):
            jwt_value = jwt.encode({'username': username,'filename': filename},secret_jwt, algorithm='HS256').decode('utf-8')
            link = "https://edi.iem.pw.edu.pl/zychp/dl/sharedl/" + jwt_value
            return render_template("share.html", link = link)
        else:
            return render_template("base.html", message='Wystąpił błąd.')
    return render_template("base.html", message='Nie zalogowano.')

@app.route('/zychp/webapp/upload', methods=['GET', 'POST'])
@requires_auth
def upload():
    username = checkUserLogin()
    if (username):
        redis_n_files = red.hget('zychp:webapp:userfiles'+ getHash(username), 'nfiles')
        if (redis_n_files != None):
            n_files = redis_n_files
            n_to_upload = 5 - int(n_files)
        else:
            n_to_upload = 5   
        jwt_value = getToken(username)
        return render_template("upload.html", username=username, n_to_upload=n_to_upload, iterlist=range(1,n_to_upload+1), jwt_value=jwt_value)
    return render_template("base.html", message='Nie zalogowano.')

@app.route('/zychp/webapp/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

def checkUserLogin():
    nickname = session['profile']['name']
    return nickname
   
def getHash(string):
    string += secret_jwt
    return hashlib.sha256(string.encode()).hexdigest() 

def getToken(username):
    jwt_value = jwt.encode({'username': username,'exp': datetime.datetime.utcnow()
     + datetime.timedelta(seconds=100)},secret_jwt, algorithm='HS256').decode('utf-8')
    return jwt_value

def emptyLocalList():
    return [] 
