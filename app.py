from flask import Flask, render_template, request, redirect, url_for
from mailjet_rest import Client
import os

app = Flask(__name__)

mailjet = Client(
    auth=(
        os.environ.get("MAILJET_API_KEY"),
        os.environ.get("MAILJET_SECRET_KEY")
    ),
    version="v3.1"
)

# --------------------
# ROUTES
# --------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask")
def ask_page():
    return render_template("ask.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/intake", methods=["GET", "POST"])
def intake():
    if request.method == "POST":
        intake_data = {
            "full_name": request.form.get("full_name"),
            "age_dob": request.form.get("age_dob"),
            "country": request.form.get("country"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "concern": request.form.get("concern"),
            "duration": request.form.get("duration"),
            "pregnant": bool(request.form.get("pregnant")),
            "severe_pain": bool(request.form.get("severe_pain")),
            "bleeding": bool(request.form.get("bleeding")),
            "fever": bool(request.form.get("fever")),
            "emergency": bool(request.form.get("emergency")),
            "conditions": request.form.get("conditions"),
            "medications": request.form.get("medications"),
            "allergies": request.form.get("allergies"),
        }
    print("NEW INTAKE SUBMISSION:")
    for key, value in intake_data.items():
      print(f"{key}: {value}")

        # --- EMAIL TO DOCTOR (YOU) ---

email_body = f"""
NEW GYNAECOLOGICAL INTAKE SUBMISSION

Name: {intake_data['full_name']}
Email: {intake_data['email']}
Phone: {intake_data['phone']}
Country: {intake_data['country']}
Age / DOB: {intake_data['age_dob']}

Main concern:
{intake_data['concern']}

Duration:
{intake_data['duration']}

Pregnant: {intake_data['pregnant']}
Severe pain: {intake_data['severe_pain']}
Bleeding: {intake_data['bleeding']}
Fever: {intake_data['fever']}
Emergency flagged: {intake_data['emergency']}

Known conditions:
{intake_data['conditions']}

Medications:
{intake_data['medications']}

Allergies:
{intake_data['allergies']}
"""

data = {
    "Messages": [
        {
            "From": {
                "Email": os.environ.get("MAILJET_FROM_EMAIL"),
                "Name": "Online Gynaecology Intake"
            },
            "To": [
                {
                    "Email": os.environ.get("MAILJET_TO_EMAIL"),
                    "Name": "Dr Dariusz"
                }
            ],
            "Subject": "New Patient Intake Submission",
            "TextPart": email_body
        }
    ]
}

result = mailjet.send.create(data=data)
print("MAILJET RESULT:", result.status_code)

     return redirect(url_for("intake_submitted"))
        
return render_template("intake.html")


@app.route("/intake-submitted")
def intake_submitted():
    return render_template("intake_submitted.html")
