from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask")
def ask():
    return render_template("ask.html")

v@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email", "").strip()
    question = request.form.get("question", "").strip()

    # Basic validation
    if not email or not question:
        return render_template("ask.html", error="Please provide your email and question.")

    # Build email body (no sending yet if Mailjet fails)
    email_body = f"""
A new consultation has been submitted.

Name: {name}
Email: {email}

Question:
{question}
"""

    try:
        # --- OPTIONAL: Mailjet send (can fail safely) ---
        # If Mailjet is not configured, this block can be removed
        url = "https://api.mailjet.com/v3.1/send"
        payload = {
            "Messages": [
                {
                    "From": {
                        "Email": os.environ.get("MAILJET_FROM_EMAIL", "no-reply@example.com"),
                        "Name": "Gynae Consulting Platform"
                    },
                    "To": [
                        {
                            "Email": os.environ.get("MAILJET_TO_EMAIL", "doctor@example.com"),
                            "Name": "Dr Dariusz"
                        }
                    ],
                    "Subject": "New Consultation Request",
                    "TextPart": email_body
                }
            ]
        }

        # Comment this out if Mailjet causes issues
        requests.post(
            url,
            auth=(
                os.environ.get("MAILJET_API_KEY", ""),
                os.environ.get("MAILJET_SECRET_KEY", "")
            ),
            json=payload,
            timeout=10
        )

    except Exception as e:
        # IMPORTANT: still return a page even if email fails
        print("Email error:", e)

    # ✅ FINAL, GUARANTEED RETURN
    return render_template("thankyou.html")
    
@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")

if __name__ == "__main__":
    app.run()
