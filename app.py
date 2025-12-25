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
        return render_template("error.html", message="Email and question are required.")

    # --- Send confirmation email via Mailjet ---
    try:
        mailjet = Client(
            auth=(os.environ.get("MJ_APIKEY_PUBLIC"), os.environ.get("MJ_APIKEY_PRIVATE")),
            version="v3.1"
        )

        email_body = f"""
Dear {name or "Patient"},

Thank you for your message.

Your question has been received and will be reviewed personally.

If clarification is needed, you may be contacted using the details you provided.
Otherwise, you can expect a thoughtful response once your concern has been carefully considered.

Please note that response times may vary depending on the nature of the inquiry and clinical priorities.

If your concern becomes acute or urgent, please seek immediate in-person medical care.

Kind regards,
Dr Dariusz
"""

        data = {
            "Messages": [
                {
                    "From": {
                        "Email": "noreply@drdariuszconsults.com",
                        "Name": "Dr Dariusz Consults"
                    },
                    "To": [
                        {
                            "Email": email,
                            "Name": name or "Patient"
                        }
                    ],
                    "Subject": "We have received your message",
                    "TextPart": email_body
                }
            ]
        }

        mailjet.send.create(data=data)

    except Exception as e:
        print("Mailjet error:", e)

    # --- Show Thank You page ---

    v        # Patient confirmation email
        patient_payload = {
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
                    "Subject": "We have received your consultation request",
                    "TextPart": f"""
Dear {name},

Thank you for contacting the Gynae Consulting Platform.

Your question has been received and will be reviewed carefully.
If further clarification is required, you may be contacted by email.

Please note:
This service does not replace emergency or urgent medical care.

Kind regards,
Gynae Consulting Platform
"""
                }
            ]
        }

        requests.post(
            url,
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            ),
            json=patient_payload
        )       
    return render_template("thank_you.html")
# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
