from flask import Flask, session, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
import json, os

app = Flask(__name__)
app.secret_key = b'q2qeh827287[/234'
dbfile = open('database.json', 'r')
database = json.loads(dbfile.read())


@app.route('/zychp/login/base')
def baseTest():
    return render_template("base.html")


@app.route('/zychp/login/register')
def registerTest():
    return render_template("register.html")


@app.route('/zychp/login/', methods=['GET', 'POST'])
def login():
    if (checkUser()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            if validateLogin():
                return redirect("/zychp/login/fileslist")
            else:
                return render_template("login.html", error="Niepoprawny login lub/i hasło")
        else:
            return render_template("login.html")


@app.route('/zychp/login/logout')
def logout():
    username = checkUser()
    if (username):
        session.pop(username)
    return redirect('/zychp/login')


@app.route('/zychp/login/fileslist')
def filesList():
    username = checkUser()
    if (username):
        userpath = 'userfiles/' + username + '/'
        listed_files = listUserFiles(username)
        for i in range(len(listed_files),5):
            listed_files.append("Brak pliku")
        return render_template("fileslist.html", username=username, file1 = userpath+listed_files[0],  
        file2 = userpath+listed_files[1],  file3 = userpath+listed_files[2], file4 = userpath+listed_files[3], file5 = userpath+listed_files[4])
    return render_template("base.html", message='Nie zalogowano.')

@app.route('/zychp/login/userfiles/<path:filename>', methods=['GET', 'POST'])
def download(filename):    
    return send_from_directory(directory='userfiles', filename=filename)

@app.route('/zychp/login/upload', methods=['GET', 'POST'])
def upload():
    username = checkUser()
    if (username):
        crateUploadDirectoryIfNotExist(username)
        num_uploaded_files = len(listUserFiles(username))
        num_possible_to_upload = 5-num_uploaded_files
        if request.method == 'POST':
            userpath = 'userfiles/' + username + '/'
            for i in range(1,num_possible_to_upload+1):
                f = request.files['file'+str(i)]
                print(f)
                f.save(userpath + secure_filename(f.filename))
            return redirect('/zychp/login/fileslist')
        else:
            return render_template("upload.html", username=username, num_possible_to_upload = num_possible_to_upload)
    return render_template("base.html", message='Nie zalogowano.')


def validateLogin():
    username = request.form['username']
    for user in database['userslist']:
        if request.form['password'] == user['password'] and username == user['login']:
            session[username] = True
            return True
    return False


def checkUser():
    for user in database['userslist']:
        username = user['login']
        if (session.get(username)):
            return username
    return False

def listUserFiles(username):
    userpath = 'userfiles/' + username + '/'
    return  os.listdir(userpath)

def crateUploadDirectoryIfNotExist(username):
    userpath = 'userfiles/' + username + '/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    return