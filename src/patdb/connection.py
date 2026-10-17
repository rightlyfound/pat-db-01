"""Connection lifecycle owner. Fixes the F3 caller-owned-connection tripwire by making ownership explicit."""
import sqlite3
from typing import Optional

class Database:
    """Owns a single sqlite3 connection. Use as a context manager."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.isolation_level = None
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
