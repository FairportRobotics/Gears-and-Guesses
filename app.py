from flask import Flask, render_template
import random as rand
import json
import requests
import os

app = Flask(__name__)

tba_api_key = os.environ.get("TBA_API_KEY")


@app.route("/")
def hello_world():
    a = rand.randint(0, 10000)
    return render_template("test.html", a = a)

app.run(host="0.0.0.0", port=80)

def tba_matches(key: str):
    headers = { "X-TBA-Auth-Key": tba_api_key }
    response = requests.get(f"https://www.thebluealliance.com/api/v3/event/{key}/matches", headers)
    with open(f'matches_{key}.json', 'wb') as f:
        f.write(response.content)
    return()

tba_matches("2023nyrr")