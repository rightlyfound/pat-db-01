"""T1-T7, carried from pat-db-01 v1.1.0 audit. T3 records the amendment; T7 records the closure caveat."""
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

import pytest

from patdb import Database, execute, execute_query


def test_t1_select_returns_rows(tmp_path: Path):
    db_path = tmp_path / "t1.db"
    execute_query(db_path, "CREATE TABLE t (id INTEGER, name TEXT)")
    execute_query(db_path, "INSERT INTO t VALUES (1, 'a'), (2, 'b')")
    rows = execute_query(db_path, "SELECT id, name FROM t ORDER BY id")
    assert rows == [(1, "a"), (2, "b")]


def test_t2_partial_dml_rollback(tmp_path: Path):
    db_path = tmp_path / "t2.db"
    execute_query(db_path, "CREATE TABLE t (id INTEGER)")
    execute_query(db_path, "INSERT INTO t VALUES (1)")
    with closing(sqlite3.connect(db_path)) as conn:
        conn.isolation_level = None
        with pytest.raises(sqlite3.OperationalError):
            execute(conn, "INSERT INTO t VALUES (2)")
            execute(conn, "INSERT INTO nonexistent VALUES (3)")
    assert execute_query(db_path, "SELECT COUNT(*) FROM t") == [(1,)]


def test_t3_no_open_transaction_after_success_and_exception(tmp_path: Path):
    # Amendment record: original assertion (count==1) was a harness bug; corrected to count==2.
    db_path = tmp_path / "t3.db"
    execute_query(db_path, "CREATE TABLE t (id INTEGER)")
    execute_query(db_path, "INSERT INTO t VALUES (1)")
    with closing(sqlite3.connect(db_path)) as conn:
        conn.isolation_level = None
        conn.execute("BEGIN")
        conn.execute("INSERT INTO t VALUES (2)")
        conn.commit()
        assert conn.in_transaction is False
    with pytest.raises(sqlite3.OperationalError):
        execute_query(db_path, "INSERT INTO missing VALUES (1)")
    assert execute_query(db_path, "SELECT COUNT(*) FROM t") == [(2,)]


def test_t4_failure_propagation_and_cleanup(tmp_path: Path):
    db_path = tmp_path / "t4.db"
    execute_query(db_path, "CREATE TABLE t (id INTEGER)")
    execute_query(db_path, "INSERT INTO t VALUES (1)")
    with pytest.raises(sqlite3.OperationalError):
        execute_query(db_path, "INSERT INTO missing VALUES (9)")
    assert execute_query(db_path, "SELECT COUNT(*) FROM t") == [(1,)]


def test_t5_repeated_failure_stability(tmp_path: Path):
    db_path = tmp_path / "t5.db"
    execute_query(db_path, "CREATE TABLE t (id INTEGER)")
    for _ in range(50):
        with pytest.raises(sqlite3.OperationalError):
            execute_query(db_path, "INSERT INTO missing VALUES (1)")
    assert execute_query(db_path, "SELECT COUNT(*) FROM t") == [(0,)]


def test_t6_ddl_commit_and_rollback(tmp_path: Path):
    db1 = tmp_path / "t6a.db"
    execute_query(db1, "CREATE TABLE committed (id INTEGER)")
    assert execute_query(db1, "SELECT name FROM sqlite_master WHERE name='committed'")

    db2 = tmp_path / "t6b.db"
    with closing(sqlite3.connect(db2)) as conn:
        conn.isolation_level = None
        with pytest.raises(sqlite3.OperationalError):
            execute(conn, "CREATE TABLE rolled_back (id INTEGER)")
            execute(conn, "INSERT INTO missing VALUES (1)")
    assert execute_query(db2, "SELECT name FROM sqlite_master WHERE name='rolled_back'") == []


def test_t7_close_invoked_on_failure_path(tmp_path: Path, monkeypatch):
    # Measures close() invocation via proxy spy (weakref unsupported on sqlite3.Connection).
    db_path = tmp_path / "t7.db"
    execute_query(db_path, "CREATE TABLE t (id INTEGER)")

    class ConnSpy:
        def __init__(self, real):
            self._real = real
            self.closed = False
        def close(self):
            self.closed = True
            return self._real.close()
        def __getattr__(self, name):
            return getattr(self._real, name)
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return self._real.__exit__(*a)

    spies = []
    real_connect = sqlite3.connect
    def spy_connect(*a, **k):
        s = ConnSpy(real_connect(*a, **k))
        spies.append(s)
        return s
    monkeypatch.setattr(sqlite3, "connect", spy_connect)
    for _ in range(3):
        with pytest.raises(sqlite3.OperationalError):
            execute_query(db_path, "INSERT INTO missing VALUES (1)")
    assert len(spies) == 3
    assert all(s.closed for s in spies)


def test_database_context_manager_closes(tmp_path: Path):
    db_path = tmp_path / "ctx.db"
    with Database(db_path) as db:
        execute(db.connect(), "CREATE TABLE t (id INTEGER)")
        execute(db.connect(), "INSERT INTO t VALUES (1)")
        assert execute(db.connect(), "SELECT COUNT(*) FROM t") == [(1,)]
    # Reusing after close reconnects cleanly
    with Database(db_path) as db:
        assert execute(db.connect(), "SELECT COUNT(*) FROM t") == [(1,)]
