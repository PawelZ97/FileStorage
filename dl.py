from flask import Flask, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import json
import os
import uuid
import jwt

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
secret_jwt= 'testSecret'

username = "Dummy"

@app.route('/zychp/dl/jwtest', methods=['POST'])
def jwtest():
    print("JWTest")
    encoded = request.form['jwt']
    print("jwt_value: {}".format(encoded))
    decoded = jwt.decode(encoded, secret_jwt, algorithms='HS256')
    print("decoded: {}".format(decoded))
    return decoded['user']

@app.route('/zychp/dl/test')
def test():
    return "Hello"

@app.route('/zychp/dl/getfileslist', methods=['POST'])
def getFilesList(username):
    if (auth()):
        return listUserFiles(username)
    else:
        return "No auth"


@app.route('/zychp/dl/download/<path:filename>', methods=['POST'])
def download(filename):
    if (auth()):
         userpath = getUserDirPath(username)
         return send_from_directory(directory=userpath, filename=filename)
    else:
        return "No auth"
   

@app.route('/zychp/dl/upload', methods=['POST'])
def upload():
    if (auth()):
        n_to_upload = 5-countUserFiles(username)
        userpath = getUserDirPath(username)
        n_uploaded = 0
        for filee in request.files:
            if(n_uploaded < n_to_upload):
                f = request.files[filee]
                f.save(userpath + secure_filename(f.filename))
                n_uploaded += 1
        return "Files uploaded"
    else:
        return "No auth"
     

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
    return True