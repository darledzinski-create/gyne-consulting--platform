from flask import Flask, render_template, request
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask")
def ask_page():
    return render_template("ask.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")

    body = f"""
A new consultation has been submitted.

Name: {name}
Email: {email}

Question:
{question}
"""

    msg = MIMEText(body)
    msg["Subject"] = "New Consultation Request"
    msg["From"] = os.environ.get("EMAIL_ADDRESS")
    msg["To"] = os.environ.get("EMAIL_ADDRESS")

    try:
        smtp_server = os.environ.get("MAILJET_SMTP_SERVER")
        smtp_user = os.environ.get("MAILJET_API_KEY")
        smtp_pass = os.environ.get("MAILJET_SECRET_KEY")

        with smtplib.SMTP(smtp_server, 587) as smtp:

            # *** FIX: establish explicit connection first ***
            smtp.connect(smtp_server, 587)

            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

        return render_template("thankyou.html")

    except Exception as e:
        return f"An error occurred while sending the email: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=500)
