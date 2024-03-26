from wiki import race
from flask import Flask, flash, redirect, render_template, request, session

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "GET":
        return render_template("index.html", data=[], message = "")
    else:
        start = request.form.get("start")
        end = request.form.get("end")

        path = race(start, end)

        return render_template("index.html", data=path[0], message = path[1])


        




