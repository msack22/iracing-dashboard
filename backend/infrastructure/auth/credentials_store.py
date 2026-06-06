"""
Stores iRacing credentials encrypted in a local SQLite database.
The encryption key is auto-generated on first run and stored in .secret_key
(excluded from git). Without the key file the database contents are unreadable.
"""
import os
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
_KEY_PATH = _BASE_DIR / ".secret_key"
_DB_PATH  = _BASE_DIR / "credentials.db"


def _load_or_create_key() -> bytes:
    if _KEY_PATH.exists():
        return _KEY_PATH.read_bytes()
    key = Fernet.generate_key()
    _KEY_PATH.write_bytes(key)
    _KEY_PATH.chmod(0o600)  # only owner can read
    return key


def _get_fernet() -> Fernet:
    return Fernet(_load_or_create_key())


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS credentials (
               id       INTEGER PRIMARY KEY,
               username BLOB NOT NULL,
               password BLOB NOT NULL
           )"""
    )
    conn.commit()
    return conn


def save_credentials(username: str, password: str) -> None:
    fernet = _get_fernet()
    enc_user = fernet.encrypt(username.encode())
    enc_pass = fernet.encrypt(password.encode())
    with _get_connection() as conn:
        conn.execute("DELETE FROM credentials")
        conn.execute("INSERT INTO credentials (username, password) VALUES (?, ?)", (enc_user, enc_pass))


def load_credentials():
    # Returns (username, password) tuple or None
    """Returns (username, password) or None if not configured."""
    with _get_connection() as conn:
        row = conn.execute("SELECT username, password FROM credentials LIMIT 1").fetchone()
    if not row:
        return None
    fernet = _get_fernet()
    username = fernet.decrypt(row[0]).decode()
    password = fernet.decrypt(row[1]).decode()
    return username, password


def credentials_exist() -> bool:
    with _get_connection() as conn:
        row = conn.execute("SELECT 1 FROM credentials LIMIT 1").fetchone()
    return row is not None


def delete_credentials() -> None:
    with _get_connection() as conn:
        conn.execute("DELETE FROM credentials")
