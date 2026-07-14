from flask import Flask, request, redirect, url_for, render_template, session
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from zoneinfo import ZoneInfo
import sqlite3
import os
import csv
import io
import logging

from database import get_db_connection, create_appointment

from mail import ( send_email, send_appointment_email, send_consultation_email )

app = Flask(__name__)
csrf = CSRFProtect(app)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

APP_VERSION = "1.0.0"

app.secret_key = os.environ.get("SECRET_KEY")

logger.info(f"Starting Dr Dariusz Consulting v{APP_VERSION}")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


@app.route("/")

def homepage():

    return render_template("home.html")


@app.route("/thank-you")

def thank_you():
    urgency = request.args.get("urgency", '')
    return render_template("thank_you.html", urgency=urgency)

@app.route("/consultation", methods=["GET", "POST"])

def consultation():

    if request.method == "POST":

        try:

            # ----------------------------

            # Read form values

            # ----------------------------

            name = request.form.get("name", "").strip()

            email = request.form.get("email", "").strip()

            mobile = request.form.get("mobile", "").strip()

            contact_method = request.form.get("contact_method", "").strip()

            urgency = request.form.get("urgency", "").strip()

            message = request.form.get("message", "").strip()

            timestamp = datetime.now(

                ZoneInfo("Africa/Johannesburg")

            ).strftime("%d %B %Y, %H:%M")

            # ----------------------------

            # Honeypot spam protection

            # ----------------------------

            website = request.form.get("website", "").strip()

            if website:

                logger.warning("Spam submission blocked.")

                return "Spam detected", 400

            # ----------------------------

            # Required fields

            # ----------------------------

            if not name or not email or not urgency or not message:

                logger.warning("Required fields missing.")

                return "All fields are required", 400

            urgency_clean = urgency.lower()

            # ----------------------------

            # Save consultation

            # ----------------------------

            conn = get_db_connection()

            conn.execute(

                """

                INSERT INTO consultations

                (

                    name,

                    email,

                    mobile,

                    contact_method,

                    urgency,

                    message,

                    timestamp

                )

                VALUES (?, ?, ?, ?, ?, ?, ?)

                """,

                (

                    name,

                    email,

                    mobile,

                    contact_method,

                    urgency_clean,

                    message,

                    timestamp

                )

            )

            conn.commit()

            conn.close()

            logger.info(

                f"Consultation saved for {name} ({email})"

            )

            # ----------------------------

            # Build email content

            # ----------------------------

            if urgency_clean == "urgent":

                subject = "CONSULTATION REQUEST"

                patient_text = """

Your urgent consultation request has been received.

This platform is not suitable for medical emergencies.

Please seek immediate in-person medical care if necessary.

Dr Dariusz

"""

                doctor_text = f"""

CONSULTATION REQUEST

Submitted:

{timestamp}

Name: {name}

Email: {email}

Mobile: {mobile}

Preferred Contact Method: {contact_method}

Message:

{message}

"""

            elif urgency_clean == "not_urgent":

                subject = "Standard Consultation"

                patient_text = """

Thank you for your consultation request.

Your message has been received and will be reviewed carefully.

Dr Dariusz

"""

                doctor_text = f"""

Consultation Request

Submitted:

{timestamp}

Name: {name}

Email: {email}

Message:

{message}

"""

            else:

                logger.warning(

                    f"Unknown urgency value: {urgency_clean!r}"

                )

                return "Invalid submission", 400

            # ----------------------------

            # Send emails

            # ----------------------------

            logger.info("Sending doctor consultation email")

            send_consultation_email(

                "darledzinski@gmail.com",

                "Consultation System",

                subject,

                doctor_text

            )

            logger.info("Sending patient confirmation email")

            send_consultation_email(

                email,

                "Dr Dariusz",

                subject,

                patient_text

            )

            logger.info(

                f"Consultation workflow completed for {email}"

            )

            return redirect(

                url_for("thank_you", urgency=urgency_clean)

            )

        except Exception as e:

            logger.exception(

                f"Consultation route failed: {e}"

            )

            return "Something went wrong", 500

    return render_template("consultation.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(url_for("admin"))

  

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

@app.route("/export-csv")

def export_csv():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    conn = get_db_connection()

    consultations = conn.execute("""

       SELECT id, name, email, urgency, status,
              message, doctor_notes, timestamp
       FROM consultations
       ORDER BY id DESC
       
    """).fetchall()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Name",
        "Email",
        "Urgency",
        "Status",
        "Message",
        "Doctor Notes",
        "Timestamp"
    ])

   
    for row in consultations:

        writer.writerow([
            row["id"],
            row["name"],
            row["email"],
            row["urgency"],
            row["status"],
            row["message"],
            row["doctor_notes"],
            row["timestamp"]
        ])

    conn.close()

    return Response(

        output.getvalue(),

        mimetype="text/csv",

        headers={

            "Content-Disposition":

            "attachment; filename=consultations.csv"

        }

    )

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "")
    per_page = 10
    offset = (page - 1) * per_page

    search = request.args.get("search", "").strip().lower()

    print("SEARCH TERM =", (search))

    if search and status_filter:
        consultations = conn.execute("""
            SELECT *
            FROM consultations
            WHERE status = ?
            AND (
                LOWER(name) LIKE ?
                OR LOWER(email) LIKE ?
            )
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (
            status_filter,
            f"%{search}%",
            f"%{search}%",
            per_page,
            offset
        )).fetchall()

    elif search:
        consultations = conn.execute("""
            SELECT *
            FROM consultations
            WHERE LOWER(name) LIKE ?
            OR LOWER(email) LIKE ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (
            f"%{search}%",
            f"%{search}%",
            per_page,
            offset
        )).fetchall() 

    elif status_filter:

        consultations = conn.execute("""
            SELECT *
            FROM consultations
            WHERE status = ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
        """, (
            status_filter,
            per_page,
            offset
        )).fetchall()
        
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
                LIMIT ? OFFSET ?
            """, (per_page, offset)).fetchall()

    total_count = conn.execute(
        "SELECT COUNT(*) FROM consultations"
    ).fetchone()[0]

    total_pages = (total_count + per_page - 1) // per_page

    urgent_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE urgency='urgent'"
    ).fetchone()[0]

    non_urgent_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE urgency='not_urgent'"
    ).fetchone()[0]

    new_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE status='New'"
    ).fetchone()[0]

    in_progress_count = conn.execute(
        "SELECT COUNT(*) FROM consultations WHERE status='In Progress'"
    ).fetchone()[0]

    completed_count = conn.execute(
         "SELECT COUNT(*) FROM consultations WHERE status='Completed'"
    ).fetchone()[0]

    appointment_count = conn.execute(
        "SELECT COUNT(*) FROM appointments"
    ).fetchone()[0]

    conn.close()

    print("RESULT COUNT =", len(consultations))

    for row in consultations:
        print("FOUND:", row["name"], row["email"])

    print("TOTAL CONSULTATIONS =", total_count)
    print("CONSULTATIONS OBJECT =", consultations)
    print("LENGTH =", len(consultations))

    return render_template(
        "admin.html",
        consultations=consultations,
        total_count=total_count,
        urgent_count=urgent_count,
        non_urgent_count=non_urgent_count,
        new_count=new_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        appointment_count=appointment_count,
        page=page,
        total_pages=total_pages,
    )
    
@app.route("/delete/<int:id>")
def delete_consultation(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    conn = get_db_connection()

    search = request.args.get("search", '').strip()

    conn.execute(
        "DELETE FROM consultations WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/offer-appointment/<int:consultation_id>", methods=["GET", "POST"])

def offer_appointment(consultation_id):

    conn = get_db_connection()

    consultation = conn.execute(

        "SELECT * FROM consultations WHERE id = ?",

        (consultation_id,)

    ).fetchone()

    if request.method == "POST":

        create_appointment(
            consultation_id
            consultation,
            request.form["practice"],
            request.form["preferred_date"],
            request.form["preferred_time"],
            request.form["reason"]
        )
        
        logger.info("Sending appointment email")

        result_patient = send_appointment_email(
            consultation["email"],
            consultation["name"],
            request.form["practice"],
            request.form["preferred_date"],
            request.form["preferred_time"],
            request.form["reason"]
        )

        logger.info(
            f"Appointment email status: {result_patient.status_code}"
        )
        
        count = conn.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

        logger.info(f"Appointments after insert: {count}")

        conn.close()

        return redirect(url_for("appointments"))
    return render_template(

        "book_appointment.html",

        consultation=consultation

    )
    
@app.route("/appointments")
def appointments():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    conn = get_db_connection()

    search = request.args.get("search", "").strip().lower()

    logger.info(f"Search term: {search}")
    
    if search:
        appointments = conn.execute("""
            SELECT *
            FROM appointments
            WHERE LOWER(name) LIKE ?
            OR LOWER(email) LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

        print("RAW APPOINTMENTS =", appointments)
    else:
        appointments = conn.execute("""
            SELECT *
            FROM appointments
            ORDER BY id DESC
        """).fetchall()

        count = conn.execute(
            "SELECT COUNT(*) FROM appointments"
        ).fetchone()[0]

        logger.info(f"Appointments in database: {count}")
        
        logger.info(f"Appointments found: {len(appointments)}")

        for a in appointments:
            logger.info(f"Appointment: {a['name']}")

    conn.close()

    return render_template(

        "appointments.html",

        appointments=appointments
    )

@app.route("/delete-appointment/<int:id>")
def delete_appointment(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM appointments WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("appointments"))
    
@app.route("/appointment-status/<int:id>/<status>")
def appointment_status(id, status):

    conn = get_db_connection()

    conn.execute(

        "UPDATE appointments SET status = ? WHERE id = ?",

        (status, id)
    )

    conn.commit()

    conn.close()

    return redirect(url_for("appointments"))

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
