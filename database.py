import sqlite3

from datetime import datetime

print("DATABASE.PY IMPORTED")

def get_db_connection():

    conn = sqlite3.connect("consultations.db")

    conn.row_factory = sqlite3.Row

    return conn



    
    conn.execute(

        """

        UPDATE consultations

        SET status = 'In Progress'

        WHERE id = ?

        """,

        (consultation_id,)

    )

    conn.commit()

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

    conn = get_db_connection ()

    conn.execute("""
        INSERT INTO consultations (
            name,
            email,
            mobile,
            contact_method,
            urgency,
            message,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        email,
        mobile,
        contact_method,
        urgency,
        message,
        timestamp
    )

    conn.commit()
    conn.close()


    print("SAVING APPOINTMENT MOBILE =", consultation["mobile"])
    print(
        "SAVING APPOINTMENT CONTACT METHOD =",
        consultation["contact_method"]
    )


    
