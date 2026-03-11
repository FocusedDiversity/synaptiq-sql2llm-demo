"""Generate membership_plans (4), member_subscriptions (~120), membership_billing."""

import random
from datetime import date, timedelta


MEMBERSHIP_PLANS = [
    ("Bronze", 30.00, 1, 4, "Basic wash package, up to 4 washes per month"),
    ("Silver", 50.00, 2, 8, "Standard wash package, up to 8 washes per month"),
    ("Gold", 75.00, 3, None, "Premium wash package, unlimited washes per month"),
    ("Platinum", 120.00, 4, None, "Ultimate wash package, unlimited washes plus free detailing discount"),
]

# wash_package_id: 1=Express, 2=Basic, 3=Standard, 4=Premium, 5=Ultimate
# Plan maps: Bronze->Basic(2), Silver->Standard(3), Gold->Premium(4), Platinum->Ultimate(5)
PLAN_WASH_PKG_IDS = [2, 3, 4, 5]

NUM_SUBSCRIPTIONS = 120

CANCELLATION_REASONS = [
    "Moving out of area",
    "Financial reasons",
    "Switched to competitor",
    "Not using enough to justify cost",
    "Poor service experience",
    "Seasonal - will resubscribe",
    "Vehicle sold",
]

PAYMENT_METHODS = ["credit_card", "debit_card", "bank_account"]


def seed_memberships(conn):
    """Seed membership_plans, member_subscriptions, and membership_billing."""

    # Fetch wash package IDs to link plans
    wash_pkg_ids = [r[0] for r in conn.execute(
        "SELECT id FROM wash_packages ORDER BY id"
    ).fetchall()]

    # --- Membership Plans ---
    plan_rows = []
    for i, (name, price, pkg_idx, max_washes, desc) in enumerate(MEMBERSHIP_PLANS):
        # Map to actual wash_package_id
        wpkg_id = wash_pkg_ids[PLAN_WASH_PKG_IDS[i] - 1] if PLAN_WASH_PKG_IDS[i] - 1 < len(wash_pkg_ids) else wash_pkg_ids[-1]
        plan_rows.append((name, price, wpkg_id, max_washes, desc))

    conn.executemany(
        """INSERT INTO membership_plans
           (name, monthly_price, wash_package_id, max_washes_per_month, description)
           VALUES (?, ?, ?, ?, ?)""",
        plan_rows,
    )
    conn.commit()

    plan_data = conn.execute(
        "SELECT id, name, monthly_price FROM membership_plans ORDER BY id"
    ).fetchall()
    plan_ids = [r[0] for r in plan_data]
    plan_prices = {r[0]: r[2] for r in plan_data}
    plan_weights = [35, 30, 25, 10]  # Bronze most popular

    customer_ids = [r[0] for r in conn.execute("SELECT id FROM customers").fetchall()]

    # ~24% of customers get memberships - pick unique customers
    member_customers = random.sample(customer_ids, min(NUM_SUBSCRIPTIONS, len(customer_ids)))

    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)

    # --- Member Subscriptions ---
    sub_rows = []
    for cust_id in member_customers:
        plan_id = random.choices(plan_ids, weights=plan_weights, k=1)[0]

        # Start date spread across the year, weighted toward earlier months
        month_start = random.choices(range(1, 13), weights=[15, 12, 10, 9, 8, 8, 7, 7, 7, 6, 6, 5], k=1)[0]
        sub_start = date(2024, month_start, random.randint(1, 28))

        # ~20% cancel at some point
        if random.random() < 0.20:
            months_active = random.randint(1, 12 - month_start + 1)
            sub_end = sub_start + timedelta(days=months_active * 30)
            if sub_end > end_date:
                sub_end = end_date
            status = "cancelled"
            cancel_reason = random.choice(CANCELLATION_REASONS)
        else:
            sub_end = None
            status = "active"
            cancel_reason = None

        sub_rows.append((
            cust_id, plan_id, sub_start.isoformat(),
            sub_end.isoformat() if sub_end else None,
            status, cancel_reason,
        ))

    conn.executemany(
        """INSERT INTO member_subscriptions
           (customer_id, plan_id, start_date, end_date, status, cancellation_reason)
           VALUES (?, ?, ?, ?, ?, ?)""",
        sub_rows,
    )
    conn.commit()

    # --- Membership Billing (monthly for each subscription) ---
    sub_data = conn.execute(
        "SELECT id, plan_id, start_date, end_date, status FROM member_subscriptions ORDER BY id"
    ).fetchall()

    billing_rows = []
    for sub_id, plan_id, start_str, end_str, status in sub_data:
        monthly_price = plan_prices[plan_id]
        sub_start = date.fromisoformat(start_str)
        sub_end = date.fromisoformat(end_str) if end_str else end_date

        # Generate a billing record for each month the subscription was active
        billing_date = date(sub_start.year, sub_start.month, 1)
        while billing_date <= sub_end and billing_date <= end_date:
            pay_method = random.choice(PAYMENT_METHODS)

            # ~95% paid, 3% past_due, 2% failed
            bill_status = random.choices(
                ["paid", "past_due", "failed"],
                weights=[95, 3, 2],
                k=1,
            )[0]

            billing_rows.append((
                sub_id, billing_date.isoformat(),
                monthly_price, bill_status, pay_method,
            ))

            # Advance to next month
            if billing_date.month == 12:
                billing_date = date(billing_date.year + 1, 1, 1)
            else:
                billing_date = date(billing_date.year, billing_date.month + 1, 1)

    conn.executemany(
        """INSERT INTO membership_billing
           (subscription_id, billing_date, amount, status, payment_method)
           VALUES (?, ?, ?, ?, ?)""",
        billing_rows,
    )
    conn.commit()

    print(f"  Inserted {len(MEMBERSHIP_PLANS)} membership plans")
    print(f"  Inserted {len(sub_rows)} member subscriptions")
    print(f"  Inserted {len(billing_rows)} membership billing records")
