import sqlite3
from datetime import datetime
from flask_bcrypt import Bcrypt

DB_NAME = "journal.db"
bcrypt = Bcrypt()

def init_db():
    """Initializes the database with a users table and an upgraded entries table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Create secure Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # 2. Create Entries table with a foreign key linking to the user
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            text TEXT NOT NULL,
            mood TEXT NOT NULL,
            score REAL NOT NULL,
            tags TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username, password):
    """Hashes the password and saves the user. Returns True if successful, False if username exists."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Username already taken!
        
    conn.close()
    return success

def verify_user(username, password):
    """Verifies user credentials against the stored secure hash. Returns user dict or None."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row and bcrypt.check_password_hash(row[2], password):
        return {"id": row[0], "username": row[1]}
    return None

def save_entry(user_id: int, text: str, mood: str, score: float, tags: list):
    """Saves a processed journal entry linked to a specific user ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    tags_str = ",".join(tags)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO entries (user_id, date, text, mood, score, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, current_date, text, mood, score, tags_str))
    
    conn.commit()
    conn.close()

def get_user_entries(user_id: int):
    """Retrieves all past journal entries for a SPECIFIC user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT date, text, mood, score, tags FROM entries WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for row in rows:
        entries.append({
            "date": row[0],
            "text": row[1],
            "mood": row[2],
            "score": row[3],
            "tags": row[4].split(",") if row[4] else []
        })
    return entries