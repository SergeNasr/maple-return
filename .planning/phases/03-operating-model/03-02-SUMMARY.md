---
phase: 03-operating-model
plan: 02
subsystem: cashflow-integration
tags: [tdd, cash-flow, fx-conversion, integration]

dependency_graph:
  requires:
    - "maple_return/operating.py: calculate_monthly_operating, OperatingInput, MonthlyOperating"
    - "maple_return/mortgage.py: AmortizationEntry, calculate_multi_term"
  provides:
    - "Complete monthly cash flow projections (CAD + USD)"
    - "FX conversion from CAD to USD"
    - "Annual operating summaries by calendar year"
    - "Integration layer between operating model and mortgage engine"
  affects:
    - "Phase 4 will use these cash flows for ROI metrics"
    - "Phase 5 will use annual summaries for scenario analysis"

tech_stack:
  added:
    - "MonthlyCashFlow dataclass: Complete monthly cash flow statement"
    - "AnnualOperatingSummary dataclass: Calendar year aggregation"
  patterns:
    - "TDD red-green workflow (no refactor needed)"
    - "Decimal precision for all monetary calculations"
    - "FX conversion: CAD / (CAD per USD) = USD"
    - "Pipeline pattern: operating -> mortgage -> net cash flow"

key_files:
  created:
    - path: "maple_return/cashflow.py"
      lines: 212
      purpose: "Cash flow integration and FX conversion engine"
    - path: "tests/test_cashflow.py"
      lines: 446
      purpose: "13 test cases covering cash flow pipeline and FX"
  modified: []

decisions:
  - decision: "FX conversion divides CAD by CAD-per-USD rate"
    rationale: "Locked decision from 03-CONTEXT.md - standard FX formula"
    alternatives: ["Multiply by USD-per-CAD rate"]
    impact: "Straightforward conversion, matches financial conventions"

  - decision: "Use itertools.groupby for annual summaries"
    rationale: "Efficient grouping by year, handles partial years naturally"
    alternatives: ["Manual dictionary grouping", "pandas groupby"]
    impact: "Clean, efficient, standard library only"

  - decision: "USD amounts only in summaries (not all line items)"
    rationale: "Locked decision from 03-CONTEXT.md - USD in summary/rollup views only"
    alternatives: ["USD for every line item"]
    impact: "Simplified data model, focused on high-level metrics"

metrics:
  duration_minutes: 2.9
  tasks_completed: 1
  tests_added: 13
  files_created: 2
  commits: 2
  completed_date: "2026-02-12"
---

# Phase 03 Plan 02: Cash Flow Integration and FX Conversion

**One-liner:** TDD integration layer combining operating model with mortgage schedule, producing complete monthly and annual cash flow projections with CAD and USD amounts via FX conversion.

## What Was Built

Built the cash flow integration layer that combines Phase 3 Plan 01 (operating model) with Phase 2 (mortgage engine) to produce complete financial projections:

1. **Cash Flow Pipeline:**
   - Gross rent → vacancy deduction → effective rent
   - Effective rent → operating expenses → NOI
   - NOI → mortgage payment → net cash flow
   - All components tracked monthly with full detail

2. **FX Conversion:**
   - `convert_to_usd()` function: CAD / (CAD per USD) = USD
   - Handles zero rate gracefully (returns $0.00)
   - Quantizes to 2 decimal places with ROUND_HALF_UP
   - Applied to NOI and net cash flow for summary metrics

3. **Monthly Cash Flow Projections:**
   - `generate_monthly_cashflows()` combines operating + mortgage
   - Length matches mortgage schedule (handles early payoff)
   - 15 fields per month: income, expenses, mortgage, cash flow (CAD + USD)
   - Each entry provides complete financial picture for that month

4. **Annual Operating Summaries:**
   - `generate_annual_operating_summaries()` groups by calendar year
   - Sums all monetary fields within each year
   - Handles partial first/last years naturally
   - Uses itertools.groupby for efficient grouping
   - Includes both CAD and USD totals

## Deviations from Plan

None - plan executed exactly as written.

All 13 test cases specified in the plan were implemented and pass:
1. `test_convert_to_usd_basic` - Basic FX conversion
2. `test_convert_to_usd_rounding` - Decimal precision
3. `test_convert_to_usd_zero_rate` - Edge case handling
4. `test_monthly_cashflow_structure` - All fields populated
5. `test_cashflow_pipeline_gross_to_net` - Full pipeline verification
6. `test_net_cashflow_is_noi_minus_mortgage` - Formula verification
7. `test_usd_amounts_present` - FX conversion in output
8. `test_cashflow_length_matches_mortgage` - Length consistency
9. `test_annual_summary_groups_by_calendar_year` - Year grouping
10. `test_annual_summary_totals_match_monthly` - Aggregation accuracy
11. `test_annual_summary_includes_usd` - USD in annual summaries
12. `test_positive_cashflow_scenario` - Positive cash flow case
13. `test_negative_cashflow_scenario` - Negative cash flow case

## Key Technical Decisions

### 1. FX Conversion Formula
**Decision:** Divide CAD by CAD-per-USD rate to get USD.

**Context:** Locked decision from 03-CONTEXT.md specifying FX conversion approach.

**Rationale:** Standard financial formula. Example: $1,350 CAD / 1.35 = $1,000 USD.

**Implementation:** `convert_to_usd(cad_amount, cad_per_usd)` with zero-rate handling.

### 2. USD Amounts Placement
**Decision:** Include USD amounts only for NOI and net cash flow (summary metrics).

**Context:** Locked decision from 03-CONTEXT.md: "USD amounts appear in summary/rollup views."

**Rationale:** Keeps data model focused on high-level decision-making metrics. CAD remains the primary currency for detailed line items.

**Impact:** Simplified dataclass, reduced redundancy, focused on what matters for investment decisions.

### 3. Annual Grouping Strategy
**Decision:** Use `itertools.groupby` for calendar year aggregation.

**Rationale:** Efficient, handles partial years naturally, standard library only (no pandas dependency).

**Implementation:** Sort by date first, then group by year key function, sum all fields per group.

## Test Coverage

All 13 test cases pass with realistic data:
- $2,500/month rent
- 5% vacancy rate
- $4,000 annual property tax
- $2,400 annual insurance
- $1,200 annual maintenance
- 10% management fee
- 1.35 CAD/USD exchange rate
- ~$2,100/month mortgage payment (5% on $400k)

**Test categories:**
- FX conversion (3 tests): basic, rounding, edge cases
- Pipeline structure (5 tests): field population, formula verification, length consistency
- Annual summaries (3 tests): grouping, totals, USD inclusion
- Scenarios (2 tests): positive and negative cash flow cases

## Integration Points

**Inputs Required:**
- `OperatingInput` from maple_return.operating
- `list[AmortizationEntry]` from mortgage schedule (calculate_multi_term)
- `cad_per_usd: Decimal` (FX rate parameter)

**Outputs Provided:**
- `MonthlyCashFlow` dataclass: 15 fields with full monthly breakdown
- `AnnualOperatingSummary` dataclass: 12 fields with yearly totals
- `convert_to_usd()` utility function (reusable)

**Dependencies:**
- Imports `calculate_monthly_operating` from `maple_return.operating`
- Imports `AmortizationEntry` from `maple_return.mortgage`
- Uses standard library: `itertools`, `dataclasses`, `datetime`, `decimal`

**Next Phase Integration:**
Phase 4 (ROI metrics) will use these cash flows to calculate:
- Cash-on-cash return
- Annualized ROI
- Cap rate
- Return metrics over time

## Verification

1. All 13 new tests pass
2. Full test suite passes (74 tests total: 61 existing + 13 new)
3. Lint passes clean (no warnings or errors)
4. Cash flow pipeline verified: gross → vacancy → effective → expenses → NOI → mortgage → net
5. FX conversion produces correct USD amounts
6. Annual summaries correctly group by calendar year
7. Integration with both operating.py and mortgage.py works correctly

## Files Changed

**Created:**
- `maple_return/cashflow.py` (212 lines) - Cash flow integration engine
- `tests/test_cashflow.py` (446 lines) - Complete test coverage

**Modified:** None

## Commits

1. `e67c77b` - test(03-02): add failing tests for cash flow integration and FX conversion (RED phase)
2. `7c08fa2` - feat(03-02): implement cash flow integration and FX conversion (GREEN phase)

No refactor commit needed - implementation was clean and well-structured from the start.

## Self-Check: PASSED

**Files exist:**
```
FOUND: maple_return/cashflow.py
FOUND: tests/test_cashflow.py
```

**Commits exist:**
```
FOUND: e67c77b
FOUND: 7c08fa2
```

**Tests pass:**
```
74 passed in 0.47s (includes 13 new cash flow tests)
```

**Lint clean:**
```
All checks passed!
```

**Must-haves verified:**
- ✓ Monthly cash flow combines operating income/expenses with mortgage payment
- ✓ Cash flow pipeline: gross rent → vacancy-adjusted rent → expenses → NOI → mortgage payment → net cash flow
- ✓ FX conversion divides CAD amounts by CAD-per-USD rate to get USD
- ✓ USD amounts appear in monthly and annual summary totals
- ✓ Annual operating summaries aggregate monthly data by calendar year
- ✓ `maple_return/cashflow.py` provides all required functions
- ✓ Imports from `maple_return.operating` and `maple_return.mortgage` work correctly
- ✓ `tests/test_cashflow.py` has 446 lines (exceeds min_lines: 80)
