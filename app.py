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
        print("EMAIL:" "22mozorro@gmail.com")
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

             urgency_clean = (urgency or "").strip().lower()
             print("CLEAN URGENCY:", urgency_clean)

             confirmation_body = f"""
             <html>
             <body>
                 <h2>Consultation Received</h2>
                 <p>Dear {name},</p>
                 <p>We received your request.</p>
                 <p>We will respond within 24 hours.</p>
                 <p>Kind regards,<br>Dr Dariusz</p>
             </body>
             </html>
             """

             data = {
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
                         "Subject": "Consultation received",
                         "HTMLPart": confirmation_body

                     }

                ]

           }

           print("SENDING EMAIL TO:", email)

           result = mailjet.send.create(data=data)

           print("MAILJET STATUS:", result.status_code)
           print("MAILJET RESPONSE:", result.json())

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
