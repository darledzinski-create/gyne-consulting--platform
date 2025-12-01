from flask import Flask, render_template, request
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Ask a Question page
@app.route("/ask")
def ask_page():
    return render_template("ask.html")


# About the Doctor page
@app.route("/about")
def about():
    return render_template("about.html")


# Process submitted question
@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")

    # Build the email
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

    # Send the email via Gmail with your App Password
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(
                os.environ.get("EMAIL_ADDRESS"),
                os.environ.get("EMAIL_PASSWORD")
            )
            smtp.send_message(msg)

        return render_template("thankyou.html")

    except Exception as e:
        return f"An error occurred while sending the email: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=500
