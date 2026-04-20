from flask import Flask, request, redirect, url_for, render_template
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
        try:
            print("🔥 POST RECEIVED")
            print("=== CURRENT VERSION ===")

            name = request.form.get("name")
            email = request.form.get("email")
            urgency = request.form.get("urgency")

            print("NAME:", repr(name))
            print("EMAIL:", repr(email))
            print("URGENCY:", repr(urgency))

            return redirect(url_for("thank_you"))

        except Exeption as e:
            print(" ERROR:", e )
            return f"ERROR: {repr(e)}", 500

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")
