"""Generate water_usage (365 daily), chemical_disposal, permits (8), regulatory_inspections (12)."""

import random
import math
from datetime import date, timedelta


PERMITS = [
    ("Water Discharge", "WD-2024-0451", "Arizona Dept of Environmental Quality", "2023-06-15", "2025-06-14"),
    ("Air Quality", "AQ-2024-1123", "Maricopa County Air Quality", "2024-01-10", "2025-01-09"),
    ("Business License", "BL-2024-7890", "City of Phoenix", "2024-01-01", "2024-12-31"),
    ("Hazardous Materials", "HM-2023-3344", "Arizona Dept of Environmental Quality", "2023-09-01", "2025-08-31"),
    ("Stormwater Permit", "SW-2024-0567", "EPA Region 9", "2024-03-01", "2029-02-28"),
    ("Fire Safety", "FS-2024-2211", "Phoenix Fire Department", "2024-02-15", "2025-02-14"),
    ("Health Permit", "HP-2024-8877", "Maricopa County Health", "2024-04-01", "2025-03-31"),
    ("Signage Permit", "SP-2023-5566", "City of Phoenix Planning", "2023-11-01", "2025-10-31"),
]

INSPECTION_TYPES = [
    "Water quality",
    "Air emissions",
    "Chemical storage",
    "Fire safety",
    "Health and sanitation",
    "Stormwater management",
    "Waste disposal",
    "General compliance",
]

INSPECTOR_NAMES = [
    "Robert Chen", "Maria Gonzalez", "James Wilson", "Patricia Adams",
    "David Kim", "Susan Miller", "Thomas Brown", "Linda Jackson",
]

DISPOSAL_METHODS = [
    "Licensed waste hauler pickup",
    "On-site neutralization",
    "Recycling through certified facility",
    "Hazardous waste collection event",
]


def seed_compliance(conn):
    """Seed water_usage, chemical_disposal, permits, regulatory_inspections."""

    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)

    # --- Water Usage (365 daily records) ---
    water_rows = []
    current = start_date
    while current <= end_date:
        day_of_year = current.timetuple().tm_yday
        day_of_week = current.weekday()

        # Seasonal pattern: more water in summer, less in winter
        base_gallons = 800 + 400 * math.sin(2 * math.pi * (day_of_year - 91) / 365)
        # Weekend bump
        if day_of_week >= 5:
            base_gallons *= 1.25

        # Add daily noise
        total = round(base_gallons * random.uniform(0.85, 1.15), 1)
        reclaim_rate = round(random.uniform(0.55, 0.75), 2)
        recycled = round(total * reclaim_rate, 1)
        fresh = round(total - recycled, 1)

        water_rows.append((
            current.isoformat(), fresh, recycled, total, reclaim_rate,
        ))
        current += timedelta(days=1)

    conn.executemany(
        """INSERT INTO water_usage
           (usage_date, fresh_gallons, recycled_gallons, total_gallons, reclaim_rate)
           VALUES (?, ?, ?, ?, ?)""",
        water_rows,
    )
    conn.commit()

    # --- Chemical Disposal ---
    chem_rows = conn.execute("SELECT id, name FROM chemicals").fetchall()
    employee_ids = [r[0] for r in conn.execute("SELECT id FROM employees").fetchall()]

    disposal_rows = []
    date_range = (end_date - start_date).days

    # ~3-6 disposals per chemical per year for some chemicals
    disposal_chems = random.sample(chem_rows, min(8, len(chem_rows)))
    for chem_id, chem_name in disposal_chems:
        num_disposals = random.randint(2, 6)
        for _ in range(num_disposals):
            disp_date = start_date + timedelta(days=random.randint(0, date_range))
            amount = round(random.uniform(1.0, 15.0), 1)
            method = random.choice(DISPOSAL_METHODS)
            manifest = f"MAN-{random.randint(10000, 99999)}"
            handler = random.choice(employee_ids)

            disposal_rows.append((
                chem_id, disp_date.isoformat(), amount,
                method, manifest, handler,
            ))

    conn.executemany(
        """INSERT INTO chemical_disposal
           (chemical_id, disposal_date, amount, disposal_method, manifest_number, handled_by)
           VALUES (?, ?, ?, ?, ?, ?)""",
        disposal_rows,
    )
    conn.commit()

    # --- Permits ---
    permit_rows = []
    for ptype, pnum, authority, issue, expiry in PERMITS:
        status = "active"
        if date.fromisoformat(expiry) < date(2024, 12, 31):
            status = "expired" if random.random() < 0.3 else "active"  # some renewed
        permit_rows.append((ptype, pnum, authority, issue, expiry, status))

    conn.executemany(
        """INSERT INTO permits
           (permit_type, permit_number, issuing_authority, issue_date, expiry_date, status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        permit_rows,
    )
    conn.commit()

    # --- Regulatory Inspections (12) ---
    inspection_rows = []
    for month in range(1, 13):
        insp_type = INSPECTION_TYPES[month % len(INSPECTION_TYPES)]
        inspector = random.choice(INSPECTOR_NAMES)
        insp_date = date(2024, month, random.randint(5, 25))

        result = random.choices(
            ["pass", "pass_with_conditions", "fail"],
            weights=[70, 25, 5],
            k=1,
        )[0]
        score = round(random.uniform(75, 100) if result != "fail" else random.uniform(50, 74), 1)

        findings = None
        corrective = None
        follow_up = None

        if result == "pass_with_conditions":
            findings_options = [
                "Minor chemical labeling deficiency noted",
                "Secondary containment needs repair in storage area",
                "Eye wash station needs monthly testing documentation",
                "Spill kit inventory slightly below requirement",
                "Record-keeping gaps in waste manifest log",
            ]
            corrective_options = [
                "Update labels within 30 days",
                "Repair containment berm by next inspection",
                "Implement monthly testing checklist",
                "Restock spill kit materials",
                "Complete missing entries in log",
            ]
            findings = random.choice(findings_options)
            corrective = random.choice(corrective_options)
            follow_up = (insp_date + timedelta(days=random.choice([30, 60, 90]))).isoformat()
        elif result == "fail":
            findings = "Significant non-compliance with discharge limits"
            corrective = "Submit corrective action plan within 15 days"
            follow_up = (insp_date + timedelta(days=15)).isoformat()

        inspection_rows.append((
            insp_type, inspector, insp_date.isoformat(), result,
            score, findings, corrective, follow_up,
        ))

    conn.executemany(
        """INSERT INTO regulatory_inspections
           (inspection_type, inspector_name, inspection_date, result,
            score, findings, corrective_actions, follow_up_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        inspection_rows,
    )
    conn.commit()

    print(f"  Inserted {len(water_rows)} water usage records")
    print(f"  Inserted {len(disposal_rows)} chemical disposal records")
    print(f"  Inserted {len(permit_rows)} permits")
    print(f"  Inserted {len(inspection_rows)} regulatory inspections")
