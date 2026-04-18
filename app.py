from flask import Flask, render_template, request, redirect, url_for
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
        print("FORM SUBMITTED")

        name = request.form.get("name")
        email = request.form.get("email")
        if not email:
            return "MISSING EMAIL", 400
        message = request.form.get("message")
        symptoms = request.form.get("symptoms")
        duration = request.form.get("duration")
        urgency = request.form.get("urgency")
        print("URGENCY RAW:", repr(urgency))
        print("FINAL EMAIL:", "22mozorro@gmail.com")
        history = request.form.get("history")

        # SAVE TO FILE
        with open("submissions.txt", "a") as f:
            f.write(f"{datetime.now()} | {name} | {email} | {message}\n")

        # EMAIL BODY TO YOU
        body = f"""
NEW CONSULTATION REQUEST

Name: {name}
Email: {email}

Message:
{message}

Symptoms:
{symptoms}

Duration:
{duration}

Urgency:
{urgency}

History:
{history}
"""

        try:
            print("CONNECTING TO EMAIL SERVER")

            mailjet = Client(
                auth=(
                    os.environ.get("MAILJET_API_KEY"),
                    os.environ.get("MAILJET_SECRET_KEY")
                ),
                version='v3.1'
            )

            # ✅ BUILD EMAIL FIRST
            urgency_clean = (urgency or "").strip().lower()
            print("CLEAN URGENCY:", urgency_clean)
            if urgency_clean == "urgent":
                confirmation_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color:#c0392b;">Important</h2>
                    <p>Dear {name},</p>
                    <p>Your request has been received.</p>
                    <p style="color:#c0392b; font-weight:bold;">
                        Based on your selection, your condition may require urgent medical attention.
                        Please seek immediate in-person care.
                    </p>
                    <p>This platform is not suitable for emergencies.</p>
                    <p>Kind regards,<br>Dr Dariusz</p>
                </body>
                </html>
                """
            else:
                confirmation_body = f"""

                <html>

                <body>

                <h2 style="color:red;">Important</h2>

                <p>Dear {name},</p>

                <p>Your request has been received.</p>

                <p><strong>Please seek immediate care.</strong></p>

                <p>This platform is not for emergencies.</p>

                <p>Kind regards,<br>Dr Dariusz</p>

                </body>

                </html>

                """

            # ✅ SEND EMAIL WITH MAILJET
            data = {
                     "Messages": [
                         {
                             "From": {
                                 "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                                 "Name": "Dr Dariusz"
                             },
                             "To": [
                                 {
                                     "Email": email,
                                     "Name": name
                                 }
                             ],
                             "Subject": "We received your consultation request",
                             "HTMLPart": confirmation_body
                         }
                     ]
                 }
            print("SENDING EMAIL WITH:", email)
            print("ENTERED NON-URGENT BRANCH")
            print("ENTERED URGENT BRANCH")
            print("BODY PREVIEW:", confirmation_body[:100])
            
            result = mailjet.send.create(data=data)
            
            print("MAILJET STATUS:", result.status_code)
            print("MAILJET RESPONSE:",result.json())
            
        except Exception as e:
            print("❌ FULL ERROR:", repr(e))
            return f"ERROR: {repr(e)}", 500
        return redirect(url_for("thank_you"))

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
