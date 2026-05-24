"""
Simple SQLite database for the Chronosat real-time dashboard.
Handles users, roles, and query history.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib
import secrets

DB_PATH = Path(__file__).parent / "chronosat_dashboard.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('basic', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    # Query history / activity log
    c.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query_type TEXT,           -- 'coverage', 'search', 'gee_search'
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            result_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # GEE Export tasks (for real-time monitoring)
    c.execute("""
        CREATE TABLE IF NOT EXISTS gee_exports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            scene_id TEXT,
            status TEXT DEFAULT 'PENDING',   -- PENDING, RUNNING, COMPLETED, FAILED
            drive_folder TEXT,
            task_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

    # Create default admin user if none exists
    create_default_admin()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_default_admin():
    """Create a default admin user (admin / admin123) for first run."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, 'admin')
        """, ("admin", hash_password("admin123")))
        conn.commit()
        print("[Dashboard] Default admin created: username=admin, password=admin123")
    conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    conn = get_connection()
    c = conn.cursor()
    password_hash = hash_password(password)
    c.execute("""
        SELECT id, username, role, is_active FROM users
        WHERE username = ? AND password_hash = ?
    """, (username, password_hash))
    row = c.fetchone()
    conn.close()

    if row and row["is_active"]:
        # Update last login
        conn = get_connection()
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.utcnow(), row["id"]))
        conn.commit()
        conn.close()
        return dict(row)
    return None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username: str, password: str, role: str = "basic") -> bool:
    """Admin only function to create new users."""
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        """, (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # username exists


def list_all_users() -> List[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, username, role, created_at, last_login, is_active
        FROM users ORDER BY created_at DESC
    """)
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return users


def log_query(user_id: int, query_type: str, location: str, start_date: str, end_date: str, summary: str):
    conn = get_connection()
    conn.execute("""
        INSERT INTO query_logs (user_id, query_type, location, start_date, end_date, result_summary)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, query_type, location, start_date, end_date, summary))
    conn.commit()
    conn.close()


def get_user_query_history(user_id: int, limit: int = 20) -> List[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM query_logs 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (user_id, limit))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def get_all_query_logs(limit: int = 50) -> List[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT q.*, u.username 
        FROM query_logs q
        JOIN users u ON q.user_id = u.id
        ORDER BY q.created_at DESC 
        LIMIT ?
    """, (limit,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows