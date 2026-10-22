import os
import uuid
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

print("DATABASE.PY IMPORTED")


def get_db_connection():

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    conn = psycopg2.connect(
    database_url,
    cursor_factory=DictCursor
)

    return conn

def make_invoice_number(invoice_id, issue_year):
    return f"INV-{issue_year}-{invoice_id:06d}"


def create_paid_invoice(
    consultation_id,
    consultation_date,
    amount,
    tariff_code,
    icd10_code,
    payment_date,
    payment_method,
    payment_verified
):
    if payment_verified is not True:
        raise ValueError(
            "Payment must be verified before issuing a paid invoice."
        )

    if amount <= 0:
        raise ValueError(
            "Invoice amount must be greater than zero."
        )

    conn = get_db_connection()
    cursor = None

    try:
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, invoice_number
            FROM paid_invoices
            WHERE consultation_id = %s
            """,
            (consultation_id,)
        )

        existing_invoice = cursor.fetchone()

        if existing_invoice:
            return existing_invoice

        issue_date = datetime.now(ZoneInfo("Africa/Johannesburg"))
        issue_year = issue_date.year

        temporary_invoice_number = (
            "PENDING-" + str(uuid.uuid4())
        )

        
        cursor.execute(
            """
            INSERT INTO paid_invoices (
                consultation_id,
                invoice_number,
                consultation_date,
                amount,
                tariff_code,
                icd10_code,
                payment_date,
                payment_method,
                payment_verified
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                consultation_id,
                temporary_invoice_number,
                consultation_date,
                amount,
                tariff_code,
                icd10_code,
                payment_date,
                payment_method,
                payment_verified
            )
        )

        new_invoice_id = cursor.fetchone()["id"]

        permanent_invoice_number = make_invoice_number(
            new_invoice_id,
            issue_year
        )

        cursor.execute(
            """
            UPDATE paid_invoices
            SET invoice_number = %s
            WHERE id = %s
            """,
            (
                permanent_invoice_number,
                new_invoice_id
            )
        )


        conn.commit()

        return {
            "id": new_invoice_id,
            "invoice_number": permanent_invoice_number
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        conn.close()

def create_table():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultations (

            id SERIAL PRIMARY KEY,

            name TEXT NOT NULL,

            email TEXT NOT NULL,

            mobile TEXT,

            contact_method TEXT,

            urgency TEXT NOT NULL,

            message TEXT NOT NULL,

            timestamp TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'New',

            doctor_notes TEXT

        )
    """)

    cursor.execute("""
        ALTER TABLE consultations
        ADD COLUMN IF NOT EXISTS follow_up_date DATE
    """)

    cursor.execute("""
        ALTER TABLE consultations
        ADD COLUMN IF NOT EXISTS follow_up_completed_at TIMESTAMP
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS follow_up_history (
            id SERIAL PRIMARY KEY,
            consultation_id INTEGER NOT NULL
                REFERENCES consultations(id),
            follow_up_date DATE NOT NULL,
            completed_at TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        ALTER TABLE follow_up_history
        ADD COLUMN IF NOT EXISTS outcome TEXT
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (

            id SERIAL PRIMARY KEY,

            name TEXT NOT NULL,

            email TEXT NOT NULL,

            mobile TEXT,

            contact_method TEXT,

            practice TEXT,

            preferred_date TEXT,

            preferred_time TEXT,

            reason TEXT,

            status TEXT DEFAULT 'Pending',

            created_at TEXT

        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prescription_email_sends (

            submission_token TEXT PRIMARY KEY,

            consultation_id INTEGER NOT NULL,

            status TEXT NOT NULL DEFAULT 'processing',

            created_at TEXT NOT NULL

        )
    """)

    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paid_invoices (

           
            

            consultation_date DATE NOT NULL,

            amount NUMERIC(10, 2) NOT NULL
                CHECK (amount > 0),

            tariff_code TEXT,

            icd10_code TEXT,

            payment_date DATE NOT NULL,

            payment_method TEXT NOT NULL,

            payment_verified BOOLEAN NOT NULL
                DEFAULT FALSE,

            issued_at TIMESTAMP NOT NULL
                DEFAULT CURRENT_TIMESTAMP

        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        paid_invoices_consultation_unique
        ON paid_invoices (consultation_id)
    """)


    conn.commit()

    cursor.close()
    conn.close()

    print("POSTGRES TABLES READY")


create_table()


def create_appointment(
    consultation_id,
    consultation,
    practice,
    preferred_date,
    preferred_time,
    reason
):

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)

    cursor.execute(
        """
        INSERT INTO appointments
        (
            name,
            email,
            mobile,
            contact_method,
            practice,
            preferred_date,
            preferred_time,
            reason,
            status,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            consultation["name"],
            consultation["email"],
            consultation["mobile"],
            consultation["contact_method"],
            practice,
            preferred_date,
            preferred_time,
            reason,
            "Awaiting Payment",
            datetime.now().strftime("%d %B %Y, %H:%M")
        )
    )

    cursor.execute(
        """
        UPDATE consultations
        SET status = 'In Progress'
        WHERE id = %s
        """,
        (consultation_id,)
    )

    cursor.execute(
        """
        SELECT mobile, contact_method
        FROM appointments
        ORDER BY id DESC
        LIMIT 1
        """
    )

    saved = cursor.fetchone()

    print("SAVED APPOINTMENT MOBILE =", saved["mobile"])
    print(
        "SAVED APPOINTMENT CONTACT METHOD =",
        saved["contact_method"]
    )

    conn.commit()

    cursor.close()
    conn.close()


def save_consultation(
    name,
    email,
    mobile,
    contact_method,
    urgency,
    message,
    timestamp
):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO consultations (
            name,
            email,
            mobile,
            contact_method,
            urgency,
            message,
            timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        name,
        email,
        mobile,
        contact_method,
        urgency,
        message,
        timestamp
    ))

    conn.commit()

    cursor.close()
    conn.close()
