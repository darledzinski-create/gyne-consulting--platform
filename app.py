from flask import Flask, request, redirect, url_for, render_template

from mailjet_rest import Client

import os

app = Flask(__name__)

@app.route("/")

def homepage():

    return render_template("home.html")

@app.route("/consultation", methods=["GET", "POST"])

def consultation():

    if request.method == "POST":

        try:

            print("🔥 POST RECEIVED")

            name = request.form.get("name")

            email = request.form.get("email")

            urgency = request.form.get("urgency")

            print("NAME:", repr(name))

            print("EMAIL:", repr(email))

            print("URGENCY:", repr(urgency))

            urgency_clean = (urgency or "").strip().lower()

            if urgency_clean == "urgent":

                patient_message = f"""
                Dear {name},

                Your request has been received.

                IMPORTANT:
                Please seek immediate in-person medical care.
                This platform is not suitable for urgent conditions.

                Kind regards,
                Dr Dariusz
                """

                doctor_message = f"""
                🚨 URGENT CASE

                Name: {name}
                Email: {email}
                """
            else:

                patient_message = f"""
                Dear {name},

                Thank you for your consultation request.
                We will review your case and respond within 24 hours.

                Kind regards,
                Dr Dariusz
                """

                doctor_message = f"""
                NON-URGENT CASE

                Name: {name}
                Email: {email}
                """

            data = {
                "Messages": [

                    # 📧 Email to YOU
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
                        "Subject": f"New Consultation ({urgency_clean})",
                        "TextPart": doctor_message
                    },
                    # 📧 Email to PATIENT
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
                        "TextPart": patient_message
                    }
                ]
            }

            try:

                result = mailjet.send.create(data=data)

                print("STATUS:", result.status_code)

                print("BODY:", result.json())

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
