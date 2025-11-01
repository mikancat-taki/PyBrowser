import sqlite3, os

DB_PATH = "cache.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            query TEXT PRIMARY KEY,
            html TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_page(query, html):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("REPLACE INTO pages (query, html) VALUES (?, ?)", (query, html))
    conn.commit()
    conn.close()

def get_cached_page(query):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT html FROM pages WHERE query = ?", (query,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

init_db()
