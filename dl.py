from flask import Flask, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import json
import os
import uuid
import jwt

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
secret_jwt= 'testSecret'

@app.route('/zychp/dl/download/<path:filename>', methods=['POST'])
def download(filename):
    username = auth()['user']
    if (username):
        userpath = getUserDirPath(username)
        if (filename!="Brak pliku"):
            print("File downloaded")
            return send_from_directory(directory=userpath, filename=filename, as_attachment=True)
        else: 
            print("Brak pliku")
            return redirect("/zychp/webapp/fileslist")
    else:
        print("No auth")
        return redirect("/zychp/webapp/fileslist")
   

@app.route('/zychp/dl/upload', methods=['POST'])
def upload():
    username = auth()['user']
    crateUploadDirectoryIfNotExist(username)
    if (username):
        n_to_upload = 5-countUserFiles(username)
        userpath = getUserDirPath(username)
        n_uploaded = 0
        for filee in request.files:
            if(n_uploaded < n_to_upload):
                f = request.files[filee]
                f.save(userpath + secure_filename(f.filename))
                n_uploaded += 1
        print("Files uploaded")
        return redirect("/zychp/webapp/fileslist")
    else:
        print("No auth")
        return redirect("/zychp/webapp/fileslist")


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

def auth():
    encoded = request.form['jwt']
    decoded = jwt.decode(encoded, secret_jwt, algorithms='HS256')
    return decoded