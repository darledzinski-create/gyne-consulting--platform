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

        print(name, email, message)

        # Save to file
        with open("submissions.txt", "a") as f:
            f.write(f"{datetime.now()} | {name} | {email} | {message}\n")

        # ✅ EMAIL TO YOU (DEFINE BODY FIRST)
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
        <h2>New Consultation Request</h2>

        <p><strong>Name:</strong> {name}</p>
        <p><strong>Email:</strong> {email}</p>

        <p><strong>Message:</strong></p>
        <p>{message}</p>

        </body>
        </html>
        """

        msg = MIMEText(body, "html")
        msg["Subject"] = "New Consultation Submission"
        msg["From"] = "darledzinski@gmail.com"
        msg["To"] = "darledzinski@gmail.com"

        try:
            print("CONNECTING TO EMAIL SERVER")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("darledzinski@gmail.com", "umifeyujipwnweml")

                # ✅ SEND TO YOU
                server.send_message(msg)

                # ✅ CONFIRMATION EMAIL TO CLIENT
                confirmation_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif;">
                <h2>Thank you for reaching out</h2>

                <p>Dear {name},</p>

                <p>Your message has been received and will be reviewed carefully.</p>

                <p><strong>You will receive a response within 24 hours.</strong></p>

                <p>Kind regards,<br>Dr Dariusz</p>

                </body>
                </html>
                """

                confirmation_msg = MIMEText(confirmation_body, "html")
                confirmation_msg["Subject"] = "We received your consultation request"
                confirmation_msg["From"] = "darledzinski@gmail.com"
                confirmation_msg["To"] = email

                # ✅ SEND TO CLIENT
                server.send_message(confirmation_msg)

            print("✅ Both emails sent successfully")

        except Exception as e:
            print("❌ EMAIL ERROR:", str(e))

        return redirect(url_for("thank_you"))

    return render_template("consultation.html")
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


if __name__ == "__main__":
    app.run(debug=True)
