"""Connection lifecycle tests (Tier 1 scope only — no pooling)."""
from patdb import Database


def test_database_reuse_same_connection(tmp_path):
    db = Database(tmp_path / "x.db")
    c1 = db.connect()
    c2 = db.connect()
    assert c1 is c2
    db.close()
    c3 = db.connect()
    assert c3 is not c1
    db.close()


def test_database_close_idempotent(tmp_path):
    db = Database(tmp_path / "x.db")
    db.connect()
    db.close()
    db.close()  # no error
