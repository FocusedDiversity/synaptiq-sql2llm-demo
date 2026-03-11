# Car Wash Database Schema (`carwash.db`)

This is a **car wash business management** database for "Sparkle Car Wash" in the Phoenix, AZ metro area. It contains **43 tables** modeling the full operation.

## Domain Areas & Tables

### Customers & Vehicles
| Table | Rows | Description |
|-------|------|-------------|
| `customers` | 500 | Customer profiles (name, contact, address, acquisition source) |
| `vehicles` | 650 | Customer vehicles (make, model, year, color, type, plate) |
| `referrals` | 0 | Customer-to-customer referral tracking |

### Wash Operations (core workflow)
| Table | Rows | Description |
|-------|------|-------------|
| `check_ins` | 8,940 | Vehicle check-in/check-out with bay and employee |
| `wash_packages` | 5 | **Express** ($8) / **Basic** ($12) / **Standard** ($18) / **Premium** ($25) / **Ultimate** ($35) |
| `wash_sessions` | 8,940 | 1:1 with check-ins, tracks package, water usage, equipment |
| `wash_cycle_steps` | 59,965 | Individual steps per wash session (~6-7 per wash) |
| `finishing_services` | 5 | Add-ons: Hand Dry, Tire Shine, Interior Wipe, Air Freshener, Window Clean |
| `finishing_records` | 6,008 | Finishing service completions |
| `quality_inspections` | 2,640 | Post-wash quality scores (1-10 scale) |
| `vehicle_condition_notes` | 0 | Pre-existing damage notes |

### Detailing
| Table | Rows | Description |
|-------|------|-------------|
| `detail_packages` | 4 | Interior ($80) / Exterior ($100) / Full ($160) / Premium ($250) |
| `detail_appointments` | 600 | Scheduled detailing jobs |
| `detail_line_items` | 2,395 | Individual services per appointment |

### Equipment & Supplies
| Table | Rows | Description |
|-------|------|-------------|
| `equipment` | 20 | Tunnel washers, pressure washers, dryers, etc. |
| `maintenance_logs` | 158 | Equipment maintenance records |
| `equipment_downtime` | 73 | Downtime incidents with impact level |
| `chemicals` | 15 | Soaps, waxes, degreasers, sealants from suppliers |
| `chemical_usage_logs` | 15,789 | Chemical consumption per wash session |
| `purchase_orders` / `purchase_order_items` | 50 / 145 | Supply chain purchasing |
| `chemical_disposal` | 39 | Hazardous waste disposal records |

### Employees & Scheduling
| Table | Rows | Description |
|-------|------|-------------|
| `roles` | 7 | Manager ($25/hr), Shift Lead ($20/hr), Washer ($15/hr), Detailer ($18/hr), etc. |
| `employees` | 25 | Staff roster |
| `shifts` | 4 | Morning / Midday / Afternoon / Weekend |
| `timecards` | 7,646 | Clock-in/out with overtime tracking |
| `employee_performance` | 296 | Monthly metrics (cars processed, quality, attendance, ratings) |

### Customer Experience
| Table | Rows | Description |
|-------|------|-------------|
| `customer_feedback` | 2,500 | Ratings (1-5) and NPS scores (0-10) |
| `complaints` | 200 | Issue tracking with category, severity, resolution |
| `loyalty_programs` | 3 | Points-based reward programs |
| `loyalty_transactions` | 3,000 | Points earned/redeemed |

### Memberships & Billing
| Table | Rows | Description |
|-------|------|-------------|
| `membership_plans` | 4 | Bronze ($30/mo) / Silver ($50/mo) / Gold ($75/mo) / Platinum ($120/mo) |
| `member_subscriptions` | 120 | Active/cancelled memberships |
| `membership_billing` | 874 | Monthly recurring charges |
| `invoices` | 9,316 | All invoices (wash + detail) |
| `payments` | 9,316 | Payment records |
| `payment_methods` | 705 | Stored cards per customer |
| `refunds` | 66 | Refund records tied to complaints |

### Compliance & Environment
| Table | Rows | Description |
|-------|------|-------------|
| `water_usage` | 366 | Daily fresh/recycled water tracking with reclaim rates |
| `permits` | 8 | Business/environmental permits |
| `regulatory_inspections` | 12 | Government inspection results |

### Marketing (empty)
| Table | Rows | Description |
|-------|------|-------------|
| `marketing_campaigns` | 0 | Campaign tracking (not yet populated) |
| `leads` | 0 | Lead pipeline (not yet populated) |

## Key Characteristics

- **Location**: Arizona (Phoenix metro — Avondale, Goodyear, Buckeye, etc.)
- **Time span**: Customers since ~2024, with operational data spanning ~a year
- **Scale**: ~500 customers, 650 vehicles, ~9K wash sessions, 25 employees
- **Rich relational model**: Extensive foreign keys connecting check-ins to sessions, invoices, feedback, quality inspections, etc.
- **Empty tables**: `leads`, `marketing_campaigns`, `referrals`, and `vehicle_condition_notes` have no data

## Full Schema (DDL)

```sql
CREATE TABLE customers (
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
);

CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    color TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    license_plate TEXT
);

CREATE TABLE check_ins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    check_in_time DATETIME NOT NULL,
    check_out_time DATETIME,
    bay_number INTEGER,
    employee_id INTEGER REFERENCES employees(id)
);

CREATE TABLE vehicle_condition_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
    note TEXT NOT NULL,
    location TEXT,
    severity TEXT DEFAULT 'minor'
);

CREATE TABLE wash_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL
);

CREATE TABLE wash_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
    package_id INTEGER NOT NULL REFERENCES wash_packages(id),
    equipment_id INTEGER REFERENCES equipment(id),
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    water_gallons REAL,
    status TEXT NOT NULL DEFAULT 'completed'
);

CREATE TABLE wash_cycle_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES wash_sessions(id),
    step_name TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    duration_seconds INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed'
);

CREATE TABLE finishing_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    price REAL NOT NULL,
    duration_minutes INTEGER NOT NULL
);

CREATE TABLE finishing_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
    service_id INTEGER NOT NULL REFERENCES finishing_services(id),
    employee_id INTEGER REFERENCES employees(id),
    completed_at DATETIME
);

CREATE TABLE quality_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_in_id INTEGER NOT NULL REFERENCES check_ins(id),
    inspector_id INTEGER REFERENCES employees(id),
    score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 10),
    passed INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    inspected_at DATETIME NOT NULL
);

CREATE TABLE detail_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL
);

CREATE TABLE detail_appointments (
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
);

CREATE TABLE detail_line_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER NOT NULL REFERENCES detail_appointments(id),
    service_name TEXT NOT NULL,
    price REAL NOT NULL,
    duration_minutes INTEGER
);

CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    manufacturer TEXT,
    model TEXT,
    serial_number TEXT,
    install_date DATE,
    status TEXT NOT NULL DEFAULT 'operational',
    bay_number INTEGER
);

CREATE TABLE maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    maintenance_type TEXT NOT NULL,
    description TEXT,
    performed_by INTEGER REFERENCES employees(id),
    performed_date DATE NOT NULL,
    cost REAL,
    next_due_date DATE
);

CREATE TABLE equipment_downtime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL REFERENCES equipment(id),
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    reason TEXT NOT NULL,
    impact_level TEXT NOT NULL DEFAULT 'low',
    resolution TEXT
);

CREATE TABLE chemicals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    unit TEXT NOT NULL,
    cost_per_unit REAL NOT NULL,
    current_stock REAL NOT NULL DEFAULT 0,
    reorder_level REAL NOT NULL,
    supplier TEXT
);

CREATE TABLE chemical_usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chemical_id INTEGER NOT NULL REFERENCES chemicals(id),
    session_id INTEGER REFERENCES wash_sessions(id),
    amount_used REAL NOT NULL,
    usage_date DATE NOT NULL
);

CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier TEXT NOT NULL,
    order_date DATE NOT NULL,
    expected_delivery DATE,
    actual_delivery DATE,
    status TEXT NOT NULL DEFAULT 'pending',
    total_amount REAL NOT NULL
);

CREATE TABLE purchase_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES purchase_orders(id),
    chemical_id INTEGER NOT NULL REFERENCES chemicals(id),
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL
);

CREATE TABLE chemical_disposal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chemical_id INTEGER NOT NULL REFERENCES chemicals(id),
    disposal_date DATE NOT NULL,
    amount REAL NOT NULL,
    disposal_method TEXT NOT NULL,
    manifest_number TEXT,
    handled_by INTEGER REFERENCES employees(id)
);

CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    hourly_rate REAL NOT NULL,
    description TEXT
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    role_id INTEGER NOT NULL REFERENCES roles(id),
    hire_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL
);

CREATE TABLE timecards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    shift_id INTEGER NOT NULL REFERENCES shifts(id),
    work_date DATE NOT NULL,
    clock_in DATETIME NOT NULL,
    clock_out DATETIME,
    hours_worked REAL,
    overtime_hours REAL DEFAULT 0
);

CREATE TABLE employee_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    month DATE NOT NULL,
    cars_processed INTEGER DEFAULT 0,
    quality_score REAL,
    attendance_rate REAL,
    customer_rating REAL
);

CREATE TABLE customer_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    check_in_id INTEGER REFERENCES check_ins(id),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    nps_score INTEGER CHECK(nps_score BETWEEN 0 AND 10),
    comment TEXT,
    feedback_date DATE NOT NULL
);

CREATE TABLE complaints (
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
);

CREATE TABLE loyalty_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    points_per_dollar REAL NOT NULL,
    redemption_rate REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE loyalty_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    program_id INTEGER NOT NULL REFERENCES loyalty_programs(id),
    transaction_type TEXT NOT NULL,
    points INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    description TEXT
);

CREATE TABLE marketing_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    budget REAL NOT NULL,
    spend REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'planned'
);

CREATE TABLE leads (
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
);

CREATE TABLE referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER NOT NULL REFERENCES customers(id),
    referred_id INTEGER NOT NULL REFERENCES customers(id),
    referral_date DATE NOT NULL,
    reward_status TEXT NOT NULL DEFAULT 'pending',
    reward_amount REAL
);

CREATE TABLE membership_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    monthly_price REAL NOT NULL,
    wash_package_id INTEGER REFERENCES wash_packages(id),
    max_washes_per_month INTEGER,
    description TEXT
);

CREATE TABLE member_subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    plan_id INTEGER NOT NULL REFERENCES membership_plans(id),
    start_date DATE NOT NULL,
    end_date DATE,
    status TEXT NOT NULL DEFAULT 'active',
    cancellation_reason TEXT
);

CREATE TABLE membership_billing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL REFERENCES member_subscriptions(id),
    billing_date DATE NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'paid',
    payment_method TEXT
);

CREATE TABLE water_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usage_date DATE NOT NULL UNIQUE,
    fresh_gallons REAL NOT NULL,
    recycled_gallons REAL NOT NULL,
    total_gallons REAL NOT NULL,
    reclaim_rate REAL NOT NULL
);

CREATE TABLE permits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    permit_type TEXT NOT NULL,
    permit_number TEXT NOT NULL,
    issuing_authority TEXT NOT NULL,
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE regulatory_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_type TEXT NOT NULL,
    inspector_name TEXT NOT NULL,
    inspection_date DATE NOT NULL,
    result TEXT NOT NULL,
    score REAL,
    findings TEXT,
    corrective_actions TEXT,
    follow_up_date DATE
);

CREATE TABLE payment_methods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    method_type TEXT NOT NULL,
    last_four TEXT,
    is_default INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    check_in_id INTEGER REFERENCES check_ins(id),
    detail_appointment_id INTEGER REFERENCES detail_appointments(id),
    invoice_date DATE NOT NULL,
    subtotal REAL NOT NULL,
    tax REAL NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id),
    payment_method_id INTEGER REFERENCES payment_methods(id),
    amount REAL NOT NULL,
    payment_date DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed'
);

CREATE TABLE refunds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id INTEGER NOT NULL REFERENCES payments(id),
    complaint_id INTEGER REFERENCES complaints(id),
    amount REAL NOT NULL,
    reason TEXT NOT NULL,
    refund_date DATE NOT NULL,
    status TEXT NOT NULL DEFAULT 'processed'
);
```
