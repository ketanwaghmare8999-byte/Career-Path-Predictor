# database.py
# Database layer. Uses SQLite (file-based, zero setup) so the project runs
# instantly on any laptop without installing/configuring a MySQL server.
# The table structure is written to be MySQL-compatible, so it can be swapped
# to MySQL later just by changing the connection (as listed as an option
# in the synopsis: "Database: MySQL or MongoDB").

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "careerpath.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skills TEXT NOT NULL,
            interests TEXT,
            top_career TEXT NOT NULL,
            confidence REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER,
            career TEXT NOT NULL,
            is_relevant INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(prediction_id) REFERENCES predictions(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(name, email, password_hash):
    conn = get_connection()
    try:  # the connection is always closed, even if the insert fails (for example a duplicate e-mail)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_prediction(user_id, skills, interests, top_career, confidence):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO predictions (user_id, skills, interests, top_career, confidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, ",".join(skills), ",".join(interests), top_career, confidence,
             datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def prediction_exists(prediction_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM predictions WHERE id = ?", (prediction_id,))
    found = cur.fetchone() is not None
    conn.close()
    return found


def save_feedback(prediction_id, career, is_relevant):
    """One vote per result card: voting again for the same career only changes the earlier vote."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        now = datetime.utcnow().isoformat()
        cur.execute("SELECT id FROM feedback WHERE prediction_id = ? AND career = ?", (prediction_id, career))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE feedback SET is_relevant = ?, created_at = ? WHERE id = ?",
                (1 if is_relevant else 0, now, existing["id"]),
            )
        else:
            cur.execute(
                "INSERT INTO feedback (prediction_id, career, is_relevant, created_at) VALUES (?, ?, ?, ?)",
                (prediction_id, career, 1 if is_relevant else 0, now),
            )
        conn.commit()
    finally:
        conn.close()


def get_feedback_stats():
    """Used for the admin-style summary: how often each career is marked relevant."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT career,
               SUM(CASE WHEN is_relevant=1 THEN 1 ELSE 0 END) as relevant_count,
               SUM(CASE WHEN is_relevant=0 THEN 1 ELSE 0 END) as irrelevant_count
        FROM feedback
        GROUP BY career
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows
