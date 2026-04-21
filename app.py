from flask import Flask, request, redirect, url_for, render_template
from datetime import datetime
import os
from mailjet_rest import Client

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

            # CLEAN VALUE

            urgency_clean = (urgency or "").strip().lower()

            # SIMPLE LOGIC TEST

            if urgency_clean == "urgent":
                print("🚨 URGENT CASE")
            else:
                print("🟢 NON-URGENT CASE")
                # 📧 EMAIL SETUP

            mailjet = Client(
                auth=(
                    os.environ.get("MAILJET_API_KEY"),
                    os.environ.get("MAILJET_SECRET_KEY")
                ),
                version='v3.1'
            )

            urgency_clean = (urgency or "").strip().lower()

            # SIMPLE MESSAGE
            if urgency_clean == "urgent":
                text_message = f"""
            URGENT CONSULTATION

            Name: {name}
            Email: {email}

           ⚠️ This case was marked as URGENT.
            Advise immediate in-person care.
            """
            else:
                text_message = f"""
            New consultation received:

            Name: {name}
            Email: {email}

            This is a non-urgent request.
            """

            print("📧 SENDING EMAIL NOW")

            data = {
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
                        "Subject": "New Consultation",
                        "TextPart": text_message
                    }
                ]
            }
         
            try:
                result = mailjet.send.create(data=data)
                print("STATUS:", result.status_code)
                print("BODY:", result.json())

            except Exception as e:
                print("❌ MAIL ERROR:", e)

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")
