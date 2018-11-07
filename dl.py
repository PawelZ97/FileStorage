from flask import Flask, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import json, os, jwt


app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
secret_jwt = open('NoSecretThere.cfg', 'rb').read().decode('utf-8')

@app.route('/zychp/dl/download/<path:filename>', methods=['POST'])
def download(filename):
    username = auth()
    if (username):
        userpath = getUserDirPath(username)
        if (filename!="Brak pliku"):
            print("File downloaded")
            return send_from_directory(directory=userpath, filename=filename, as_attachment=True)
        else: 
            print("Brak pliku")
            return redirect("/zychp/webapp/fileslist")
    else:
        return redirect("/zychp/webapp/fileslist")
   

@app.route('/zychp/dl/upload', methods=['POST'])
def upload():
    username = auth()
    if (username):
        crateUploadDirectoryIfNotExist(username)
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
        return redirect("/zychp/webapp/fileslist")


@app.route('/zychp/dl/getfilesnames', methods=['POST'])
def getFilesNames():
    username = auth()
    if (username):
        crateUploadDirectoryIfNotExist(username)
        listed_files = listUserFiles(username)
        print("List read")
        return redirect("/zychp/webapp/readfilesnames/" + listed_files[0] + "/" + listed_files[1] + "/" + listed_files[2] + "/" + listed_files[3] + "/" + listed_files[4])
    else:
        redirect("/zychp/webapp/fileslist")



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
    try:
        decoded = jwt.decode(encoded, secret_jwt, algorithms='HS256')
        return decoded['user']
    except jwt.ExpiredSignatureError:
        print("JWT expired")
        return False
    except jwt.exceptions.DecodeError:
        print("JWT wrong signature")
        return False
   