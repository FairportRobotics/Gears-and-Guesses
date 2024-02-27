from flask import Flask, request, render_template, redirect, session, url_for
import random as rand
import json
import os
from dotenv import load_dotenv, find_dotenv
import datetime as dt

app = Flask(__name__)
app.secret_key = "eTZrxydtcufyviubgioy8t675r46de5ytcfy"
session
tba_api_key = os.environ.get("TBA_API_KEY")


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
    return render_template("leaderboard.html")


@app.route("/games")
def games():
    return render_template("games.html")


@app.route("/games/red-or-blue")
def red_or_blue():
    return render_template("red_or_blue.html")


@app.route("/games/point-picker")
def point_picker():
    return render_template("point_picker.html")

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
