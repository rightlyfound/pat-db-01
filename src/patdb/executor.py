"""Query executor with explicit transaction control. Direct descendant of pat-db-01 v1.1.0."""
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, List, Sequence, Union

QueryResult = Union[List[tuple], int]

def execute(conn: sqlite3.Connection, query: str, params: Sequence[Any] = ()) -> QueryResult:
    """Execute a query on an existing connection. Returns rows for SELECT, rowcount for DML."""
    try:
        conn.execute("BEGIN")
        with closing(conn.cursor()) as cur:
            cur.execute(query, params)
            result: QueryResult = cur.fetchall() if cur.description else cur.rowcount
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise

def execute_query(db_path: Union[str, Path], query: str, params: Sequence[Any] = ()) -> QueryResult:
    """Legacy v1.1.0 contract: fresh connection per call, closed on all paths."""
    with closing(sqlite3.connect(db_path)) as conn:
        conn.isolation_level = None
        return execute(conn, query, params)
