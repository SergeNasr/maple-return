---
phase: 05-exit-strategy
plan: 02
subsystem: total-return
tags: [total-return, hold-period-irr, simple-roi, cashflow-truncation, tdd]

dependency_graph:
  requires:
    - maple_return/exit_model.py (ExitInput, ExitResult, calculate_exit from 05-01)
    - maple_return/metrics.py (calculate_irr)
    - maple_return/cashflow.py (MonthlyCashFlow, convert_to_usd)
  provides:
    - TotalReturnSummary dataclass
    - calculate_total_return function
  affects:
    - Exit model module (extended with total return calculation)

tech_stack:
  added:
    - Total return calculation with hold-period IRR
    - Simple ROI and total profit metrics
  patterns:
    - TDD RED-GREEN cycle (no refactor needed)
    - Cash flow truncation at sale year boundary
    - IRR reuse with exit proceeds as terminal value
    - Decimal precision for all monetary calculations

key_files:
  created:
    - None (extended existing module)
  modified:
    - maple_return/exit_model.py (256 lines total, added 82 lines)
    - tests/test_exit_model.py (696 lines total, added 467 lines)

decisions:
  - Cash flows truncate at sale_year * 12 months (clean hold period per user decision)
  - Hold-period IRR uses net_proceeds as terminal value (replaces operations-only IRR per user decision)
  - Simple ROI = total_profit / down_payment (per user decision)
  - Total profit = cumulative_cashflow + net_proceeds - down_payment (per user decision)
  - Zero down payment edge case returns ROI = 0.0000 (avoid division by zero)
  - Sale year 0 returns zero months, zero cumulative, IRR = None

metrics:
  duration: 255 seconds (4m 15s)
  completed_date: 2026-02-15
  tasks_completed: 1
  tests_added: 8
  test_coverage: 100% (total return functions fully covered)
  commits: 2 (RED + GREEN, no refactor needed)
---

# Phase 5 Plan 2: Total Return Calculator Summary

**One-liner:** Total return calculator truncates cash flows at sale year, computes hold-period IRR with exit proceeds as terminal value, and calculates simple ROI and total profit metrics.

## What Was Built

Built the total return calculation engine that combines cumulative cash flows with exit proceeds to compute comprehensive investment return metrics. This is the "was this investment worth it" calculation that shows total profit, simple ROI, and hold-period IRR using the actual exit proceeds instead of estimated property value.

**Core Components:**

1. **TotalReturnSummary dataclass** — Complete return metrics:
   - hold_period_years, total_months — hold period dimensions
   - cumulative_net_cashflow — sum of all monthly net cash flows through sale year
   - net_proceeds — from exit waterfall (05-01)
   - total_profit, total_profit_usd — cumulative + net proceeds - down payment
   - simple_roi — total_profit / down_payment (4 decimal places)
   - hold_period_irr — annualized IRR with exit proceeds as terminal value
   - exit_result — nested full waterfall breakdown

2. **calculate_total_return function** — Pure function that:
   - Truncates cash flows at sale year boundary (sale_year * 12 months)
   - Calls calculate_exit to get net proceeds waterfall
   - Sums cumulative net cash flow from truncated months
   - Computes total profit: cumulative + net_proceeds - down_payment
   - Computes simple ROI: total_profit / down_payment
   - Converts total profit to USD
   - Computes hold-period IRR using existing calculate_irr with net_proceeds as terminal value
   - Returns comprehensive summary with nested exit result

3. **Edge case handling:**
   - Zero down payment → simple_roi = 0.0000 (avoid division by zero)
   - Sale year 0 → total_months = 0, cumulative = 0, IRR = None
   - Negative profit → ROI negative, all calculations work correctly
   - More cash flows than needed → truncates at sale year boundary

## Execution Notes

**TDD Approach:**

- **RED phase:** Created 8 comprehensive test cases covering basic scenarios, edge cases, truncation, IRR calculation, USD conversion, and nesting
  - Commit: c1959c1 — "test(05-02): add failing tests for total return with exit"
- **GREEN phase:** Implemented TotalReturnSummary and calculate_total_return, fixed lint errors (unused variables)
  - Commit: 9d7f945 — "feat(05-02): implement total return with hold-period IRR and ROI"
- **REFACTOR phase:** Not needed — code was clean on first pass

**Test Coverage (8 new tests):**

1. `test_total_return_basic` — 5-year hold, 60 months, positive cash flows, verify all fields
2. `test_total_return_irr_includes_exit` — IRR with exit differs from operations-only IRR
3. `test_total_return_cashflow_truncation` — 360 months available, sell year 5 → uses only 60
4. `test_total_return_negative_profit` — Underwater exit, negative total profit, negative ROI
5. `test_total_return_zero_down_payment` — Edge case: ROI = 0.0000
6. `test_total_return_sale_year_zero` — Immediate sale: 0 months, 0 cumulative, IRR = None
7. `test_total_return_usd_conversion` — Verify total_profit_usd correct
8. `test_total_return_exit_result_nested` — Verify exit_result contains full waterfall

**Manual Verification:**

- Cash flow truncation confirmed: 360 months input, year 5 sale → 60 months used ✓
- Total profit formula verified: $9,000 + $215,000 - $100,000 = $124,000 ✓
- Simple ROI verified: $124,000 / $100,000 = 1.2400 ✓
- Hold-period IRR computed: 0.1801 (18.01% annualized) ✓
- Exit result nesting verified: all waterfall fields accessible ✓

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Lint Error] Fixed unused start_date variables in tests**
- **Found during:** GREEN phase after implementation
- **Issue:** Test code had unused `start_date = date(...)` assignments in 8 test functions
- **Fix:** Removed all unused start_date variable assignments
- **Files modified:** tests/test_exit_model.py
- **Commit:** Included in GREEN commit 9d7f945

No other deviations — plan executed exactly as written.

## Verification Results

✅ `just test` — All 133 tests pass (125 existing + 8 new total return tests)
✅ `just lint` — No errors (clean code after fixing unused variables)
✅ Cash flow truncation verified: 360 months → 60 months for year 5 sale
✅ Total profit formula verified: cumulative + net_proceeds - down_payment
✅ Simple ROI formula verified: total_profit / down_payment
✅ Hold-period IRR verified: exists and is positive for profitable case
✅ Edge cases verified: zero down, year 0, negative profit all handled correctly

## Output Artifacts

**Modified Files:**
- `/Users/sergenasr/Workspace/maple-return/maple_return/exit_model.py` (256 lines, +82 new)
  - TotalReturnSummary dataclass
  - calculate_total_return function
  - Imports for MonthlyCashFlow and calculate_irr
- `/Users/sergenasr/Workspace/maple-return/tests/test_exit_model.py` (696 lines, +467 new)
  - 8 comprehensive total return tests
  - Lint fixes for unused variables

**Commits:**
- `c1959c1` — test(05-02): add failing tests for total return with exit (RED)
- `9d7f945` — feat(05-02): implement total return with hold-period IRR and ROI (GREEN)

## Integration Points

**Dependencies:**
- `maple_return.exit_model.calculate_exit` — Reused for net proceeds waterfall (05-01)
- `maple_return.metrics.calculate_irr` — Reused for hold-period IRR with exit proceeds as terminal value
- `maple_return.cashflow.MonthlyCashFlow` — Input cash flow data structure
- `maple_return.cashflow.convert_to_usd` — Reused for total_profit_usd conversion

**Provides to downstream:**
- TotalReturnSummary available for API/frontend integration
- calculate_total_return ready for scenario comparison (user reruns with different sale years)
- Hold-period IRR replaces operations-only IRR when exit is modeled (per user decision)

**Key Formula Implemented:**

```
Total Profit = Cumulative Net Cash Flow + Net Proceeds - Down Payment

Simple ROI = Total Profit / Down Payment

Hold-Period IRR = IRR(down_payment, truncated_cashflows, net_proceeds_terminal)
```

## Next Steps

Phase 5 complete (2/2 plans). Exit strategy module fully implemented with:
- Net proceeds waterfall (05-01)
- Total return with hold-period IRR (05-02)

Next phase (Phase 6) will integrate all components into user-facing features:
- Web API endpoints for analysis
- Frontend dashboard
- Scenario comparison tools
- Export/reporting capabilities

## Self-Check: PASSED

**Files verified:**
```
✓ maple_return/exit_model.py exists (256 lines)
✓ tests/test_exit_model.py exists (696 lines)
✓ TotalReturnSummary dataclass defined
✓ calculate_total_return function defined
```

**Commits verified:**
```
✓ c1959c1 exists (RED phase commit)
✓ 9d7f945 exists (GREEN phase commit)
```

**Tests verified:**
```
✓ All 133 tests passing
✓ 8 new total return tests included
✓ No test failures or skips
```

**Lint verified:**
```
✓ No lint errors
✓ No unused imports
✓ No unused variables
✓ Code follows project style
```

**Functionality verified:**
```
✓ Cash flow truncation works (360 → 60 months)
✓ Total profit formula correct
✓ Simple ROI formula correct
✓ Hold-period IRR calculated correctly
✓ Edge cases handled (zero down, year 0, negative profit)
✓ USD conversion works
✓ Exit result nested correctly
```
