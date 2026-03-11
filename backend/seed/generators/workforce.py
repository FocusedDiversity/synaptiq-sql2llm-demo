"""Generate roles, employees (25), shifts, timecards (~6500), employee_performance."""

import random
from datetime import date, timedelta, datetime


ROLES = [
    ("Manager", 25.00, "Oversees daily operations and staff management"),
    ("Shift Lead", 20.00, "Supervises shift operations and team coordination"),
    ("Washer", 15.00, "Operates wash equipment and performs vehicle washing"),
    ("Detailer", 18.00, "Performs detailed interior and exterior vehicle cleaning"),
    ("Cashier", 14.00, "Handles customer transactions and front desk duties"),
    ("Maintenance Tech", 22.00, "Maintains and repairs wash equipment"),
    ("Attendant", 13.00, "Assists customers, guides vehicles, general duties"),
]

SHIFTS = [
    ("Morning", "06:00", "14:00"),
    ("Midday", "10:00", "18:00"),
    ("Afternoon", "14:00", "22:00"),
    ("Weekend", "08:00", "16:00"),
]

# (first_name, last_name, role_name, hire_date, status)
EMPLOYEES = [
    ("Carlos", "Mendez", "Manager", "2020-03-15", "active"),
    ("Sarah", "Thompson", "Manager", "2021-06-01", "active"),
    ("Mike", "Rivera", "Shift Lead", "2021-09-10", "active"),
    ("Jennifer", "Park", "Shift Lead", "2022-01-15", "active"),
    ("David", "Nguyen", "Shift Lead", "2022-07-20", "active"),
    ("Marcus", "Williams", "Washer", "2022-04-01", "active"),
    ("Tyler", "Johnson", "Washer", "2022-08-15", "active"),
    ("Ramon", "Garcia", "Washer", "2023-01-10", "active"),
    ("Brandon", "Lee", "Washer", "2023-03-20", "active"),
    ("Alexis", "Martinez", "Washer", "2023-06-15", "active"),
    ("Kevin", "Brown", "Washer", "2023-09-01", "active"),
    ("Jake", "Wilson", "Washer", "2024-02-01", "active"),
    ("Tony", "Cruz", "Detailer", "2021-11-01", "active"),
    ("Lisa", "Chen", "Detailer", "2022-05-10", "active"),
    ("Robert", "Kim", "Detailer", "2023-02-15", "active"),
    ("Angela", "Davis", "Detailer", "2023-08-20", "active"),
    ("Jessica", "Moore", "Cashier", "2022-03-01", "active"),
    ("Amanda", "Taylor", "Cashier", "2023-04-15", "active"),
    ("Emily", "White", "Cashier", "2023-11-01", "active"),
    ("Frank", "Santos", "Maintenance Tech", "2020-06-15", "active"),
    ("Greg", "Patel", "Maintenance Tech", "2022-09-01", "active"),
    ("Chris", "Anderson", "Attendant", "2023-05-01", "active"),
    ("Daniel", "Lopez", "Attendant", "2023-07-15", "active"),
    ("Ryan", "Harris", "Attendant", "2024-01-10", "active"),
    ("Justin", "Clark", "Attendant", "2024-03-01", "active"),
]


def seed_workforce(conn):
    """Seed roles, employees, shifts, timecards, and employee_performance."""

    # --- Roles ---
    conn.executemany(
        "INSERT INTO roles (name, hourly_rate, description) VALUES (?, ?, ?)",
        ROLES,
    )
    conn.commit()

    role_map = {r[1]: r[0] for r in conn.execute("SELECT id, name FROM roles").fetchall()}

    # --- Employees ---
    emp_rows = []
    for first, last, role_name, hire_date, status in EMPLOYEES:
        role_id = role_map[role_name]
        email = f"{first.lower()}.{last.lower()}@sparklecarwash.com"
        area = random.choice(["480", "602", "623"])
        phone = f"({area}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        emp_rows.append((first, last, email, phone, role_id, hire_date, status))

    conn.executemany(
        """INSERT INTO employees
           (first_name, last_name, email, phone, role_id, hire_date, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        emp_rows,
    )
    conn.commit()

    # --- Shifts ---
    conn.executemany(
        "INSERT INTO shifts (name, start_time, end_time) VALUES (?, ?, ?)",
        SHIFTS,
    )
    conn.commit()

    shift_map = {r[1]: r[0] for r in conn.execute("SELECT id, name FROM shifts").fetchall()}
    shift_ids = list(shift_map.values())
    weekend_shift_id = shift_map["Weekend"]
    weekday_shifts = [shift_map[s] for s in ["Morning", "Midday", "Afternoon"]]

    employee_ids = [r[0] for r in conn.execute("SELECT id FROM employees").fetchall()]
    emp_hire_dates = {
        r[0]: date.fromisoformat(r[1])
        for r in conn.execute("SELECT id, hire_date FROM employees").fetchall()
    }

    # --- Timecards (~6500) ---
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    timecard_rows = []

    current = start_date
    while current <= end_date:
        is_weekend = current.weekday() >= 5

        for emp_id in employee_ids:
            # Skip if not yet hired
            if emp_hire_dates[emp_id] > current:
                continue

            # ~85% chance of working on any given day
            if random.random() > 0.85:
                continue

            if is_weekend:
                shift_id = weekend_shift_id
            else:
                shift_id = random.choice(weekday_shifts)

            # Get shift times
            shift_info = conn.execute(
                "SELECT start_time, end_time FROM shifts WHERE id = ?", (shift_id,)
            ).fetchone()
            s_hour, s_min = map(int, shift_info[0].split(":"))
            e_hour, e_min = map(int, shift_info[1].split(":"))

            # Add some clock-in variance (-10 to +5 minutes)
            clock_in_dt = datetime(current.year, current.month, current.day, s_hour, s_min)
            clock_in_dt += timedelta(minutes=random.randint(-10, 5))
            # Clock-out variance (-5 to +30 minutes for overtime)
            clock_out_dt = datetime(current.year, current.month, current.day, e_hour, e_min)
            clock_out_dt += timedelta(minutes=random.randint(-5, 30))

            hours_worked = round((clock_out_dt - clock_in_dt).total_seconds() / 3600, 2)
            overtime = max(0, round(hours_worked - 8, 2))

            timecard_rows.append((
                emp_id, shift_id, current.isoformat(),
                clock_in_dt.strftime("%Y-%m-%d %H:%M:%S"),
                clock_out_dt.strftime("%Y-%m-%d %H:%M:%S"),
                hours_worked, overtime,
            ))

        current += timedelta(days=1)

    conn.executemany(
        """INSERT INTO timecards
           (employee_id, shift_id, work_date, clock_in, clock_out, hours_worked, overtime_hours)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        timecard_rows,
    )
    conn.commit()

    # --- Employee Performance (monthly) ---
    perf_rows = []
    for emp_id in employee_ids:
        hire = emp_hire_dates[emp_id]
        for month in range(1, 13):
            month_date = date(2024, month, 1)
            if hire > month_date:
                continue

            cars = random.randint(80, 300)
            quality = round(random.uniform(6.0, 10.0), 1)
            attendance = round(random.uniform(0.80, 1.00), 2)
            cust_rating = round(random.uniform(3.5, 5.0), 1)

            perf_rows.append((
                emp_id, month_date.isoformat(),
                cars, quality, attendance, cust_rating,
            ))

    conn.executemany(
        """INSERT INTO employee_performance
           (employee_id, month, cars_processed, quality_score, attendance_rate, customer_rating)
           VALUES (?, ?, ?, ?, ?, ?)""",
        perf_rows,
    )
    conn.commit()

    print(f"  Inserted {len(ROLES)} roles")
    print(f"  Inserted {len(EMPLOYEES)} employees")
    print(f"  Inserted {len(SHIFTS)} shifts")
    print(f"  Inserted {len(timecard_rows)} timecards")
    print(f"  Inserted {len(perf_rows)} employee performance records")
