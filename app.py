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
def about_page():
    return render_template("about.html")

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")

    # Build the email content
    body = f"""
A new consultation has been submitted.

Name: {name}
Email: {email}

Question:
{question}
"""

    msg = MIMEText(body)
    msg["Subject"] = "New Consultation Request"
    msg["From"] = os.environ.get("MAILJET_FROM_EMAIL")
    msg["To"] = os.environ.get("MAILJET_FROM_EMAIL")

    try:
        with smtplib.SMTP(os.environ.get("MAILJET_SMTP_SERVER"), 587) as smtp:
            smtp.starttls()
            smtp.login(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            )
            smtp.send_message(msg)

        return render_template("thankyou.html")

    except Exception as e:
        return f"An error occurred while sending the email: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=500)
