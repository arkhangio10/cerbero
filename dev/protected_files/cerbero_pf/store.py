"""SQLite persistente: esquema, conexiones y transacciones de escritura serializadas."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value BLOB NOT NULL);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    notify_email TEXT,
    pw_salt BLOB NOT NULL,
    pw_hash BLOB NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    csrf_token TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS login_failures (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    ip TEXT NOT NULL,
    at_utc TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS login_failures_user ON login_failures(username, at_utc);
CREATE INDEX IF NOT EXISTS login_failures_ip ON login_failures(ip, at_utc);
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    display_name TEXT NOT NULL,
    container_name TEXT NOT NULL,
    media_type TEXT NOT NULL,
    size INTEGER NOT NULL,
    container_sha256 TEXT NOT NULL,
    wrap_nonce BLOB NOT NULL,
    wrapped_key BLOB NOT NULL,
    master_key_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state IN ('active', 'lost', 'revoked')),
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    state_changed_at TEXT
);
CREATE INDEX IF NOT EXISTS documents_owner ON documents(owner_id);
CREATE TABLE IF NOT EXISTS grants (
    id INTEGER PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES documents(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    granted_at TEXT NOT NULL,
    revoked_at TEXT
);
CREATE INDEX IF NOT EXISTS grants_doc ON grants(doc_id, user_id);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    at_utc TEXT NOT NULL,
    kind TEXT NOT NULL,
    result TEXT NOT NULL,
    reason TEXT NOT NULL,
    verified INTEGER NOT NULL,
    doc_id TEXT REFERENCES documents(id),
    claimed_doc_id TEXT,
    owner_id INTEGER REFERENCES users(id),
    actor_user_id INTEGER REFERENCES users(id),
    actor_label TEXT NOT NULL,
    ip TEXT NOT NULL,
    ip_source TEXT NOT NULL,
    forwarded_header TEXT NOT NULL DEFAULT '',
    geo TEXT NOT NULL,
    client_location TEXT NOT NULL,
    user_agent TEXT NOT NULL DEFAULT '',
    detail TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS events_owner ON events(owner_id, id);
CREATE INDEX IF NOT EXISTS events_claimed ON events(claimed_doc_id);
CREATE INDEX IF NOT EXISTS events_ip ON events(ip, at_utc);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL REFERENCES users(id),
    doc_id TEXT REFERENCES documents(id),
    first_event_id INTEGER NOT NULL REFERENCES events(id),
    last_event_id INTEGER NOT NULL REFERENCES events(id),
    dedup_key TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    first_at TEXT NOT NULL,
    last_at TEXT NOT NULL,
    count INTEGER NOT NULL,
    read_at TEXT,
    email_state TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS notifications_dedup ON notifications(owner_id, dedup_key, last_at);
CREATE TABLE IF NOT EXISTS email_outbox (
    id INTEGER PRIMARY KEY,
    notification_id INTEGER NOT NULL UNIQUE REFERENCES notifications(id),
    owner_id INTEGER NOT NULL REFERENCES users(id),
    recipient TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'sent', 'failed')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL,
    next_attempt_at TEXT NOT NULL,
    last_error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    sent_at TEXT
);
CREATE INDEX IF NOT EXISTS outbox_due ON email_outbox(status, next_attempt_at);
"""


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=15, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 15000")
    conn.execute("PRAGMA synchronous = FULL")
    return conn


def initialize(path: Path) -> None:
    conn = connect(path)
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA)
    finally:
        conn.close()


@contextmanager
def write_tx(conn: sqlite3.Connection):
    """BEGIN IMMEDIATE: las escrituras se serializan; el orden de `events.id` es el orden de confirmación."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")
