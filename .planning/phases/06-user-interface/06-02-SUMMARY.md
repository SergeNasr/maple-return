---
phase: 06-user-interface
plan: 02
subsystem: wizard-ui
tags: [frontend, wizard, forms, validation, auto-save, htmx]
dependency_graph:
  requires: [database, api-routes, css-framework]
  provides: [property-wizard, step-navigation, client-validation]
  affects: [results-pages]
tech_stack:
  added: []
  patterns: [multi-step-wizard, client-side-validation, auto-save-on-blur, dynamic-form-rows]
key_files:
  created:
    - maple_return/templates/wizard.html
    - maple_return/templates/partials/step_property.html
    - maple_return/templates/partials/step_mortgage.html
    - maple_return/templates/partials/step_operating.html
    - maple_return/templates/partials/step_scenarios.html
    - maple_return/templates/partials/step_exit.html
  modified:
    - maple_return/main.py
    - tests/test_main.py
decisions:
  - Wizard state tracked via currentStep JavaScript variable with URL hash sync
  - Client-side validation runs on Next button click, blocks advancement if invalid
  - Auto-save triggers on input blur/change with 2-second visual indicator
  - Scenario step uses dynamic term rows (max 5 per scenario) with JSON serialization
  - Home route (/) redirects to /wizard for main entry point
  - Fields start blank with placeholder hints (no pre-filled defaults)
metrics:
  tasks_completed: 2
  tests_added: 5
  total_tests: 155
  duration_minutes: 3.8
  completed_date: 2026-02-15
---

# Phase 06 Plan 02: Property Wizard Summary

Multi-step wizard UI with 5 steps, client-side validation, auto-save, and dynamic scenario management.

## Objective

Build a guided wizard interface for capturing all property investment inputs across 5 steps (Property, Mortgage, Operating, Scenarios, Exit) with inline validation, auto-save to SQLite on field blur, and state restoration on page load.

## What Was Built

### 1. Main Wizard Template (`maple_return/templates/wizard.html`)

**Progress Indicator:**
- Horizontal 5-step indicator with numbered circles
- Active step highlighted with maple red accent (#d32f2f)
- Completed steps show checkmark styling
- Step labels: Property, Mortgage, Operating, Scenarios, Exit

**Step Container:**
- Single container with 5 step divs (only active step visible)
- Each step includes its partial template via Jinja2 `{% include %}`
- CSS class `.active` controls visibility

**Navigation Buttons:**
- Back button (hidden on step 1)
- Next button (steps 1-4)
- Run Simulation button (step 5 only, primary style)
- Navigation updates based on current step

**Client-Side JavaScript (inline):**
- `showStep(n)` — Shows step N, updates progress indicator, manages button visibility
- `validateStep(n)` — Validates all required fields in step:
  - Checks for empty required fields
  - Validates number ranges (min/max)
  - Validates date formats
  - Adds `.error` class and error messages to invalid inputs
  - Returns true/false
- `nextStep()` — Validates current step before advancing
- `prevStep()` — Moves back without validation
- `autoSave(field, value)` — POST to `/api/save` with single field, shows "Saved" indicator
- `loadSavedData()` — Fetches from `/api/load` on page load, populates all fields
- `submitWizard()` — Validates step 5, POST to `/api/simulate`, redirects to `/results` on success

**Auto-Save Behavior:**
- Each input has `onblur="autoSave(this.name, this.value)"`
- Selects use `onchange` instead of `onblur`
- Visual feedback: green "Saved" text appears for 2 seconds
- Only saves changed field (partial update pattern)

**State Restoration:**
- On page load, fetch `/api/load`
- Populate all form fields with saved values
- Special handling for scenario JSON data (triggers custom event)

### 2. Step Partial Templates

**Step 1: Property (`step_property.html`)**
- purchase_date — date input, required
- purchase_price — number (step 0.01, min 0), required
- down_payment — number (step 0.01, min 0), required

All fields:
- Placeholder hints (e.g., "e.g. 500000")
- Auto-save on blur
- Error message spans for validation

**Step 2: Mortgage (`step_mortgage.html`)**
- annual_rate — number (step 0.001, min 0, max 1), required, with hint text "Enter as decimal: 0.045 = 4.5%"
- monthly_payment — number (step 0.01, min 0), required
- amortization_years — number (min 1, max 40), required
- rate_type — select dropdown (variable/fixed), required, auto-save on change

**Step 3: Operating (`step_operating.html`)**
9 operating expense fields:
- monthly_rent — number (step 0.01, min 0), required
- vacancy_rate — number (step 0.01, min 0, max 1), required
- property_tax_annual — number (step 0.01, min 0), required
- insurance_annual — number (step 0.01, min 0), required
- maintenance_annual — number (step 0.01, min 0), required
- management_fee_rate — number (step 0.01, min 0, max 1), required
- rent_escalation_rate — number (step 0.001, min 0, max 1), required
- expense_escalation_rate — number (step 0.001, min 0, max 1), required
- cad_per_usd — number (step 0.01, min 0), required

**Step 4: Scenarios (`step_scenarios.html`)**

Most complex step with dynamic functionality:

**3 Scenarios:**
1. Scenario 1 (Base Case) — required, first term required
2. Scenario 2 (Optional) — all fields optional
3. Scenario 3 (Optional) — all fields optional

**Dynamic Term Rows:**
- Each scenario starts with 1 term row
- "Add Term" button adds new rows (max 5 renewal terms per scenario)
- Each row has: term label, rate input (number, step 0.001), type select (variable/fixed)
- "Remove" button on rows 2-5
- JavaScript manages term counts per scenario

**JSON Serialization:**
- `serializeScenario(scenarioNum)` — Collects all term rows for a scenario
- Builds JSON array: `[{"rate": "0.05", "type": "fixed"}, ...]`
- Stores in hidden input (`renewal_scenario_1/2/3`)
- Auto-saves JSON string via `autoSave()` on any change

**State Restoration:**
- Listens for `load-scenario` custom event
- Parses JSON from saved config
- Recreates term rows with saved values
- Restores rate and type selections

**Inline Styles:**
- Grid layout for term rows (100px label, 1fr rate, 150px type, auto remove)
- Gray background (#f5f5f5) for scenario containers
- Compact spacing for multiple rows

**Step 5: Exit (`step_exit.html`)**
- sale_price — number (step 0.01, min 0), required
- sale_year — number (min 1, max 30), required
- commission_rate — number (step 0.001, min 0, max 1), required
- closing_costs — number (step 0.01, min 0), required

### 3. Route Updates (`maple_return/main.py`)

**New Routes:**
- `GET /wizard` — Renders wizard.html template
- `GET /` — Redirects to `/wizard` with 307 status (replaces old test page)

**Integration:**
- Uses existing Jinja2 templates configuration
- Leverages FastAPI RedirectResponse for home redirect
- Wizard connects to existing `/api/save`, `/api/load`, `/api/simulate` endpoints

### 4. Updated Tests (`tests/test_main.py`)

Replaced old home route tests with wizard-specific tests:

**5 New Tests:**
1. `test_home_route_redirects_to_wizard` — Verifies 307 redirect to /wizard
2. `test_wizard_route_returns_200` — Wizard page loads successfully
3. `test_wizard_route_contains_title` — Contains "Property Wizard" and "Maple Return"
4. `test_wizard_has_progress_indicator` — All 5 step labels present in HTML
5. `test_wizard_has_all_step_partials` — All step field names present (purchase_price, annual_rate, monthly_rent, renewal_scenario_1, sale_price)

**Test Metrics:** 155 total tests pass (5 new wizard tests, removed 4 old home tests, net +1)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test failures after home route redirect**
- **Found during:** Running test suite after Task 1
- **Issue:** 4 tests in test_main.py expected home route to return 200 and render test page, but route now redirects to /wizard
- **Fix:** Replaced old tests with new tests for redirect behavior and wizard page content
- **Files modified:** tests/test_main.py
- **Commit:** 803a301

None - plan executed exactly as written. The test fix was a necessary update to match the new behavior specified in the plan.

## Decisions Made

1. **JavaScript state in wizard.html** — Single-page wizard with client-side step management. URL hash tracks current step for browser back/forward support. Simple vanilla JS (no framework) keeps footprint small.

2. **Client-side validation on Next** — Validation runs when user clicks Next, not on blur. This provides better UX (user can fill form without interruption) while still preventing advancement with invalid data.

3. **Auto-save on blur/change** — Every field auto-saves individually on blur (inputs) or change (selects). Granular saves minimize data loss if user closes tab. Visual indicator confirms save happened.

4. **Dynamic scenario rows with JSON** — Scenario step dynamically adds/removes term rows up to 5 per scenario. JavaScript serializes to JSON array string for database storage. This keeps DB schema simple (3 text columns for scenarios) while supporting variable-length renewal definitions.

5. **Home redirect to wizard** — Main entry point is wizard (not test page). Users land directly in the workflow. Simplifies navigation (no separate "start" page needed).

6. **Fields start blank** — No pre-filled defaults. User sees placeholder hints but must explicitly enter all values. This ensures user reviews and confirms all inputs (no accidental defaults).

## Self-Check: PASSED

All created files exist:
- FOUND: maple_return/templates/wizard.html
- FOUND: maple_return/templates/partials/step_property.html
- FOUND: maple_return/templates/partials/step_mortgage.html
- FOUND: maple_return/templates/partials/step_operating.html
- FOUND: maple_return/templates/partials/step_scenarios.html
- FOUND: maple_return/templates/partials/step_exit.html

All commits exist:
- FOUND: bf861db (Task 1: wizard page and step partials)
- FOUND: 803a301 (Bug fix: updated tests for redirect)

All tests pass: 155/155 ✓

Linter clean: No errors ✓

Server tested: Wizard loads at http://localhost:8001/wizard ✓

## Next Steps

With the wizard complete, ready for:
- **Plan 06-03**: Results dashboard (loads simulation data from `/api/simulate`, renders PnL tables, metrics, charts, scenario comparison)

The wizard provides a complete data entry flow with:
- ✓ All 25+ property input fields across 5 logical steps
- ✓ Inline validation with error messages
- ✓ Auto-save on every field change
- ✓ State restoration on page reload
- ✓ Dynamic scenario management
- ✓ Integration with backend API

User can now enter property data, save progress, return later, and run simulations. The `/api/simulate` endpoint is already functional (from plan 06-01). Next plan will build the results visualization layer.
