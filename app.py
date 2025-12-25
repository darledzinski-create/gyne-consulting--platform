from flask import Flask, render_template, request, redirect, url_for
import os
import requests

app = Flask(__name__)

# -----------------------------
# ROUTES – PAGES
# -----------------------------

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

@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")

@app.route("/prescriptions")
def prescriptions():
    return render_template("prescriptions.html")

@app.route("/referral")
def referral():
    return render_template("referral.html")

@app.route("/communication")
def communication():
    return render_template("communication.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# -----------------------------
# FORM SUBMISSION
# -----------------------------

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Patient")
    email = request.form.get("email")
    question = request.form.get("question")

    # ---- Patient confirmation email (plain text) ----
    confirmation_text = f"""
Dear {name},

Thank you for submitting your private gynaecological consultation.

Your message has been received safely.
I will review your question carefully and respond as soon as possible.

Please note:
• This service is not suitable for acute or emergency matters
• If your condition worsens, seek immediate local medical care

Warm regards,

Dr Dariusz Ledzinski
Gynae Consulting Platform
"""

    mailjet_payload = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": "Gynae Consulting Platform"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": name
                    }
                ],
                "Subject": "Your consultation has been received",
                "TextPart": confirmation_text
            }
        ]
    }

    try:
        requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            ),
            json=mailjet_payload,
            timeout=10
        )
    except Exception:
        # Email failure must NOT block consultation flow
        pass

    return redirect(url_for("thankyou"))


# -----------------------------
# RUN
# -----------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
