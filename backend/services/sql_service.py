"""SQL validation service — whitelist approach allowing only SELECT statements."""

import re


def _strip_comments(sql: str) -> str:
    """Remove SQL comments (single-line and multi-line) from the query."""
    # Remove multi-line comments /* ... */
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    # Remove single-line comments -- ...
    sql = re.sub(r"--[^\n]*", " ", sql)
    return sql.strip()


_BLOCKED_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA)\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> tuple[bool, str | None]:
    """Validate that *sql* is a safe read-only SELECT statement.

    Returns (True, None) when the query is acceptable, or
    (False, reason) when it should be rejected.
    """
    cleaned = _strip_comments(sql)

    if not cleaned:
        return False, "Empty query"

    # Reject multiple statements (semicolons not at the very end)
    without_trailing = cleaned.rstrip().rstrip(";")
    if ";" in without_trailing:
        return False, "Multiple statements are not allowed"

    # Check for blocked keywords anywhere in the cleaned SQL
    match = _BLOCKED_KEYWORDS.search(cleaned)
    if match:
        keyword = match.group(1).upper()
        return False, f"{keyword} statements are not allowed — only SELECT queries are permitted"

    # Must start with SELECT (or WITH for CTEs)
    first_word = cleaned.split()[0].upper()
    if first_word not in ("SELECT", "WITH"):
        return False, f"Only SELECT queries are allowed (got {first_word})"

    return True, None
