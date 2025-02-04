from passlib.context import CryptContext
import sqlite3
import time

DATABASE_NAME = "database.db"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            last_edited_by TEXT,
            last_edited_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            typed_key TEXT,
            row INTEGER,
            col INTEGER,
            timestamp TEXT,
            document_id INTEGER,
            FOREIGN KEY (document_id) REFERENCES documents(document_id)
        )
    """)
    # cursor.execute(
    #     "INSERT INTO documents (data, last_edited_by, last_edited_at) VALUES ('', '', '')",
    # )

    conn.commit()
    conn.close()

def add_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = pwd_context.hash(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   (username, hashed_pw))
    conn.commit()
    conn.close()

def get_user_hashed_password(username):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["password"]
    return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def log_user_action(username, action):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO auth_logs (username, action, timestamp) VALUES (?, ?, ?)",
        (username, action, time.strftime('%Y-%m-%d %H:%M:%S'))
    )
    conn.commit()
    conn.close()

def log_data_change(username, typed_char, row, col, document_id=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO data_logs (username, typed_key, row, col, timestamp, document_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, typed_char, row, col, time.strftime('%Y-%m-%d %H:%M:%S'), document_id))
    conn.commit()
    conn.close()

def get_document_data(document_id=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM documents WHERE document_id = ?", (document_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return ""

def update_document_data(full_text, username, document_id=1):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE documents
           SET data = ?, last_edited_by = ?, last_edited_at = ?
         WHERE document_id = ?
    """, (full_text, username, time.strftime('%Y-%m-%d %H:%M:%S'), document_id))
    conn.commit()
    conn.close()
