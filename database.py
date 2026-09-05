import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

print("DATABASE.PY IMPORTED")


def get_db_connection():

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    conn = psycopg2.connect(database_url)

    return conn


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
