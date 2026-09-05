from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template,
    session,
    Response
)
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import csv
import io
import logging

from database import (
    get_db_connection,
    create_appointment,
    save_consultation
)

from mail import (
    send_email,
    send_appointment_email,
    send_appointment_confirmation_email,
    send_consultation_email
)


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

    urgency = request.args.get("urgency", "")

    return render_template(
        "thank_you.html",
        urgency=urgency
    )


@app.route("/consultation", methods=["GET", "POST"])
def consultation():

    if request.method == "POST":

        try:

            # ----------------------------
            # Read form values
            # ----------------------------

            name = request.form.get(
                "name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            mobile = request.form.get(
                "mobile",
                ""
            ).strip()

            contact_method = request.form.get(
                "contact_method",
                ""
            ).strip()

            urgency = request.form.get(
                "urgency",
                ""
            ).strip()

            message = request.form.get(
                "message",
                ""
            ).strip()

            timestamp = datetime.now(
                ZoneInfo("Africa/Johannesburg")
            ).strftime(
                "%d %B %Y, %H:%M"
            )

            # ----------------------------
            # Honeypot spam protection
            # ----------------------------

            website = request.form.get(
                "website",
                ""
            ).strip()

            if website:

                logger.warning(
                    "Spam submission blocked."
                )

                return "Spam detected", 400

            # ----------------------------
            # Required fields
            # ----------------------------

            if (
                not name
                or not email
                or not urgency
                or not message
            ):

                logger.warning(
                    "Required fields missing."
                )

                return "All fields are required", 400

            urgency_clean = urgency.lower()

            save_consultation(
                name,
                email,
                mobile,
                contact_method,
                urgency_clean,
                message,
                timestamp
            )

            logger.info(
                f"Consultation saved for "
                f"{name} ({email})"
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
                    f"Unknown urgency value: "
                    f"{urgency_clean!r}"
                )

                return "Invalid submission", 400

            # ----------------------------
            # Send emails
            # ----------------------------

            logger.info(
                "Sending doctor consultation email"
            )

            send_consultation_email(
                "darledzinski@gmail.com",
                "Consultation System",
                subject,
                doctor_text
            )

            logger.info(
                "Sending patient confirmation email"
            )

            send_consultation_email(
                email,
                "Dr Dariusz",
                subject,
                patient_text
            )

            logger.info(
                f"Consultation workflow completed "
                f"for {email}"
            )

            return redirect(
                url_for(
                    "thank_you",
                    urgency=urgency_clean
                )
            )

        except Exception as e:

            logger.exception(
                f"Consultation route failed: {e}"
            )

            return "Something went wrong", 500

    return render_template(
        "consultation.html"
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        password = request.form.get(
            "password"
        )

        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        return render_template(
            "login.html",
            error="Incorrect password."
        )

    return render_template(
        "login.html"
    )


@app.route("/logout")
def logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("login")
    )


@app.route(
    "/update-notes/<int:id>",
    methods=["POST"]
)
def update_notes(id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    doctor_notes = request.form.get(
        "doctor_notes"
    )

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE consultations
        SET doctor_notes = %s
        WHERE id = %s
        """,
        (
            doctor_notes,
            id
        )
    )

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        WHERE urgency = 'urgent'
        """
    )

    urgent_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        WHERE urgency = 'not_urgent'
        """
    )

    non_urgent_count = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("admin")
    )


@app.route("/export-csv")
def export_csv():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            urgency,
            status,
            message,
            doctor_notes,
            timestamp
        FROM consultations
        ORDER BY id DESC
        """
    )

    consultations = cursor.fetchall()

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
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7]
        ])

    cursor.close()
    conn.close()

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; "
                "filename=consultations.csv"
        }
    )


@app.route("/admin")
def admin():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor()

    page = request.args.get(
        "page",
        1,
        type=int
    )

    status_filter = request.args.get(
        "status",
        ""
    )

    per_page = 10

    offset = (
        page - 1
    ) * per_page

    search = request.args.get(
        "search",
        ""
    ).strip().lower()

    print(
        "SEARCH TERM =",
        search
    )

    if search and status_filter:

        cursor.execute(
            """
            SELECT *
            FROM consultations
            WHERE status = %s
            AND (
                LOWER(name) LIKE %s
                OR LOWER(email) LIKE %s
            )
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (
                status_filter,
                f"%{search}%",
                f"%{search}%",
                per_page,
                offset
            )
        )

        consultations = cursor.fetchall()

    elif search:

        cursor.execute(
            """
            SELECT *
            FROM consultations
            WHERE LOWER(name) LIKE %s
            OR LOWER(email) LIKE %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (
                f"%{search}%",
                f"%{search}%",
                per_page,
                offset
            )
        )

        consultations = cursor.fetchall()

    elif status_filter:

        cursor.execute(
            """
            SELECT *
            FROM consultations
            WHERE status = %s
            ORDER BY id DESC
            LIMIT %s OFFSET %s
            """,
            (
                status_filter,
                per_page,
                offset
            )
        )

        consultations = cursor.fetchall()

    else:

        cursor.execute(
            """
            SELECT *
            FROM consultations
            ORDER BY
                CASE
                    WHEN status = 'New'
                        THEN 1
                    WHEN status = 'In Progress'
                        THEN 2
                    WHEN status = 'Completed'
                        THEN 3
                    ELSE 4
                END,
                id DESC
            LIMIT %s OFFSET %s
            """,
            (
                per_page,
                offset
            )
        )

        consultations = cursor.fetchall()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        """
    )

    total_count = cursor.fetchone()[0]

    total_pages = (
        total_count
        + per_page
        - 1
    ) // per_page

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        WHERE urgency = 'urgent'
        """
    )

    urgent_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        WHERE urgency = 'not_urgent'
        """
    )

    non_urgent_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        WHERE status = 'New'
        """
    )

    new_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        WHERE status = 'In Progress'
        """
    )

    in_progress_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM consultations
        WHERE status = 'Completed'
        """
    )

    completed_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM appointments
        """
    )

    appointment_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(
        "RESULT COUNT =",
        len(consultations)
    )

    for row in consultations:

        print(
            "FOUND:",
            row["name"],
            row["email"]
        )

    print(
        "TOTAL CONSULTATIONS =",
        total_count
    )

    print(
        "CONSULTATIONS OBJECT =",
        consultations
    )

    print(
        "LENGTH =",
        len(consultations)
    )

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
        total_pages=total_pages
    )


@app.route("/delete/<int:id>")
def delete_consultation(id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM consultations
        WHERE id = %s
        """,
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("admin")
    )


@app.route(
    "/offer-appointment/<int:consultation_id>",
    methods=["GET", "POST"]
)
def offer_appointment(
    consultation_id
):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        cursor_factory=__import__(
            "psycopg2.extras",
            fromlist=["DictCursor"]
        ).DictCursor
    )

    cursor.execute(
        """
        SELECT *
        FROM consultations
        WHERE id = %s
        """,
        (consultation_id,)
    )

    consultation = cursor.fetchone()

    if consultation is None:

        cursor.close()
        conn.close()

        return "Consultation not found", 404

    logger.info(
        f"Appointment source mobile: "
        f"{consultation['mobile']}"
    )

    logger.info(
        f"Appointment source contact method: "
        f"{consultation['contact_method']}"
    )

    if request.method == "POST":

        create_appointment(
            consultation_id,
            consultation,
            request.form["practice"],
            request.form["preferred_date"],
            request.form["preferred_time"],
            request.form["reason"]
        )

        logger.info(
            "Sending appointment email"
        )

        result_patient = send_appointment_email(
            consultation["email"],
            consultation["name"],
            request.form["practice"],
            request.form["preferred_date"],
            request.form["preferred_time"],
            request.form["reason"]
        )

        logger.info(
            f"Appointment email status: "
            f"{result_patient.status_code}"
        )

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            """
        )

        count = cursor.fetchone()[0]

        logger.info(
            f"Appointments after insert: "
            f"{count}"
        )

        cursor.close()
        conn.close()

        return redirect(
            url_for("appointments")
        )

    cursor.close()
    conn.close()

    return render_template(
        "book_appointment.html",
        consultation=consultation
    )


@app.route("/appointments")
def appointments():

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor(
        cursor_factory=__import__(
            "psycopg2.extras",
            fromlist=["DictCursor"]
        ).DictCursor
    )

    search = request.args.get(
        "search",
        ""
    ).strip().lower()

    logger.info(
        f"Search term: {search}"
    )

    cursor.execute(
        """
        SELECT name
        FROM appointments
        """
    )

    all_names = cursor.fetchall()

    print(
        "ALL APPOINTMENT NAMES =",
        [row["name"] for row in all_names]
    )

    if search:

        cursor.execute(
            """
            SELECT *
            FROM appointments
            WHERE LOWER(name) LIKE %s
            OR LOWER(email) LIKE %s
            ORDER BY id DESC
            """,
            (
                f"%{search}%",
                f"%{search}%"
            )
        )

        appointments = cursor.fetchall()

        print(
            "RAW APPOINTMENTS =",
            appointments
        )

    else:

        cursor.execute(
            """
            SELECT *
            FROM appointments
            ORDER BY id DESC
            """
        )

        appointments = cursor.fetchall()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            """
        )

        count = cursor.fetchone()[0]

        logger.info(
            f"Appointments in database: "
            f"{count}"
        )

        logger.info(
            f"Appointments found: "
            f"{len(appointments)}"
        )

        for appointment in appointments:

            logger.info(
                f"Appointment: "
                f"{appointment['name']}"
            )

            logger.info(
                f"Appointment mobile: "
                f"{appointment['mobile']}"
            )

            logger.info(
                f"Appointment contact method: "
                f"{appointment['contact_method']}"
            )

            logger.info(
                f"Appointment email: "
                f"{appointment['email']}"
            )

    cursor.close()
    conn.close()

    return render_template(
        "appointments.html",
        appointments=appointments
    )


@app.route(
    "/delete-appointment/<int:id>"
)
def delete_appointment(id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM appointments
        WHERE id = %s
        """,
        (id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return redirect(
        url_for("appointments")
    )


@app.route(
    "/appointment-status/<int:id>/<status>",
    methods=["GET", "POST"]
)
def appointment_status(
    id,
    status
):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    allowed_statuses = {
        "Awaiting Payment",
        "Paid",
        "Confirmed",
        "Cancelled"
    }

    if status not in allowed_statuses:

        return "Invalid appointment status", 400

    conn = get_db_connection()

    cursor = conn.cursor(
        cursor_factory=__import__(
            "psycopg2.extras",
            fromlist=["DictCursor"]
        ).DictCursor
    )

    cursor.execute(
        """
        SELECT
            id,
            name,
            email,
            practice,
            preferred_date,
            preferred_time,
            reason,
            status
        FROM appointments
        WHERE id = %s
        """,
        (id,)
    )

    appointment = cursor.fetchone()

    if appointment is None:

        cursor.close()
        conn.close()

        return "Appointment not found", 404

    old_status = appointment["status"]

    cursor.execute(
        """
        UPDATE appointments
        SET status = %s
        WHERE id = %s
        """,
        (
            status,
            id
        )
    )

    conn.commit()

    logger.info(
        f"Appointment {id} status changed "
        f"from {old_status} to {status}"
    )

    if (
        status == "Confirmed"
        and old_status != "Confirmed"
    ):

        result = (
            send_appointment_confirmation_email(
                appointment["email"],
                appointment["name"],
                appointment["practice"],
                appointment["preferred_date"],
                appointment["preferred_time"],
                appointment["reason"]
            )
        )

        logger.info(
            f"Appointment confirmation email "
            f"status: {result.status_code}"
        )

    elif (
        status == "Confirmed"
        and old_status == "Confirmed"
    ):

        logger.info(
            f"Appointment {id} was already "
            f"confirmed. No duplicate "
            f"confirmation email sent."
        )

    cursor.close()
    conn.close()

    return redirect(
        url_for("appointments")
    )
