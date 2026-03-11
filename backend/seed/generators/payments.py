"""Generate payment_methods, invoices (~8600), payments (~8600), refunds,
finishing_services, finishing_records, quality_inspections."""

import random
from datetime import date, timedelta, datetime


FINISHING_SERVICES = [
    ("Hand Dry", "Towel hand-dry for a streak-free finish", 5.00, 10),
    ("Tire Shine", "Apply tire shine gel for a glossy look", 3.00, 5),
    ("Interior Wipe", "Quick wipe-down of dashboard and console", 7.00, 10),
    ("Air Freshener", "Premium air freshener installation", 2.00, 2),
    ("Window Clean", "Interior and exterior window cleaning", 4.00, 8),
]

PAYMENT_TYPES = ["credit_card", "debit_card", "cash", "mobile_pay"]
TAX_RATE = 0.086  # Arizona sales tax


def seed_payments(conn):
    """Seed finishing_services, finishing_records, quality_inspections,
    payment_methods, invoices, payments, and refunds."""

    # --- Finishing Services ---
    conn.executemany(
        """INSERT INTO finishing_services (name, description, price, duration_minutes)
           VALUES (?, ?, ?, ?)""",
        FINISHING_SERVICES,
    )
    conn.commit()

    finishing_svc_rows = conn.execute(
        "SELECT id, name, price FROM finishing_services"
    ).fetchall()
    finishing_ids = [r[0] for r in finishing_svc_rows]
    finishing_prices = {r[0]: r[2] for r in finishing_svc_rows}

    # Fetch check-ins
    checkin_data = conn.execute(
        "SELECT id, customer_id, check_out_time FROM check_ins"
    ).fetchall()

    employee_ids = [r[0] for r in conn.execute("SELECT id FROM employees").fetchall()]
    customer_ids = [r[0] for r in conn.execute("SELECT id FROM customers").fetchall()]

    # --- Finishing Records ---
    # ~40% of check-ins get 1-3 finishing services
    finishing_rows = []
    for ci_id, cust_id, co_time in checkin_data:
        if random.random() < 0.40:
            num_services = random.choices([1, 2, 3], weights=[50, 35, 15], k=1)[0]
            selected = random.sample(finishing_ids, min(num_services, len(finishing_ids)))
            for svc_id in selected:
                emp_id = random.choice(employee_ids)
                completed_at = co_time  # completed around checkout
                finishing_rows.append((ci_id, svc_id, emp_id, completed_at))

    conn.executemany(
        """INSERT INTO finishing_records
           (check_in_id, service_id, employee_id, completed_at)
           VALUES (?, ?, ?, ?)""",
        finishing_rows,
    )
    conn.commit()

    # --- Quality Inspections ---
    # ~30% of check-ins get a quality inspection
    inspection_rows = []
    for ci_id, cust_id, co_time in checkin_data:
        if random.random() < 0.30:
            inspector_id = random.choice(employee_ids)
            score = random.choices(
                list(range(1, 11)),
                weights=[1, 1, 2, 3, 5, 8, 15, 25, 25, 15],
                k=1,
            )[0]
            passed = 1 if score >= 6 else 0

            notes = None
            if score < 7:
                note_options = [
                    "Spots missed on rear bumper",
                    "Water spots on driver window",
                    "Wax application uneven on hood",
                    "Tire shine not applied evenly",
                    "Interior wipe missed center console",
                ]
                notes = random.choice(note_options)

            inspection_rows.append((
                ci_id, inspector_id, score, passed, notes, co_time,
            ))

    conn.executemany(
        """INSERT INTO quality_inspections
           (check_in_id, inspector_id, score, passed, notes, inspected_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        inspection_rows,
    )
    conn.commit()

    # --- Payment Methods ---
    # Each customer gets 1-2 payment methods
    pm_rows = []
    for cust_id in customer_ids:
        num_methods = random.choices([1, 2], weights=[60, 40], k=1)[0]
        methods = random.sample(PAYMENT_TYPES, num_methods)
        for i, method in enumerate(methods):
            last_four = f"{random.randint(1000, 9999)}" if method != "cash" else None
            is_default = 1 if i == 0 else 0
            pm_rows.append((cust_id, method, last_four, is_default))

    conn.executemany(
        """INSERT INTO payment_methods
           (customer_id, method_type, last_four, is_default)
           VALUES (?, ?, ?, ?)""",
        pm_rows,
    )
    conn.commit()

    # Build customer -> payment_method_id map (default)
    pm_data = conn.execute(
        "SELECT id, customer_id FROM payment_methods WHERE is_default = 1"
    ).fetchall()
    cust_pm_map = {r[1]: r[0] for r in pm_data}
    # Fallback for any customer without a default
    all_pm_data = conn.execute("SELECT id, customer_id FROM payment_methods").fetchall()
    for pm_id, cust_id in all_pm_data:
        if cust_id not in cust_pm_map:
            cust_pm_map[cust_id] = pm_id

    # --- Get wash session prices for each check-in ---
    wash_prices = {}
    ws_data = conn.execute(
        """SELECT ws.check_in_id, wp.price
           FROM wash_sessions ws
           JOIN wash_packages wp ON ws.package_id = wp.id"""
    ).fetchall()
    for ci_id, price in ws_data:
        wash_prices[ci_id] = price

    # Get finishing service totals per check-in
    finishing_totals = {}
    fr_data = conn.execute(
        """SELECT fr.check_in_id, SUM(fs.price)
           FROM finishing_records fr
           JOIN finishing_services fs ON fr.service_id = fs.id
           GROUP BY fr.check_in_id"""
    ).fetchall()
    for ci_id, total in fr_data:
        finishing_totals[ci_id] = total

    # --- Invoices for Check-ins ---
    invoice_rows = []
    for ci_id, cust_id, co_time in checkin_data:
        wash_price = wash_prices.get(ci_id, 0)
        finish_price = finishing_totals.get(ci_id, 0)
        subtotal = round(wash_price + finish_price, 2)
        tax = round(subtotal * TAX_RATE, 2)
        total = round(subtotal + tax, 2)
        invoice_date = co_time[:10] if co_time else "2024-06-15"

        invoice_rows.append((
            cust_id, ci_id, None,  # no detail_appointment_id
            invoice_date, subtotal, tax, total, "paid",
        ))

    # --- Invoices for Detail Appointments ---
    detail_data = conn.execute(
        """SELECT da.id, da.customer_id, da.scheduled_date, dp.price, da.status
           FROM detail_appointments da
           JOIN detail_packages dp ON da.package_id = dp.id"""
    ).fetchall()

    for da_id, cust_id, sched_date, pkg_price, da_status in detail_data:
        if da_status not in ("completed",):
            continue
        subtotal = round(pkg_price, 2)
        tax = round(subtotal * TAX_RATE, 2)
        total = round(subtotal + tax, 2)

        invoice_rows.append((
            cust_id, None, da_id,  # no check_in_id
            sched_date, subtotal, tax, total, "paid",
        ))

    conn.executemany(
        """INSERT INTO invoices
           (customer_id, check_in_id, detail_appointment_id,
            invoice_date, subtotal, tax, total, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        invoice_rows,
    )
    conn.commit()

    # --- Payments ---
    invoice_data = conn.execute(
        "SELECT id, customer_id, invoice_date, total FROM invoices ORDER BY id"
    ).fetchall()

    payment_rows = []
    for inv_id, cust_id, inv_date, total in invoice_data:
        pm_id = cust_pm_map.get(cust_id)
        # Payment on same day or next day
        pay_date = inv_date
        status = "completed"
        if random.random() < 0.02:
            status = "failed"

        payment_rows.append((
            inv_id, pm_id, total,
            f"{pay_date} {random.randint(8, 19):02d}:{random.randint(0, 59):02d}:00",
            status,
        ))

    conn.executemany(
        """INSERT INTO payments
           (invoice_id, payment_method_id, amount, payment_date, status)
           VALUES (?, ?, ?, ?, ?)""",
        payment_rows,
    )
    conn.commit()

    # --- Refunds (linked to complaints) ---
    complaint_data = conn.execute(
        "SELECT id, check_in_id, created_date FROM complaints WHERE status = 'resolved'"
    ).fetchall()

    refund_rows = []
    for comp_id, ci_id, comp_date in complaint_data:
        # ~40% of resolved complaints result in a refund
        if random.random() > 0.40:
            continue

        # Find the payment for this check-in
        payment_row = conn.execute(
            """SELECT p.id, p.amount FROM payments p
               JOIN invoices i ON p.invoice_id = i.id
               WHERE i.check_in_id = ?
               LIMIT 1""",
            (ci_id,),
        ).fetchone()

        if not payment_row:
            continue

        payment_id, original_amount = payment_row
        # Refund 50-100% of original amount
        refund_pct = random.choice([0.5, 0.75, 1.0])
        refund_amount = round(original_amount * refund_pct, 2)

        reasons = [
            "Customer dissatisfied with wash quality",
            "Service not delivered as promised",
            "Damage compensation",
            "Billing error correction",
            "Goodwill refund per manager approval",
        ]
        reason = random.choice(reasons)
        refund_date = (
            date.fromisoformat(comp_date) + timedelta(days=random.randint(1, 7))
        ).isoformat()

        refund_rows.append((
            payment_id, comp_id, refund_amount,
            reason, refund_date, "processed",
        ))

    conn.executemany(
        """INSERT INTO refunds
           (payment_id, complaint_id, amount, reason, refund_date, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        refund_rows,
    )
    conn.commit()

    print(f"  Inserted {len(FINISHING_SERVICES)} finishing services")
    print(f"  Inserted {len(finishing_rows)} finishing records")
    print(f"  Inserted {len(inspection_rows)} quality inspections")
    print(f"  Inserted {len(pm_rows)} payment methods")
    print(f"  Inserted {len(invoice_rows)} invoices")
    print(f"  Inserted {len(payment_rows)} payments")
    print(f"  Inserted {len(refund_rows)} refunds")
