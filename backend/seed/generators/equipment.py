"""Generate equipment (20 items), maintenance_logs, and equipment_downtime."""

import random
from datetime import date, datetime, timedelta


EQUIPMENT_LIST = [
    ("Main Tunnel Washer", "tunnel", "WashTec", "SoftCare Pro", "WT-2019-001", "2019-03-15", 1),
    ("Secondary Tunnel Washer", "tunnel", "WashTec", "SoftCare Pro", "WT-2020-002", "2020-06-10", 2),
    ("High-Pressure Washer Bay 1", "pressure_washer", "Karcher", "HD 7/20-4 M", "KR-2021-003", "2021-01-20", 1),
    ("High-Pressure Washer Bay 2", "pressure_washer", "Karcher", "HD 7/20-4 M", "KR-2021-004", "2021-01-20", 2),
    ("High-Pressure Washer Bay 3", "pressure_washer", "Karcher", "HD 10/25-4 S", "KR-2022-005", "2022-05-12", 3),
    ("Vacuum Station 1", "vacuum", "Vacutech", "Pro-Vac 450", "VT-2020-006", "2020-08-01", None),
    ("Vacuum Station 2", "vacuum", "Vacutech", "Pro-Vac 450", "VT-2020-007", "2020-08-01", None),
    ("Vacuum Station 3", "vacuum", "Vacutech", "Pro-Vac 550", "VT-2022-008", "2022-03-15", None),
    ("Vacuum Station 4", "vacuum", "Vacutech", "Pro-Vac 550", "VT-2022-009", "2022-03-15", None),
    ("Main Blower Dryer", "dryer", "AirBlast", "Hurricane 3000", "AB-2019-010", "2019-03-15", 1),
    ("Secondary Blower Dryer", "dryer", "AirBlast", "Hurricane 3000", "AB-2020-011", "2020-06-10", 2),
    ("Spot-Free Dryer", "dryer", "AirBlast", "Precision Dry", "AB-2021-012", "2021-09-20", 3),
    ("Entry Conveyor", "conveyor", "Belanger", "FreeStyle 2800", "BL-2019-013", "2019-03-15", 1),
    ("Exit Conveyor", "conveyor", "Belanger", "FreeStyle 2800", "BL-2019-014", "2019-03-15", 1),
    ("Chemical Pump Station A", "pump", "ChemProbe", "IntelliChem 200", "CP-2020-015", "2020-04-10", None),
    ("Chemical Pump Station B", "pump", "ChemProbe", "IntelliChem 200", "CP-2020-016", "2020-04-10", None),
    ("Water Reclaim System", "pump", "WaterGen", "Reclaim Pro 500", "WG-2019-017", "2019-03-15", None),
    ("RO Water System", "pump", "PureLine", "RO-4000", "PL-2021-018", "2021-07-05", None),
    ("Tire Shine Applicator", "applicator", "NeoGlide", "TireMax 100", "NG-2022-019", "2022-02-28", 1),
    ("Foam Arch", "applicator", "WashTec", "FoamMaster 500", "WT-2021-020", "2021-11-15", 2),
]

MAINTENANCE_TYPES = [
    "preventive",
    "corrective",
    "inspection",
    "calibration",
    "replacement",
]

DOWNTIME_REASONS = [
    "Mechanical failure",
    "Electrical fault",
    "Sensor malfunction",
    "Belt replacement",
    "Pump failure",
    "Nozzle blockage",
    "Motor overheating",
    "Control system error",
    "Water pressure loss",
    "Chemical feed issue",
]


def seed_equipment(conn):
    """Seed 20 equipment items, maintenance_logs, and equipment_downtime."""

    # --- Equipment ---
    eq_rows = []
    for name, eq_type, manufacturer, model, serial, install_date, bay in EQUIPMENT_LIST:
        status = "operational"
        if random.random() < 0.05:
            status = random.choice(["maintenance", "offline"])
        eq_rows.append((name, eq_type, manufacturer, model, serial, install_date, status, bay))

    conn.executemany(
        """INSERT INTO equipment
           (name, type, manufacturer, model, serial_number, install_date, status, bay_number)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        eq_rows,
    )
    conn.commit()

    equipment_ids = [r[0] for r in conn.execute("SELECT id FROM equipment").fetchall()]
    maint_tech_ids = [r[0] for r in conn.execute(
        "SELECT e.id FROM employees e JOIN roles r ON e.role_id = r.id "
        "WHERE r.name = 'Maintenance Tech'"
    ).fetchall()]
    if not maint_tech_ids:
        maint_tech_ids = [r[0] for r in conn.execute("SELECT id FROM employees").fetchall()]

    # --- Maintenance Logs ---
    # Each piece of equipment gets 4-12 maintenance records across 2024
    maint_rows = []
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    date_range = (end_date - start_date).days

    for eq_id in equipment_ids:
        num_records = random.randint(4, 12)
        for _ in range(num_records):
            mtype = random.choices(
                MAINTENANCE_TYPES,
                weights=[40, 20, 20, 10, 10],
                k=1,
            )[0]

            performed_date = start_date + timedelta(days=random.randint(0, date_range))
            tech_id = random.choice(maint_tech_ids)

            descriptions = {
                "preventive": [
                    "Routine lubrication and inspection",
                    "Filter replacement and cleaning",
                    "Belt tension check and adjustment",
                    "Fluid level check and top-off",
                ],
                "corrective": [
                    "Replaced worn bearing",
                    "Fixed water leak at connection",
                    "Repaired electrical connection",
                    "Replaced damaged nozzle",
                ],
                "inspection": [
                    "Monthly safety inspection",
                    "Quarterly performance review",
                    "Annual compliance inspection",
                ],
                "calibration": [
                    "Chemical dispenser calibration",
                    "Pressure sensor calibration",
                    "Flow meter calibration",
                ],
                "replacement": [
                    "Replaced main drive motor",
                    "New brush set installed",
                    "Conveyor chain replacement",
                    "Replaced control board",
                ],
            }
            description = random.choice(descriptions[mtype])

            cost_ranges = {
                "preventive": (25, 150),
                "corrective": (50, 500),
                "inspection": (0, 50),
                "calibration": (30, 200),
                "replacement": (200, 2000),
            }
            cost_min, cost_max = cost_ranges[mtype]
            cost = round(random.uniform(cost_min, cost_max), 2)

            next_due = performed_date + timedelta(days=random.choice([30, 60, 90, 180, 365]))
            next_due_str = next_due.isoformat() if next_due <= date(2025, 12, 31) else None

            maint_rows.append((
                eq_id, mtype, description, tech_id,
                performed_date.isoformat(), cost, next_due_str,
            ))

    conn.executemany(
        """INSERT INTO maintenance_logs
           (equipment_id, maintenance_type, description, performed_by,
            performed_date, cost, next_due_date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        maint_rows,
    )
    conn.commit()

    # --- Equipment Downtime ---
    # ~2-6 downtime events per equipment over the year
    downtime_rows = []
    for eq_id in equipment_ids:
        num_events = random.randint(2, 6)
        for _ in range(num_events):
            start_day = start_date + timedelta(days=random.randint(0, date_range))
            start_hour = random.randint(7, 18)
            start_min = random.randint(0, 59)
            dt_start = f"{start_day.isoformat()} {start_hour:02d}:{start_min:02d}:00"

            # Downtime duration: 30 minutes to 48 hours
            duration_minutes = random.choices(
                [30, 60, 120, 240, 480, 1440, 2880],
                weights=[20, 25, 20, 15, 10, 7, 3],
                k=1,
            )[0]
            end_dt = datetime(start_day.year, start_day.month, start_day.day,
                              start_hour, start_min) + timedelta(minutes=duration_minutes)
            dt_end = end_dt.strftime("%Y-%m-%d %H:%M:%S")

            reason = random.choice(DOWNTIME_REASONS)
            impact = random.choices(
                ["low", "medium", "high", "critical"],
                weights=[30, 40, 20, 10],
                k=1,
            )[0]

            resolutions = [
                "Part replaced and tested",
                "System reset and calibrated",
                "Temporary fix applied, permanent repair scheduled",
                "Cleaned and restored to operation",
                "Vendor technician resolved issue",
                "Replaced faulty component",
            ]
            resolution = random.choice(resolutions)

            downtime_rows.append((eq_id, dt_start, dt_end, reason, impact, resolution))

    conn.executemany(
        """INSERT INTO equipment_downtime
           (equipment_id, start_time, end_time, reason, impact_level, resolution)
           VALUES (?, ?, ?, ?, ?, ?)""",
        downtime_rows,
    )
    conn.commit()

    print(f"  Inserted {len(eq_rows)} equipment items")
    print(f"  Inserted {len(maint_rows)} maintenance logs")
    print(f"  Inserted {len(downtime_rows)} equipment downtime records")
