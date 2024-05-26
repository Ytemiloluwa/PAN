import sqlite3

def initialize_db():
    conn = sqlite3.connect('pans.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pan TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

initialize_db()
