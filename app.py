from flask import Flask, render_template, request, redirect, url_for
from mailjet_rest import Client
import os

app = Flask(__name__)

mailjet = Client(
    auth=(
        os.environ.get("MAILJET_API_KEY"),
        os.environ.get("MAILJET_SECRET_KEY")
    ),
    version="v3.1"
)

def send_email(to_email, subject, text):
    data = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": os.environ.get("MAILJET_FROM_NAME")
                },
                "To": [
                    {
                        "Email": to_email
                    }
                ],
                "Subject": subject,
                "TextPart": text
            }
        ]
    }
    result = mailjet.send.create(data=data)
    return result.status_code

def send_doctor_notification(intake_data):
    subject = "New Gynecology Intake Submission"

    body_lines = []
    for key, value in intake_data.items():
        body_lines.append(f"{key}: {value}")

    body_text = "\n".join(body_lines)

    data = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": os.environ.get("MAILJET_FROM_NAME"),
                },
                "To": [
                    {
                        "Email": os.environ.get("MAILJET_TO_EMAIL"),
                        "Name": "Doctor",
                    }
                ],
                "Subject": subject,
                "TextPart": body_text,
            }
        ]
    }

    mailjet.send.create(data=data)

# --------------------
# ROUTES
# --------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask")
def ask_page():
    return render_template("ask.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/intake", methods=["GET", "POST"])
def intake():

    if request.method == "POST":
        intake_data = {
            "full_name": request.form.get("full_name"),
            "age_dob": request.form.get("age_dob"),
            "country": request.form.get("country"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "concern": request.form.get("concern"),
            "duration": request.form.get("duration"),
            "pregnant": bool(request.form.get("pregnant")),
            "severe_pain": bool(request.form.get("severe_pain")),
            "bleeding": bool(request.form.get("bleeding")),
            "fever": bool(request.form.get("fever")),
            "emergency": bool(request.form.get("emergency")),
            "conditions": request.form.get("conditions"),
            "medications": request.form.get("medications"),
            "allergies": request.form.get("allergies"),
        }

    doctor_email_body = "\n".join(
    f"{key.replace('_', ' ').title()}: {value}"
    for key, value in intake_data.items()
)

send_email(
    to_email=os.environ.get("MAILJET_DOCTOR_EMAIL"),
    subject="New Online Gynaecology Intake",
    text=doctor_email_body
)

patient_email_body = (
    "Dear " + (intake_data.get("full_name") or "Patient") + ",\n\n"
    "Thank you for submitting your online gynaecological consultation request.\n\n"
    "Your information has been received and will be reviewed.\n\n"
    "If your symptoms worsen or you require urgent care, please seek immediate in-person medical attention.\n\n"
    "Kind regards,\n"
    "Dr Dariusz Ledzinski"
)

send_email(
    to_email=intake_data.get("email"),
    subject="Your consultation request has been received",
    text=patient_email_body
)

print("NEW INTAKE SUBMISSION:")
for key, value in intake_data.items():
    print(f"{key}: {value}")
         
send_doctor_notification(intake_data)

return redirect(url_for("intake_submitted"))

    return render_template("intake.html")

@app.route("/intake-submitted")
def intake_submitted():
    return render_template("intake_submitted.html")
