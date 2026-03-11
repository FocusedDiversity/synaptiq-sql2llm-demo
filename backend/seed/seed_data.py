"""Master orchestrator that calls all seed generators in the correct order."""

import random
import time

from backend.seed.generators.customers import seed_customers
from backend.seed.generators.vehicles import seed_vehicles
from backend.seed.generators.workforce import seed_workforce
from backend.seed.generators.equipment import seed_equipment
from backend.seed.generators.wash_operations import seed_wash_operations
from backend.seed.generators.detailing import seed_detailing
from backend.seed.generators.chemicals import seed_chemicals
from backend.seed.generators.customer_experience import seed_customer_experience
from backend.seed.generators.compliance import seed_compliance
from backend.seed.generators.memberships import seed_memberships
from backend.seed.generators.payments import seed_payments


def seed_all(conn):
    """Run all seed generators in dependency order.

    Order matters:
    1. Customers (no deps)
    2. Vehicles (depends on customers)
    3. Workforce: roles, employees, shifts (no deps on customer data)
    4. Equipment (no deps on customer data, needed by wash_operations)
    5. Wash operations: wash_packages, check_ins, wash_sessions, wash_cycle_steps
       (depends on vehicles, customers, employees, equipment)
    6. Detailing: detail_packages, detail_appointments, detail_line_items
       (depends on vehicles, customers, employees)
    7. Chemicals: chemicals, chemical_usage_logs, purchase_orders
       (depends on wash_sessions)
    8. Customer experience: feedback, complaints, loyalty
       (depends on customers, check_ins)
    9. Compliance: water_usage, chemical_disposal, permits, inspections
       (depends on chemicals, employees)
    10. Memberships: plans, subscriptions, billing
        (depends on customers, wash_packages)
    11. Payments: finishing_services, finishing_records, quality_inspections,
        payment_methods, invoices, payments, refunds
        (depends on check_ins, detail_appointments, customers, complaints)
    """
    random.seed(42)

    total_start = time.time()

    steps = [
        ("Customers", seed_customers),
        ("Vehicles", seed_vehicles),
        ("Workforce (roles, employees, shifts, timecards, performance)", seed_workforce),
        ("Equipment (items, maintenance, downtime)", seed_equipment),
        ("Wash Operations (packages, check-ins, sessions, cycle steps)", seed_wash_operations),
        ("Detailing (packages, appointments, line items)", seed_detailing),
        ("Chemicals (inventory, usage, purchase orders)", seed_chemicals),
        ("Customer Experience (feedback, complaints, loyalty)", seed_customer_experience),
        ("Compliance (water, disposal, permits, inspections)", seed_compliance),
        ("Memberships (plans, subscriptions, billing)", seed_memberships),
        ("Payments (finishing, inspections, invoices, payments, refunds)", seed_payments),
    ]

    for i, (label, func) in enumerate(steps, 1):
        print(f"[{i}/{len(steps)}] Seeding {label}...")
        step_start = time.time()
        func(conn)
        elapsed = time.time() - step_start
        print(f"  Done in {elapsed:.2f}s\n")

    total_elapsed = time.time() - total_start
    print(f"All seed data inserted in {total_elapsed:.2f}s")

    # Print summary counts
    print("\n--- Summary ---")
    tables = [
        "customers", "vehicles", "roles", "employees", "shifts", "timecards",
        "employee_performance", "equipment", "maintenance_logs", "equipment_downtime",
        "wash_packages", "check_ins", "wash_sessions", "wash_cycle_steps",
        "detail_packages", "detail_appointments", "detail_line_items",
        "chemicals", "chemical_usage_logs", "purchase_orders", "purchase_order_items",
        "customer_feedback", "complaints", "loyalty_programs", "loyalty_transactions",
        "water_usage", "chemical_disposal", "permits", "regulatory_inspections",
        "membership_plans", "member_subscriptions", "membership_billing",
        "finishing_services", "finishing_records", "quality_inspections",
        "payment_methods", "invoices", "payments", "refunds",
    ]
    for table in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count:,}")
        except Exception:
            print(f"  {table}: (table not found)")
