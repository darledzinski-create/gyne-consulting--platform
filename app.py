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

app.secret_key = supersecretkey123"

@app.route("/")

def homepage():

    return render_template("home.html")

@app.route("/consultation", methods=["GET", "POST"])

def consultation():

    if request.method == "POST":
        print("  NEW REQUEST  ")

        # Prevent double submission (refresh / double click)
        if "last_submit" in session:
            if time.time() - session["last_submit"] < 3:
                print("⚠️ Duplicate submission blocked")
                return redirect(url_for("thank_you"))

        session["last_submit"] = time.time()

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

            urgency_clean = (urgency or "").strip().lower()

            print("STEP 2 - after urgency_clean:", urgency_clean)

            if urgency_clean == "urgent":
                
                patient_message = f"""Dear {name},
      
            Your request has been received.

            IMPORTANT:
            Please seek immediate in-person medical care.
            This platform is not suitable for urgent conditions.

            Kind regards,
            Dr Dariusz
            """
                doctor_message = f"""URGENT CASE

            Name: {name}
            Email: {email}
            """
            else:

                patient_message = f"""Dear {name},

            Thank you for your consultation request.
            We will review your case and respond within 24 hours.

            Kind regards,
            Dr Dariusz
            """

                doctor_message = f"""NON-URGENT CASE

            Name: {name}
            Email: {email}
            """

            data_doctor =  {
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
                        "Subject": f"New Consultation - {'URGENT' if urgency_clean == 'urgent' else 'NON URGENT'}",
                        "HTMLPart": f"""
                        <html>
                        <body style="font-family: Arial, sans-serif;">
                        <h2> New Consultation - {urgency_clean.upper()}</h2>

                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>

                        </body>
                        </html>
                        """
                    },
                ]
            }
            
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
                        "HTMLPart": f"""
                        <html>
                        <body style="font-family: Arial, sans-serif; background-color:#f5f7fa; padding:20px;">
                          <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:8px;">

                            <h2 style="color:#2c3e50;">Consultation Request Received</h2>

                            <p>Dear {name},</p>

                            {"<p style='color:#c0392b; font-weight:bold;'>Please seek immediate in-person medical care. This platform is not suitable for urgent conditions.</p>" if urgency_clean == "urgent" else "<p>Thank you for your consultation request. We will review your case and respond within 24 hours.</p>"}

                            <hr>

                            <p style="color:#777;">Kind regards,<br>Dr Dariusz</p>

                         </div>
                       </body>
                       </html>
                       """
                    }
                ]
            }

            try:

                print("📧 ABOUT TO SEND EMAIL")

                # Send doctor email

                result1 = mailjet.send.create(data=data_doctor)
                print("DOCTOR RESPONSE:", result1.json())

                # Send patient email
                result2 = mailjet.send.create(data=data_patient)
                print("PATIENT RESPONSE:", result2.json())

            except Exception as e:

                print("❌ MAIL ERROR:", e)

            return redirect(url_for("thank_you"))

        except Exception as e:

            print("ERROR:", e)

            return "Something went wrong", 500

    return render_template("consultation.html")

# ✅ MUST BE OUTSIDE

@app.route("/thank-you")

def thank_you():

    return render_template("thank_you.html")
