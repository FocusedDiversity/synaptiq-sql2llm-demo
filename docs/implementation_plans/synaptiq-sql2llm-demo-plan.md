# Synaptiq SQL2LLM Demo - Implementation Plan

## Context

Build a demo app in the `synaptiq-sql2llm-demo` repo where users enter natural language queries in a web UI, which are converted to SQL via Claude API, executed against a local SQLite database containing 12 months of realistic car wash business data (500 customers), and results are returned as tables/charts with AI-generated insights.

## Tech Stack

- **Backend**: Python / FastAPI
- **Frontend**: React + Vite + Tailwind CSS
- **LLM**: Claude API (Anthropic SDK, Sonnet model)
- **Database**: SQLite (seeded with deterministic test data)
- **Visualization**: Chart.js via react-chartjs-2

---

## Project Structure

```
synaptiq-sql2llm-demo/
├── .env.example
├── .gitignore
├── README.md
├── setup.sh                      # One-command setup (venv, pip, npm, seed DB)
├── run.sh                        # Start backend + frontend
├── pyproject.toml
├── ddx-library/                  # Existing submodule (not a runtime dependency)
├── backend/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app with CORS
│   ├── config.py                 # pydantic-settings (API key, DB path, model)
│   ├── database.py               # SQLite connection, read-only query execution
│   ├── schema.py                 # Schema introspection (cached at startup)
│   ├── models.py                 # Pydantic request/response models
│   ├── routes/
│   │   ├── query.py              # POST /api/query
│   │   ├── schema.py             # GET /api/schema
│   │   └── suggestions.py        # GET /api/suggestions
│   ├── services/
│   │   ├── llm_service.py        # Claude API: NL-to-SQL + viz + insight
│   │   ├── sql_service.py        # SQL validation (SELECT-only whitelist)
│   │   └── viz_service.py        # Visualization config builder
│   ├── prompts/
│   │   ├── nl_to_sql.py          # System prompt with schema + examples
│   │   ├── insight.py            # Insight generation prompt
│   │   └── viz_recommend.py      # Viz recommendation prompt
│   └── seed/
│       ├── __main__.py           # Entry: python -m backend.seed
│       ├── create_tables.py      # All DDL statements (38 tables)
│       ├── seed_data.py          # Master orchestrator (random.seed(42))
│       ├── generators/           # 11 domain-specific generators
│       │   ├── customers.py, vehicles.py, wash_operations.py,
│       │   ├── detailing.py, equipment.py, chemicals.py,
│       │   ├── workforce.py, customer_experience.py,
│       │   ├── compliance.py, memberships.py, payments.py
│       └── data/                 # Static data (names, vehicle makes/models, etc.)
├── frontend/
│   ├── package.json
│   ├── vite.config.ts            # Proxy /api to localhost:8000
│   ├── tailwind.config.js
│   └── src/
│       ├── App.tsx               # Main layout
│       ├── api/client.ts         # Fetch wrappers
│       ├── types/index.ts        # TypeScript interfaces
│       ├── hooks/
│       │   ├── useQuery.ts       # Query submission state
│       │   └── useQueryHistory.ts # localStorage-backed history
│       ├── utils/chartConfig.ts  # Chart.js data/options builders
│       └── components/
│           ├── Header.tsx
│           ├── QueryInput.tsx    # Textarea + submit + generated SQL display
│           ├── SuggestionChips.tsx
│           ├── ResultsPanel.tsx  # Switches between table/chart + insight
│           ├── DataTable.tsx     # Sortable table with sticky header
│           ├── ChartDisplay.tsx  # Bar, line, pie via react-chartjs-2
│           ├── InsightPanel.tsx  # AI insight card
│           ├── QueryHistory.tsx  # Left sidebar, last 20 queries
│           ├── LoadingSpinner.tsx
│           └── ErrorDisplay.tsx
└── data/
    └── carwash.db                # Generated at seed time (gitignored)
```

---

## Database Schema (38 tables, 12 domains)

### Domain 1: Customer Acquisition & Sales
- **customers** - 500 records: name, email, phone, address, acquisition_source, customer_since
- **marketing_campaigns** - 15 records: name, type, dates, budget, spend, status
- **leads** - ~300 records: from campaigns, status tracking, conversion
- **referrals** - referrer/referred tracking, reward status

### Domain 2: Vehicle Intake
- **vehicles** - ~650 records: customer FK, make, model, year, color, type, license plate
- **check_ins** - ~8,000 records: vehicle, customer, timestamps, bay number, employee
- **vehicle_condition_notes** - pre-existing damage documentation

### Domain 3: Automated Wash Cycles
- **wash_packages** - 5 packages: Express ($8), Basic ($12), Standard ($18), Premium ($25), Ultimate ($35)
- **wash_sessions** - ~8,000: linked to check-ins, package, equipment, water usage
- **wash_cycle_steps** - individual steps (pre-soak, soap, scrub, rinse, wax, dry)

### Domain 4: Post-Wash Finishing
- **finishing_services** - hand dry, tire shine, interior wipe, etc.
- **finishing_records** - service performed per check-in
- **quality_inspections** - scored 1-10, pass/fail, by inspector

### Domain 5: Detailing Services
- **detail_packages** - 4 packages: Interior ($80), Exterior ($100), Full ($160), Premium ($250)
- **detail_appointments** - ~600: scheduled/completed/cancelled
- **detail_line_items** - individual services within a detail job

### Domain 6: Equipment Operations
- **equipment** - 20 items: tunnels, pressure washers, vacuums, dryers, conveyors, pumps
- **maintenance_logs** - preventive/corrective/emergency maintenance
- **equipment_downtime** - start/end, reason, impact level, resolution

### Domain 7: Chemical & Supply Management
- **chemicals** - 15 items: soaps, waxes, degreasers, tire cleaners, sealants
- **chemical_usage_logs** - per-session usage tracking
- **purchase_orders** - ~50 orders to suppliers
- **purchase_order_items** - line items per PO

### Domain 8: Workforce Management
- **roles** - 7 roles: Manager, Shift Lead, Washer, Detailer, Cashier, Maintenance Tech, Attendant
- **employees** - 25 staff members
- **shifts** - morning, afternoon, evening, weekend
- **timecards** - ~6,500 daily clock in/out records
- **employee_performance** - monthly metrics per employee

### Domain 9: Customer Experience & Retention
- **customer_feedback** - ~2,500 surveys: ratings (1-5), NPS (0-10), comments
- **complaints** - ~200: categorized, severity, resolution tracking
- **loyalty_programs** - points-based program definition
- **loyalty_transactions** - ~3,000 earn/redeem records

### Domain 10: Environmental & Regulatory Compliance
- **water_usage** - 365 daily records: fresh, recycled, reclaim rate
- **chemical_disposal** - disposal method, manifest tracking
- **permits** - 8 permits: water discharge, business license, hazmat, etc.
- **regulatory_inspections** - 12 inspections: environmental, health, fire, OSHA

### Domain 11: Membership Management
- **membership_plans** - 4 tiers: Bronze ($30/mo), Silver ($50/mo), Gold ($75/mo), Platinum ($120/mo)
- **member_subscriptions** - ~120 active/cancelled subscriptions (~24% of customers)
- **membership_billing** - monthly billing records

### Domain 12: Payments & Transactions
- **payment_methods** - credit/debit/cash/mobile per customer
- **invoices** - ~8,600: per check-in and detail appointment
- **payments** - ~8,600: linked to invoices
- **refunds** - complaint-related refunds

### Seed Data Characteristics
- **Time span**: Jan 2024 - Dec 2024 (12 months)
- **Seasonal patterns**: Summer peak (~30 cars/day), winter low (~15 cars/day), weekend spikes
- **Deterministic**: `random.seed(42)` for reproducibility
- Realistic names, vehicle makes/models, dates, amounts

---

## API Endpoints

### `POST /api/query`
1. Receive natural language query
2. Call Claude to generate SQL (with full schema context)
3. Validate SQL is SELECT-only (whitelist approach)
4. Execute against SQLite (read-only, LIMIT 500)
5. Call Claude to recommend visualization type + generate insight (single API call)
6. Return: `{ generated_sql, columns, rows, visualization, insight }`

### `GET /api/schema`
Returns introspected database schema (all tables, columns, types, FKs).

### `GET /api/suggestions`
Returns hardcoded sample queries grouped by category (Revenue, Customers, Operations, Memberships, Environmental).

---

## Request Flow

```
User types query → QueryInput → POST /api/query →
  → Claude NL-to-SQL → SQL validation → SQLite execution →
  → Claude viz+insight (single call) → QueryResponse →
  → Frontend renders Chart or Table + Insight panel
```

---

## Key Design Decisions

1. **Two Claude API calls per query** (not three): NL-to-SQL is one call; viz recommendation + insight are combined into a single second call to minimize latency
2. **SQL safety via whitelist**: Only SELECT allowed; no ORM needed since DB is read-only
3. **No auth**: Demo app, local use only
4. **localStorage for query history**: No backend storage needed
5. **Tailwind CSS**: Lightweight, no component library overhead
6. **Vite proxy**: Frontend dev server proxies `/api` to FastAPI on port 8000

---

## Implementation Order

| Step | What | Depends On |
|------|------|------------|
| 1 | Root config files (.gitignore, pyproject.toml, .env.example, setup.sh, run.sh) | - |
| 2 | Backend skeleton (main.py, config.py, database.py, models.py) | Step 1 |
| 3 | Database DDL (create_tables.py - all 38 tables) | Step 2 |
| 4 | Static data files (names, vehicles, business data) | - |
| 5 | Seed generators (11 modules) + master seeder | Steps 3, 4 |
| 6 | Schema introspection module | Step 3 |
| 7 | SQL safety service | Step 2 |
| 8 | LLM service + prompt templates | Step 2 |
| 9 | Route handlers (query, schema, suggestions) | Steps 6, 7, 8 |
| 10 | Frontend scaffold (Vite, Tailwind, types, API client) | - |
| 11 | Frontend components (Header → QueryInput → Charts → ResultsPanel → History) | Step 10 |
| 12 | End-to-end testing and README | Steps 9, 11 |

---

## Verification

1. `./setup.sh` completes without errors
2. `sqlite3 data/carwash.db ".tables"` shows all 38 tables
3. `sqlite3 data/carwash.db "SELECT COUNT(*) FROM customers"` returns 500
4. `./run.sh` starts backend on :8000 and frontend on :5173
5. `curl http://localhost:8000/api/suggestions` returns sample queries
6. `curl -X POST http://localhost:8000/api/query -d '{"query":"How many customers do we have?"}' -H 'Content-Type: application/json'` returns valid response with SQL, results, viz config, and insight
7. Browser at http://localhost:5173 shows the UI, suggestions load, queries execute, charts render, insights display
