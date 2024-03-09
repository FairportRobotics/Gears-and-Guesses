from flask import Flask, request, render_template, redirect, session, url_for
import random as rand
import json
import os
from dotenv import load_dotenv, find_dotenv
import datetime as dt
import requests
import glob

load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.environ.get("secret_key")
session
tba_api_key = os.environ.get("TBA_API_KEY")

def tba_matches(key: str):
    headers = { "X-TBA-Auth-Key": tba_api_key }
    response = requests.get(f"https://www.thebluealliance.com/api/v3/event/{key}/matches", headers)
    with open(f'matches_{key}.json', 'wb') as f:
        f.write(response.content)
    return()

key="2024mose"
tba_matches(key)

def read_json(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return(data)

def writeJson(path, data):
    with open(path, 'w') as f:
        f.write(json.dumps(data))

path1 = (f"matches_{key}.json")


match_data = read_json(path1)


gameMatches = {}
scorableMatches = []
for item in match_data:
    if(item["actual_time"] is None):
        blue_text = ", ".join([x.replace("frc","") for x in item["alliances"]["blue"]["team_keys"]])
        red_text = ", ".join([x.replace("frc","") for x in item["alliances"]["red"]["team_keys"]])
        gameMatches[item["match_number"]] = {"match_number":item["match_number"], "key": item["key"], "blue": f"Teams {blue_text}", "red": f"Teams {red_text}"}
    else:
        scorableMatches.append(item["key"])
        scorableMatches.append(item["winning_alliance"])
        scorableMatches.append({"blue": item["score_breakdown"]["blue"]["totalPoints"], "red": item["score_breakdown"]["red"]["totalPoints"]})
gameMatches = dict(sorted(gameMatches.items()))
gameMatches = gameMatches.values()

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
        users = read_json("data/users.json")
        if username in users:
            return render_template("/auth/register.html", errorMessage="This user already exists")
        else:
            users[username] = {
                "password": password,
                "balance": 100,
                "administrator": False,
            }
            writeJson("data/users.json", users)
            return redirect("/login")
    return render_template("auth/register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        print(username)
        password = request.form["password"]
        session["username"] = username
        user = read_json("data/users.json")
        if username in user and user[username]["password"] == password:
            session["admin"] = user[username]["administrator"]
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
    users = read_json("data/users.json")
    userBalances = {}
    for k in users:
        balance = users[k]["balance"]
        certainBalance = userBalances.get(balance, [])
        certainBalance.append(k)
        userBalances[balance] = certainBalance
    userScores = []
    i=0
    sortedBalances = sorted(userBalances, reverse=True)
    for k1 in sortedBalances:
        for user in userBalances[k1]:
            i+=1
            userScores.append((i, user, k1))
    return render_template("leaderboard.html", userScores=userScores)


@app.route("/games")
def games():
    return render_template("games.html")


@app.route("/games/red-or-blue", methods=['POST', 'GET'])
def red_or_blue():
    
    if request.method == 'POST':
        match = request.form["match"]
        alliance = request.form["alliance"]
        wager = request.form["wager"]
        #print(match+" "+alliance+" "+wager)
        file_path = f'data/red_or_blue/{match}.json'
        username = session["username"]
        if checkValidity(username, wager):

            try:
                data = read_json(file_path)
            except:
                data = []
            data.append({"username": username, "alliance": alliance, "wager": wager, "results": "undetermined"})
            writeJson(f'data/red_or_blue/{match}.json', data)
        else:
            return render_template("red_or_blue.html", gameMatches=gameMatches, error_message=f"You don't have {wager} roboCoins!")
    return render_template("red_or_blue.html", gameMatches=gameMatches)


@app.route("/games/point-picker")
def point_picker():
    return render_template("point_picker.html", gameMatches=gameMatches)


@app.route("/admin")
def admin():
    if(not session["admin"]):
        redirect("/")
    for name in glob.glob("data/red_or_blue/*.json"):
        print(name)
    # use glob to get the list of files in data/red_or_blue
    # loop over those files and open the json
    # check the status of the first item to see if it's unscored
    # if so, add the match key to the scorable rd or blue list
    # pass the list into the template
    return render_template("admin.html")


def checkValidity(username:str, wager:float)->bool:
    users = read_json("data/users.json")
    return float(users[username]["balance"]) >= float(wager)

def accountPayment(username:str, wager:float):
    users = read_json("data/users.json")
    users[username]["balance"] -= wager
    writeJson("data/users.json", users)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
