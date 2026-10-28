import sqlite3
import hashlib
import secrets
import hmac
from pathlib import Path


# Database file location
DB_PATH = Path(__file__).with_name("expenses.db")


# Connect to the database
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


# -----------------------------
# PASSWORD SECURITY
# -----------------------------

def hash_password(password):
    """
    Hash a password using PBKDF2 and a random salt.
    We never store the original password.
    """

    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        200_000
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password, stored_hash):
    """
    Check whether the entered password matches
    the stored password hash.
    """

    try:
        salt, original_hash = stored_hash.split("$")

        entered_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            200_000
        ).hex()

        return hmac.compare_digest(entered_hash, original_hash)

    except ValueError:
        return False


# -----------------------------
# CREATE DATABASE TABLES
# -----------------------------

def create_table():

    connection = get_connection()

    # Users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL
        )
    """)

    # Transactions table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            date TEXT NOT NULL,

            type TEXT NOT NULL
                CHECK (type IN ('Income', 'Expense')),

            category TEXT NOT NULL,

            amount REAL NOT NULL
                CHECK (amount > 0),

            description TEXT,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # Add user_id to an older transactions table if needed
    columns = connection.execute(
        "PRAGMA table_info(transactions)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "user_id" not in column_names:
        connection.execute(
            "ALTER TABLE transactions ADD COLUMN user_id INTEGER"
        )

    connection.commit()
    connection.close()


# -----------------------------
# CREATE A USER ACCOUNT
# -----------------------------

def create_user(username, password):

    username = username.strip()

    if not username or not password:
        return False

    password_hash = hash_password(password)

    connection = get_connection()

    try:
        connection.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        """, (username, password_hash))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        # Username already exists
        return False

    finally:
        connection.close()


# -----------------------------
# LOGIN / AUTHENTICATION
# -----------------------------

def authenticate_user(username, password):

    connection = get_connection()

    user = connection.execute("""
        SELECT id, username, password_hash
        FROM users
        WHERE username = ?
    """, (username.strip(),)).fetchone()

    connection.close()

    if user and verify_password(password, user["password_hash"]):
        return {
            "id": user["id"],
            "username": user["username"]
        }

    return None


# -----------------------------
# ADD A TRANSACTION
# -----------------------------

def add_transaction(
    user_id,
    date,
    transaction_type,
    category,
    amount,
    description
):

    connection = get_connection()

    connection.execute("""
        INSERT INTO transactions
        (user_id, date, type, category, amount, description)

        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        date,
        transaction_type,
        category,
        amount,
        description
    ))

    connection.commit()
    connection.close()


# -----------------------------
# GET A USER'S TRANSACTIONS
# -----------------------------

def get_transactions(user_id):

    connection = get_connection()

    cursor = connection.execute("""
        SELECT id, date, type, category, amount, description
        FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
    """, (user_id,))

    records = cursor.fetchall()

    connection.close()

    return records


# -----------------------------
# DELETE A USER'S TRANSACTION
# -----------------------------

def delete_transaction(transaction_id, user_id):

    connection = get_connection()

    connection.execute("""
        DELETE FROM transactions
        WHERE id = ?
        AND user_id = ?
    """, (transaction_id, user_id))

    connection.commit()
    connection.close()


# Create tables when this file is imported
create_table()