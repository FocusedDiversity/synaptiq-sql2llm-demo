import sqlite3
from contextlib import contextmanager
from pathlib import Path

from backend.config import settings

MAX_ROWS = 500


def get_db_path() -> Path:
    return Path(settings.database_path)


@contextmanager
def get_connection(readonly: bool = True):
    db_path = get_db_path()
    uri = f"file:{db_path}{'?mode=ro' if readonly else ''}"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def execute_query(sql: str) -> dict:
    """Execute a read-only SQL query and return columns + rows."""
    with get_connection(readonly=True) as conn:
        cursor = conn.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchmany(MAX_ROWS + 1)
        truncated = len(rows) > MAX_ROWS
        if truncated:
            rows = rows[:MAX_ROWS]
        return {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "truncated": truncated,
        }
