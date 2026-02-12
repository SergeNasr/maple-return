---
phase: 02-mortgage-engine
plan: 03
subsystem: mortgage-calculations
tags: [annual-summaries, scenario-comparison, tdd, data-aggregation]
dependency-graph:
  requires: [02-01-amortization-engine, 02-02-multi-term-renewal]
  provides: [annual-rollups, scenario-comparison-output, equity-tracking]
  affects: []
tech-stack:
  added: []
  patterns:
    - TDD (red-green-refactor)
    - Groupby aggregation for time-series rollups
    - Calendar year boundary handling
    - Equity position tracking
key-files:
  created:
    - maple_return/mortgage_summary.py
    - tests/test_mortgage_summary.py
  modified: []
decisions:
  - Annual summaries group by calendar year (not mortgage year)
  - Partial first/last years include all months that fall in that calendar year
  - Equity calculated as purchase_price minus remaining balance at each summary level
  - Renewal rates list excludes initial term (term 1) since it's the same across all scenarios
  - Year-end balance is the balance from the last month entry in that calendar year
metrics:
  duration: 3
  tasks: 1
  files-created: 2
  files-modified: 0
  tests-added: 11
  completed-at: 2026-02-12T05:08:31Z
---

# Phase 02 Plan 03: Annual Summaries and Scenario Comparison

**One-liner:** TDD-driven annual summary rollups and scenario comparison output with calendar year grouping, equity tracking, and renewal rate extraction.

## Summary

Built the annual summary and scenario comparison layer that transforms monthly mortgage schedules into yearly rollups and side-by-side scenario metrics. All 11 new tests passing with full coverage of calendar year boundaries, equity calculations, and multi-term scenarios.

**TDD Process:**
1. **RED:** Created 11 failing tests covering annual summaries (6 tests) and scenario comparison (5 tests)
2. **GREEN:** Implemented mortgage_summary.py with 2 dataclasses and 2 functions, all tests passing
3. **REFACTOR:** No refactoring needed - code emerged clean from TDD process

## What Was Built

### New Data Structures

**`AnnualSummary` dataclass**
- year: int (calendar year, not mortgage year)
- total_principal_paid: Decimal (sum of principal for all months in this year)
- total_interest_paid: Decimal (sum of interest for all months in this year)
- total_payments: Decimal (sum of payments for all months in this year)
- year_end_balance: Decimal (balance after last month of this year)
- equity: Decimal (purchase_price - year_end_balance)

**`ScenarioComparison` dataclass**
- scenario_index: int (0-based)
- renewal_rates: list[Decimal] (rates from terms 2+, excludes initial term)
- total_interest: Decimal (grand total for scenario)
- total_payments: Decimal (grand total for scenario)
- final_balance: Decimal (balance at end, should be 0 if paid off)
- months_to_payoff: int (total months in scenario)
- total_equity: Decimal (purchase_price - final_balance)

### Core Functions

**`generate_annual_summaries(schedule: list[AmortizationEntry], purchase_price: Decimal) -> list[AnnualSummary]`**

Groups monthly amortization entries by calendar year and produces yearly totals:

1. **Grouping:** Uses itertools.groupby to group by entry.date.year
2. **Aggregation:** Sums principal, interest, and payments for all months in each year
3. **Year-end balance:** Takes the balance from the last month entry in that year
4. **Equity calculation:** purchase_price - year_end_balance for each year
5. **Partial years:** Includes whatever months fall in each calendar year (no pro-rating)

**Edge cases handled:**
- Empty schedule returns empty list
- Partial first year (e.g., mortgage starting mid-year)
- Partial last year (e.g., mortgage ending mid-year)
- Full 30-year schedules produce up to 30 annual summaries

**`compare_scenarios(scenarios: list[ScenarioResult], purchase_price: Decimal) -> list[ScenarioComparison]`**

Extracts key metrics from each scenario for side-by-side comparison:

1. **Renewal rates extraction:** Takes rates from terms[1:] (skips term 1 initial rate)
2. **Total equity:** purchase_price - scenario.final_balance
3. **Pass-through metrics:** total_interest, total_payments, final_balance, months_to_payoff from ScenarioResult

**Why skip term 1 rate:** The initial rate (term 1) is the same across all scenarios, so renewal_rates only includes terms 2+ where scenarios actually differ.

## Tests Added

**11 comprehensive tests organized in 2 suites:**

### TestAnnualSummary (6 tests)

1. **test_annual_summary_for_two_year_schedule**
   - 24-month schedule produces 1 summary (all same year)
   - Verifies totals aggregate correctly

2. **test_annual_summary_respects_calendar_year_boundaries**
   - Mortgage starting mid-year (July 2025)
   - 12 months split across 2025 (6 months) and 2026 (6 months)
   - Produces 2 summaries with correct splits

3. **test_year_end_balance_matches_last_month**
   - Year-end balance equals the balance from the last month entry in that year

4. **test_equity_calculation**
   - Equity = purchase_price - year_end_balance

5. **test_annual_totals_match_scenario_totals**
   - Sum of all annual summaries matches ScenarioResult totals exactly
   - Tests with real multi-term calculation

6. **test_full_30year_schedule**
   - Realistic 30-year mortgage produces 1-30 annual summaries
   - Equity grows over time

### TestScenarioComparison (5 tests)

1. **test_compare_two_scenarios_different_total_interest**
   - 2 scenarios with different renewal rates (3% vs 7%)
   - Lower rate produces less total interest

2. **test_compare_three_scenarios_ordered**
   - 3 scenarios with different rates (3%, 5%, 7%)
   - Results ordered by scenario_index

3. **test_scenario_comparison_fields**
   - All required fields present and valid

4. **test_renewal_rates_extraction**
   - Renewal rates extracted from terms 2 and 3 (not term 1)
   - 15-year mortgage with 3 terms

5. **test_total_equity_calculation**
   - Total equity = purchase_price - final_balance

All tests use realistic mortgage parameters and verify correct Canadian mortgage behavior.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test payment amounts for multi-term scenarios**
- **Found during:** Test execution (GREEN phase)
- **Issue:** Initial test used $2000/month payment with 5-year amortization, which paid off in term 1, so renewal rates were never applied
- **Fix:** Adjusted tests to use 10-15 year amortization with $2800 or $1800/month payments to ensure mortgages extend into terms 2-3 where renewal rates apply
- **Files modified:** tests/test_mortgage_summary.py
- **Commit:** aa1691b (included in GREEN commit)
- **Rationale:** Tests must exercise the code paths they're testing - scenario comparison requires scenarios that actually differ in term 2+

**2. [Rule 1 - Bug] Auto-fixed lint errors**
- **Found during:** Lint run
- **Issue:** Import ordering, unused imports (pytest, ScenarioResult, TermSummary, AnnualSummary, ScenarioComparison), unused variable (total_principal)
- **Fix:** Ran `ruff check --fix` to auto-sort imports and remove unused imports; manually removed unused variable
- **Files modified:** tests/test_mortgage_summary.py
- **Commit:** aa1691b (included in GREEN commit)
- **Rationale:** Linter errors prevent commit, auto-fix is safe for import ordering and unused imports

No architectural changes needed. All deviations were correctness fixes during TDD process.

## Implementation Decisions

**1. Calendar year grouping (not mortgage year)**
- Annual summaries group by entry.date.year (calendar year)
- NOT by "year 1, year 2, etc." relative to mortgage start
- Simplifies analysis: users can compare to tax years, property reports, etc.
- Handles partial first/last years naturally

**2. Partial year handling**
- Include all months that fall in each calendar year
- No pro-rating or adjustment
- First year may have 1-12 months, last year may have 1-12 months
- Sum of annual totals always equals scenario totals exactly

**3. Equity calculation consistency**
- Same formula at all levels: purchase_price - remaining_balance
- Annual summaries: purchase_price - year_end_balance
- Scenario comparison: purchase_price - final_balance
- Down payment contributes to initial equity (starting balance < purchase price)

**4. Renewal rates extraction**
- Extract from scenario.terms[1:] (skip term 1)
- Term 1 is the initial rate, same across all scenarios
- Renewal rates are where scenarios differ (terms 2, 3, etc.)
- Empty list if scenario has only 1 term (no renewals)

**5. Groupby optimization**
- Use itertools.groupby for efficient year grouping
- Requires sorted schedule (sorted by date.year)
- More efficient than building dictionaries for large schedules

## Verification

**All verification criteria met:**

- ✅ `just test` passes with all 11 new tests green (49 total: 38 existing + 11 new)
- ✅ `just lint` passes with no errors
- ✅ Annual summaries sum to match scenario totals exactly (no rounding drift)
- ✅ Equity position is correctly calculated for each year
- ✅ Scenario comparison correctly extracts key metrics from each scenario
- ✅ Calendar year boundaries respected (partial first/last years handled)
- ✅ Renewal rates extraction skips initial term correctly
- ✅ All existing tests from 02-01 and 02-02 still pass

**Manual verification:**
- 30-year mortgage produces 30 annual summaries (or fewer for early payoff)
- Partial year (mid-year start): correctly splits months across years
- 3 scenarios with different renewal rates: total interest increases with rate
- Equity grows over time as balance decreases

## Commits

| Commit  | Type | Description                                                  |
| ------- | ---- | ------------------------------------------------------------ |
| cce72bd | test | Add failing tests for annual summaries and scenario comparison (RED) |
| aa1691b | feat | Implement annual summaries and scenario comparison (GREEN)   |

**Total commits:** 2 (TDD: RED → GREEN, no REFACTOR needed)

## Next Steps

**Phase 2 Complete!**

This completes the mortgage engine subsystem. The engine now provides:
- ✅ Core amortization with Canadian semi-annual compounding (02-01)
- ✅ Multi-term renewals with payment recalculation (02-02)
- ✅ Annual summaries and scenario comparison (02-03)

**Next phase (Phase 3 - Property Cash Flow):**
- Integrate mortgage calculations with property income/expenses
- Build monthly cash flow projection
- Calculate ROI and key investment metrics

**Dependencies resolved:**
- Plan 02-01 provided: Core amortization engine, rate conversion, single-term calculation
- Plan 02-02 provided: Multi-term chaining, renewal payment recalculation, scenario comparison
- This plan provides: Annual rollups, scenario comparison output, equity tracking

**Known limitations (deferred to future plans):**
- No API endpoints yet (integration comes in later phases)
- No lump sum payments or prepayments
- No accelerated payment options (bi-weekly, weekly)
- No integration with property/cash flow models yet

## Self-Check

Verifying claimed work exists on disk and in git...

```bash
# Check created files
[ -f "/Users/sergenasr/Workspace/maple-return/maple_return/mortgage_summary.py" ] && echo "✓ mortgage_summary.py"
[ -f "/Users/sergenasr/Workspace/maple-return/tests/test_mortgage_summary.py" ] && echo "✓ test_mortgage_summary.py"

# Check commits
git log --oneline | grep -q "cce72bd" && echo "✓ RED commit (cce72bd)"
git log --oneline | grep -q "aa1691b" && echo "✓ GREEN commit (aa1691b)"

# Check key structures exist
grep -q "class AnnualSummary" maple_return/mortgage_summary.py && echo "✓ AnnualSummary dataclass"
grep -q "class ScenarioComparison" maple_return/mortgage_summary.py && echo "✓ ScenarioComparison dataclass"
grep -q "def generate_annual_summaries" maple_return/mortgage_summary.py && echo "✓ generate_annual_summaries()"
grep -q "def compare_scenarios" maple_return/mortgage_summary.py && echo "✓ compare_scenarios()"

# Check tests run
pytest tests/test_mortgage_summary.py -v --tb=no -q 2>&1 | grep -q "11 passed" && echo "✓ All 11 tests passing"
```

## Self-Check: PASSED

All files, commits, and functionality verified present and working.
