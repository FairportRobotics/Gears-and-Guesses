from flask import Flask, render_template
import random as rand

app = Flask(__name__)

@app.route("/")
def hello_world():
    a = rand.randint(0, 10000)
    return render_template("test.html", a = a)

app.run(host="0.0.0.0", port=80)