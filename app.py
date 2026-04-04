from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime   # ✅ MOVE THIS TO THE TOP
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route("/")
def homepage():
    return render_template("first-consultation.html")

@app.route("/consultation", methods=["GET", "POST"])
def consultation():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        print(name, email, message)  # debug

        # ✅ SAVE DATA (correct indentation)
        with open("submissions.txt", "a") as f:
            f.write(f"{datetime.now()} | {name} | {email} | {message}\n")
        
        # ✅ ADD THIS EMAIL BLOCK HERE
        subject = "New Consultation Submission"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "darledzinski@gmail.com"
        msg["To"] = "darledzinski@gmail.com"

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("darledzinski@gmail.com", "glttpxgyezwnzozl")
                server.send_message(msg)
            print("✅ Email sent successfully")
       
        except Exception as e:
           print("❌ Email failed:", e)

        return redirect(url_for("thank_you"))

    return render_template("index.html")


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


if __name__ == "__main__":
    app.run(debug=True)
