from flask import Flask, request, redirect, url_for, render_template, session
from mailjet_rest import Client
from flask_wtf.csrf import CSRFProtect
from flask import Response
from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3
import os


mailjet = Client(
    auth=(os.environ.get("MAILJET_API_KEY"), os.environ.get("MAILJET_SECRET_KEY")),
    version='v3.1'
)

app = Flask(__name__)
csrf = CSRFProtect(app)

app.secret_key = os.environ.get("SECRET_KEY")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "DrDariusz1952"

def get_db_connection():
    conn = sqlite3.connect("consultations.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = sqlite3.connect("consultations.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            urgency TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'New',
            doctor_notes TEXT
        )
    """)

    conn.commit()
    conn.close()

create_table()

conn = get_db_connection()

try:
    conn.execute(
        "ALTER TABLE consultations ADD COLUMN status TEXT NOT NULL DEFAULT 'New'"
    )
    conn.commit()
except:
    pass

conn.close()

conn = get_db_connection()

try:
    conn.execute(
        "ALTER TABLE consultations ADD COLUMN doctor_notes TEXT"
    )
    conn.commit()
except:
    pass

conn.close()


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
            timestamp = datetime.now(ZoneInfo("Africa/Johannesburg")).strftime("%d %B %Y, %H:%M")
            website = request.form.get("website")
            if website:
                return "Spam detected", 400

            if not name or not email or not urgency or not message:
                return "All fields are required", 400
            
            conn = get_db_connection()

            conn.execute("""
                INSERT INTO consultations
                (name, email, urgency, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, urgency, message, timestamp))

            conn.commit()
            conn.close()
            
            urgency_clean = (urgency or "").strip().lower()

           
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

def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return Response(
        "Access denied",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'}
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == "DrDariusz1952":

            session["admin_logged_in"] = True

            return redirect(url_for("admin"))

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("login"))

@app.route("/update-notes/<int:id>", methods=["POST"])
def update_notes(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    doctor_notes = request.form.get("doctor_notes")

    conn = get_db_connection()

    conn.execute(
        "UPDATE consultations SET doctor_notes = ? WHERE id = ?",
        (doctor_notes, id)
    )

    conn.commit()

    urgent_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE urgency='urgent'"
    ).fetchone()[0]

    non_urgent_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE urgency='not_urgent'"
    ).fetchone()[0]

    conn.close()

    return redirect(url_for("admin"))

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    search = request.args.get("search", "").strip().lower()

    if search:
        consultations = conn.execute("""
            SELECT *
            FROM consultations
            WHERE LOWER(name) LIKE ?
            OR LOWER(email) LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%")).fetchall()
        
    else:
        consultations = conn.execute("""
            SELECT * FROM consultations
            ORDER BY
                CASE
                    WHEN status = 'New' THEN 1
                    WHEN status = 'In Progress' THEN 2
                    WHEN status = 'Completed' THEN 3
                END,
                id DESC
        """).fetchall()
    
    total_count = conn.execute(
        "SELECT COUNT(*) FROM consultations"
    ).fetchone()[0]

    urgent_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE urgency='urgent'"
    ).fetchone()[0]

    non_urgent_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE urgency='not_urgent'"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        consultations=consultations,
        total_count=total_count,
        urgent_count=urgent_count,
        non_urgent_count=non_urgent_count
    )
@app.route("/delete/<int:id>")
def delete_consultation(id):

    auth = request.authorization

    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

    conn = get_db_connection()

    search = request.args.get("search", '').strip()

    conn.execute(
        "DELETE FROM consultations WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/update-status/<int:id>/<status>")
def update_status(id, status):

    status = status.replace("_", " ")

    conn = get_db_connection()

    conn.execute(
        "UPDATE consultations SET status = ? WHERE id = ?",
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")
