"""DDL statements for all 38 tables across 12 domains."""

DDL_STATEMENTS = [
    # Domain 1: Customer Acquisition & Sales
    """CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip_code TEXT,
        acquisition_source TEXT NOT NULL,
        customer_since DATE NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS marketing_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE,
        budget REAL NOT NULL,
        spend REAL NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'planned'
    )""",
    """CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER REFERENCES marketing_campaigns(id),
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        created_date DATE NOT NULL,
        converted_date DATE,
        customer_id INTEGER REFERENCES customers(id)
    )""",
    """CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER NOT NULL REFERENCES customers(id),
        referred_id INTEGER NOT NULL REFERENCES customers(id),
        referral_date DATE NOT NULL,
        reward_status TEXT NOT NULL DEFAULT 'pending',
        reward_amount REAL
    )""",
    # Domain 2: Vehicle Intake
    """CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        make TEXT NOT NULL,
        model TEXT NOT NULL,
        year INTEGER NOT NULL,
        color TEXT NOT NULL,
        vehicle_type TEXT NOT NULL,
        license_plate TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS check_ins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        check_in_time DATETIME NOT NULL,
        check_out_time DATETIME,
        bay_number INTEGER,
        employee_id INTEGER REFERENCES employees(id)
    )""",
    """CREATE TABLE IF NOT EXISTS vehicle_condition_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
        note TEXT NOT NULL,
        location TEXT,
        severity TEXT DEFAULT 'minor'
    )""",
    # Domain 3: Automated Wash Cycles
    """CREATE TABLE IF NOT EXISTS wash_packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL,
        description TEXT,
        duration_minutes INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS wash_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
        package_id INTEGER NOT NULL REFERENCES wash_packages(id),
        equipment_id INTEGER REFERENCES equipment(id),
        start_time DATETIME NOT NULL,
        end_time DATETIME,
        water_gallons REAL,
        status TEXT NOT NULL DEFAULT 'completed'
    )""",
    """CREATE TABLE IF NOT EXISTS wash_cycle_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL REFERENCES wash_sessions(id),
        step_name TEXT NOT NULL,
        step_order INTEGER NOT NULL,
        duration_seconds INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'completed'
    )""",
    # Domain 4: Post-Wash Finishing
    """CREATE TABLE IF NOT EXISTS finishing_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        price REAL NOT NULL,
        duration_minutes INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS finishing_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
        service_id INTEGER NOT NULL REFERENCES finishing_services(id),
        employee_id INTEGER REFERENCES employees(id),
        completed_at DATETIME
    )""",
    """CREATE TABLE IF NOT EXISTS quality_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
        inspector_id INTEGER REFERENCES employees(id),
        score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 10),
        passed INTEGER NOT NULL DEFAULT 1,
        notes TEXT,
        inspected_at DATETIME NOT NULL
    )""",
    # Domain 5: Detailing Services
    """CREATE TABLE IF NOT EXISTS detail_packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL,
        description TEXT,
        duration_minutes INTEGER NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS detail_appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
        package_id INTEGER NOT NULL REFERENCES detail_packages(id),
        scheduled_date DATE NOT NULL,
        scheduled_time TEXT,
        status TEXT NOT NULL DEFAULT 'scheduled',
        employee_id INTEGER REFERENCES employees(id),
        completed_at DATETIME,
        notes TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS detail_line_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL REFERENCES detail_appointments(id),
        service_name TEXT NOT NULL,
        price REAL NOT NULL,
        duration_minutes INTEGER
    )""",
    # Domain 6: Equipment Operations
    """CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        manufacturer TEXT,
        model TEXT,
        serial_number TEXT,
        install_date DATE,
        status TEXT NOT NULL DEFAULT 'operational',
        bay_number INTEGER
    )""",
    """CREATE TABLE IF NOT EXISTS maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL REFERENCES equipment(id),
        maintenance_type TEXT NOT NULL,
        description TEXT,
        performed_by INTEGER REFERENCES employees(id),
        performed_date DATE NOT NULL,
        cost REAL,
        next_due_date DATE
    )""",
    """CREATE TABLE IF NOT EXISTS equipment_downtime (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL REFERENCES equipment(id),
        start_time DATETIME NOT NULL,
        end_time DATETIME,
        reason TEXT NOT NULL,
        impact_level TEXT NOT NULL DEFAULT 'low',
        resolution TEXT
    )""",
    # Domain 7: Chemical & Supply Management
    """CREATE TABLE IF NOT EXISTS chemicals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        unit TEXT NOT NULL,
        cost_per_unit REAL NOT NULL,
        current_stock REAL NOT NULL DEFAULT 0,
        reorder_level REAL NOT NULL,
        supplier TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS chemical_usage_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chemical_id INTEGER NOT NULL REFERENCES chemicals(id),
        session_id INTEGER REFERENCES wash_sessions(id),
        amount_used REAL NOT NULL,
        usage_date DATE NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS purchase_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier TEXT NOT NULL,
        order_date DATE NOT NULL,
        expected_delivery DATE,
        actual_delivery DATE,
        status TEXT NOT NULL DEFAULT 'pending',
        total_amount REAL NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS purchase_order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL REFERENCES purchase_orders(id),
        chemical_id INTEGER NOT NULL REFERENCES chemicals(id),
        quantity REAL NOT NULL,
        unit_price REAL NOT NULL,
        total_price REAL NOT NULL
    )""",
    # Domain 8: Workforce Management
    """CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        hourly_rate REAL NOT NULL,
        description TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        role_id INTEGER NOT NULL REFERENCES roles(id),
        hire_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
    )""",
    """CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS timecards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL REFERENCES employees(id),
        shift_id INTEGER NOT NULL REFERENCES shifts(id),
        work_date DATE NOT NULL,
        clock_in DATETIME NOT NULL,
        clock_out DATETIME,
        hours_worked REAL,
        overtime_hours REAL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS employee_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL REFERENCES employees(id),
        month DATE NOT NULL,
        cars_processed INTEGER DEFAULT 0,
        quality_score REAL,
        attendance_rate REAL,
        customer_rating REAL
    )""",
    # Domain 9: Customer Experience & Retention
    """CREATE TABLE IF NOT EXISTS customer_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        check_in_id INTEGER REFERENCES check_ins(id),
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        nps_score INTEGER CHECK(nps_score BETWEEN 0 AND 10),
        comment TEXT,
        feedback_date DATE NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        check_in_id INTEGER REFERENCES check_ins(id),
        category TEXT NOT NULL,
        severity TEXT NOT NULL DEFAULT 'low',
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        resolution TEXT,
        created_date DATE NOT NULL,
        resolved_date DATE
    )""",
    """CREATE TABLE IF NOT EXISTS loyalty_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        points_per_dollar REAL NOT NULL,
        redemption_rate REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
    )""",
    """CREATE TABLE IF NOT EXISTS loyalty_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        program_id INTEGER NOT NULL REFERENCES loyalty_programs(id),
        transaction_type TEXT NOT NULL,
        points INTEGER NOT NULL,
        transaction_date DATE NOT NULL,
        description TEXT
    )""",
    # Domain 10: Environmental & Regulatory Compliance
    """CREATE TABLE IF NOT EXISTS water_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usage_date DATE NOT NULL UNIQUE,
        fresh_gallons REAL NOT NULL,
        recycled_gallons REAL NOT NULL,
        total_gallons REAL NOT NULL,
        reclaim_rate REAL NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS chemical_disposal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chemical_id INTEGER NOT NULL REFERENCES chemicals(id),
        disposal_date DATE NOT NULL,
        amount REAL NOT NULL,
        disposal_method TEXT NOT NULL,
        manifest_number TEXT,
        handled_by INTEGER REFERENCES employees(id)
    )""",
    """CREATE TABLE IF NOT EXISTS permits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        permit_type TEXT NOT NULL,
        permit_number TEXT NOT NULL,
        issuing_authority TEXT NOT NULL,
        issue_date DATE NOT NULL,
        expiry_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'active'
    )""",
    """CREATE TABLE IF NOT EXISTS regulatory_inspections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inspection_type TEXT NOT NULL,
        inspector_name TEXT NOT NULL,
        inspection_date DATE NOT NULL,
        result TEXT NOT NULL,
        score REAL,
        findings TEXT,
        corrective_actions TEXT,
        follow_up_date DATE
    )""",
    # Domain 11: Membership Management
    """CREATE TABLE IF NOT EXISTS membership_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        monthly_price REAL NOT NULL,
        wash_package_id INTEGER REFERENCES wash_packages(id),
        max_washes_per_month INTEGER,
        description TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS member_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        plan_id INTEGER NOT NULL REFERENCES membership_plans(id),
        start_date DATE NOT NULL,
        end_date DATE,
        status TEXT NOT NULL DEFAULT 'active',
        cancellation_reason TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS membership_billing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER NOT NULL REFERENCES member_subscriptions(id),
        billing_date DATE NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'paid',
        payment_method TEXT
    )""",
    # Domain 12: Payments & Transactions
    """CREATE TABLE IF NOT EXISTS payment_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        method_type TEXT NOT NULL,
        last_four TEXT,
        is_default INTEGER NOT NULL DEFAULT 0
    )""",
    """CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL REFERENCES customers(id),
        check_in_id INTEGER REFERENCES check_ins(id),
        detail_appointment_id INTEGER REFERENCES detail_appointments(id),
        invoice_date DATE NOT NULL,
        subtotal REAL NOT NULL,
        tax REAL NOT NULL,
        total REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending'
    )""",
    """CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL REFERENCES invoices(id),
        payment_method_id INTEGER REFERENCES payment_methods(id),
        amount REAL NOT NULL,
        payment_date DATETIME NOT NULL,
        status TEXT NOT NULL DEFAULT 'completed'
    )""",
    """CREATE TABLE IF NOT EXISTS refunds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_id INTEGER NOT NULL REFERENCES payments(id),
        complaint_id INTEGER REFERENCES complaints(id),
        amount REAL NOT NULL,
        reason TEXT NOT NULL,
        refund_date DATE NOT NULL,
        status TEXT NOT NULL DEFAULT 'processed'
    )""",
]


def create_all_tables(conn):
    """Create all 38 tables."""
    for ddl in DDL_STATEMENTS:
        conn.execute(ddl)
    conn.commit()
