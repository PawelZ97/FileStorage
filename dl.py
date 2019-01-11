from flask import Flask, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import json, os, jwt, redis, hashlib
import pika


app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
secret_jwt = open('NoSecretThere.cfg', 'rb').read().decode('utf-8')

red = redis.Redis()

@app.route('/zychp/dl/download/<path:filename>', methods=['POST'])
def download(filename):
    username = getUserAndCheckAuth()
    if (username):
        userpath = getUserDirPath(username)
        print("File downloaded")
        return send_from_directory(directory=userpath, filename=filename, as_attachment=True)
    else:
        return redirect("/zychp/webapp/fileslist")

@app.route('/zychp/dl/sharedl/<string:jwtToken>', methods=['GET'])
def shareDownload(jwtToken):
    try:
        decoded = jwt.decode(jwtToken, secret_jwt, algorithms='HS256')
        path = getUserDirPath(decoded['username'])
        filename = decoded['filename']
        return send_from_directory(directory=path, filename=filename, as_attachment=True)
    except jwt.exceptions.DecodeError:
        print("JWT wrong signature")
    return redirect("/zychp/webapp/login")   

@app.route('/zychp/dl/thumb/<string:username>/<string:filename>', methods=['GET'])
def thumbDownload(username,filename):
    try:
        path = 'thumbs/' + username + '/'
        return send_from_directory(directory=path, filename=filename, as_attachment=True)
    except jwt.exceptions.DecodeError:
        print("Can't serve thumb")
    return redirect("/zychp/webapp/login")   


@app.route('/zychp/dl/upload', methods=['POST'])
def upload():
    username = getUserAndCheckAuth()
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
                produceConversion(username,userpath,secure_filename(f.filename))
            else:
                print("File upload aborted")
        print("Files uploaded")
        return redirect("/zychp/webapp/fileslist")
    else:
        return redirect("/zychp/webapp/fileslist")


@app.route('/zychp/dl/getfilesnames', methods=['POST'])
def getFilesNames():
    username = getUserAndCheckAuth()
    if (username):
        crateUploadDirectoryIfNotExist(username)
        listed_files = listUserFiles(username)
        red.hset('zychp:webapp:userfiles'+ getHash(username), 'fileslist', json.dumps(listed_files))
        red.hset('zychp:webapp:userfiles'+ getHash(username), 'nfiles', countUserFiles(username))
        print("Fileslist read")
        return redirect("/zychp/webapp/fileslist")
    else:
        return redirect("/zychp/webapp/fileslist")



def listUserFiles(username):
    userpath = getUserDirPath(username)
    listed_files = [filename for filename in os.listdir(userpath) if not filename.startswith('.')]
    return listed_files

def countUserFiles(username):
    return len(os.listdir(getUserDirPath(username)))

def crateUploadDirectoryIfNotExist(username):
    userpath = getUserDirPath(username)
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    thumbpath = getThumbDirPath(username)
    if not os.path.exists(thumbpath):
        os.makedirs(thumbpath)
    return

def getHash(string):
    string += secret_jwt
    return hashlib.sha256(string.encode()).hexdigest() 

def getUserDirPath(username):
    return 'userfiles/' + secure_filename(getHash(username)) + '/'

def getThumbDirPath(username):
    return 'thumbs/' + secure_filename(username) + '/'

def getUserAndCheckAuth():
    encoded = request.form['jwt']
    try:
        decoded = jwt.decode(encoded, secret_jwt, algorithms='HS256')
        return decoded['username']
    except jwt.ExpiredSignatureError:
        print("JWT expired")
    except jwt.exceptions.DecodeError:
        print("JWT wrong signature")
    return False

def produceConversion(username,userpath,filename):
    if (filename.endswith('.png') or filename.endswith('.jpg')):
        exchange = 'zychp-xchange'
        exchange_type = 'direct'
        routing_key = 'zychp'

        body ='{}'.format(json.dumps({'username': secure_filename(username), 'userpath': userpath, 'filename': filename}))

        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.exchange_declare(exchange=exchange,
                         exchange_type=exchange_type)
        channel.basic_publish(exchange=exchange,
                      routing_key=routing_key,
                      body=body)
        print("Sent '{}'".format(body))
        connection.close()
    else:
        print("Not graphics")
    return
