from flask import Flask, session, request, redirect, render_template, send_from_directory
from werkzeug.utils import secure_filename
import json, uuid, redis, jwt

app = Flask(__name__)

app.config.from_pyfile('NoSecretThere.cfg')  # for SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_PATH'] = "/zychp/webapp"

secret_jwt = 'testSecret'

red = redis.Redis()

@app.route('/zychp/webapp/base') 
def baseTest():
    return render_template("base.html")

@app.route('/zychp/webapp/register')
def registerTest():
    return render_template("register.html")


@app.route('/zychp/webapp/login', methods=['GET', 'POST'])
def login():
    if (checkUserLogin()):
        return render_template("base.html", message="Już zalogowany.")
    else:
        if request.method == 'POST':
            if doLogin():
                return redirect("/zychp/webapp/fileslist")
            else:
                return render_template("login.html", error="Niepoprawny login lub/i hasło")
        else:
            return render_template("login.html")


@app.route('/zychp/webapp/logout')
def logout():
    username = checkUserLogin()
    if (username):
        cookie_uuid = session['uuid']
        red.hdel('zychp:webapp:'+ cookie_uuid, 'login')

        session.pop('username',None)
        session.pop('uuid',None)
    return redirect('/zychp/webapp/login')



@app.route('/zychp/webapp/fileslist', methods=['GET', 'POST'])
def filesList():
    username = checkUserLogin()
    if (username):
        print("Pobierz liste")
        if request.method == 'POST':
            print("POST fileslist")
        else:
            return render_template("fileslist.html", username=username)
            #return render_template("fileslist.html", username=username, file1=listed_files[0],
            #                   file2=listed_files[1],  file3=listed_files[2], file4=listed_files[3], file5=listed_files[4])
    else:                  
        return render_template("base.html", message='Nie zalogowano.')


@app.route('/zychp/webapp/upload', methods=['GET', 'POST'])
def upload():
    username = checkUserLogin()
    n_to_upload = 5
    if (username):
        if request.method == 'POST':
            return redirect('/zychp/webapp/fileslist')
        else:
            jwt_value = jwt.encode({'user': username}, secret_jwt, algorithm='HS256').decode('utf-8')
            print("jwt_value: {}".format(jwt_value))

            decoded = jwt.decode(jwt_value, secret_jwt, algorithms='HS256')
            print("decoded: {}".format(decoded))

            return render_template("upload.html", username=username, n_to_upload=n_to_upload, jwt_value=jwt_value)
    return render_template("base.html", message='Nie zalogowano.')



def doLogin():
    username = request.form['username']
    users_credentials = getUsersCredentials()

    for user in users_credentials:
        if username == user and request.form['password'] == users_credentials[user]:
            user_uuid = str(uuid.uuid4())
            session['username'] = username
            session['uuid'] = user_uuid

            red.hset('zychp:webapp:'+ user_uuid, 'login', username)

            #crateUploadDirectoryIfNotExist(username)
            return True
    return False


def checkUserLogin():
    users_credentials = getUsersCredentials()
    if(session):
        cookie_username = session['username']
        cookie_uuid = session['uuid']
        redis_username = red.hget('zychp:webapp:'+ cookie_uuid, 'login')
        if redis_username is None:
            redis_username="NONE"
        else:
            redis_username=redis_username.decode('utf-8')

        print("Uuid: {}".format(cookie_uuid))
        print("Cookie_username: {}".format(cookie_username))
        print("Redis_username: {}".format(redis_username))

        if cookie_username in users_credentials:
            if(redis_username == cookie_username):
                return cookie_username
            else:
                print("Brak wpisu w redis, podrzucone ciastko")
                return False
        else:
            print("Brak loginu w bazie")
            return False
    else:
        print("Brak ciastka")
        return False


def getUsersCredentials():
    dbfile = open('database.json', 'r')
    database = json.loads(dbfile.read())
    users_credentials = {}
    for user_data in database['userslist']:
        users_credentials[user_data['login']] =  user_data['password']      
    return users_credentials