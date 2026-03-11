"""Generate chemicals (15), chemical_usage_logs, purchase_orders (~50), purchase_order_items."""

import random
from datetime import date, timedelta


CHEMICALS = [
    ("All-Purpose Car Soap", "soap", "gallon", 12.50, 200, 50, "CleanChem Supply"),
    ("Heavy Duty Degreaser", "degreaser", "gallon", 18.75, 80, 20, "CleanChem Supply"),
    ("Triple Foam Polish", "soap", "gallon", 22.00, 120, 30, "ShineMax Inc"),
    ("Carnauba Spray Wax", "wax", "gallon", 28.50, 90, 25, "ShineMax Inc"),
    ("Ceramic Sealant", "wax", "gallon", 45.00, 40, 10, "ShineMax Inc"),
    ("Tire Shine Gel", "specialty", "gallon", 15.00, 60, 15, "AutoChem Pro"),
    ("Bug & Tar Remover", "degreaser", "gallon", 16.50, 45, 10, "CleanChem Supply"),
    ("Wheel Cleaner Acid", "specialty", "gallon", 20.00, 50, 12, "AutoChem Pro"),
    ("Spot-Free Rinse Agent", "rinse_aid", "gallon", 14.00, 100, 25, "PureLine Chemicals"),
    ("Interior Fabric Cleaner", "specialty", "gallon", 17.50, 35, 8, "AutoChem Pro"),
    ("Leather Conditioner", "specialty", "gallon", 32.00, 25, 6, "AutoChem Pro"),
    ("Glass Cleaner Concentrate", "specialty", "gallon", 11.00, 55, 12, "PureLine Chemicals"),
    ("Undercarriage Rust Inhibitor", "specialty", "gallon", 24.00, 40, 10, "CleanChem Supply"),
    ("Fragrance Foam - Cherry", "fragrance", "gallon", 19.00, 30, 8, "ShineMax Inc"),
    ("Fragrance Foam - Ocean Breeze", "fragrance", "gallon", 19.00, 30, 8, "ShineMax Inc"),
]

NUM_PURCHASE_ORDERS = 50

SUPPLIERS = ["CleanChem Supply", "ShineMax Inc", "AutoChem Pro", "PureLine Chemicals"]


def seed_chemicals(conn):
    """Seed chemicals, chemical_usage_logs, purchase_orders, purchase_order_items."""

    # --- Chemicals ---
    chem_rows = [(name, ctype, unit, cost, stock, reorder, supplier)
                 for name, ctype, unit, cost, stock, reorder, supplier in CHEMICALS]

    conn.executemany(
        """INSERT INTO chemicals
           (name, type, unit, cost_per_unit, current_stock, reorder_level, supplier)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        chem_rows,
    )
    conn.commit()

    chem_ids = [r[0] for r in conn.execute("SELECT id FROM chemicals").fetchall()]
    chem_data = conn.execute("SELECT id, cost_per_unit, supplier FROM chemicals").fetchall()
    chem_map = {r[0]: {"cost": r[1], "supplier": r[2]} for r in chem_data}

    # --- Chemical Usage Logs ---
    # Link to wash sessions - each session uses 1-3 chemicals
    session_rows = conn.execute(
        "SELECT id, start_time FROM wash_sessions WHERE status = 'completed'"
    ).fetchall()

    usage_rows = []
    for sess_id, start_time in session_rows:
        usage_date = start_time[:10]  # extract date portion
        num_chemicals = random.choices([1, 2, 3], weights=[40, 40, 20], k=1)[0]
        used_chems = random.sample(chem_ids[:9], min(num_chemicals, 9))  # mainly wash chemicals

        for chem_id in used_chems:
            amount = round(random.uniform(0.05, 0.5), 3)
            usage_rows.append((chem_id, sess_id, amount, usage_date))

    conn.executemany(
        """INSERT INTO chemical_usage_logs
           (chemical_id, session_id, amount_used, usage_date)
           VALUES (?, ?, ?, ?)""",
        usage_rows,
    )
    conn.commit()

    # --- Purchase Orders and Items ---
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    date_range = (end_date - start_date).days

    po_rows = []
    po_item_rows = []

    for po_num in range(1, NUM_PURCHASE_ORDERS + 1):
        supplier = random.choice(SUPPLIERS)
        order_date = start_date + timedelta(days=random.randint(0, date_range))
        expected_delivery = order_date + timedelta(days=random.randint(3, 14))

        # Most orders are delivered
        if random.random() < 0.85:
            actual_delivery = expected_delivery + timedelta(days=random.randint(-2, 5))
            status = "delivered"
        elif random.random() < 0.5:
            actual_delivery = None
            status = "pending"
        else:
            actual_delivery = None
            status = "shipped"

        # Items for this PO: 2-5 chemicals from this supplier
        supplier_chems = [cid for cid in chem_ids if chem_map[cid]["supplier"] == supplier]
        if not supplier_chems:
            supplier_chems = random.sample(chem_ids, random.randint(2, 4))

        num_items = random.randint(2, min(5, len(supplier_chems)))
        selected_chems = random.sample(supplier_chems, num_items)

        total_amount = 0.0
        items_for_po = []
        for chem_id in selected_chems:
            quantity = random.choice([5, 10, 15, 20, 25, 50])
            unit_price = round(chem_map[chem_id]["cost"] * random.uniform(0.9, 1.1), 2)
            total_price = round(quantity * unit_price, 2)
            total_amount += total_price
            items_for_po.append((chem_id, quantity, unit_price, total_price))

        total_amount = round(total_amount, 2)

        po_rows.append((
            supplier, order_date.isoformat(),
            expected_delivery.isoformat(),
            actual_delivery.isoformat() if actual_delivery else None,
            status, total_amount,
        ))

        for chem_id, qty, uprice, tprice in items_for_po:
            po_item_rows.append((po_num, chem_id, qty, uprice, tprice))

    conn.executemany(
        """INSERT INTO purchase_orders
           (supplier, order_date, expected_delivery, actual_delivery, status, total_amount)
           VALUES (?, ?, ?, ?, ?, ?)""",
        po_rows,
    )
    conn.commit()

    # Re-fetch PO IDs for correct foreign keys
    po_ids = [r[0] for r in conn.execute(
        "SELECT id FROM purchase_orders ORDER BY id"
    ).fetchall()]

    # Rebuild items with correct PO IDs
    final_items = []
    item_idx = 0
    for po_idx, po_row in enumerate(po_rows):
        real_po_id = po_ids[po_idx]
        # Find items for this PO (they were stored with 1-based po_num)
        po_num = po_idx + 1
        for _, chem_id, qty, uprice, tprice in po_item_rows:
            if _ == po_num:
                final_items.append((real_po_id, chem_id, qty, uprice, tprice))

    conn.executemany(
        """INSERT INTO purchase_order_items
           (order_id, chemical_id, quantity, unit_price, total_price)
           VALUES (?, ?, ?, ?, ?)""",
        final_items,
    )
    conn.commit()

    print(f"  Inserted {len(CHEMICALS)} chemicals")
    print(f"  Inserted {len(usage_rows)} chemical usage logs")
    print(f"  Inserted {len(po_rows)} purchase orders")
    print(f"  Inserted {len(final_items)} purchase order items")
