from flask import Flask, request, redirect, url_for, render_template, session
from datetime import datetime
import os
import time

from mailjet_rest import Client
mailjet = Client(
    auth=(os.environ.get("MAILJET_API_KEY"), os.environ.get("MAILJET_SECRET_KEY")),
    version='v3.1'
)

app = Flask(__name__)

app.secret_key = "supersecretkey123"

@app.route("/")

def homepage():

    return render_template("home.html")

@app.route("/consultation", methods=["GET", "POST"])
def consultation():

    if request.method == "POST":
        if session.get("submitted"):
            return redirect(url_for("thank_you"))

        session["submitted"] = True
        
        try:
            print("🔥 POST RECEIVED")
            
            name = request.form.get("name")
            email = request.form.get("email")
            urgency = request.form.get("urgency")

            if not name or not email or not urgency:
                return "Missing required fields", 400

            if "@" not in email:
                return "Invalid email", 400

            urgency_clean = (urgency or "").strip().lower()
            print("DEBUG URGENCY:", urgency_clean)

            # ----------------------------
            # 1. Decide subject
            # ----------------------------

            if urgency_clean == "urgent":
                subject = "URGENT CONSULTATION"
                
                patient_text = f"""
            Dear {name},

            Your request has been received.

            IMPORTANT:
            Please seek immediate in-patient medical care.
            This platform is not suitable for urgent conditions.

            Kind regards,
            Dr Dariusz
            """
            
            elif urgency_clean == "not_urgent":
                subject = "Consultation Request"

                patient_text = f"""
            Dear {name},

            Thank you for your consultation request.
            We will review your case and respond within 24 hours.

            Kind regards,
            Dr Dariusz
            """
            else:
                print(" UNKNOWN URGENCY:", urgency_clean)
                return "Invalid submission", 400
            
            doctor_text = f"""
            New Consultation ({urgency_clean.upper()})
            Name: {name}
            Email: {email}
            """
            
            data_doctor = {
                "Messages": [
                    {
                        "From": {
                            "Email": "contact@drdariuszconsults.com",
                            "Name": "Consultation System"
                        },
                        "To": [{"Email": "your_real_@email.com"}],
                        "Subject": subject,
                        "TextPart": doctor_text
                    }
                ]
            }

            data_patient = {
                "Messages": [
                    {
                        "From": {
                            "Email": "contact@drdariuszconsults.com",
                            "Name": "Dr Dariusz"
                            },
                            "To": [{"Email": email}],
                            "Subject": subject,
                            "TextPart": patient_text
                    }
                ]

            }
            
            print("SENDING DOCTOR EMAIL")
            result_doctor = mailjet.send.create(data=data_doctor)
            print("DOCTOR STATUS:", result_doctor.status_code)
            
            print("SENDING PATIENT EMAIL")
            result_patient = mailjet.send.create(data=data_patient)
            print("PATIENT STATUS:", result_patient.status_code)
            session.pop("submitted", None)
            print("REDIRECT WITH:", urgency_clean)
            print("REDIRECTING WITH:", urgency_clean)
            print("🔥 NEW VERSION ACTIVE 🔥", urgency_clean)
            return redirect(url_for("thank_you", urgency=urgency_clean))

        except Exception as e:
            print("❌ ERROR:", e)
            return "Something went wrong", 500

    return render_template("consultation.html")


@app.route("/thank-you")

def thank_you():
    urgency = request.args.get("urgency")
    print("THANK YOU PAGE RECEIVED:", urgency)
    return render_template("thank_you.html", urgency=urgency)
