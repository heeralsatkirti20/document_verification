import sqlite3
import json
from datetime import datetime

DATABASE_NAME = "database.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_number TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            document_type TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            reasons TEXT
        )
    """)

    # Demo blacklist entries only.
    demo_entries = [
        "DEMO-BLACKLIST-001",
        "DEMO-BLACKLIST-002",
        "DL-DEMO-9999"
    ]

    for entry in demo_entries:
        try:
            cursor.execute(
                "INSERT INTO blacklist (id_number) VALUES (?)",
                (entry,)
            )
        except sqlite3.IntegrityError:
            pass

    connection.commit()
    connection.close()


def is_blacklisted(extracted_text):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id_number FROM blacklist")
    entries = cursor.fetchall()

    connection.close()

    text_upper = extracted_text.upper()

    for entry in entries:
        number = entry["id_number"]

        if number.upper() in text_upper:
            return True, number

    return False, None


def save_log(document_type, risk_level, risk_score, reasons):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO verification_logs
        (timestamp, document_type, risk_level, risk_score, reasons)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        document_type,
        risk_level,
        risk_score,
        json.dumps(reasons)
    ))

    connection.commit()
    connection.close()


def get_all_logs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM verification_logs
        ORDER BY id DESC
    """)

    logs = cursor.fetchall()

    connection.close()

    result = []

    for log in logs:
        item = dict(log)

        try:
            item["reasons"] = json.loads(item["reasons"])
        except:
            item["reasons"] = []

        result.append(item)

    return result