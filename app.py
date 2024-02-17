from flask import Flask, request, render_template, redirect
import random as rand
import json
import requests
import os
from dotenv import load_dotenv, find_dotenv
import datetime as dt

app = Flask(__name__)

tba_api_key = os.environ.get("TBA_API_KEY")

@app.route("/")
def hello_world():
    return render_template("base.html")
#"<h1>This user already exists</h1><p><a href='/auth'>Try again</a> or <a href='/login'>login</a></p>"
@app.route("/auth", methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        user = read_json("users.json")
        if username in user:
            errorMessage = "This user already exists"
            return render_template("auth/register.html" , errorMessage=errorMessage)
        else:
            user[username] = {"password": password, "balance": 100}
            with open(f'users.json', 'w') as f:
                json.dump(user, f)
            return redirect("/login")
    else:
        return render_template("auth/register.html")

@app.route("/login")
def login():
    return render_template("auth/login.html")


def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
