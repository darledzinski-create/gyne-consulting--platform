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
    print("MAILJET RAW RESPONSE:")
    print(result.json())
    print("END MAILJET RESPONSE")
    return result.status_code

def send_intake_emails(intake_data):
    try:
        # =========================
        # EMAIL TO YOU (CLINICAL)
        # =========================
        admin_body = "\n".join(
            [f"{key}: {value}" for key, value in intake_data.items()]
        )

        mailjet.send.create(data={
            "Messages": [
                {
                    "From": {
                        "Email": "no-reply@drdariuszconsults.com",
                        "Name": "Gyne Consulting Platform"
                    },
                    "To": [
                        {
                            "Email": os.environ.get("ADMIN_EMAIL"),
                            "Name": "Dr Dariusz"
                        }
                    ],
                    "Subject": "New Patient Intake Submission",
                    "TextPart": f"NEW INTAKE SUBMISSION:\n\n{admin_body}"
                }
            ]
        })

        # =========================
        # EMAIL TO PATIENT
        # =========================
        patient_email = intake_data.get("email")

        if patient_email:
            mailjet.send.create(data={
                "Messages": [
                    {
                        "From": {
                            "Email": "no-reply@drdariuszconsults.com",
                            "Name": "Gyne Consulting Platform"
                        },
                        "To": [
                            {
                                "Email": patient_email
                            }
                        ],
                        "Subject": "We have received your request",
                        "TextPart": (
                            "Thank you for your submission.\n\n"
                            "Your request has been received and will be reviewed.\n\n"
                            "If your symptoms worsen or you require urgent care, "
                            "please seek immediate in-person medical attention.\n\n"
                            "— Gyne Consulting Platform"
                        )
                    }
                ]
            })

        print("Emails sent successfully")

    except Exception as e:
        print("EMAIL ERROR:", str(e))
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
    print("STEP A - route entered")
    
    if request.method == "POST":
        print("STEP B - POST detected")
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
        
        print("ABOUT TO CALL send_doctor_email")
        send_doctor_email(intake_data)
        print("RETURNING RESPONSE")

        print("STEP C - intake data built")
        print(intake_data)

        print("STEP D - about to call send_doctor_email")
        send_doctor_email(intake_data)
        print("STEP E - send_doctor_email returned")

    payload = {
    "Messages": [{
        "From": {
            "Email": os.environ.get("MAILJET_DOCTOR_EMAIL"),
            "Name": os.environ.get("MAILJET_FROM_NAME")
        },
        "To": [{
            "Email": os.environ.get("MAILJET_TO_EMAIL")
        }],
        "Subject": "New Online Gynaecology Intake",
        "TextPart": body
    }]

    }

        result = mailjet.send.create(data=payload)
        log_mailjet_response(result)

        return "Thank you"

        # GET request
        return render_template("intake.html")

        print("NEW INTAKE SUBMISSION:")
        for k, v in intake_data.items():
            print(f"{k}: {v}")
        
       
    # GET request
    return render_template("intake.html")

@app.route("/intake-submitted")
def intake_submitted():
    return render_template("intake_submitted.html")

@app.route("/test-email")
def test_email():
    send_email(
        to_email=os.environ.get("MAILJET_DOCTOR_EMAIL"),
        subject="Test email – Doctor",
        text="This is a test email to confirm Mailjet is working."
    )

    send_email(
        to_email=os.environ.get("MAILJET_TEST_PATIENT_EMAIL"),
        subject="Test email – Patient",
        text="This is a test email to confirm patient notifications work."
    )
    return "Test emails sent successfully."

def send_doctor_email(intake_data):
    print("ABOUT TO CALL send_doctor_email")
    print("SEND_DOCTOR_EMAIL called")
    print("INTAKE DATA",intake_data)

    result = mailjet.send.create(data=payload)
    log_mailjet_response(result)

def log_mailjet_response(result):
    print("MAILJET HTTP STATUS:", result.status_code)

    try:
        response = result.json()
        print("MAILJET RAW RESPONSE:", response)

        message = response["Messages"][0]
        print("MAILJET MESSAGE STATUS:", message.get("Status"))

        if "To" in message and message["To"]:
            message_id = message["To"][0].get("MessageID")
            print("MAILJET MESSAGE ID:", message_id)

    except Exception as e:
        print("MAILJET RESPONSE PARSE ERROR:", str(e))
        
    payload= {
        "Messages": [{
            "From": {
                "Email": os.environ.get("MAILJET_DOCTOR_EMAIL"),
                "Name": os.environ.get("MAILJET_FROM_NAME")
            },
            "To": [{
                "Email": os.environ.get("MAILJET_TO_EMAIL")
            }],
            "Subject": "New Online Gynaecology Intake",
            "TextPart": body
            }]
    }
    
    response = result.json()
    message = response["Messages"][0]

    status = message["Status"]
    print("MAILJET STATUS:", status)

    if "To" in message and message["To"]:
        message_id = message["To"][0].get("MessageID")
        print("MAILJET MESSAGE ID:", message_id)

    status = result.status_code
    print("MAILJET DOCTOR STATUS:", status)

    if status != 200:
       print("WARNING: Doctor email failed:", result.json())
       return

def send_patient_email(intake_data):
    patient_email = intake_data.get("email")

    if not patient_email:
        print("No patient email provided — skipping")
        return

    body = (
        "Dear Patient,\n\n"
        "Your consultation request has been received and will be reviewed.\n\n"
        "If your symptoms worsen or you require urgent care, please seek immediate medical attention.\n\n"
        "Kind regards,\n"
        "Dr Dariusz Ledzinski"
    )

    try:
        print("SENDING PATIENT EMAIL TO:", patient_email)

        result = mailjet.send.create(data={
            "Messages": [{
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": os.environ.get("MAILJET_FROM_NAME")
                },
                "To": [{
                    "Email": patient_email
                }],
                "Subject": "Your consultation request has been received",
                "TextPart": body
            }]
        })

        print("MAILJET PATIENT STATUS:", result.status_code)

    except Exception as e:
        print("PATIENT EMAIL FAILED:", str(e))
