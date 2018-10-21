from flask import Flask, session, request, redirect, render_template
import json

app = Flask(__name__)
app.secret_key = b'q2qeh827287[/234'

@app.route('/zychp/base')
def baseTest():
    return render_template("base.html")

@app.route('/zychp/register')
def registerTest():
    return render_template("register.html")

@app.route('/zychp/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if validateLogin():
            session['logged_in'] = True
            return redirect("/zychp/login/fileslist")
        else:
            return "Wrong Login or Password"
    else:
        return render_template("login.html")

@app.route('/zychp/login/fileslist')
def filesList():
    
    return render_template("fileslist.html")

@app.route('/zychp/login/upload')
def upload():
       return render_template("upload.html")


def validateLogin():
    username = request.form['username']
    dbfile = open('database.json','r')
    database = json.loads(dbfile.read())

    for user in database['userslist']:
        print(user["login"])
        print(user["password"])

    for user in database['userslist']:
        if request.form['password'] == user['password'] and username == user['login']:
            session[username] = True
            return True

    return False