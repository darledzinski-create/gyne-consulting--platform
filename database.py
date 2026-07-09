import sqlite3

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

        mobile TEXT,

        contact_method TEXT,

        urgency TEXT NOT NULL,

        message TEXT NOT NULL,

        timestamp TEXT NOT NULL,

        status TEXT NOT NULL DEFAULT 'New',

        doctor_notes TEXT

    )

    """)

    conn.execute("""

    CREATE TABLE IF NOT EXISTS appointments (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

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

    # Upgrade older databases

    try:

        conn.execute("""

            ALTER TABLE consultations

            ADD COLUMN status TEXT NOT NULL DEFAULT 'New'

        """)

    except sqlite3.OperationalError:

        pass

    try:

        conn.execute("""

            ALTER TABLE consultations

            ADD COLUMN doctor_notes TEXT

        """)

    except sqlite3.OperationalError:

        pass

    conn.commit()

    conn.close()

create_table()
