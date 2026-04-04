from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime   # ✅ MOVE THIS TO THE TOP
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/consultation", methods=["GET", "POST"])
def consultation():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        print(name, email, message)

        with open("submissions.txt", "a") as f:
            f.write(f"{datetime.now()} | {name} | {email} | {message}\n")

        return redirect(url_for("thank_you"))

    return render_templateation("consultation.html")  


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")
