---
phase: 03-operating-model
plan: 01
subsystem: operating-engine
tags: [tdd, income-calculation, expense-calculation, escalation]

dependency_graph:
  requires:
    - "maple_return/models.py: Property dataclass"
    - "maple_return/mortgage.py: _add_months helper"
  provides:
    - "Operating income calculation with vacancy and escalation"
    - "Operating expense calculation with annual escalation"
    - "NOI (Net Operating Income) calculation"
    - "Monthly operating schedule generation"
  affects:
    - "Next plan (03-02) will integrate this with mortgage data"

tech_stack:
  added:
    - "OperatingInput dataclass: Input parameters for operating calculations"
    - "MonthlyOperating dataclass: Monthly operating statement structure"
  patterns:
    - "TDD red-green-refactor workflow"
    - "Decimal precision for all monetary calculations"
    - "Lease anniversary-based escalation timing"
    - "Compounding escalation (not simple interest)"

key_files:
  created:
    - path: "maple_return/operating.py"
      lines: 156
      purpose: "Operating income and expense calculation engine"
    - path: "tests/test_operating.py"
      lines: 153
      purpose: "12 test cases covering all operating model scenarios"
  modified: []

decisions:
  - decision: "Use lease anniversary for both rent and expense escalation timing"
    rationale: "Consistent timing model - both escalate on same anniversary date"
    alternatives: ["Calendar year for expenses", "Separate timing for each"]
    impact: "Simpler implementation, easier to test and understand"

  - decision: "Management fee calculated as % of gross rent (not effective rent)"
    rationale: "Matches locked requirement from 03-CONTEXT.md"
    alternatives: ["% of effective rent (after vacancy)"]
    impact: "Property manager earns on full rent potential, not actual collected"

  - decision: "Compounding escalation formula: base * (1 + rate)^years"
    rationale: "Standard financial compounding, accurate long-term projections"
    alternatives: ["Simple interest: base * (1 + rate * years)"]
    impact: "More accurate multi-year projections, standard practice"

metrics:
  duration_minutes: 2.75
  tasks_completed: 1
  tests_added: 12
  files_created: 2
  commits: 2
  completed_date: "2026-02-12"
---

# Phase 03 Plan 01: Operating Income and Expense Engine

**One-liner:** TDD implementation of rental income calculator with vacancy/escalation and expense calculator with annual inputs and compounding escalation on lease anniversary.

## What Was Built

Built the core operating model calculation engine that models:

1. **Rental Income:**
   - Base monthly rent with annual escalation
   - Vacancy rate applied evenly across all months
   - Escalation timing: lease anniversary date (not calendar year)
   - Compounding formula: base × (1 + rate)^years

2. **Operating Expenses:**
   - Four categories: property tax, insurance, maintenance, management fee
   - Annual inputs divided by 12 for monthly amounts
   - Property tax/insurance/maintenance escalate at single annual rate
   - Management fee is % of gross rent (scales with income)
   - All expenses escalate on lease anniversary (same as rent)

3. **Net Operating Income (NOI):**
   - Calculated as: effective_rent - total_expenses
   - Effective rent = gross_rent - vacancy_deduction

4. **Schedule Generation:**
   - `generate_operating_schedule()` produces multi-month projections
   - Uses `_add_months` helper from mortgage.py for date progression
   - Preserves day-of-month consistency across months

## Deviations from Plan

None - plan executed exactly as written.

All 12 test cases specified in the plan were implemented and pass. The implementation follows all locked decisions from 03-CONTEXT.md:
- Single unit property (one income stream)
- Vacancy applied evenly across all months
- Rent escalation on lease anniversary
- Expenses input as annual amounts
- Single escalation rate for all expense categories
- Property management fee as % of gross rent

## Key Technical Decisions

### 1. Escalation Timing Consistency
**Decision:** Use lease anniversary date for both rent and expense escalation.

**Context:** Plan left expense escalation timing to Claude's discretion (could be calendar year or lease anniversary).

**Rationale:** Using the same anniversary date for all escalations simplifies the model and makes it easier to reason about. Real-world property management often aligns expense increases with lease renewals.

**Implementation:** Both rent and expenses use the same `years_elapsed` calculation based on lease_start_date.

### 2. Compounding Escalation Formula
**Decision:** Use compounding formula: `base * (1 + rate)^years`

**Rationale:** Standard financial practice for multi-year projections. Simple interest (`base * (1 + rate * years)`) would underestimate long-term values.

**Impact:** More accurate projections over 5-30 year timeframes typical for real estate investments.

### 3. Management Fee Base
**Decision:** Calculate management fee as % of gross_rent, not effective_rent.

**Rationale:** Matches locked requirement from 03-CONTEXT.md: "Property management fee is % of gross rent (scales with income)."

**Impact:** Property manager earns fee based on rental potential, not actual collected rent. This is a common industry practice.

## Test Coverage

All 12 test cases pass:

1. `test_base_rent_no_escalation` - Verifies month 1 uses base rent
2. `test_vacancy_deduction` - Confirms 5% vacancy deducts correctly
3. `test_rent_escalation_on_anniversary` - Rent stays flat for 12 months, then escalates
4. `test_rent_escalation_compounding` - Verifies compounding after 2 years
5. `test_monthly_expenses_from_annual` - Annual amounts divided by 12
6. `test_expense_escalation` - Expenses escalate on anniversary
7. `test_management_fee_scales_with_gross_rent` - Fee is % of gross rent
8. `test_management_fee_increases_with_rent_escalation` - Fee grows with rent
9. `test_noi_calculation` - NOI = effective_rent - total_expenses
10. `test_generate_schedule_length` - Schedule produces correct number of months
11. `test_zero_vacancy_rate` - 0% vacancy means effective = gross
12. `test_zero_escalation_rates` - Flat rates produce flat projections

**Realistic test data:** $2,500/month rent, $4,000 property tax, $2,400 insurance, $1,200 maintenance, 10% management fee, 5% vacancy, 2% escalation rates.

## Integration Points

**Inputs Required:**
- `OperatingInput` dataclass with 9 fields (rent, vacancy, 3 expense categories, 2 escalation rates, dates)

**Outputs Provided:**
- `MonthlyOperating` dataclass with full income/expense breakdown
- `generate_operating_schedule()` for multi-month projections

**Dependencies:**
- Imports `_add_months` from `maple_return.mortgage` for date progression
- Uses standard library: `dataclasses`, `datetime`, `decimal`

**Next Plan Integration:**
Plan 03-02 will combine this operating schedule with mortgage payment schedule to produce net cash flow projections.

## Verification

1. All 12 operating tests pass
2. Full test suite passes (61 tests total)
3. Lint passes clean (no warnings or errors)
4. Decimal precision maintained throughout (2 decimal places)
5. All monetary values properly quantized with ROUND_HALF_UP

## Files Changed

**Created:**
- `maple_return/operating.py` (156 lines) - Operating calculation engine
- `tests/test_operating.py` (153 lines) - Test coverage

**Modified:** None

## Commits

1. `2711450` - test(03-01): add failing tests for operating model (RED phase)
2. `12b6fb1` - feat(03-01): implement operating income and expense engine (GREEN phase)

No refactor commit needed - implementation was clean and well-structured from the start.

## Self-Check: PASSED

**Files exist:**
```
FOUND: maple_return/operating.py
FOUND: tests/test_operating.py
```

**Commits exist:**
```
FOUND: 2711450
FOUND: 12b6fb1
```

**Tests pass:**
```
61 passed in 0.45s (includes 12 new operating tests)
```

**Lint clean:**
```
All checks passed!
```
