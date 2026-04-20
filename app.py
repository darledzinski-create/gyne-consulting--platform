from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
from mailjet_rest import Client

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/consultation", methods=["GET", "POST"])

def consultation():

    if request.method == "POST":

        print("🔥 POST RECEIVED")

        return "POST WORKED"

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")
