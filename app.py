from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

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
        message = request.form.get("message")
        symptoms = request.form.get("symptoms")
        duration = request.form.get("duration")
        urgency = request.form.get("urgency")
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

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                print("EMAIL_USER:", os.environ.get("EMAIL_USER"))
                print("EMAIL_PASS:", os.environ.get("EMAIL_PASS"))
                server.login(
                    os.environ.get("EMAIL_USER"),
                    os.environ.get("EMAIL_PASS")
                )

                # ✅ EMAIL TO YOU (ONLY ONCE)
                msg = MIMEText(body, "plain")
                msg["Subject"] = "New Consultation Submission"
                msg["From"] = os.environ.get("EMAIL_USER")
                msg["To"] = os.environ.get("EMAIL_USER")

                server.send_message(msg)

                # ✅ BUILD CLIENT EMAIL
                if urgency and urgency.lower() == "urgent":
                    confirmation_body = f"""Dear {name},

Your request has been received.

Based on your selection, your condition may require urgent medical attention.

Please seek immediate in-person care.

This platform is not suitable for emergencies.

Kind regards,
Dr Dariusz
"""
                else:
                    confirmation_body = f"""Dear {name},

Thank you for reaching out.

Your message has been received and will be reviewed carefully.

You will receive a response within 24 hours.

Kind regards,
Dr Dariusz
"""

                # ✅ EMAIL TO CLIENT (ONLY ONCE)
                if email:
                    confirmation_msg = MIMEText(confirmation_body, "plain")
                    confirmation_msg["Subject"] = "We received your consultation request"
                    confirmation_msg["From"] = os.environ.get("EMAIL_USER")
                    confirmation_msg["To"] = email

                    server.send_message(confirmation_msg)

                print("✅ EMAILS SENT")

        except Exception as e:
            print("❌ EMAIL ERROR:", str(e))

        return redirect(url_for("thank_you"))

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
