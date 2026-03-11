"""Tests for database module and seeded data."""

import sqlite3
import pytest

from backend.database import execute_query, get_db_path


@pytest.fixture(scope="module")
def db_conn():
    """Use the seeded database for tests."""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


class TestDatabaseSeeding:
    def test_customers_count(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        assert count == 500

    def test_vehicles_count(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
        assert count == 650

    def test_employees_count(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        assert count == 25

    def test_roles_count(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM roles").fetchone()[0]
        assert count == 7

    def test_wash_packages_count(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM wash_packages").fetchone()[0]
        assert count == 5

    def test_check_ins_populated(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM check_ins").fetchone()[0]
        assert count > 7000

    def test_wash_sessions_match_check_ins(self, db_conn):
        ci = db_conn.execute("SELECT COUNT(*) FROM check_ins").fetchone()[0]
        ws = db_conn.execute("SELECT COUNT(*) FROM wash_sessions").fetchone()[0]
        assert ci == ws

    def test_detail_appointments_populated(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM detail_appointments").fetchone()[0]
        assert count == 600

    def test_equipment_count(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0]
        assert count == 20

    def test_chemicals_count(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM chemicals").fetchone()[0]
        assert count == 15

    def test_customer_feedback_populated(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM customer_feedback").fetchone()[0]
        assert count == 2500

    def test_water_usage_365_days(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM water_usage").fetchone()[0]
        assert count >= 365

    def test_membership_plans(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM membership_plans").fetchone()[0]
        assert count == 4

    def test_member_subscriptions(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM member_subscriptions").fetchone()[0]
        assert count == 120

    def test_invoices_populated(self, db_conn):
        count = db_conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        assert count > 8000

    def test_all_38_tables_exist(self, db_conn):
        tables = db_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        expected = [
            "customers", "marketing_campaigns", "leads", "referrals",
            "vehicles", "check_ins", "vehicle_condition_notes",
            "wash_packages", "wash_sessions", "wash_cycle_steps",
            "finishing_services", "finishing_records", "quality_inspections",
            "detail_packages", "detail_appointments", "detail_line_items",
            "equipment", "maintenance_logs", "equipment_downtime",
            "chemicals", "chemical_usage_logs", "purchase_orders", "purchase_order_items",
            "roles", "employees", "shifts", "timecards", "employee_performance",
            "customer_feedback", "complaints", "loyalty_programs", "loyalty_transactions",
            "water_usage", "chemical_disposal", "permits", "regulatory_inspections",
            "membership_plans", "member_subscriptions", "membership_billing",
            "payment_methods", "invoices", "payments", "refunds",
        ]
        for tbl in expected:
            assert tbl in table_names, f"Missing table: {tbl}"


class TestExecuteQuery:
    def test_simple_select(self):
        result = execute_query("SELECT COUNT(*) as cnt FROM customers")
        assert result["columns"] == ["cnt"]
        assert result["rows"][0][0] == 500
        assert result["truncated"] is False

    def test_truncation(self):
        result = execute_query("SELECT * FROM check_ins")
        assert result["truncated"] is True
        assert len(result["rows"]) == 500

    def test_join_query(self):
        result = execute_query(
            "SELECT c.first_name, v.make FROM customers c "
            "JOIN vehicles v ON c.id = v.customer_id LIMIT 5"
        )
        assert len(result["columns"]) == 2
        assert len(result["rows"]) == 5
