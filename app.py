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
from urllib.parse import quote
import os
import csv
import io
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

from database import (
    get_db_connection,
    create_appointment,
    save_consultation
)

from mail import (
    send_appointment_email,
    send_appointment_confirmation_email,
    send_consultation_email,
    send_pdf_email
)


app = Flask(__name__)

csrf = CSRFProtect(app)

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

APP_VERSION = "1.0.0"

app.secret_key = os.environ.get("SECRET_KEY")

logger.info(f"Starting Dr Dariusz Consulting v{APP_VERSION}")


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
                "Consultation record saved successfully."
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
                "Consultation workflow completed successfully."
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

@app.route("/create-referral/<int:id>", methods=["GET", "POST"])
def create_referral(id):

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
        SELECT *
        FROM consultations
        WHERE id = %s
        """,
        (id,)
    )

    consultation = cursor.fetchone()

    if not consultation:

        cursor.close()
        conn.close()

        return "Consultation not found", 404

    if request.method == "POST":

        patient_name = request.form.get(
            "patient_name",
            ""
        ).strip()

        age = request.form.get(
            "age",
            ""
        ).strip()

        contact = request.form.get(
            "contact",
            ""
        ).strip()

        referred_to = request.form.get(
            "referred_to",
            ""
        ).strip()

        reason = request.form.get(
            "reason",
            ""
        ).strip()

        history = request.form.get(
            "history",
            ""
        ).strip()

        cursor.close()
        conn.close()

        return render_template(
            "referral_letter.html",
            consultation=consultation,
            patient_name=patient_name,
            age=age,
            contact=contact,
            referred_to=referred_to,
            reason=reason,
            history=history
        )

    cursor.close()
    conn.close()

    return render_template(
        "create_referral.html",
        consultation=consultation
    )

@app.route(
    "/generate-referral-pdf/<int:id>",
    methods=["POST"]
)
def generate_referral_pdf(id):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    patient_name = request.form.get(
        "patient_name",
        ""
    ).strip()

    age = request.form.get(
        "age",
        ""
    ).strip()

    contact = request.form.get(
        "contact",
        ""
    ).strip()

    referred_to = request.form.get(
        "referred_to",
        ""
    ).strip()

    reason = request.form.get(
        "reason",
        ""
    ).strip()

    history = request.form.get(
        "history",
        ""
    ).strip()


    document_action = request.form.get(
        "document_action",
        "draft"
    )

    is_signed = (
        document_action in (
            "signed",
            "email"
        )
    )

    send_to_patient = (
        document_action == "email"
    )

    patient_email = None

    if send_to_patient:

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT email
            FROM consultations
            WHERE id = %s
            """,
            (id,)
        )

        patient_record = cursor.fetchone()

        cursor.close()
        conn.close()

        if not patient_record or not patient_record[0]:

            return (
                "Patient email address not found",
                400
            )

        patient_email = patient_record[0]

    pdf_buffer = io.BytesIO()

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=A4
    )
        
                
    width, height = A4

    left = 60
    right = 60
    y = height - 60 
    
    status_label = (
        "APPROVED ELECTRONICALLY"
        if is_signed
        else "DRAFT — NOT A VALID PRESCRIPTION"
    )
    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        left,
        y,
        "MD, M Med (Obs & Gyne)"
    )

    y -= 15

    pdf.drawString(
        left,
        y,
        "HPCSA: MP0249688 | Practice No.: 1605690"
    )

    y -= 15

    pdf.drawString(
        left,
        y,
        "Email: consult@drdariusz.online | "
        "Phone: +27 820478579"
    )

    y -= 30

    pdf.setFont(
        "Helvetica-Bold",
        15
    )

    pdf.drawString(
        left,
        y,
        "REFERRAL LETTER"
    )

    y -= 30

    pdf.setFont(
        "Helvetica",
        11
    )

    current_date = datetime.now(
        ZoneInfo("Africa/Johannesburg")
    ).strftime(
        "%d %B %Y"
    )

    pdf.drawString(
        left,
        y,
        f"Date: {current_date}"
    )

    y -= 25

    pdf.drawString(
        left,
        y,
        f"To: {referred_to}"
    )

    y -= 30

    pdf.drawString(
        left,
        y,
        "Dear Colleague,"
    )

    y -= 25

    introductory_text = (
        "I am referring the following patient for "
        "further assessment and management:"
    )

    for line in simpleSplit(
        introductory_text,
        "Helvetica",
        11,
        width - left - right
    ):

        pdf.drawString(
            left,
            y,
            line
        )

        y -= 15

    y -= 10

    pdf.drawString(
        left,
        y,
        f"Patient Name: {patient_name}"
    )

    y -= 18

    pdf.drawString(
        left,
        y,
        f"Age: {age}"
    )

    y -= 18

    pdf.drawString(
        left,
        y,
        f"Contact: {contact}"
    )

    y -= 30

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        left,
        y,
        "Reason for Referral"
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        11
    )

    reason_lines = simpleSplit(
        reason,
        "Helvetica",
        11,
        width - left - right
    )

    for line in reason_lines:

        pdf.drawString(
            left,
            y,
            line
        )

        y -= 15

    y -= 15

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        left,
        y,
        "Relevant History / Findings"
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        11
    )

    history_lines = simpleSplit(
        history,
        "Helvetica",
        11,
        width - left - right
    )

    for line in history_lines:

        pdf.drawString(
            left,
            y,
            line
        )

        y -= 15

    y -= 25

    pdf.drawString(
        left,
        y,
        "Yours sincerely,"
    )

    y -= 40

    pdf.setFont(
        "Helvetica-Bold",
        11
    )

    pdf.drawString(
        left,
        y,
        "Dr. Dariusz Ledzinski"
    )

    y -= 20

    pdf.setFont(
        "Helvetica",
        11
    )

    if is_signed:

        pdf.setFont(
            "Helvetica-Bold",
            11
        )

        pdf.drawString(
            left,
            y,
            "Electronically approved by:"
        )

        y -= 18

        pdf.drawString(
            left,
            y,
            "Dr. Dariusz Ledzinski"
        )

        y -= 18

        approval_timestamp = datetime.now(
            ZoneInfo("Africa/Johannesburg")
        ).strftime(
            "%d %B %Y at %H:%M"
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawString(
            left,
            y,
            f"Date and time: {approval_timestamp}"
        )

    else:

        pdf.setFont(
            "Helvetica",
            11
        )

        pdf.drawString(
            left,
            y,
            "Signature: ______________________________"
        )
    pdf.save()

    pdf_buffer.seek(0)

    if send_to_patient:

        email_result = send_pdf_email(
            patient_email,
            patient_name,
            "Referral Letter from Dr Dariusz",
            f"""Dear {patient_name},

Please find attached your referral letter from Dr Dariusz Ledzinski.

Kind regards,

Dr Dariusz Ledzinski
""",
            pdf_buffer.getvalue(),
            "Referral_Letter_Signed.pdf"
        )

        logger.info(
            f"Signed referral letter email status: "
            f"{email_result.status_code}"
        )

        if email_result.status_code != 200:

            logger.error(
                "Signed referral letter email failed."
            )

            return (
                "Referral letter email could not be sent",
                500
            )

    return Response(
        pdf_buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
                "inline; "
                "filename="
                + (
                    "Referral_Letter_Signed.pdf"
                    if is_signed
                    else "Referral_Letter_Draft.pdf"
                )
        }
    )

@app.route(
    "/create-prescription/<int:id>",
    methods=["GET", "POST"]
)
def create_prescription(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM consultations
        WHERE id = %s
        """,
        (id,)
    )

    consultation = cursor.fetchone()

    if not consultation:

        cursor.close()
        conn.close()

        return "Consultation not found", 404

    today_date = datetime.now(
        ZoneInfo("Africa/Johannesburg")
    ).strftime("%Y-%m-%d")

    if request.method == "GET":

        cursor.close()
        conn.close()

        return render_template(
            "create_prescription.html",
            consultation=consultation,
            today_date=today_date
        )

    patient_name = request.form.get(
        "patient_name", ""
    ).strip()

    age = request.form.get(
        "age", ""
    ).strip()

    contact = request.form.get(
        "contact", ""
    ).strip()

    prescription_date = request.form.get(
        "prescription_date", ""
    ).strip()

    medication = request.form.get(
        "medication", ""
    ).strip()

    dosage_instructions = request.form.get(
        "dosage_instructions", ""
    ).strip()

    cursor.close()
    conn.close()

    if not all([
        patient_name,
        prescription_date,
        medication,
        dosage_instructions
    ]):

        return (
            "Please complete the required "
            "prescription fields.",
            400
        )

    return render_template(
        "prescription_review.html",
        consultation=consultation,
        patient_name=patient_name,
        age=age,
        contact=contact,
        prescription_date=prescription_date,
        medication=medication,
        dosage_instructions=dosage_instructions
    )

@app.route(
    "/generate-prescription-pdf/<int:id>",
    methods=["POST"]
)
def generate_prescription_pdf(id):

    if not session.get("admin_logged_in"):

        return redirect(
            url_for("login")
        )

    document_action = request.form.get(
        "document_action",
        "draft"
    )

       if document_action not in ("draft", "signed"):

           return (
               "Email delivery is not enabled yet. "
               "Please select Draft PDF or Approve & Sign.",
               400
           )

       is_signed = (
           document_action == "signed"
       )

    patient_name = request.form.get(
        "patient_name", ""
    ).strip()

    age = request.form.get(
        "age", ""
    ).strip()

    contact = request.form.get(
        "contact", ""
    ).strip()

    prescription_date = request.form.get(
        "prescription_date", ""
    ).strip()

    medication = request.form.get(
        "medication", ""
    ).strip()

    dosage_instructions = request.form.get(
        "dosage_instructions", ""
    ).strip()

    if not all([
        patient_name,
        prescription_date,
        medication,
        dosage_instructions
    ]):

        return (
            "Please complete all required fields.",
            400
        )

    # Confirm that this consultation exists.
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM consultations
        WHERE id = %s
        """,
        (id,)
    )

    consultation_record = cursor.fetchone()

    cursor.close()
    conn.close()

    if not consultation_record:

        return "Consultation not found", 404

    pdf_buffer = io.BytesIO()

    pdf = canvas.Canvas(
        pdf_buffer,
        pagesize=A4
    )

    width, height = A4

    left = 55
    y = height - 50

    def draw_wrapped_text(
        text,
        font_name="Helvetica",
        font_size=11,
        leading=16
    ):

        nonlocal y

        pdf.setFont(
            font_name,
            font_size
        )

        lines = simpleSplit(
            text or "",
            font_name,
            font_size,
            width - left - 55
        )

        for line in lines:

            if y < 55:

                pdf.showPage()
                y = height - 55

                # Make the draft status visible on each page.
                pdf.setFont(
                    "Helvetica-Bold",
                    10
                )

                pdf.drawString(
                    left,
                    y,
                    "DRAFT — NOT A VALID PRESCRIPTION"
                )

                y -= 30

                pdf.setFont(
                    font_name,
                    font_size
                )

            pdf.drawString(
                left,
                y,
                line
            )

            y -= leading

    draw_wrapped_text(
        "DRAFT — NOT A VALID PRESCRIPTION",
        "Helvetica-Bold",
        13,
        20
    )

    y -= 5

    draw_wrapped_text(
        "DR. DARIUSZ LEDZINSKI",
        "Helvetica-Bold",
        15,
        20
    )

    draw_wrapped_text(
        "MD, M Med (Obs & Gyne)"
    )

    draw_wrapped_text(
        "HPCSA: MP0249688 | Practice No.: 1605690"
    )

    draw_wrapped_text(
        "Email: consult@drdariusz.online | "
        "Phone: +27 820478579"
    )

    y -= 12

    draw_wrapped_text(
        "PRESCRIPTION — DRAFT",
        "Helvetica-Bold",
        14,
        22
    )

    y -= 5

    draw_wrapped_text(
        f"Patient Name: {patient_name}"
    )

    draw_wrapped_text(
        f"Age: {age or 'Not provided'}"
    )

    draw_wrapped_text(
        f"Contact: {contact or 'Not provided'}"
    )

    draw_wrapped_text(
        f"Date: {prescription_date}"
    )

    y -= 10

    draw_wrapped_text(
        "Medication Prescribed",
        "Helvetica-Bold",
        12,
        18
    )

    draw_wrapped_text(
        medication
    )

    y -= 10

    draw_wrapped_text(
        "Dosage & Instructions",
        "Helvetica-Bold",
        12,
        18
    )

    draw_wrapped_text(
        dosage_instructions
    )

    y -= 20

    draw_wrapped_text(
        "Doctor's approval and signature: "
        "NOT YET PROVIDED"
    )

    y -= 12

    draw_wrapped_text(
        "This document is a draft for review. "
        "It is not authorised for dispensing.",
        "Helvetica-Bold",
        10,
        15
    )

    pdf.save()

    pdf_buffer.seek(0)

    return Response(
        pdf_buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
                "inline; filename=Prescription_Draft.pdf"
        }
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

@app.route("/clear-consultations", methods=["POST"])
def clear_consultations():

    logger.info("CLEAR CONSULTATIONS ROUTE REACHED")

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("login")
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM consultations
            """
        )

        logger.info("ALL CONSULTATIONS DELETE EXECUTED")

        conn.commit()

        logger.info("ALL CONSULTATIONS DELETE COMMITTED")
    except Exception:

        conn.rollback()
        raise

    finally:

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

    

    if request.method == "POST":

        create_appointment(
            consultation_id,
            consultation,
            request.form["practice"],
            request.form["preferred_date"],
            request.form["preferred_time"],
            request.form["reason"]
        )

        if consultation["contact_method"] in (
            "Email",
            "Either"
        ):

            logger.info(
                f"Sending appointment email "
                f"for contact method: "
                f"{consultation['contact_method']}"
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

        elif consultation["contact_method"] == "WhatsApp":

            logger.info(
                "Patient selected WhatsApp - "
                "no automatic appointment email sent"
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

    else:

        cursor.execute(
            """
            SELECT *
            FROM appointments
            ORDER BY id DESC
            """
        )

        appointments = cursor.fetchall()
    whatsapp_urls = {}

    email_urls = {}

    whatsapp_confirmation_urls = {}

    for appointment in appointments:

        if appointment["mobile"]:

            whatsapp_message = f"""Dear {appointment['name']},

Your appointment has been offered.

Practice: {appointment['practice']}
Date: {appointment['preferred_date']}
Time: {appointment['preferred_time']}

Consultation fee: R 500.

PAYMENT BY EFT

Bank: GoTyme
Account holder: Dariusz Ledzinski
Account number: 510 1312 9386

Please make payment by EFT and send your proof of payment.

Your appointment will be confirmed once payment has been received and verified.

If you need any changes to the appointment, please contact us.

Dr Dariusz Ledzinski"""

            whatsapp_urls[appointment["id"]] = (
                f"whatsapp://send?phone=27{appointment['mobile'][1:]}"
                 f"&text={quote(whatsapp_message)}"
            )

            if appointment["email"]:

                email_message = f"""Dear {appointment['name']},

    Your appointment has been offered.

    Practice: {appointment['practice']}
    Date: {appointment['preferred_date']}
    Time: {appointment['preferred_time']}

Consultation fee: R 500.
PAYMENT BY EFT

Bank: GoTyme
Account holder: Dariusz Ledzinski
Account number: 510 1312 9386

Please make payment by EFT and send your proof of payment.

Your appointment will be confirmed once payment has been received and verified.

If you need any changes to the appointment, please contact us.

Dr Dariusz Ledzinski"""

                email_urls[appointment["id"]] = (
                    f"mailto:{appointment['email']}"
                    f"?subject={quote('Appointment Offer')}"
                    f"&body={quote(email_message)}"
                )

            if (
                appointment["mobile"]
                and appointment["status"] == "Confirmed"
            ):

                confirmation_message = f"""Dear {appointment['name']},

    Your appointment with Dr Dariusz has been confirmed.

    Payment has been received and verified.

    Practice: {appointment['practice']}
    Date: {appointment['preferred_date']}
    Time: {appointment['preferred_time']}

    We look forward to your consultation.

    Dr Dariusz Ledzinski"""

                whatsapp_confirmation_urls[appointment["id"]] = (
                    f"whatsapp://send?phone=27{appointment['mobile'][1:]}"
                    f"&text={quote(confirmation_message)}"
                )
                
    cursor.close()
    conn.close()

    return render_template(
        "appointments.html",
        appointments=appointments,
        whatsapp_urls=whatsapp_urls,
        email_urls=email_urls,
        whatsapp_confirmation_urls=whatsapp_confirmation_urls
    )
  
@app.route(
    "/update-status/<int:consultation_id>/<status>",
    methods=["GET", "POST"]
)
def update_status(
    consultation_id,
    status
):

    if not session.get(
        "admin_logged_in"
    ):

        return redirect(
            url_for("login")
        )

    status_map = {
        "New": "New",
        "In_Progress": "In Progress",
        "Completed": "Completed"
    }

    if status not in status_map:

        return "Invalid consultation status", 400

    new_status = status_map[status]

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE consultations
        SET status = %s
        WHERE id = %s
        """,
        (
            new_status,
            consultation_id
        )
    )

    conn.commit()

    logger.info(
        f"Consultation {consultation_id} "
        f"status changed to {new_status}"
    )

    cursor.close()
    conn.close()

    return redirect(
        url_for("admin")
    )

@app.route("/delete-appointment/<int:id>")
def delete_appointment(id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM appointments
            WHERE id = %s
            """,
            (id,)
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise

    finally:

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
        "Completed",
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
            contact_method,
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

        if appointment["contact_method"] in (
            "Email",
            "Either"
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

        elif appointment["contact_method"] == "WhatsApp":

            logger.info(
                "Patient selected WhatsApp - "
                "no automatic confirmation email sent"
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

@app.route("/clear-appointments", methods=["POST"])
def clear_appointments():

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("login")
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM appointments
            """
        )

        logger.info("ALL APPOINTMENTS DELETE EXECUTED")

        conn.commit()

        logger.info("ALL APPOINTMENTS DELETE COMMITTED")

    except Exception:

        conn.rollback()
        raise

    finally:

        cursor.close()
        conn.close()

    return redirect(
        url_for("appointments")
    )
