from flask import Flask, request, render_template
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

@app.route("/auth", methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(username, password)
        user = read_json(path)
        if username in user:
            return "<h1>This user already exists</h1><p><a href='/auth'>Try again</a> or <a href='/login'>login</a></p>"
        else:
            return "<p>a</p>"
    else:
        return render_template("auth/register.html")

@app.route("/login")
def login():
    return render_template("auth/login.html")

path = "c:/Users/pig04/Gears-and-Guesses/flaskr/users.json"
def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return(data)

user = read_json(path)

app.run(host="0.0.0.0", port=80)
