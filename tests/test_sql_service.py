"""Tests for SQL validation service."""

import pytest

from backend.services.sql_service import validate_sql


class TestValidateSQL:
    def test_valid_select(self):
        ok, reason = validate_sql("SELECT * FROM customers")
        assert ok is True
        assert reason is None

    def test_valid_select_with_where(self):
        ok, _ = validate_sql("SELECT name FROM customers WHERE id = 1")
        assert ok is True

    def test_valid_select_with_join(self):
        ok, _ = validate_sql(
            "SELECT c.name, v.make FROM customers c JOIN vehicles v ON c.id = v.customer_id"
        )
        assert ok is True

    def test_valid_with_cte(self):
        ok, _ = validate_sql("WITH top AS (SELECT * FROM customers) SELECT * FROM top")
        assert ok is True

    def test_valid_select_with_trailing_semicolon(self):
        ok, _ = validate_sql("SELECT * FROM customers;")
        assert ok is True

    def test_reject_insert(self):
        ok, reason = validate_sql("INSERT INTO customers (name) VALUES ('test')")
        assert ok is False
        assert "INSERT" in reason

    def test_reject_update(self):
        ok, reason = validate_sql("UPDATE customers SET name = 'test'")
        assert ok is False
        assert "UPDATE" in reason

    def test_reject_delete(self):
        ok, reason = validate_sql("DELETE FROM customers")
        assert ok is False
        assert "DELETE" in reason

    def test_reject_drop(self):
        ok, reason = validate_sql("DROP TABLE customers")
        assert ok is False
        assert "DROP" in reason

    def test_reject_alter(self):
        ok, reason = validate_sql("ALTER TABLE customers ADD COLUMN age INTEGER")
        assert ok is False
        assert "ALTER" in reason

    def test_reject_create(self):
        ok, reason = validate_sql("CREATE TABLE test (id INTEGER)")
        assert ok is False
        assert "CREATE" in reason

    def test_reject_pragma(self):
        ok, reason = validate_sql("PRAGMA table_info(customers)")
        assert ok is False
        assert "PRAGMA" in reason

    def test_reject_multiple_statements(self):
        ok, reason = validate_sql("SELECT 1; SELECT 2")
        assert ok is False
        assert "Multiple" in reason

    def test_reject_empty(self):
        ok, reason = validate_sql("")
        assert ok is False
        assert "Empty" in reason

    def test_reject_comment_only(self):
        ok, reason = validate_sql("-- just a comment")
        assert ok is False

    def test_strip_comments_valid(self):
        ok, _ = validate_sql("-- this is a comment\nSELECT * FROM customers")
        assert ok is True

    def test_reject_non_select(self):
        ok, reason = validate_sql("EXPLAIN SELECT * FROM customers")
        assert ok is False
        assert "EXPLAIN" in reason
