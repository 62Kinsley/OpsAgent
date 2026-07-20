import sqlite3
import uuid
from datetime import datetime, timezone

from utils.path_tool import get_abs_path

DB_PATH = get_abs_path("data/chat_history.db")

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)        
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_conversations() -> list[dict]:
    """Return conversations, newest first."""
    init_db()
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def create_conversation(title: str = "New chat") -> str:
    init_db()
    conversation_id = str(uuid.uuid4())
    now = _now()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO conversations (id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, title, now, now),
        )
        conn.commit()
        return conversation_id
    finally:
        conn.close()


def get_messages(conversation_id: str) -> list[dict]:
    init_db()
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()
        #the format should be a list of dictionaries with the following keys: role, content
        return [{"role": row["role"], "content": row["content"]} for row in rows]
    finally:
        conn.close()


def add_message(conversation_id: str, role: str, content: str) -> None:
    init_db()
    now = _now()
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, content, now),
        )
        conn.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (now, conversation_id),
        )
        conn.commit()
    finally:
        conn.close()

def update_title(conversation_id: str, title: str) -> None:
    init_db()
    now = _now()
    conn = _connect()
    try:
        conn.execute(
            """
            UPDATE conversations
            SET title = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, now, conversation_id),
        )
        conn.commit()
    finally:
        conn.close()


def ensure_at_least_one_conversation() -> str:
    """If DB is empty, create one chat and return its id."""
    conversations = list_conversations()
    if conversations:
        return conversations[0]["id"]
    return create_conversation()