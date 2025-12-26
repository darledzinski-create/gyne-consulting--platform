from flask import Flask, render_template, request, redirect
from mailjet_rest import Client
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

# ================================
# SUBMIT QUESTION + CONFIRMATION EMAIL
# ================================
@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    question = request.form.get("question", "").strip()

    # Basic validation
    if not email or not question:
        return render_template(
            "error.html",
            message="Email and question are required."
        )

    # Initialize Mailjet client
    mailjet = Client(
        auth=(
            os.environ.get("MAILJET_API_KEY"),
            os.environ.get("MAILJET_SECRET_KEY")
        ),
        version="v3.1"
    )

    # Email content
    data = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": "Dr Dariusz Gynecological Consults"
                },
                "To": [
                    {
                        "Email": os.environ.get("MAILJET_TO_EMAIL"),
                        "Name": name or "Patient"
                    }
                ],
                "Subject": "New Gynecological Consultation Request",
                "TextPart": f"""
New consultation request received.

Name: {name}
Email: {email}

Question:
{question}
"""
            }
        ]
    }

    # Send email
    try:
        result = mailjet.send.create(data=data)
        print("Mailjet response:", result.status_code, result.json())
    except Exception as e:
        print("Mailjet error:", str(e))

    return render_template("thank_you.html")
# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
