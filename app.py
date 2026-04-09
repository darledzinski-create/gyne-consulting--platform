from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
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

        print(name, email, message)

        # SAVE TO FILE
        with open("submissions.txt", "a") as f:
            f.write(f"{datetime.now()} | {name} | {email} | {message}\n")

        # EMAIL BODY TO YOU
        body = f"""
NEW CONSULTATION REQUEST

Name: {name}
Email: {email}

Main Concern:
{message}

Symptoms:
{symptoms}

Duration:
{duration}

Urgency:
{urgency}

Medical History:
{history}
"""

        try:
            import os
            import smtlib
            from email.mime.text import MIMEText

            print("CONNECTING TO EMAIL SERVER")

            msg = MIMEText(body, "plain")
            msg["Subject"] = "New Consultation Submission"
            msg["From"] = "darledzinski@gmail.com"
            msg["To"] = "darledzinski@gmail.com"

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(
                    os.environ.get("EMAIL_USER"),
                    os.environ.get("EMAIL_PASS")
                )
                # SEND TO YOU
                server.send_message(msg)

               
                # ===== CLIENT EMAIL =====
                IF urgency == "Urgent":
                    confirmation_body = f"""

Dear {name},

Your requestnhas been received.

Based on your selection, your condition may require urgent medical attention.

Please seek immediate in-person care

This platform is not suitable foremergencies.

Kind regards,
Dr Dariusz
"""  

              else:
                  confirmation_body = f"""

Dear {name},

Thank you for reaching out.

Your message has been received and will be reviewed carefully.

You will receive a response within 24 hours.

Kind regards,
Dr Dariusz
"""

                if email:
                    confirmation_msg = MIMEText(confirmation_body, "html")
                    confirmation_msg["Subject"] = "We received your consultation request"
                    confirmation_msg["From"] = "darledzinski@gmail.com"
                    confirmation_msg["To"] = email

                    server.send_message(confirmation_msg)

            print("EMAILS SENT")

        except Exception as e:
            print("EMAIL ERROR:", str(e))

        return redirect(url_for("thank_you"))

    return render_template(consultation.html")

@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__=="__":
    app.run(debug=True)
