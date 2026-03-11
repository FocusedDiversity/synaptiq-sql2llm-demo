"""Generate detail_packages, detail_appointments (~600), and detail_line_items."""

import random
from datetime import date, timedelta, datetime


DETAIL_PACKAGES = [
    ("Interior Detail", 80.00, "Full interior cleaning, vacuuming, and conditioning", 90),
    ("Exterior Detail", 100.00, "Clay bar, polish, and sealant", 120),
    ("Full Detail", 160.00, "Complete interior and exterior detailing", 180),
    ("Premium Detail", 250.00, "Full detail with ceramic coating and engine bay", 240),
]

# Line items that correspond to each package
PACKAGE_LINE_ITEMS = {
    "Interior Detail": [
        ("Vacuum and steam clean", 25.00, 20),
        ("Leather/upholstery conditioning", 20.00, 20),
        ("Dashboard and console detailing", 15.00, 15),
        ("Window cleaning (interior)", 10.00, 15),
        ("Odor elimination", 10.00, 20),
    ],
    "Exterior Detail": [
        ("Hand wash and dry", 20.00, 20),
        ("Clay bar treatment", 30.00, 30),
        ("Machine polish", 30.00, 40),
        ("Paint sealant application", 20.00, 30),
    ],
    "Full Detail": [
        ("Hand wash and dry", 20.00, 20),
        ("Clay bar treatment", 25.00, 25),
        ("Machine polish", 25.00, 35),
        ("Paint sealant", 15.00, 25),
        ("Interior vacuum and steam", 25.00, 20),
        ("Leather conditioning", 20.00, 20),
        ("Dashboard detailing", 15.00, 15),
        ("Window cleaning", 15.00, 20),
    ],
    "Premium Detail": [
        ("Hand wash and dry", 20.00, 20),
        ("Clay bar treatment", 25.00, 25),
        ("Multi-stage polish", 40.00, 45),
        ("Ceramic coating", 50.00, 40),
        ("Engine bay cleaning", 25.00, 25),
        ("Interior deep clean", 30.00, 25),
        ("Leather conditioning", 20.00, 20),
        ("Dashboard and trim restoration", 20.00, 20),
        ("Window and mirror treatment", 20.00, 20),
    ],
}

NUM_APPOINTMENTS = 600


def seed_detailing(conn):
    """Seed detail_packages, detail_appointments, and detail_line_items."""

    # --- Detail Packages ---
    conn.executemany(
        """INSERT INTO detail_packages (name, price, description, duration_minutes)
           VALUES (?, ?, ?, ?)""",
        DETAIL_PACKAGES,
    )
    conn.commit()

    pkg_rows = conn.execute("SELECT id, name, price FROM detail_packages").fetchall()
    pkg_map = {row[1]: (row[0], row[2]) for row in pkg_rows}  # name -> (id, price)
    pkg_names = [row[1] for row in pkg_rows]
    pkg_weights = [30, 25, 30, 15]

    # Fetch dependencies
    vehicle_rows = conn.execute("SELECT id, customer_id FROM vehicles").fetchall()
    detailer_ids = [r[0] for r in conn.execute(
        "SELECT e.id FROM employees e JOIN roles r ON e.role_id = r.id WHERE r.name = 'Detailer'"
    ).fetchall()]
    if not detailer_ids:
        detailer_ids = [r[0] for r in conn.execute("SELECT id FROM employees").fetchall()]

    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    date_range = (end_date - start_date).days

    appt_rows = []
    line_items = []
    statuses = ["completed", "completed", "completed", "completed", "cancelled", "no-show"]
    time_slots = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]

    for i in range(NUM_APPOINTMENTS):
        vehicle_id, customer_id = random.choice(vehicle_rows)
        pkg_name = random.choices(pkg_names, weights=pkg_weights, k=1)[0]
        pkg_id, pkg_price = pkg_map[pkg_name]

        scheduled_date = start_date + timedelta(days=random.randint(0, date_range))
        scheduled_time = random.choice(time_slots)
        emp_id = random.choice(detailer_ids)
        status = random.choice(statuses)

        completed_at = None
        if status == "completed":
            dur_minutes = [p[3] for p in DETAIL_PACKAGES if p[0] == pkg_name][0]
            hour, minute = map(int, scheduled_time.split(":"))
            start_dt = datetime(
                scheduled_date.year, scheduled_date.month, scheduled_date.day,
                hour, minute,
            )
            completed_at = (start_dt + timedelta(minutes=dur_minutes + random.randint(-10, 20))).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        notes = None
        if random.random() < 0.15:
            note_options = [
                "Customer requested extra attention on seats",
                "Heavy pet hair in cabin",
                "Deep scratches on driver side",
                "Smoke odor removal needed",
                "Customer will wait on-site",
                "Bird droppings on roof",
                "Tree sap on hood",
                "Customer wants before/after photos",
            ]
            notes = random.choice(note_options)

        appt_rows.append((
            customer_id, vehicle_id, pkg_id,
            scheduled_date.isoformat(), scheduled_time,
            status, emp_id, completed_at, notes,
        ))

        # Line items for completed appointments
        if status == "completed":
            items = PACKAGE_LINE_ITEMS[pkg_name]
            for service_name, price, dur in items:
                # Small price variance
                actual_price = round(price * random.uniform(0.95, 1.05), 2)
                actual_dur = max(5, dur + random.randint(-3, 5))
                line_items.append((i + 1, service_name, actual_price, actual_dur))

    conn.executemany(
        """INSERT INTO detail_appointments
           (customer_id, vehicle_id, package_id, scheduled_date, scheduled_time,
            status, employee_id, completed_at, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        appt_rows,
    )
    conn.commit()

    # Re-fetch appointment IDs to link line items correctly
    appt_ids = [r[0] for r in conn.execute(
        "SELECT id FROM detail_appointments ORDER BY id"
    ).fetchall()]

    # Rebuild line items with correct appointment IDs
    final_line_items = []
    appt_idx = 0
    for i, (_, _, _, _, _, status, _, _, _) in enumerate(appt_rows):
        if status == "completed":
            pkg_name = pkg_names[
                next(j for j, (n, _) in enumerate(
                    [(pn, pkg_map[pn]) for pn in pkg_names]
                ) if pkg_map[n][0] == appt_rows[i][2])
            ]
            items = PACKAGE_LINE_ITEMS[pkg_name]
            real_appt_id = appt_ids[i]
            for service_name, price, dur in items:
                actual_price = round(price * random.uniform(0.95, 1.05), 2)
                actual_dur = max(5, dur + random.randint(-3, 5))
                final_line_items.append((real_appt_id, service_name, actual_price, actual_dur))

    conn.executemany(
        """INSERT INTO detail_line_items
           (appointment_id, service_name, price, duration_minutes)
           VALUES (?, ?, ?, ?)""",
        final_line_items,
    )
    conn.commit()

    print(f"  Inserted {len(DETAIL_PACKAGES)} detail packages")
    print(f"  Inserted {len(appt_rows)} detail appointments")
    print(f"  Inserted {len(final_line_items)} detail line items")
