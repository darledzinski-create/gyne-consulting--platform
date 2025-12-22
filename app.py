
from flask import Flask, render_template, request
import os
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask")
def ask_page():
    return render_template("ask.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/consent")
def consent():
    return render_template("consent.html")

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")

@app.route("/communication")
def communication():
    return render_template("communication.html")

@app.route("/referral")
def referral():
    return render_template("referral.html")

@app.route("/prescriptions")
def prescriptions():
    return render_template("prescriptions.html")

@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")
    return render_template("disclaimer.html")

    email_body = f"""
A new consultation request has been submitted.

Name: {name}
Email: {email}

Question:
{question}
"""

    payload = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": "Gynae Consulting Platform"
                },
                "To": [
                    {
                        "Email": os.environ.get("MAILJET_TO_EMAIL"),
                        "Name": "Dr Dariusz Ledzinski"
                    }
                ],
                "Subject": "New Consultation Request",
                "TextPart": email_body
            }
        ]
    }

    try:
        result = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            ),
            json=payload
        )

        if result.status_code not in (200, 201):
            return "Email delivery failed.", 500

        return render_template("thankyou.html")

    except Exception as e:
        return f"Unexpected error: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
