# patdb

Production-grade SQLite query executor. Direct descendant of pat-db-01 v1.1.0 (7/7 deterministic tests, effective_confidence 0.80).

## Preconditions

- Caller-owned connections are unsupported; `Database` owns the connection lifecycle.
- Pooling and nested transactions are out of scope (Tier 2, unverified).

## Usage

```python
from patdb import Database, execute

with Database("app.db") as db:
    rows = execute(db.connect(), "SELECT * FROM users")
```
