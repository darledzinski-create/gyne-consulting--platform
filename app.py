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

            name = request.form.get("name")
            email = request.form.get("email")
            urgency = request.form.get("urgency")

            print("NAME:", repr(name))
            print("EMAIL:", repr(email))
            print("URGENCY:", repr(urgency))

            # CLEAN VALUE

            urgency_clean = (urgency or "").strip().lower()

            # SIMPLE LOGIC TEST

            if urgency_clean == "urgent":
                print("🚨 URGENT CASE")
            else:
                print("🟢 NON-URGENT CASE")

            return redirect(url_for("thank_you"))

        except Exception as e:
            print("❌ ERROR:", repr(e))
            return "Internal Server Error", 500

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")
