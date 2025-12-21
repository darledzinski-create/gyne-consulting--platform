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
    # Confirmation email to patient (if email provided)
    if email:
    patient_message = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": "Dr Dariusz Consults"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": name
                    }
                ],
                "Subject": "Your message has been received",
                "TextPart": f"""
Dear {name},

Thank you for your message.

Your question has been received and will be reviewed personally.
If any clarification is required, you may be contacted using the details you provided.

Otherwise, you can expect a thoughtful response once your concern has been carefully considered.
Please note that response times may vary depending on clinical priorities.

If your concern becomes acute or urgent, please seek immediate in-person medical care.

Kind regards,
Dr Dariusz
"""
            }
        ]
    }

    requests.post(
        "https://api.mailjet.com/v3.1/send",
        auth=(
            os.environ.get("MAILJET_API_KEY"),
            os.environ.get("MAILJET_SECRET_KEY")
        )
        json=patient_message

if __name__=="__main__":
    app.run(host="0.0.0.",port=5000)
