from flask import Flask, request, redirect, url_for, render_template, session
from mailjet_rest import Client
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import sqlite3
import os


mailjet = Client(
    auth=(os.environ.get("MAILJET_API_KEY"), os.environ.get("MAILJET_SECRET_KEY")),
    version='v3.1'
)

app = Flask(__name__)
csrf = CSRFProtect(app)

app.secret_key = os.environ.get("SECRET_KEY")

def get_db_connection():
    conn = sqlite3.connect("consultations.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            urgency TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

    create_table()

@app.route("/")

def homepage():

    return render_template("home.html")

@app.route("/consultation", methods=["GET", "POST"])
def consultation():

    if request.method == "POST":
        
        try:
            name = request.form.get("name")
            email = request.form.get("email")
            urgency = request.form.get("urgency")
            message = request.form.get("message")
            timestamp = datetime.now().strftime("%d %B %Y, %H:%M")

            conn = get_db_connection()

            conn.execute("""
                INSERT INTO consultations
                (name, email, urgency, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, urgency, message, timestamp))

            conn.commit()
            conn.close()

            website = request.form.get("website")
            if website:
                return "Spam detected", 400

            if not name or not email or not urgency or not message:
                return "All fields are required", 400
            urgency_clean = (urgency or "").strip().lower()

            urgency_clean = urgency_clean.replace(" ", "_")

            # ----------------------------
            # 1. Decide subject
            # ----------------------------

           
            if urgency_clean == "urgent":

                subject = "CONSULTATION REQUEST"

                patient_text = f"""
            Your urgent consultation request has been received.

            This platform is not suitable for medical emergencies.

            Please seek immediate in-person medical care if necessary.

            Dr Dariusz
            """

                doctor_text = f"""
            CONSULTATIOIN REQUEST

            Submitted:
            {timestamp}

            Name: {name}
            Email: {email}

            Message:
            {message}
            """

            elif urgency_clean == "not_urgent":

                subject = "Consultation Request"

                patient_text = f"""
            Thank you for your consultation request.

            Your message has been received and will be reviewed carefully.

            Dr Dariusz
            """

                doctor_text = f"""
            Consultation Request

            Sunbmitted:
            {timestamp}

            Name: {name}
            Email: {email}

            Message:
            {message}
            """

            else:
                print("UNKNOWN URGENCY:", repr(urgency_clean))
                return "Invalid submission", 400
                
            data_doctor = {
                "Messages": [
                    {
                        "From": {
                            "Email": "contact@drdariuszconsults.com",
                            "Name": "Consultation System"
                        },
                        "To": [{"Email": "darledzinski@gmail.com"}],
                        "Subject": subject,
                        "TextPart": doctor_text
                    }
                ]
            }

            data_patient = {
                "Messages": [
                    {
                        "From": {
                            "Email": "contact@drdariuszconsults.com",
                            "Name": "Dr Dariusz"
                            },
                            "To": [{"Email": email}],
                            "Subject": subject,
                            "TextPart": patient_text
                    }
                ]

            }
            
            print("SENDING DOCTOR EMAIL")
            result_doctor = mailjet.send.create(data=data_doctor)
            print("DOCTOR STATUS:", result_doctor.status_code)
            
            print("SENDING PATIENT EMAIL")
            result_patient = mailjet.send.create(data=data_patient)
            print("PATIENT STATUS:", result_patient.status_code)
            
            return redirect(url_for("thank_you", urgency=urgency_clean))

        except Exception as e:
            print("  ERROR:", e)
            return "Something went wrong", 500
    return render_template("consultation.html")


@app.route("/thank-you")

def thank_you():
    urgency = request.args.get("urgency", '')
    return render_template("thank_you.html", urgency=urgency)
