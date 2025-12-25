from flask import Flask, render_template, request, redirect
import os
import requests

app = Flask(__name__)

# ------------------------
# ROUTES
# ------------------------

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
    name = request.form.get("name", "Patient")
    email = request.form.get("email")
    question = request.form.get("question")

    # --- Confirmation email text (plain text) ---
    confirmation_text = f"""
Dear {name},

Thank you for submitting your question to the Gynae Consulting Platform.

Your message has been safely received. I will review your question carefully
and respond as soon as possible.

Please note that this service is not intended for urgent or acute medical matters.

Warm regards,
Dr Dariusz Ledzinski
"""

    # --- Send confirmation email via Mailjet ---
    try:
        requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            ),
            json={
                "Messages": [
                    {
                        "From": {
                            "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                            "Name": "Gynae Consulting Platform"
                        },
                        "To": [
                            {
                                "Email": email,
                                "Name": name
                            }
                        ],
                        "Subject": "We have received your message",
                        "TextPart": confirmation_text
                    }
                ]
            }
        )
    except Exception:
        pass  # Never block the user flow

    return redirect("/thankyou")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
