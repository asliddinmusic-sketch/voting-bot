"""
database.py — SQLite ma'lumotlar bazasi
Ovozlarni saqlash va olish uchun
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "votes.db"


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                user_id     INTEGER PRIMARY KEY,
                candidate_id INTEGER NOT NULL,
                voted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def has_voted(self, user_id: int) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM votes WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row is not None

    def get_user_vote(self, user_id: int) -> int | None:
        row = self.conn.execute(
            "SELECT candidate_id FROM votes WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row[0] if row else None

    def save_vote(self, user_id: int, candidate_id: int):
        self.conn.execute(
            "INSERT OR IGNORE INTO votes (user_id, candidate_id) VALUES (?, ?)",
            (user_id, candidate_id)
        )
        self.conn.commit()

    def get_all_votes(self) -> dict[int, int]:
        rows = self.conn.execute(
            "SELECT candidate_id, COUNT(*) FROM votes GROUP BY candidate_id"
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    def count_voters(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM votes").fetchone()
        return row[0]

    def reset_votes(self):
        self.conn.execute("DELETE FROM votes")
        self.conn.commit()


# Global instance
db = Database()
