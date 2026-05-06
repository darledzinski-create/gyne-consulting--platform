from flask import Flask, request, redirect, url_for, render_template, session
from datetime import datetime
import os
import time

from mailjet_rest import Client
mailjet = Client(
    auth=(os.environ.get("MAILJET_API_KEY"), os.environ.get("MAILJET_SECRET_KEY")),
    version='v3.1'
)

print("🚀 NEW VERSION ACTIVE 🚀")

app = Flask(__name__)

app.secret_key = "supersecretkey123"

@app.route("/")

def homepage():

    return render_template("home.html")

@app.route("/consultation", methods=["GET", "POST"])
def consultation():

    if request.method == "POST":
        
        try:
            print("🔥🔥🔥 NEW CODE VERSION 2 ACTIVE 🔥🔥🔥")
            print("🚀 NEW VERSION ACTIVE 🚀")
            print("🔥 POST RECEIVED")
            
            name = request.form.get("name")
            email = request.form.get("email")
            urgency = request.form.get("urgency")

            print("RAW URGENCY:", repr(urgency))

            urgency_clean = (urgency or "").strip().lower()

            # 🔥 THIS IS THE MISSING PIECE
            urgency_clean = urgency_clean.replace(" ", "_")

            print("FINAL URGENCY:", repr(urgency_clean))

            print("REDIRECTING WITH:", repr(urgency_clean))
           
            
            # ----------------------------
            # 1. Decide subject
            # ----------------------------

           
            if urgency_clean == "urgent":
                # urgent case
                subject = "URGENT CONSULTATION"

                patient_text = f"""..."""

            elif urgency_clean == "not_urgent":
                # non-urgent case
                subject = "Consultation Request"

                patient_text = f"""..."""

            else:
                print("UNKNOWN URGENCY:", repr(urgency_clean))
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
                        "To": [{"Email": "darledzinski@gmail.com"}],
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
    urgency = request.args.get("urgency", '')
    print("THANK YOU PAGE RECEIVED:", urgency)
    return render_template("thank_you.html", urgency=urgency)
