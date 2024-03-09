from flask import Flask, request, render_template, redirect, session, url_for
import random as rand
import json
import os
from dotenv import load_dotenv, find_dotenv
import datetime as dt
import requests
import glob
from hashlib import sha256

load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = os.environ.get("secret_key")
session
tba_api_key = os.environ.get("TBA_API_KEY")


def checkValidity(username: str, wager: float) -> bool:
    users = readJSON("data/users.json")
    return float(users[username]["balance"]) >= float(wager)


def accountPayment(username: str, wager: float):
    users = readJSON("data/users.json")
    users[username]["balance"] += wager
    writeJSON("data/users.json", users)


def hash_me(input):
    return sha256(input.encode("utf-8")).hexdigest()


def readJSON(path):
    with open(path) as f:
        data = json.load(f)
    return data


def writeJSON(path, data):
    with open(path, "w") as f:
        f.write(json.dumps(data))


def tba_matches(key: str):
    headers = {"X-TBA-Auth-Key": tba_api_key}
    response = requests.get(
        f"https://www.thebluealliance.com/api/v3/event/{key}/matches", headers
    )
    with open(f"data/matches_{key}.json", "wb") as f:
        f.write(response.content)
    return ()


key = "2024casf"
# Pull the latest data
tba_matches(key)

match_data = readJSON(f"data/matches_{key}.json")


gameMatches = {}
scorableMatches = []
for item in match_data:
    if item["actual_time"] is None:
        blue_text = ", ".join(
            [x.replace("frc", "") for x in item["alliances"]["blue"]["team_keys"]]
        )
        red_text = ", ".join(
            [x.replace("frc", "") for x in item["alliances"]["red"]["team_keys"]]
        )
        gameMatches[item["match_number"]] = {
            "match_number": item["match_number"],
            "key": item["key"],
            "blue": f"Teams {blue_text}",
            "red": f"Teams {red_text}",
        }
    else:
        scorableMatches.append(item["key"])
# Sort the match data
gameMatches = dict(sorted(gameMatches.items()))
gameMatches = gameMatches.values()


@app.route("/")
def home():
    if not "username" in session:
        return render_template("auth/login.html")
    # TODO Get the guesses for the user
    my_red_or_blue_wagers = []
    for file_path in glob.glob(f"data/red_or_blue/{key}*.json"):
        for row in readJSON(file_path):
            if row["username"] == session["username"]:
                match_name = (
                    file_path.replace(".json", "").replace("\\", "/").split("/")[-1]
                )
                my_red_or_blue_wagers.append(
                    {
                        "key": match_name,
                        "wager": row["wager"],
                        "results": row["results"],
                    }
                )
    return render_template("home.html", red_or_blue_wagers=my_red_or_blue_wagers)


# @app.route("/hello/<name>")
# def hello(name):
#    return render_template("hello.html", name=name)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_me(password)
        users = readJSON("data/users.json")
        if username in users:
            return render_template(
                "/auth/register.html", errorMessage="This user already exists"
            )
        else:
            users[username] = {
                "password": hashed_password,
                "balance": 1000,
                "administrator": False,
            }
            writeJSON("data/users.json", users)
            return redirect("/login")
    return render_template("auth/register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_me(password)
        session["username"] = username
        user = readJSON("data/users.json")
        if username in user and user[username]["password"] == hashed_password:
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
    users = readJSON("data/users.json")
    userBalances = {}
    for k in users:
        balance = users[k]["balance"]
        certainBalance = userBalances.get(balance, [])
        certainBalance.append(k)
        userBalances[balance] = certainBalance
    userScores = []
    i = 0
    sortedBalances = sorted(userBalances, reverse=True)
    for k1 in sortedBalances:
        for user in userBalances[k1]:
            i += 1
            userScores.append((i, user, k1))
    return render_template("leaderboard.html", userScores=userScores)


@app.route("/games")
def games():
    return render_template("games.html")


@app.route("/games/red-or-blue", methods=["POST", "GET"])
def red_or_blue():
    if request.method == "POST":
        match = request.form["match"]
        alliance = request.form["alliance"]
        wager = request.form["wager"]
        file_path = f"data/red_or_blue/{match}.json"
        username = session["username"]
        if checkValidity(username, wager):

            try:
                data = readJSON(file_path)
            except:
                data = []
            data.append(
                {
                    "username": username,
                    "alliance": alliance,
                    "wager": wager,
                    "results": "undetermined",
                }
            )
            writeJSON(f"data/red_or_blue/{match}.json", data)
            # Deduct money for the wager
            accountPayment(username, -1 * float(wager))
        else:
            return render_template(
                "red_or_blue.html",
                gameMatches=gameMatches,
                error_message=f"You don't have {wager} roboCoins!",
            )
    return render_template("red_or_blue.html", gameMatches=gameMatches)


@app.route("/games/point-picker")
def point_picker():
    return render_template("point_picker.html", gameMatches=gameMatches)


@app.route("/admin")
def admin():
    if not session["admin"]:
        redirect("/")
    # Check to see which events can be scored
    red_or_blue = []
    for file_path in glob.glob(f"data/red_or_blue/{key}*.json"):
        check_me = readJSON(file_path)
        file_name = file_path.replace(".json", "").replace("\\", "/").split("/")[-1]
        if check_me[0]["results"] == "undetermined" and file_name in scorableMatches:
            red_or_blue.append(file_name)

    return render_template("admin.html", red_or_blue=red_or_blue)


@app.route("/score/red-or-blue/<file_name>")
def score_red_or_blue(file_name):
    # Get the winning alliance
    for match in match_data:
        if match["key"] == file_name:
            winning_alliance = match["winning_alliance"]
    # Update the wagers file with wins and losses
    wagers = []
    file_path = f"data/red_or_blue/{file_name}.json"
    for row in readJSON(file_path):
        if row["alliance"] == winning_alliance:
            row["results"] = "win"
            # Award the winnings
            accountPayment(row["username"], 2 * float(row["wager"]))
        else:
            row["results"] = "lost"
        wagers.append(row)
    writeJSON(file_path, wagers)
    return redirect("/admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
