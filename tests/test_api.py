"""Tests for API endpoints (excluding LLM-dependent /query)."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestSchemaEndpoint:
    def test_schema_returns_tables(self, client):
        resp = client.get("/api/schema")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 38
        table_names = [t["name"] for t in data]
        assert "customers" in table_names

    def test_schema_table_has_columns(self, client):
        resp = client.get("/api/schema")
        data = resp.json()
        customers = next(t for t in data if t["name"] == "customers")
        assert "columns" in customers
        assert len(customers["columns"]) > 0
        assert "row_count" in customers


class TestSuggestionsEndpoint:
    def test_suggestions_returns_categories(self, client):
        resp = client.get("/api/suggestions")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        categories = [s["category"] for s in data]
        assert "Revenue" in categories
        assert "Customers" in categories

    def test_each_category_has_queries(self, client):
        resp = client.get("/api/suggestions")
        data = resp.json()
        for cat in data:
            assert "queries" in cat
            assert len(cat["queries"]) >= 2


class TestQueryEndpointValidation:
    def test_empty_query_returns_error(self, client):
        resp = client.post("/api/query", json={"query": ""})
        assert resp.status_code == 200
        data = resp.json()
        assert data["error"] is not None
        assert "empty" in data["error"].lower()

    def test_missing_api_key_returns_error(self, client):
        resp = client.post("/api/query", json={"query": "How many customers?"})
        assert resp.status_code == 200
        data = resp.json()
        # Without API key set, should get an error about API key
        assert data["error"] is not None
