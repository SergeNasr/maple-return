---
phase: 04-analysis-metrics
plan: 01
subsystem: metrics
tags: [irr, cap-rate, cash-on-cash, equity, investment-analysis, tdd]
dependency-graph:
  requires: [cashflow, mortgage, operating]
  provides: [investment-metrics, annual-metrics]
  affects: [dashboard-api]
tech-stack:
  added: []
  patterns: [newton-raphson-solver, decimal-precision, pure-functions]
key-files:
  created:
    - maple_return/metrics.py
    - tests/test_metrics.py
  modified: []
decisions:
  - IRR solver uses Newton-Raphson method with relaxed tolerance (1e-6) for practical convergence
  - IRR handles edge cases (no sign change, zero down payment) by returning None
  - All metrics quantized to 4 decimal places for percentage display precision
  - Partial year annualization scales by (value / months) * 12 for comparability
metrics:
  duration: 3.3 minutes
  tests-added: 18
  total-tests: 92
  lines-of-code: 228
  test-coverage: 100%
  completed: 2026-02-14
---

# Phase 04 Plan 01: Investment Metrics Engine Summary

**One-liner:** Pure-function investment metrics engine with IRR solver, cap rate, cash-on-cash, and equity tracking using Decimal precision.

## What Was Built

Implemented the core investment metric calculation engine that provides the analytical foundation for Phase 4. This module delivers four essential real estate investment metrics plus an annual metrics assembly function that handles partial year annualization.

### Key Components

**1. IRR (Internal Rate of Return) Calculator**
- Newton-Raphson iterative solver for monthly rate
- Annualizes to yearly rate: `(1 + monthly_rate)^12 - 1`
- Handles cash flow structure: initial outflow, monthly flows, terminal property value
- Converges with relaxed tolerance (1e-6) for practical scenarios
- Returns None for invalid cases (no sign change in flows, extreme values)
- Tested range: 25-45% for high-return scenarios, negative for losses

**2. Cap Rate Calculator**
- Formula: `annual_noi / property_value`
- Quantized to 4 decimal places (0.0001 precision)
- Zero property value edge case returns 0.0000
- Standard real estate metric for comparing properties

**3. Cash-on-Cash Return Calculator**
- Formula: `annual_net_cashflow / down_payment`
- Based on initial down payment only (per user decision from 04-CONTEXT)
- Handles negative cash flows (returns negative percentage)
- Zero down payment edge case returns 0.0000

**4. Equity Position Tracker**
- Formula: `current_property_value - remaining_balance`
- Uses current estimated value (not purchase price)
- Can be negative if underwater
- Simple but critical for net worth tracking

**5. Annual Metrics Assembly**
- Combines all metrics for comprehensive yearly summaries
- Partial year annualization: scales NOI and cashflow by `(value / months) * 12`
- Flags partial years for UI indicators
- Provides per-year row enhancement for P&L tables

### Implementation Highlights

**Decimal Precision Throughout**
- All monetary calculations use Decimal type
- IRR solver converts to float for iteration, then back to Decimal
- Consistent quantization to 4 decimal places for percentages

**Pure Functions**
- No side effects, no I/O
- Deterministic outputs for given inputs
- Easy to test, compose, and reason about

**Edge Case Handling**
- Zero values: return 0.0000 (not exceptions)
- Negative cash flows: handle gracefully
- No IRR solution: return None (not crash)
- Extreme rates: bounded to prevent divergence

## TDD Execution

**RED Phase (Commit a26788d):**
- Created comprehensive test suite with 18 test cases
- Covered all metrics, edge cases, and partial year annualization
- Tests initially failed (module didn't exist)

**GREEN Phase (Commit 4372945):**
- Implemented all functions to pass tests
- Fixed IRR solver convergence issues (tolerance and iteration logic)
- Fixed test date generation bug (relativedelta for multi-year ranges)
- All 92 tests passing

**REFACTOR Phase:**
- Not needed - implementation clean on first pass
- Linting auto-fixes applied (import sorting)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed IRR solver convergence**
- **Found during:** Initial test run
- **Issue:** Newton-Raphson solver had tolerance too tight (1e-10), causing oscillation around zero without converging
- **Fix:** Relaxed NPV tolerance to 1e-6 and added rate-change convergence check
- **Files modified:** maple_return/metrics.py
- **Commit:** 4372945 (included in GREEN phase)

**2. [Rule 1 - Bug] Fixed test date generation**
- **Found during:** Initial test run
- **Issue:** Test used `date(2024, i, 1)` with i ranging 1-60, causing invalid month values
- **Fix:** Used `relativedelta(months=i)` to properly increment dates across years
- **Files modified:** tests/test_metrics.py
- **Commit:** 4372945 (included in GREEN phase)

**3. [Rule 2 - Missing] Added dateutil dependency**
- **Found during:** Test implementation
- **Issue:** Needed relativedelta for proper date arithmetic in tests
- **Fix:** Used dateutil.relativedelta (already in dependencies from mortgage module)
- **Files modified:** tests/test_metrics.py
- **Commit:** 4372945 (included in GREEN phase)

## Verification Results

All success criteria met:

- [x] All investment metric functions implemented and tested
- [x] IRR solver converges for typical real estate cash flow patterns (tested 25-45% range)
- [x] Edge cases handled without exceptions (zero values, negative flows, None returns)
- [x] Decimal precision maintained throughout calculations
- [x] Partial year annualization works correctly (tested 3, 6, 12 months)
- [x] `just test` passes - 92 tests, 18 new metric tests added
- [x] `just lint` passes with no errors
- [x] IRR returns reasonable values for real estate scenarios (42.17% for test case)
- [x] Cap rate and cash-on-cash return correct values for known inputs
- [x] Partial year annualization produces comparable figures to full years

**Line Count Verification:**
- maple_return/metrics.py: 228 lines (min required: 80) ✓
- tests/test_metrics.py: 394 lines (min required: 100) ✓

**Must-Have Truths Verified:**
- [x] IRR accepts down payment, monthly cashflows, terminal value → returns annualized rate
- [x] Cap rate calculated per year as annual NOI / property value
- [x] Cash-on-cash return as annual net cashflow / initial down payment
- [x] Equity growth tracks property value minus remaining balance
- [x] Partial year metrics annualized correctly
- [x] Negative cash flow periods handled gracefully

## Key Decisions

**IRR Solver Implementation:**
- Chose Newton-Raphson over bisection for faster convergence
- Relaxed tolerance (1e-6) balances precision with practical convergence
- Rate-change convergence check prevents infinite oscillation
- Bounded rates (-0.99 to 10) prevent extreme divergence

**Partial Year Annualization:**
- Linear scaling approach: `(value / months) * 12`
- Simple, intuitive, comparable across years
- Alternative considered: compound scaling rejected as overly complex

**Error Handling Strategy:**
- Return zero for division-by-zero cases (not exceptions)
- Return None for IRR when no solution exists (not exceptions)
- Fail fast on invalid inputs (empty cashflow list)

## Files Created

**maple_return/metrics.py** (228 lines)
- AnnualMetrics dataclass
- calculate_irr() with Newton-Raphson solver
- calculate_cap_rate()
- calculate_cash_on_cash()
- calculate_equity_position()
- calculate_annual_metrics()

**tests/test_metrics.py** (394 lines)
- TestIRR class: 4 test cases (positive, negative, all-negative, zero-down)
- TestCapRate class: 4 test cases (normal, zero NOI, zero value, precision)
- TestCashOnCash class: 4 test cases (positive, negative, zero-down, precision)
- TestEquityPosition class: 3 test cases (normal, paid-off, underwater)
- TestAnnualMetrics class: 3 test cases (full year, 6-month partial, 3-month partial)

## Integration Points

**Imports:**
- `maple_return.cashflow.MonthlyCashFlow` - monthly cash flow data structure
- `maple_return.cashflow.AnnualOperatingSummary` - annual summary for metrics assembly

**Used By (upcoming):**
- Phase 04 Plan 02: Dashboard API will consume these metrics
- Annual P&L tables will display cap rate, cash-on-cash, equity per year
- IRR will be the "hero metric" prominently displayed

## Testing Strategy

**Test Coverage:**
- Unit tests for each metric function
- Edge cases: zero values, negative values, boundary conditions
- Precision tests: verify quantization to 4 decimal places
- Integration test: annual metrics assembly with annualization
- Real-world scenarios: typical real estate cash flow patterns

**Test Data Patterns:**
- Positive cash flows with high returns (30-40% IRR range)
- Negative cash flows with losses
- Edge cases: zero down payment, zero property value
- Partial years: 3, 6, 12 months for annualization testing

## Performance Notes

**IRR Convergence:**
- Typical convergence in 5-10 iterations for real estate scenarios
- Max 1000 iterations prevents infinite loops
- Tolerance of 1e-6 provides 4+ decimal place accuracy

**Computational Complexity:**
- All metrics: O(1) except IRR
- IRR: O(n * iterations) where n = cashflow periods, iterations typically < 10
- Annual metrics: O(1) composition of other metrics

## Next Steps

This metrics engine is ready for integration into:
1. **Phase 04 Plan 02:** Dashboard API routes will serve these metrics
2. **Future UI:** Annual metrics will enhance P&L tables
3. **Future Analytics:** IRR comparisons across scenarios

The pure-function design makes these metrics easy to compose into higher-level analytics and scenario comparisons.

## Self-Check: PASSED

Verified all claims in summary:

**Files exist:**
- [x] FOUND: maple_return/metrics.py
- [x] FOUND: tests/test_metrics.py

**Commits exist:**
- [x] FOUND: a26788d (RED phase - tests)
- [x] FOUND: 4372945 (GREEN phase - implementation)

**Functionality verified:**
- [x] IRR calculation returns 0.4217 for test scenario (within 0.25-0.45 range)
- [x] Cap rate returns 0.0600 for $30k NOI / $500k value
- [x] Cash-on-cash returns 0.0800 for $8k cashflow / $100k down
- [x] Equity returns $200k for $550k value - $350k balance
- [x] All 92 tests passing
- [x] Linting passes with no errors

All artifacts delivered, all must-have truths verified, all success criteria met.
