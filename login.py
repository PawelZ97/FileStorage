from flask import Flask, session, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
import json
import os
import uuid

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
#app.config['SESSION_COOKIE_SECURE'] = True
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
        session.pop(username,None)
        logged_sessions.pop(username)
    return redirect('/zychp/login')


@app.route('/zychp/login/fileslist', methods=['GET', 'POST'])
def filesList():
    username = checkUserLogin()
    if (username):
        userpath = 'userfiles/' + username + '/'
        listed_files = listUserFiles(username)
        for i in range(len(listed_files), 5):
            listed_files.append("Brak pliku")
        if request.method == 'POST':
            for element in request.form:
                index_to_del = int(element)
                if(listed_files[index_to_del] != "Brak pliku"):
                    os.remove(userpath + listed_files[index_to_del])
        listed_files = listUserFiles(username)
        for i in range(len(listed_files), 5):
            listed_files.append("Brak pliku")
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
        n_uploaded_files = len(listUserFiles(username))
        n_to_upload = 5-n_uploaded_files
        if request.method == 'POST':
            userpath = 'userfiles/' + username + '/'
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
    for user in accesDatabase()['userslist']:
        if request.form['password'] == user['password'] and username == user['login']:
            user_ssid = uuid.uuid4().int
            session[username] = user_ssid
            logged_sessions[username] = user_ssid
            crateUploadDirectoryIfNotExist(username)
            return True
    return False


def checkUserLogin():
    print("SesDir: {}".format(logged_sessions))
    for user in accesDatabase()['userslist']:
        username = user['login']
        print(username)

        if username in logged_sessions:
            print("Server uuid:{}".format(logged_sessions[username]))
            print("Local uuid:{}".format(session.get(username)))

            if (session.get(username) == logged_sessions[username]): 
                print("User: {} logged.".format(username))
                return username
            else:
                print("Cookies not match")
    print("User not found")
    return False

def listUserFiles(username):
    userpath = 'userfiles/' + username + '/'
    return os.listdir(userpath)


def crateUploadDirectoryIfNotExist(username):
    userpath = 'userfiles/' + username + '/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    return

def accesDatabase():
    dbfile = open('database.json', 'r')
    database = json.loads(dbfile.read())
    return database