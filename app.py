vfrom flask import Flask, render_template, request
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
def about_page():
    return render_template("about.html")

@app.route("/consent")
def consent_page():
    return render_template("consent.html")

@app.route("/disclaimer")
def disclaimer_page():
    return render_template("disclaimer.html")
@app.route("/terms")
def terms():
    return render_template("terms.html")
@app.route("/referral")
def referral():
    return render_template("referral.html")
@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")
@app.route("/prescriptions")
def prescriptions():
    return render_template("prescriptions.html")
@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")

    email_body = f"""
A new consultation has been submitted:

Name: {name}
Email: {email}

Question:
{question}
"""

    url = "https://api.mailjet.com/v3.1/send"

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
        response = requests.post(
            url,
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            ),
            json=payload
        )

        if response.status_code not in (200, 201):
            return f"Mailjet error: {response.text}", 500

        return render_template("thankyou.html")

    except Exception as e:
        return f"An unexpected error occurred: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
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
def about_page():
    return render_template("about.html")

@app.route("/consent")
def consent_page():
    return render_template("consent.html")

@app.route("/disclaimer")
def disclaimer_page():
    return render_template("disclaimer.html")
@app.route("/terms")
def terms():
    return render_template("terms.html")
@app.route("/referral")
def referral():
    return render_template("referral.html")
@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")
@app.route("/prescriptions")
def prescriptions():
    return render_template("prescriptions.html")
@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")

    email_body = f"""
A new consultation has been submitted:

Name: {name}
Email: {email}

Question:
{question}
"""

    url = "https://api.mailjet.com/v3.1/send"

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
        response = requests.post(
            url,
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            ),
            json=payload
        )

        if response.status_code not in (200, 201):
            return f"Mailjet error: {response.text}", 500

        return render_template("thankyou.html")

    except Exception as e:
        return f"An unexpected error occurred: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
