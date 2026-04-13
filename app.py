from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        print("URGENCY RECEIVED:", urgency)
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
<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; background-color:#f5f7fa; padding:20px;">

    <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:8px;">

      <h2 style="color:#2c3e50;">Consultation Request Received</h2>

      <p>Dear {name},</p>

      <p>Thank you for reaching out.</p>

      <p>Your message has been received and will be reviewed carefully.</p>

      <p>You will receive a response within <strong>24 hours</strong>.</p>

      <hr style="margin:20px 0;">

      <p style="color:#888;">Kind regards,<br>Dr Dariusz</p>

    </div>

  </body>
</html>
"""
               
                # ✅ EMAIL TO CLIENT (ONLY ONCE)
                if email:
                    confirmation_msg = MIMEMultipart("alternative")
                    confirmation_msg["Subject"] = "We received your consultation request"
                    confirmation_msg["From"] = os.environ.get("EMAIL_USER")
                    confirmation_msg["To"] = email

                    # Plain version (fallback)
                    plain_text = f"Dear {name}, your consultation request has been received."

                    # HTML version
                    html_part = MIMEText(confirmation_body, "html")
                    text_part = MIMEText(plain_text, "plain")

                    confirmation_msg.attach(text_part)
                    confirmation_msg.attach(html_part)

                    server.send_message(confirmation_msg)

                print("✅ EMAILS SENT")

        except Exception as e:
            print("❌ EMAIL ERROR:", str(e))
            return f"ERROR: {str(e)}", 500

        return redirect(url_for("thank_you"))

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run(debug=True)
