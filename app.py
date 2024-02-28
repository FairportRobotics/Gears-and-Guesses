from flask import Flask, request, render_template, redirect, session, url_for
import random as rand
import json
import os
from dotenv import load_dotenv, find_dotenv
import datetime as dt
import requests

app = Flask(__name__)
app.secret_key = "eTZrxydtcufyviubgioy8t675r46de5ytcfy"
session
tba_api_key = os.environ.get("TBA_API_KEY")

def tba_matches(key: str):
    headers = { "X-TBA-Auth-Key": tba_api_key }
    response = requests.get(f"https://www.thebluealliance.com/api/v3/event/{key}/matches", headers)
    with open(f'matches_{key}.json', 'wb') as f:
        f.write(response.content)
    return()

key = "2023nyrr"
#key = "2024paca"
tba_matches(key)

def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return(data)
path = (f"matches_{key}.json")
read_json(path)

match_data = read_json(path)

@app.route("/")
def hello_world():
    if "username" in session:
        return render_template("home.html")
    return render_template("auth/login.html")


@app.route("/hello/<name>")
def hello(name):
    return render_template("hello.html", name=name)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = read_json("users.json")
        if username in user:
            return render_template(
                "auth/register.html", errorMessage="This user already exists"
            )
        else:
            user[username] = {
                "password": password,
                "balance": 100,
                "administrator": False,
            }
            with open(f"users.json", "w") as f:
                json.dump(user, f)
            return redirect("/login")
    return render_template("auth/register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        print(username)
        password = request.form["password"]
        session["username"] = username
        user = read_json("users.json")
        if username in user and user[username]["password"] == password:
            return redirect("/")
        else:
            return render_template(
                "auth/login.html", errorMessage="Invalid username or password"
            )
    return render_template("auth/login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")


@app.route("/leaderboard")
def leaderboard():
    users = read_json("users.json")
    userBalances = {}
    for k in users:
        balance = users[k]["balance"]
        certainBalance = userBalances.get(balance, [])
        certainBalance.append(k)
        userBalances[balance] = certainBalance
    sortedBalances = sorted(userBalances(), reverse=True)
    print (sortedBalances)
    return render_template("leaderboard.html", userScores=sortedBalances, users=users)


@app.route("/games")
def games():
    return render_template("games.html")


@app.route("/points")
def points():
    return render_template("points.html")


def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
