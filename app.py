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

        try:
            print("🔥 POST RECEIVED")

            # ✅ ADD IT HERE (CORRECT PLACE)
            

            name = request.form.get("name")

            email = request.form.get("email")

            urgency = request.form.get("urgency")

            print("NAME:", repr(name))

            print("EMAIL:", repr(email))

            print("URGENCY:", repr(urgency))

            print("STEP 1 - before urgency_clean")

            # --- CLEAN EMAIL LOGIC STARTS HERE ---

            # Normalize urgency
            urgency_clean = (urgency or "").strip().lower()

            # Patient message
            if urgency_clean == "urgent":
                patient_text = f"""
                Dear {name},

                Your request has been received.

                IMPORTANT:
                Please seek immediate in-person medical care.
                This platform is not suitable for urgent conditions.

                Kind regards,
                Dr Dariusz
                """
            else:
                patient_text = f"""
                Dear {name},

                Thank you for your consultation request.
                We will review your case and respond within 24 hours.

                Kind regards,
                Dr Dariusz
                """

                # Doctor message
                doctor_text = f"""
                New Consultation ({urgency_clean.upper()})

                Name: {name}
                Email: {email}
                """

                # --- DOCTOR EMAIL ---
                data_doctor = {
                    "Messages": [
                        {
                            "From": {
                                "Email": "contact@drdariuszconsults.com",
                                "Name": "Consultation System"
                            },
                            "To": [
                                {
                                    "Email": "22mozorro@gmail.com",
                                    "Name": "Dr Dariusz"
                                }
                            ],
                            "Subject": f"New Consultation - {urgency_clean.upper()}",
                            "TextPart": doctor_text
                        }
                    ]
                }

                # --- PATIENT EMAIL ---
                data_patient = {
                    "Messages": [
                        {
                            "From": {
                                "Email": "contact@drdariuszconsults.com",
                                "Name": "Dr Dariusz"
                            },
                            "To": [
                                {
                                    "Email": email,
                                    "Name": name
                                }
                            ],
                            "Subject": "Consultation Request Received",
                            "TextPart": patient_text
                        }
                    ]
                }

                # --- SEND EMAILS ---
                print("SENDING DOCTOR EMAIL")
                mailjet.send.create(data=data_doctor)

                print("SENDING PATIENT EMAIL")
                mailjet.send.create(data=data_patient)

                # --- CLEAN EMAIL LOGIC ENDS HERE ---

           
            except Exception as e:
                print("❌ MAIL ERROR:", e)

                session.pop("submitted",None)

            return redirect(url_for("thank_you"))

        except Exception as e:

            print("ERROR:", e)

            return "Something went wrong", 500

    return render_template("consultation.html")

# ✅ MUST BE OUTSIDE

@app.route("/thank-you")

def thank_you():

    return render_template("thank_you.html")
