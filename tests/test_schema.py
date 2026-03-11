"""Tests for schema introspection."""

import pytest

from backend.schema import introspect_schema, get_schema_text, reset_cache


@pytest.fixture(autouse=True)
def clear_cache():
    reset_cache()
    yield
    reset_cache()


class TestSchemaIntrospection:
    def test_returns_tables(self):
        tables = introspect_schema()
        assert len(tables) >= 38

    def test_customers_table(self):
        tables = introspect_schema()
        customers = next(t for t in tables if t.name == "customers")
        assert customers.row_count == 500
        col_names = [c.name for c in customers.columns]
        assert "first_name" in col_names
        assert "email" in col_names

    def test_schema_text_contains_tables(self):
        text = get_schema_text()
        assert "customers" in text
        assert "vehicles" in text
        assert "wash_packages" in text
        assert "500 rows" in text

    def test_caching(self):
        t1 = introspect_schema()
        t2 = introspect_schema()
        assert t1 is t2  # Same object, from cache
