from flask import Flask, render_template, request
import os
import requests

app = Flask(__name__)

# --------------------
# Core pages
# --------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask")
def ask_page():
    return render_template("ask.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/consent")
def consent():
    return render_template("consent.html")

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")
    
@app.route("/referral")
def referral_notice():
    return render_template("referral.html")

@app.route("/prescriptions")
def prescriptions():
    return render_template("prescriptions.html")

@app.route("/first-consultation")
def first_consultation():
    return render_template("first-consultation.html")
@app.route("/communication")
def communication():
    return render_template("communication.html")
@app.route("/gp-liaison")
def gp_liaison():
    return render_template("gp-liaison.html")
@app.route("/before-you-submit")
def before_you_submit():
    return render_template("before-you-submit.html")

# --------------------
# Form submission
# --------------------

@app.route("/submit_question", methods=["POST"])
def submit_question():
    name = request.form.get("name", "Anonymous")
    email = request.form.get("email")
    question = request.form.get("question")

</html><!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Response to Your Consultation Enquiry</title>
</head>
<body style="margin:0; padding:0; background-color:#f4f6f8; font-family: Arial, Helvetica, sans-serif; color:#333;">

  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:30px 15px;">

        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:8px; padding:30px;">
          
          <tr>
            <td style="font-size:15px; line-height:1.6;">
              <p>Dear {{name}},</p>

              <p>
                Thank you for your message and for taking the time to describe your concern.
              </p>

              <p>
                Based on the information you have shared, I would like to offer the following guidance:
              </p>

              <p style="margin-left:15px; border-left:3px solid #ddd; padding-left:15px;">
                {{your_response_here}}
              </p>

              <p>
                Please note that online consultation has its limitations. If your symptoms change, worsen, or raise concern, an in-person medical assessment may be required.
              </p>

              <p>
                Should you wish to clarify any aspect of this response, you are welcome to reply.
              </p>

              <p style="margin-top:30px;">
                Kind regards,<br>
                <strong>Dr Dariusz Ledzinski</strong><br>
                Gynaecological Consulting Platform
              </p>

              <p style="font-size:12px; color:#777; margin-top:30px;">
                This response is provided based on the information available and does not replace an in-person medical consultation where clinically indicated.
              </p>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>

    email_body = f"""
New consultation submitted:

Name: {name}
Email: {email}

Question:
{question}
"""

    payload = {
        "Messages": [
            {
                "From": {
                    "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                    "Name": "Gynae Consulting Platform"
                },
                "To": [
                    {
                        "Email": os.environ.get("MAILJET_TO_EMAIL"),
                        "Name": "Dr Dariusz Ledzinski"
                    }
                ],
                "Subject": "New Consultation Request",
                "TextPart": email_body
            }
        ]
    }

    try:
        response = requests.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(
                os.environ.get("MAILJET_API_KEY"),
                os.environ.get("MAILJET_SECRET_KEY")
            ),
            json=payload,
            timeout=10
        )

        if response.status_code not in (200, 201):
            return f"Mailjet error: {response.text}", 500

        return render_template("thankyou.html")

    except Exception as e:
        return f"Unexpected error: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
