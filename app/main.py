from typing import Union
import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI

app = FastAPI()

# Database setup
DB_PATH = "test.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize database with sample data
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Insert sample data
            sample_users = [
                ("alice", "alice@example.com", "password123"),
                ("bob", "bob@example.com", "secret456"),
                ("charlie", "charlie@example.com", "pass789"),
            ]
            cursor.executemany(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                sample_users
            )
            conn.commit()

# Initialize DB on startup
init_db()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/search")
def search_user(username: str):
    query = f"SELECT * FROM users WHERE username = '{username}'"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        # Convert results to dict
        users = [dict(row) for row in results]

    return {
        "query": query,
        "results": users,
    }
