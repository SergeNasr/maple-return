---
phase: 06-user-interface
plan: 01
subsystem: backend-api
tags: [database, api, persistence, orchestration, frontend-foundation]
dependency_graph:
  requires: [mortgage, operating, cashflow, analysis, exit]
  provides: [config-persistence, simulation-api, css-framework]
  affects: [wizard, results-pages]
tech_stack:
  added: [htmx-2.0.4]
  patterns: [orm-persistence, api-orchestration, partial-auto-save]
key_files:
  created:
    - maple_return/db_models.py
    - maple_return/routes.py
    - maple_return/static/style.css
    - tests/test_routes.py
  modified:
    - maple_return/main.py
    - maple_return/templates/base.html
decisions:
  - Use SQLAlchemy ORM with single PropertyConfig row (id=1) for single-property tool
  - Store monetary values as strings to preserve Decimal precision
  - All config fields nullable to support partial auto-save as user fills wizard
  - Simulate endpoint uses purchase_price as current_property_value (no appreciation)
  - HTMX 2.0.4 for progressive enhancement and auto-save behavior
  - CSS designed for "spreadsheet-meets-modern-web" aesthetic per user decision
metrics:
  tasks_completed: 3
  tests_added: 5
  total_tests: 153
  duration_minutes: 9.0
  completed_date: 2026-02-15
---

# Phase 06 Plan 01: Backend API & Frontend Foundation Summary

Backend foundation for UI: SQLite persistence, API routes for save/load/simulate, and comprehensive CSS/HTMX setup.

## Objective

Establish data layer (auto-save/load property configs to SQLite), simulation orchestration endpoint (runs all calculation engines and returns results), and shared CSS/HTML foundation for wizard and results pages.

## What Was Built

### 1. Database Persistence (`maple_return/db_models.py`)

SQLAlchemy ORM model `PropertyConfig` with:
- Single row design (id=1) for single-property tool
- All wizard fields as nullable columns (supports partial auto-save)
- Monetary values stored as strings (preserves Decimal precision)
- Auto-updated `updated_at` timestamp using timezone-aware UTC

Fields cover all wizard steps:
- **Property**: purchase_date, purchase_price, down_payment
- **Mortgage**: annual_rate, monthly_payment, amortization_years, rate_type
- **Operating**: monthly_rent, vacancy_rate, property_tax_annual, insurance_annual, maintenance_annual, management_fee_rate, rent_escalation_rate, expense_escalation_rate, cad_per_usd
- **Scenarios**: renewal_scenario_1/2/3 (JSON strings)
- **Exit**: sale_price, sale_year, commission_rate, closing_costs

### 2. API Routes (`maple_return/routes.py`)

FastAPI router with `/api` prefix providing three endpoints:

**POST /api/save** — Partial auto-save
- Accepts JSON with any subset of PropertyConfig fields
- Upserts row id=1 (creates if missing, updates only provided fields if exists)
- Returns `{"status": "ok"}`

**GET /api/load** — Load saved configuration
- Returns full PropertyConfig as JSON dict
- Returns empty dict `{}` if no config exists
- Used to restore wizard state on page load

**POST /api/simulate** — Orchestration endpoint
- Validates all required fields present (returns 422 if missing)
- Parses renewal scenarios from JSON strings
- Builds MortgageInput, OperatingInput, ExitInput from config
- Orchestrates full calculation pipeline:
  - `calculate_multi_term` → mortgage scenarios
  - `generate_monthly_cashflows` → monthly cash flow statements
  - `generate_annual_operating_summaries` → annual operating rollups
  - `generate_annual_summaries` → annual mortgage summaries
  - `build_pnl_table` → P&L with cumulative metrics
  - `build_amortization_table` → amortization schedule
  - `build_dashboard_snapshot` → current position snapshot
  - `calculate_exit` + `calculate_total_return` → exit analysis (if exit fields present)
  - `compare_scenarios` → scenario comparison (if multiple scenarios)
- Returns JSON with all calculation results serialized (Decimal→str, date→ISO string)

Helper function `_serialize()` recursively converts dataclasses, Decimals, and dates to JSON-compatible types.

Assumptions:
- `current_property_value` = `purchase_price` (no appreciation for ongoing property)
- `remaining_balance` extracted from most recent mortgage schedule entry
- Exit calculations use mortgage balance at sale year (month = sale_year * 12)

### 3. Frontend Foundation

**Updated `maple_return/templates/base.html`:**
- Added HTMX 2.0.4 CDN script
- Added viewport meta tag for desktop-first design
- Added header with "Maple Return" app name link
- Added `head_extra` block for page-specific scripts/styles
- Widened container to 1100px for tables

**Replaced `maple_return/static/style.css`:**
Comprehensive CSS (507 lines) for "spreadsheet-meets-modern-web" aesthetic:

- **Layout**: Header, centered container (max-width 1100px), white background, subtle shadows
- **Wizard progress**: Horizontal step indicator with circles, active/completed states, maple red accent
- **Wizard forms**: Clean input styles, error states, hint text, validation messages
- **Wizard navigation**: Back/Next buttons with primary/secondary styles
- **Buttons**: Base, primary (maple red), secondary (blue) with hover states
- **Dashboard**: Grid layout for metric cards with label/value/sub structure
- **Tables**: Full-width data tables with sticky headers, zebra striping, hover effects, tabular-nums for alignment
- **Tabs**: Horizontal tab navigation for detail drill-down
- **Scenario comparison**: Side-by-side grid layout
- **HTMX loading indicator**: Spinning animation on request
- **Flash messages**: Success (green) and error (red) notification styles
- **Utility classes**: currency, percentage, text-right, text-center

Color palette: white backgrounds, subtle grays (#f5f5f5, #e0e0e0), maple red (#d32f2f) for accents, blue (#1976d2) for links.

### 4. Unit Tests (`tests/test_routes.py`)

5 async tests covering all API endpoints:

1. **test_save_creates_config** — POST /api/save with partial data returns 200
2. **test_save_partial_update** — Partial updates don't clobber existing fields
3. **test_load_returns_saved_data** — GET /api/load returns saved configuration
4. **test_simulate_missing_fields_returns_422** — POST /api/simulate validates required fields
5. **test_simulate_complete_config_returns_200** — Complete config simulation returns 200 with expected keys

Test isolation handled by explicitly clearing config with None values between tests.

**Test metrics:** 153 total tests pass (5 new route tests + 148 existing)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed datetime.utcnow() deprecation warning**
- **Found during:** Task 3 (running tests)
- **Issue:** SQLAlchemy PropertyConfig model used deprecated `datetime.utcnow()` which triggers DeprecationWarning
- **Fix:** Updated to `datetime.now(UTC)` with lambda wrappers for default/onupdate
- **Files modified:** maple_return/db_models.py
- **Commit:** 65b1b9b

**2. [Rule 1 - Bug] Corrected function parameter names in simulate endpoint**
- **Found during:** Task 3 (test execution)
- **Issue:** Multiple function calls used incorrect parameter names causing TypeErrors:
  - `generate_monthly_cashflows` used `schedule` instead of `mortgage_schedule`
  - `generate_annual_operating_summaries` used `cashflows` instead of `monthly_cashflows`
  - `generate_annual_summaries` included extra `first_year` parameter
  - `build_pnl_table` missing `current_property_value` and `down_payment`
  - `build_amortization_table` used `annual_mortgage` instead of `schedule`
  - `build_dashboard_snapshot` used `cashflows` instead of `monthly_cashflows`, missing `current_property_value`, `remaining_balance`, `cad_per_usd`
  - `ExitInput` missing `remaining_mortgage_balance`, `purchase_price`, `down_payment`
  - `calculate_exit` included extra parameters not in signature
  - `calculate_total_return` used `exit_result` instead of `exit_input`
- **Fix:** Corrected all parameter names to match function signatures, added missing parameters, calculated derived values (current_property_value, remaining_balance, sale_month_balance)
- **Files modified:** maple_return/routes.py
- **Commit:** 65b1b9b

**3. [Rule 1 - Bug] Fixed Jinja2 template syntax error**
- **Found during:** Task 2 (manual server testing)
- **Issue:** Base template used invalid Jinja2 syntax `{% if self.page_class() %}` causing UndefinedError
- **Fix:** Removed conditional body class (not needed for this plan's scope)
- **Files modified:** maple_return/templates/base.html
- **Commit:** 595bca2

**4. [Rule 1 - Bug] Fixed unused import lint error**
- **Found during:** Task 1 (running lint)
- **Issue:** tests/test_uat_phase05.py imported `TotalReturnSummary` but didn't use it
- **Fix:** Removed unused import from test file
- **Files modified:** tests/test_uat_phase05.py
- **Commit:** c3d4db2

## Decisions Made

1. **Single PropertyConfig row (id=1)** — Simplifies single-property tool design. Wizard always saves to/loads from same row. No need for user accounts or multi-property management in v1.

2. **String storage for monetary values** — Preserves Decimal precision across database round-trips. Avoids float conversion issues. Serialized as strings in JSON responses as well.

3. **Nullable config fields** — Enables incremental auto-save as user fills wizard. Validation only enforced on simulate endpoint, not on save.

4. **current_property_value = purchase_price** — For ongoing (not-yet-sold) properties, assumes no appreciation. Exit scenarios use exit.sale_price for appreciation calculation.

5. **HTMX 2.0.4 for progressive enhancement** — Enables auto-save on field blur, partial page updates, loading indicators without heavy JavaScript framework. Clean separation of concerns.

6. **Spreadsheet aesthetic** — Clean, minimal, white backgrounds, subtle grays, focus on data density and readability. No fancy gradients or animations. Desktop-first (no mobile media queries in v1).

## Self-Check: PASSED

All created files exist:
- FOUND: maple_return/db_models.py
- FOUND: maple_return/routes.py
- FOUND: maple_return/static/style.css
- FOUND: tests/test_routes.py

All commits exist:
- FOUND: c3d4db2 (Task 1: ORM model and API routes)
- FOUND: 595bca2 (Task 2: HTMX and CSS)
- FOUND: 65b1b9b (Task 3: Unit tests and bug fixes)

All tests pass: 153/153 ✓

Linter clean: No errors ✓

## Next Steps

With backend API and CSS foundation in place, ready for:
- **Plan 06-02**: Property wizard (multi-step form with auto-save to /api/save)
- **Plan 06-03**: Results dashboard (loads from /api/simulate, renders tables and metrics)

The orchestration endpoint is fully functional and tested. Wizard and results pages will be thin UI layers over these APIs.
