import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "history.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            sleep_hours REAL,
            study_hours REAL,
            stress_level REAL,
            exercise_days REAL,
            social_time INTEGER,
            took_breaks INTEGER,
            water_intake REAL,
            screen_time REAL,
            risk_level INTEGER,
            risk_label TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_entry(data: dict, risk_level: int, risk_label: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO entries 
        (date, sleep_hours, study_hours, stress_level, exercise_days,
         social_time, took_breaks, water_intake, screen_time, risk_level, risk_label)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d"),
        data["sleep_hours"], data["study_hours"], data["stress_level"],
        data["exercise_days"], data["social_time"], data["took_breaks"],
        data["water_intake"], data["screen_time"],
        risk_level, risk_label
    ))
    conn.commit()
    conn.close()

def get_history():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT date, risk_level, risk_label FROM entries ORDER BY id DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_entries():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM entries ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows
