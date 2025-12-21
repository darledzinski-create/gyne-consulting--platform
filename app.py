from flask import Flask, render_template, request
import os
import requests

app = Flask(__name__)

# --------------------
# Core pages
# --------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask")
def ask_page():
    return render_template("ask.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/consent")
def consent():
    return render_template("consent.html")

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")
    
@app.route("/referral")
def referral_notice():
    return render_template("referral.html")

@app.route("/prescriptions")
def prescriptions():
    return render_template("prescriptions.html")

@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")
@app.route("/communication")
def communication():
    return render_template("communication.html")
@app.route("/gp-liaison")
def gp_liaison():
    return render_template("gp-liaison.html")
@app.route("/before-you-submit")
def before_you_submit():
    return render_template("before-you-submit.html")

# --------------------
# Form submission
# --------------------

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")

if __name__=="__main__":
    app.run(host="0.0.0.",port=5000)
