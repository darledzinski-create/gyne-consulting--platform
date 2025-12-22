
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

@app.route("/submit_question", methods=["POST"])
def submit_question():
    confirmation_subject = "We’ve received your consultation request"

    confirmation_body = f"""
    Dear {name if name else 'Patient'},

    Thank you for submitting your consultation request through the Gynae Consulting Platform.

    Your message has been received successfully and will be reviewed personally.

    You can expect a thoughtful response once your information has been assessed. 
    Response times are usually within 24 hours on working days.

    Please note that this service does not replace emergency care. 
    If you experience acute symptoms or feel unwell, seek immediate medical attention locally.

    Kind regards,

    Dr Dariusz Ledzinski
    Gynaecological Consultant
    Gynae Consulting Platform
    """
    name = request.form.get("name", "Anonymous")
    

return render_template("thankyou.html")

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
