from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock


DB_PATH = Path("token_guardian.db")
_LOCK = Lock()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _LOCK:
        with get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    estimated_cost_usd REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

