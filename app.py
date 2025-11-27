from flask import Flask, render_template, request, redirect
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# -----------------------------
# Email Configuration
# -----------------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "darledzinski@gmail.com"
EMAIL_PASSWORD = "4537589200336905"   # <-- Your Gmail App Password


def send_confirmation_email(patient_email, patient_name):
    subject = "Your Consultation Question Has Been Received"
    body = f"""
Dear {patient_name if patient_name else 'Patient'},

Thank you for submitting your private gynaecological consultation question.
I have received your message and will respond as soon as possible.

Warm regards,
Dr. Dariusz Ledzinski
Gynae Consulting Platform
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = patient_email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [patient_email], msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", e)


# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask")
def ask_page():
    return render_template("ask.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name")
    email = request.form.get("email")
    question = request.form.get("question")

    # Send confirmation email
    send_confirmation_email(email, name)

    return redirect("/thankyou")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

