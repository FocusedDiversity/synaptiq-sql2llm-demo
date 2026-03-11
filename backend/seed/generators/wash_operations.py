"""Generate wash_packages, check_ins, wash_sessions, and wash_cycle_steps."""

import random
import math
from datetime import datetime, date, timedelta


WASH_PACKAGES = [
    ("Express", 8.00, "Quick exterior rinse and dry", 10),
    ("Basic", 12.00, "Exterior wash with soap and rinse", 15),
    ("Standard", 18.00, "Full wash with wax coating", 20),
    ("Premium", 25.00, "Full wash, wax, undercarriage, and tire shine", 30),
    ("Ultimate", 35.00, "Complete wash with hand dry and interior wipe", 45),
]

WASH_CYCLE_STEPS_BY_PACKAGE = {
    "Express": [
        ("Pre-rinse", 30),
        ("Soap application", 45),
        ("High-pressure rinse", 40),
        ("Air dry", 60),
    ],
    "Basic": [
        ("Pre-rinse", 30),
        ("Soap application", 60),
        ("Brush wash", 90),
        ("High-pressure rinse", 45),
        ("Spot-free rinse", 30),
        ("Air dry", 60),
    ],
    "Standard": [
        ("Pre-rinse", 30),
        ("Pre-soak", 45),
        ("Soap application", 60),
        ("Brush wash", 90),
        ("High-pressure rinse", 45),
        ("Wax application", 60),
        ("Spot-free rinse", 30),
        ("Air dry", 90),
    ],
    "Premium": [
        ("Pre-rinse", 30),
        ("Pre-soak", 60),
        ("Soap application", 60),
        ("Brush wash", 120),
        ("Undercarriage wash", 60),
        ("High-pressure rinse", 45),
        ("Wax application", 90),
        ("Tire shine", 45),
        ("Spot-free rinse", 30),
        ("Air dry", 120),
    ],
    "Ultimate": [
        ("Pre-rinse", 30),
        ("Pre-soak", 60),
        ("Foam bath", 90),
        ("Soap application", 60),
        ("Brush wash", 120),
        ("Undercarriage wash", 60),
        ("High-pressure rinse", 45),
        ("Triple wax application", 120),
        ("Tire shine", 45),
        ("Wheel cleaning", 60),
        ("Spot-free rinse", 30),
        ("Air dry", 120),
        ("Hand dry", 180),
    ],
}


def _daily_volume(day_of_year, day_of_week):
    """Calculate expected check-ins for a given day using seasonal + weekend patterns.

    Summer peak (~30/day around July), winter low (~15/day around January).
    Weekend bump of ~30%.
    """
    # Seasonal: sin curve peaking around day 182 (July 1)
    seasonal = 22.5 + 7.5 * math.sin(2 * math.pi * (day_of_year - 91) / 365)
    # Weekend bump
    if day_of_week >= 5:  # Saturday=5, Sunday=6
        seasonal *= 1.30
    return max(5, int(round(seasonal)))


def seed_wash_operations(conn):
    """Seed wash_packages, check_ins (~8000), wash_sessions, wash_cycle_steps."""

    # --- Wash Packages ---
    conn.executemany(
        """INSERT INTO wash_packages (name, price, description, duration_minutes)
           VALUES (?, ?, ?, ?)""",
        WASH_PACKAGES,
    )
    conn.commit()

    pkg_rows = conn.execute("SELECT id, name, duration_minutes FROM wash_packages").fetchall()
    pkg_map = {row[1]: row[0] for row in pkg_rows}  # name -> id
    pkg_ids = [row[0] for row in pkg_rows]
    pkg_names = [row[1] for row in pkg_rows]
    pkg_durations = {row[1]: row[2] for row in pkg_rows}
    pkg_weights = [35, 25, 20, 12, 8]  # Express most popular

    # Fetch dependencies
    vehicle_rows = conn.execute("SELECT id, customer_id FROM vehicles").fetchall()
    employee_ids = [r[0] for r in conn.execute("SELECT id FROM employees").fetchall()]
    equipment_ids = [r[0] for r in conn.execute("SELECT id FROM equipment WHERE type IN ('tunnel', 'conveyor')").fetchall()]
    if not equipment_ids:
        equipment_ids = [r[0] for r in conn.execute("SELECT id FROM equipment").fetchall()]

    bays = list(range(1, 6))  # 5 wash bays

    # --- Check-ins, Sessions, Steps ---
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)

    checkin_rows = []
    session_rows = []
    step_rows = []
    checkin_id = 0
    session_id = 0

    current = start_date
    while current <= end_date:
        day_of_year = current.timetuple().tm_yday
        day_of_week = current.weekday()
        volume = _daily_volume(day_of_year, day_of_week)

        for _ in range(volume):
            checkin_id += 1

            vehicle_id, customer_id = random.choice(vehicle_rows)
            emp_id = random.choice(employee_ids)
            bay = random.choice(bays)

            # Random check-in time between 7:00 and 19:00
            hour = random.randint(7, 18)
            minute = random.randint(0, 59)
            checkin_time = datetime(current.year, current.month, current.day, hour, minute)

            pkg_name = random.choices(pkg_names, weights=pkg_weights, k=1)[0]
            duration = pkg_durations[pkg_name]

            checkout_time = checkin_time + timedelta(minutes=duration + random.randint(2, 10))

            checkin_rows.append((
                vehicle_id, customer_id,
                checkin_time.strftime("%Y-%m-%d %H:%M:%S"),
                checkout_time.strftime("%Y-%m-%d %H:%M:%S"),
                bay, emp_id,
            ))

            # Wash session
            session_id += 1
            pkg_id = pkg_map[pkg_name]
            eq_id = random.choice(equipment_ids) if equipment_ids else None
            sess_start = checkin_time + timedelta(minutes=random.randint(1, 3))
            sess_end = sess_start + timedelta(minutes=duration)
            water = round(random.uniform(15, 45) * (duration / 20), 1)

            status = "completed"
            if random.random() < 0.005:
                status = "cancelled"
            elif random.random() < 0.01:
                status = "in_progress"

            session_rows.append((
                checkin_id, pkg_id, eq_id,
                sess_start.strftime("%Y-%m-%d %H:%M:%S"),
                sess_end.strftime("%Y-%m-%d %H:%M:%S"),
                water, status,
            ))

            # Wash cycle steps
            steps = WASH_CYCLE_STEPS_BY_PACKAGE[pkg_name]
            step_time = sess_start
            for step_order, (step_name, step_duration) in enumerate(steps, 1):
                # Add some variance to step duration
                actual_duration = max(10, step_duration + random.randint(-5, 5))
                step_status = "completed" if status == "completed" else "skipped"
                step_rows.append((
                    session_id, step_name, step_order, actual_duration, step_status,
                ))
                step_time += timedelta(seconds=actual_duration)

        current += timedelta(days=1)

    # Bulk insert
    conn.executemany(
        """INSERT INTO check_ins
           (vehicle_id, customer_id, check_in_time, check_out_time, bay_number, employee_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        checkin_rows,
    )
    conn.commit()

    conn.executemany(
        """INSERT INTO wash_sessions
           (check_in_id, package_id, equipment_id, start_time, end_time, water_gallons, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        session_rows,
    )
    conn.commit()

    conn.executemany(
        """INSERT INTO wash_cycle_steps
           (session_id, step_name, step_order, duration_seconds, status)
           VALUES (?, ?, ?, ?, ?)""",
        step_rows,
    )
    conn.commit()

    print(f"  Inserted {len(WASH_PACKAGES)} wash packages")
    print(f"  Inserted {len(checkin_rows)} check-ins")
    print(f"  Inserted {len(session_rows)} wash sessions")
    print(f"  Inserted {len(step_rows)} wash cycle steps")
