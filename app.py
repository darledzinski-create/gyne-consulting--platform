from flask import request, redirect, url_for, render template
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

            name = request.form.get("name")
            email = request.form.get("email")
            urgency = request.form.get("urgency")

            print("NAME:", repr(name))
            print("EMAIL:", repr(email))
            print("URGENCY:", repr(urgency))

            return redirect(url_for("thank_you"))

        except EXCEPTION as e:
            print(" ERROR:", e )
            return f"ERROR: {E}", 500

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")
