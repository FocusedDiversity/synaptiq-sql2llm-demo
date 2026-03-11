"""Generate customer_feedback (~2500), complaints (~200), loyalty_programs, loyalty_transactions (~3000)."""

import random
from datetime import date, timedelta


FEEDBACK_COMMENTS_BY_RATING = {
    5: [
        "Excellent service! My car looks brand new.",
        "Best car wash in town. Will definitely come back.",
        "Fast, friendly, and thorough. Love it!",
        "Amazing results every time. Highly recommend.",
        "Staff was incredibly helpful and professional.",
        "Spotless finish. Worth every penny.",
    ],
    4: [
        "Good wash overall, very satisfied.",
        "Nice job, just a small spot missed on the trunk.",
        "Friendly staff and quick service.",
        "Car looks great, good value for the price.",
        "Solid experience, will return.",
    ],
    3: [
        "Average wash. Nothing special but got the job done.",
        "Decent service but waited longer than expected.",
        "Wash was okay, some water spots left.",
        "Fair price for a fair wash.",
        "It was fine. Not bad, not great.",
    ],
    2: [
        "Disappointed. Streaks left on the windows.",
        "Long wait time and mediocre results.",
        "Car still had dirt on the lower panels.",
        "Expected better for the price paid.",
        "Service was slow and staff seemed uninterested.",
    ],
    1: [
        "Terrible experience. Scratches on my car!",
        "Would not recommend. Very unprofessional.",
        "Worst car wash ever. Waste of money.",
        "Car came out dirtier than when it went in.",
        "Rude staff and poor quality wash.",
    ],
}

COMPLAINT_CATEGORIES = [
    "wash_quality", "customer_service", "wait_time",
    "damage", "billing", "facility", "equipment",
]

COMPLAINT_DESCRIPTIONS = {
    "wash_quality": [
        "Streaks and water spots remained after Premium wash",
        "Wax coating was uneven and patchy",
        "Missed cleaning the wheel wells entirely",
        "Interior wipe-down was incomplete",
        "Bug residue still on windshield after wash",
    ],
    "customer_service": [
        "Staff was rude and dismissive of my concerns",
        "No one greeted me or explained the packages",
        "Employee argued about my membership benefits",
        "Waited at counter with no staff available",
    ],
    "wait_time": [
        "Waited 45 minutes for a 15-minute wash",
        "No communication about the delay",
        "Appointment time was not honored",
        "Drive-through line was extremely long with no management",
    ],
    "damage": [
        "Scratch found on driver-side door after wash",
        "Side mirror was damaged during tunnel wash",
        "Antenna was bent after going through the wash",
        "Paint chip on front bumper after visit",
    ],
    "billing": [
        "Charged twice for the same wash",
        "Membership discount was not applied",
        "Incorrect package price on receipt",
        "Refund not processed after 2 weeks",
    ],
    "facility": [
        "Vacuum station was broken and dirty",
        "Restroom was out of order",
        "Parking lot was flooded and hard to navigate",
        "Waiting area was filthy",
    ],
    "equipment": [
        "Dryer was not working properly, car left wet",
        "Brush marks on the car from malfunctioning equipment",
        "Water pressure was too low for a proper clean",
        "Chemical smell was overwhelming due to dispenser malfunction",
    ],
}

LOYALTY_PROGRAMS = [
    ("Sparkle Rewards", 10.0, 0.01, "active"),
    ("VIP Points Club", 15.0, 0.008, "active"),
    ("Wash & Save", 12.0, 0.012, "inactive"),
]

NUM_FEEDBACK = 2500
NUM_COMPLAINTS = 200
NUM_LOYALTY_TRANSACTIONS = 3000


def seed_customer_experience(conn):
    """Seed customer_feedback, complaints, loyalty_programs, loyalty_transactions."""

    customer_ids = [r[0] for r in conn.execute("SELECT id FROM customers").fetchall()]
    checkin_rows = conn.execute(
        "SELECT id, customer_id, check_in_time FROM check_ins"
    ).fetchall()

    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    date_range = (end_date - start_date).days

    # --- Customer Feedback ---
    feedback_rows = []
    # Sample check-ins for feedback (not every visit gets feedback)
    feedback_checkins = random.sample(
        checkin_rows, min(NUM_FEEDBACK, len(checkin_rows))
    )

    for ci_id, cust_id, ci_time in feedback_checkins:
        # Rating distribution: skewed toward 4-5
        rating = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 12, 35, 45], k=1)[0]
        # NPS correlates loosely with rating
        nps_base = {1: 1, 2: 3, 3: 5, 4: 7, 5: 9}
        nps_score = min(10, max(0, nps_base[rating] + random.randint(-1, 1)))

        comment = None
        if random.random() < 0.4:
            comment = random.choice(FEEDBACK_COMMENTS_BY_RATING[rating])

        feedback_date = ci_time[:10]  # same day as check-in

        feedback_rows.append((
            cust_id, ci_id, rating, nps_score, comment, feedback_date,
        ))

    conn.executemany(
        """INSERT INTO customer_feedback
           (customer_id, check_in_id, rating, nps_score, comment, feedback_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        feedback_rows,
    )
    conn.commit()

    # --- Complaints ---
    complaint_rows = []
    # Pick check-ins with low ratings for complaints, plus some random
    low_rated_checkins = [
        (ci_id, cust_id, ci_time)
        for ci_id, cust_id, ci_time in checkin_rows
    ]
    complaint_checkins = random.sample(
        low_rated_checkins, min(NUM_COMPLAINTS, len(low_rated_checkins))
    )

    for ci_id, cust_id, ci_time in complaint_checkins:
        category = random.choice(COMPLAINT_CATEGORIES)
        severity = random.choices(
            ["low", "medium", "high", "critical"],
            weights=[25, 40, 25, 10],
            k=1,
        )[0]
        description = random.choice(COMPLAINT_DESCRIPTIONS[category])
        created_date = ci_time[:10]

        # 75% of complaints are resolved
        if random.random() < 0.75:
            status = "resolved"
            resolution_options = [
                "Full refund provided",
                "Free wash coupon issued",
                "Re-wash performed to customer satisfaction",
                "Manager spoke with customer and resolved concern",
                "Billing adjustment made",
                "Repair cost reimbursed",
                "Gift card provided as compensation",
            ]
            resolution = random.choice(resolution_options)
            resolved_date = (
                date.fromisoformat(created_date) + timedelta(days=random.randint(1, 14))
            ).isoformat()
        else:
            status = random.choice(["open", "in_progress"])
            resolution = None
            resolved_date = None

        complaint_rows.append((
            cust_id, ci_id, category, severity, description,
            status, resolution, created_date, resolved_date,
        ))

    conn.executemany(
        """INSERT INTO complaints
           (customer_id, check_in_id, category, severity, description,
            status, resolution, created_date, resolved_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        complaint_rows,
    )
    conn.commit()

    # --- Loyalty Programs ---
    conn.executemany(
        """INSERT INTO loyalty_programs
           (name, points_per_dollar, redemption_rate, status)
           VALUES (?, ?, ?, ?)""",
        LOYALTY_PROGRAMS,
    )
    conn.commit()

    program_ids = [r[0] for r in conn.execute(
        "SELECT id FROM loyalty_programs WHERE status = 'active'"
    ).fetchall()]

    # --- Loyalty Transactions ---
    loyalty_rows = []
    for _ in range(NUM_LOYALTY_TRANSACTIONS):
        cust_id = random.choice(customer_ids)
        program_id = random.choice(program_ids)
        trans_date = start_date + timedelta(days=random.randint(0, date_range))

        if random.random() < 0.75:
            # Earn points
            trans_type = "earn"
            points = random.randint(10, 150)
            desc = f"Points earned from wash purchase"
        else:
            # Redeem points
            trans_type = "redeem"
            points = -random.randint(50, 500)
            desc = f"Points redeemed for discount"

        loyalty_rows.append((
            cust_id, program_id, trans_type, points,
            trans_date.isoformat(), desc,
        ))

    conn.executemany(
        """INSERT INTO loyalty_transactions
           (customer_id, program_id, transaction_type, points, transaction_date, description)
           VALUES (?, ?, ?, ?, ?, ?)""",
        loyalty_rows,
    )
    conn.commit()

    print(f"  Inserted {len(feedback_rows)} customer feedback records")
    print(f"  Inserted {len(complaint_rows)} complaints")
    print(f"  Inserted {len(LOYALTY_PROGRAMS)} loyalty programs")
    print(f"  Inserted {len(loyalty_rows)} loyalty transactions")
