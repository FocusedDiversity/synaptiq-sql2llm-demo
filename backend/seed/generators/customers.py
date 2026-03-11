"""Generate 500 customers with realistic names, emails, phones, and addresses."""

import random
from datetime import date, timedelta

from backend.seed.data.names import (
    FIRST_NAMES, LAST_NAMES, CITIES, STREETS, EMAIL_DOMAINS,
)

NUM_CUSTOMERS = 500

ACQUISITION_SOURCES = ["walk-in", "referral", "online", "social_media", "campaign"]
ACQUISITION_WEIGHTS = [30, 20, 25, 15, 10]


def _generate_phone():
    area = random.choice(["480", "602", "623", "520", "928"])
    return f"({area}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def _generate_email(first_name, last_name, used_emails):
    """Generate a unique email address."""
    base = f"{first_name.lower()}.{last_name.lower()}"
    domain = random.choice(EMAIL_DOMAINS)
    email = f"{base}@{domain}"
    suffix = 1
    while email in used_emails:
        email = f"{base}{suffix}@{domain}"
        suffix += 1
    used_emails.add(email)
    return email


def seed_customers(conn):
    """Insert 500 customers into the customers table."""
    used_emails = set()
    rows = []

    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    date_range = (end_date - start_date).days

    for _ in range(NUM_CUSTOMERS):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = _generate_email(first_name, last_name, used_emails)
        phone = _generate_phone()

        street_num = random.randint(100, 9999)
        street = random.choice(STREETS)
        address = f"{street_num} {street}"

        city, state, zip_code = random.choice(CITIES)

        source = random.choices(ACQUISITION_SOURCES, weights=ACQUISITION_WEIGHTS, k=1)[0]

        # Spread customer_since across all of 2024
        days_offset = random.randint(0, date_range)
        customer_since = start_date + timedelta(days=days_offset)

        rows.append((
            first_name, last_name, email, phone,
            address, city, state, zip_code,
            source, customer_since.isoformat(),
        ))

    conn.executemany(
        """INSERT INTO customers
           (first_name, last_name, email, phone, address, city, state, zip_code,
            acquisition_source, customer_since)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    print(f"  Inserted {NUM_CUSTOMERS} customers")
