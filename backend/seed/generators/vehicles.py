"""Generate ~650 vehicles linked to existing customers."""

import random
import string

from backend.seed.data.vehicles import (
    VEHICLE_MODELS, MODEL_TYPES, COLORS, COLOR_WEIGHTS, MAKE_WEIGHTS,
)

NUM_VEHICLES = 650


def _generate_plate():
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    digits = "".join(random.choices(string.digits, k=4))
    return f"{letters}-{digits}"


def seed_vehicles(conn):
    """Insert ~650 vehicles referencing existing customer IDs."""
    customer_ids = [r[0] for r in conn.execute("SELECT id FROM customers").fetchall()]

    makes = list(VEHICLE_MODELS.keys())
    make_wts = [MAKE_WEIGHTS[m] for m in makes]

    used_plates = set()
    rows = []

    for _ in range(NUM_VEHICLES):
        customer_id = random.choice(customer_ids)
        make = random.choices(makes, weights=make_wts, k=1)[0]
        model = random.choice(VEHICLE_MODELS[make])
        year = random.randint(2010, 2024)
        color = random.choices(COLORS, weights=COLOR_WEIGHTS, k=1)[0]
        vehicle_type = MODEL_TYPES.get(model, "sedan")

        plate = _generate_plate()
        while plate in used_plates:
            plate = _generate_plate()
        used_plates.add(plate)

        rows.append((customer_id, make, model, year, color, vehicle_type, plate))

    conn.executemany(
        """INSERT INTO vehicles
           (customer_id, make, model, year, color, vehicle_type, license_plate)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    conn.commit()
    print(f"  Inserted {NUM_VEHICLES} vehicles")
