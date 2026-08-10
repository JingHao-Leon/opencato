import sqlite3
import threading
from datetime import datetime, date

from . import config

_lock = threading.Lock()
_conn = sqlite3.connect(config.DATABASE_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row


def init():
    with _lock, _conn:
        _conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id    TEXT PRIMARY KEY,
                first_seen TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    TEXT NOT NULL,
                text       TEXT NOT NULL,
                remind_at  TEXT NOT NULL,
                kind       TEXT NOT NULL DEFAULT 'reminder',  -- reminder | focus
                sent       INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS checkins (
                user_id TEXT NOT NULL,
                day     TEXT NOT NULL,
                PRIMARY KEY (user_id, day)
            );
            """
        )


def touch_user(user_id: str):
    with _lock, _conn:
        _conn.execute(
            "INSERT OR IGNORE INTO users (user_id, first_seen) VALUES (?, ?)",
            (user_id, datetime.now().isoformat(timespec="seconds")),
        )


def add_reminder(user_id: str, text: str, remind_at: datetime, kind: str = "reminder") -> int:
    with _lock, _conn:
        cur = _conn.execute(
            "INSERT INTO reminders (user_id, text, remind_at, kind, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, text, remind_at.isoformat(timespec="seconds"), kind,
             datetime.now().isoformat(timespec="seconds")),
        )
        return cur.lastrowid


def due_reminders(now: datetime) -> list[sqlite3.Row]:
    with _lock:
        return _conn.execute(
            "SELECT * FROM reminders WHERE sent = 0 AND remind_at <= ?",
            (now.isoformat(timespec="seconds"),),
        ).fetchall()


def mark_sent(reminder_id: int):
    with _lock, _conn:
        _conn.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))


def pending_reminders(user_id: str) -> list[sqlite3.Row]:
    with _lock:
        return _conn.execute(
            "SELECT * FROM reminders WHERE user_id = ? AND sent = 0 ORDER BY remind_at",
            (user_id,),
        ).fetchall()


def checkin(user_id: str) -> int:
    """记录今日打卡，返回历史总打卡天数。"""
    with _lock, _conn:
        _conn.execute(
            "INSERT OR IGNORE INTO checkins (user_id, day) VALUES (?, ?)",
            (user_id, date.today().isoformat()),
        )
        row = _conn.execute(
            "SELECT COUNT(*) AS n FROM checkins WHERE user_id = ?", (user_id,)
        ).fetchone()
        return row["n"]
