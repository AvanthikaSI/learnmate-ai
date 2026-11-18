"""
database.py - SQLite storage engine for LearnMate AI.

Manages persistent storage for learning sessions and chat interactions,
allowing users to create, reopen, continue, and delete learning sessions.
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Optional, Any, Generator

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learnmate.db")


@contextmanager
def get_db(db_path: str = DB_FILE) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields a configured SQLite connection and guarantees
    proper commit, rollback on error, and closing the connection.
    """
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = DB_FILE) -> None:
    """Initializes the database schema if tables do not already exist."""
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        
        # Interactions table (chats / activities)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                activity TEXT NOT NULL,
                user_prompt TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
            );
            """
        )
        
        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC);")


def create_session(topic: str, title: Optional[str] = None, db_path: str = DB_FILE) -> int:
    """
    Creates a new learning session and returns its ID.
    """
    clean_topic = topic.strip()
    session_title = title.strip() if title and title.strip() else f"Session: {clean_topic}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (topic, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (clean_topic, session_title, now, now)
        )
        return cursor.lastrowid


def get_all_sessions(db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """
    Retrieves all learning sessions ordered by latest updated.
    """
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, topic, title, created_at, updated_at
            FROM sessions
            ORDER BY updated_at DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_session(session_id: int, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single session by its ID.
    """
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, topic, title, created_at, updated_at FROM sessions WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def update_session_title(session_id: int, new_title: str, db_path: str = DB_FILE) -> bool:
    """
    Updates the title of a session.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
            (new_title.strip(), now, session_id)
        )
        return cursor.rowcount > 0


def delete_session(session_id: int, db_path: str = DB_FILE) -> bool:
    """
    Deletes a session and cascades deletion to all associated interactions.
    """
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return cursor.rowcount > 0


def add_interaction(
    session_id: int,
    activity: str,
    user_prompt: str,
    ai_response: str,
    db_path: str = DB_FILE
) -> int:
    """
    Records an interaction and updates the session's updated_at timestamp.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO interactions (session_id, activity, user_prompt, ai_response, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, activity, user_prompt, ai_response, now)
        )
        interaction_id = cursor.lastrowid
        
        # Update updated_at on the parent session
        cursor.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
        return interaction_id


def get_interactions_for_session(session_id: int, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """
    Retrieves all interactions for a given session, ordered chronologically.
    """
    with get_db(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, session_id, activity, user_prompt, ai_response, created_at
            FROM interactions
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (session_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
