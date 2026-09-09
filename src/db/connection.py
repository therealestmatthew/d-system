from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import duckdb

DB_PATH = Path("data/d_system.duckdb")


@contextmanager
def get_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    try:
        yield conn
    finally:
        conn.close()
