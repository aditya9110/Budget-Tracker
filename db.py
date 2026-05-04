import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "budgeteer.db")


def get_connection():
    """Returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name e.g. row["spend"]
    return conn


def init_db():
    """Creates tables if they don't exist. Safe to call every time app starts."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            year        INTEGER NOT NULL,
            month       TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            source      TEXT,
            type        TEXT,
            spend       REAL    DEFAULT 0,
            remarks     TEXT,
            is_salary   INTEGER DEFAULT 0   -- 1 if this row is a salary entry
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# WRITE FUNCTIONS
# ─────────────────────────────────────────────

def insert_transactions(year, month, rows):
    """
    Inserts a list of transaction dicts for a given year/month.
    Clears existing data for that month before inserting (fresh import).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data for this month before inserting
    cursor.execute(
        "DELETE FROM transactions WHERE year = ? AND month = ?",
        (year, month)
    )

    for row in rows:
        cursor.execute("""
            INSERT INTO transactions (year, month, date, description, source, type, spend, remarks, is_salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            year,
            month,
            row.get("date"),
            row.get("description"),
            row.get("source"),
            row.get("type"),
            row.get("spend", 0),
            row.get("remarks"),
            row.get("is_salary", 0)
        ))

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# READ FUNCTIONS
# ─────────────────────────────────────────────

def get_transactions(year, month):
    """Returns all non-salary transactions for a given month."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM transactions
        WHERE year = ? AND month = ? AND is_salary = 0
        ORDER BY date ASC
    """, (year, month))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_salary_row(year, month):
    """Returns the salary row for a given month, if it exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM transactions
        WHERE year = ? AND month = ? AND is_salary = 1
        LIMIT 1
    """, (year, month))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_categories(year, month):
    """
    Returns spending grouped by category (type) for a given month.
    Equivalent to the Categories sheet SUMIF logic.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT type, SUM(spend) as total_spend
        FROM transactions
        WHERE year = ? AND month = ? AND is_salary = 0 AND spend > 0
        GROUP BY type
        ORDER BY total_spend DESC
    """, (year, month))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_daily_spend(year, month):
    """Returns total spend grouped by date for a given month."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT date, SUM(spend) as total_spend
        FROM transactions
        WHERE year = ? AND month = ? AND is_salary = 0
        GROUP BY date
        ORDER BY date ASC
    """, (year, month))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def add_transaction(year, month, row):
    """Inserts a single new transaction row."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (year, month, date, description, source, type, spend, remarks, is_salary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        year, month,
        row.get("date"), row.get("description"), row.get("source"),
        row.get("type"), row.get("spend", 0), row.get("remarks"), row.get("is_salary", 0)
    ))
    conn.commit()
    conn.close()


def update_transaction(tx_id, date, description, source, type_, spend, remarks):
    """Updates an existing transaction by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET date=?, description=?, source=?, type=?, spend=?, remarks=?
        WHERE id=?
    """, (date, description, source, type_, spend, remarks, tx_id))
    conn.commit()
    conn.close()


def delete_transaction(tx_id):
    """Deletes a transaction by id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=?", (tx_id,))
    conn.commit()
    conn.close()


def is_month_imported(year, month):
    """Returns True if data for this year/month already exists in DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 1 FROM transactions WHERE year = ? AND month = ? LIMIT 1
    """, (year, month))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def get_imported_months():
    """Returns list of all imported year/month combos."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT year, month FROM transactions
        ORDER BY year DESC, month DESC
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
