from flask import Flask, session, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
import json
import os
import uuid

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_PATH'] = "/zychp/login"

logged_sessions = {}

@app.route('/zychp/login/base') 
def baseTest():
    return render_template("base.html")


@app.route('/zychp/login/register')
def registerTest():
    return render_template("register.html")


@app.route('/zychp/login/', methods=['GET', 'POST'])
def login():
    if (checkUserLogin()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            if doLogin():
                return redirect("/zychp/login/fileslist")
            else:
                return render_template("login.html", error="Niepoprawny login lub/i hasło")
        else:
            return render_template("login.html")


@app.route('/zychp/login/logout')
def logout():
    username = checkUserLogin()
    if (username):
        session.pop('username',None)
        session.pop('uuid',None)
        logged_sessions.pop(username)
    return redirect('/zychp/login')


@app.route('/zychp/login/fileslist', methods=['GET', 'POST'])
def filesList():
    username = checkUserLogin()
    if (username):
        userpath = getUserDirPath(username)
        listed_files = listUserFiles(username)
        if request.method == 'POST':
            for element in request.form:
                index_to_del = int(element)
                if(listed_files[index_to_del] != "Brak pliku"):
                    os.remove(userpath + listed_files[index_to_del])
        listed_files = listUserFiles(username)
        return render_template("fileslist.html", username=username, file1=listed_files[0],
                               file2=listed_files[1],  file3=listed_files[2], file4=listed_files[3], file5=listed_files[4])
    return render_template("base.html", message='Nie zalogowano.')


@app.route('/zychp/login/userfiles/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_from_directory(directory='userfiles', filename=filename)


@app.route('/zychp/login/upload', methods=['GET', 'POST'])
def upload():
    username = checkUserLogin()
    if (username):
        n_to_upload = 5-countUserFiles(username)
        if request.method == 'POST':
            userpath = getUserDirPath(username)
            n_uploaded = 0
            for filee in request.files:
                if(n_uploaded < n_to_upload):
                    f = request.files[filee]
                    f.save(userpath + secure_filename(f.filename))
                    n_uploaded += 1
                else:
                    return  redirect('/zychp/login/fileslist')
            return redirect('/zychp/login/fileslist')
        else:
            return render_template("upload.html", username=username, n_to_upload=n_to_upload)
    return render_template("base.html", message='Nie zalogowano.')


def doLogin():
    username = request.form['username']
    users_credentials = getUsersCredentials()

    for user in users_credentials:
        if username == user and request.form['password'] == users_credentials[user]:
            user_uuid = uuid.uuid4().int
            session['username'] = username
            session['uuid'] = user_uuid
            logged_sessions[username] = user_uuid
            crateUploadDirectoryIfNotExist(username)
            return True
    return False


def checkUserLogin():
    users_credentials = getUsersCredentials()
    if(session):
        cookie_username = session['username']
        print("Username: {}".format(cookie_username))
        print("SesDir: {}".format(logged_sessions))

        if cookie_username in users_credentials:

            if cookie_username in logged_sessions:
                print("Server uuid:{}".format(logged_sessions[cookie_username]))
            print("Reque  uuid:{}".format(session['uuid']))

            if cookie_username in logged_sessions:
                if (logged_sessions[cookie_username] == session['uuid']):
                    print("Cookie OK")
                    return cookie_username
                else:
                    print("Niezgodność Cookie")
                    return False
            else:
                print("Nie zalogowany")
                return False
        else:
            print("Brak loginu w bazie")
            return False
    else:
        print("Brak ciastka")
        return False

def listUserFiles(username):
    userpath = getUserDirPath(username)
    listed_files = os.listdir(userpath)
    for i in range(len(listed_files), 5):
        listed_files.append("Brak pliku")
    return listed_files

def countUserFiles(username):
    return len(os.listdir(getUserDirPath(username)))

def crateUploadDirectoryIfNotExist(username):
    userpath = getUserDirPath(username)
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    return

def getUserDirPath(username):
    return 'userfiles/' + username + '/'

def getUsersCredentials():
    dbfile = open('database.json', 'r')
    database = json.loads(dbfile.read())
    users_credentials = {}
    for user_data in database['userslist']:
        users_credentials[user_data['login']] =  user_data['password']      
    return users_credentials