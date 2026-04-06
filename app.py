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

       
        # Create email to YOU
        body = f"""
        <html>
        <body style="margin:0; padding:0; background-color:#f5f7fa; font-family: Arial, sans-serif;">

        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
        <td align="center">

        <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden;">

        <tr>
        <td style="background:#2c3e50; color:white; padding:15px;">
        <strong>New Consultation Request</strong>
        </td>
        </tr>

        <tr>
        <td style="padding:20px;">

        <p><strong>Name:</strong><br>{name}</p>
        <p><strong>Email:</strong><br>{email}</p>

        <p><strong>Message:</strong></p>

        <div style="background:#f0f2f5; padding:15px; border-radius:6px;">
        {message}
        </div>

        </td>
        </tr>

        </table>

        </td>
        </tr>
        </table>

        </body>
        </html>
        """
        
        try:
            print("CONNECTING TO EMAIL SERVER")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("darledzinski@gmail.com", "umifeyujipwnweml")

                # Send to YOU
                server.send_message(msg)

                # Create confirmation email
                confirmation_body = f"""
Dear {name},

Thank you for reaching out.

Your message has been received and will be reviewed carefully and personally.

Many concerns become clearer once they are properly discussed.

If your symptoms are severe, worsening, or urgent, please seek immediate in-person medical care.

You will receive a response within 24 hours.

Kind regards,
Dr Dariusz
"""

                confirmation_msg = MIMEText(confirmation_body, "html")
                confirmation_msg["Subject"] = "We received your consultation request"
                confirmation_msg["From"] = "darledzinski@gmail.com"
                confirmation_msg["To"] = email

                # Send to CLIENT
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
