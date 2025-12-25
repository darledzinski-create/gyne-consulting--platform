from flask import Flask, render_template, request, redirect
import os
import requests

app = Flask(__name__)

# ------------------------
# ROUTES
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask")
def ask_page():
    return render_template("ask.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

# ================================
# SUBMIT QUESTION + CONFIRMATION EMAIL
# ================================
@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    question = request.form.get("question", "").strip()

    patient_payload = {
        "name": name,
        "email": email,
        "question": question
    }

    return render_template("thank_you.html")
# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
