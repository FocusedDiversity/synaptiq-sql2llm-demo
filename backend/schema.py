"""Schema introspection module - cached at startup."""

from backend.database import get_connection
from backend.models import SchemaColumn, SchemaTable

_cached_schema: list[SchemaTable] | None = None
_cached_schema_text: str | None = None


def introspect_schema() -> list[SchemaTable]:
    global _cached_schema
    if _cached_schema is not None:
        return _cached_schema

    tables = []
    with get_connection(readonly=True) as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        table_names = [row[0] for row in cursor.fetchall()]

        for table_name in table_names:
            col_cursor = conn.execute(f"PRAGMA table_info('{table_name}')")
            columns = []
            for col in col_cursor.fetchall():
                columns.append(
                    SchemaColumn(
                        name=col[1],
                        type=col[2] or "TEXT",
                        nullable=not col[3],
                        primary_key=bool(col[5]),
                    )
                )
            count_cursor = conn.execute(f"SELECT COUNT(*) FROM '{table_name}'")
            row_count = count_cursor.fetchone()[0]
            tables.append(SchemaTable(name=table_name, columns=columns, row_count=row_count))

    _cached_schema = tables
    return tables


def get_schema_text() -> str:
    """Get schema as formatted text for LLM prompts."""
    global _cached_schema_text
    if _cached_schema_text is not None:
        return _cached_schema_text

    tables = introspect_schema()
    lines = []
    for table in tables:
        col_defs = ", ".join(
            f"{c.name} {c.type}{'  PRIMARY KEY' if c.primary_key else ''}" for c in table.columns
        )
        lines.append(f"{table.name} ({table.row_count} rows): {col_defs}")

    _cached_schema_text = "\n".join(lines)
    return _cached_schema_text


def reset_cache():
    global _cached_schema, _cached_schema_text
    _cached_schema = None
    _cached_schema_text = None
