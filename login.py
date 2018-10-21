from flask import Flask, session, request, redirect, render_template
import json

app = Flask(__name__)
app.secret_key = b'q2qeh827287[/234'
dbfile = open('database.json', 'r')
database = json.loads(dbfile.read())


@app.route('/zychp/base')
def baseTest():
    return render_template("base.html")


@app.route('/zychp/register')
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
        return render_template("fileslist.html", username=username)
    return render_template("base.html", message='Nie zalogowano.')


@app.route('/zychp/login/upload')
def upload():
    username = checkUser()
    if (username):
        return render_template("upload.html", username=username)
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
