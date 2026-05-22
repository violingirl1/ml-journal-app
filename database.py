import sqlite3
from datetime import datetime

DB_NAME = "journal.db"

def init_db():
    """Initializes the local SQLite database and creates the entries table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            text TEXT NOT NULL,
            mood TEXT NOT NULL,
            score REAL NOT NULL,
            tags TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_entry(text: str, mood: str, score: float, tags: list):
    """Saves a processed journal entry and its ML data into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Convert list of tags into a single comma-separated string
    tags_str = ",".join(tags)
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
        INSERT INTO entries (date, text, mood, score, tags)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_date, text, mood, score, tags_str))
    
    conn.commit()
    conn.close()

def get_all_entries():
    """Retrieves all past journal entries sorted by the most recent date."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT date, text, mood, score, tags FROM entries ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    entries = []
    for row in rows:
        # Safeguard: if mood contains details or brackets, keep it clean
        display_mood = row[2]
        entries.append({
            "date": row[0],
            "text": row[1],
            "mood": display_mood,
            "score": row[3],
            "tags": row[4].split(",") if row[4] else []
        })
    return entries