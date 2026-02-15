---
phase: 05-exit-strategy
plan: 01
subsystem: exit-model
tags: [exit, proceeds, waterfall, appreciation, tdd]

dependency_graph:
  requires:
    - maple_return/cashflow.py (convert_to_usd)
  provides:
    - ExitInput dataclass
    - ExitResult dataclass
    - calculate_exit function
    - calculate_appreciation_rate function
  affects:
    - None (foundation for 05-02)

tech_stack:
  added:
    - Exit model engine with waterfall breakdown
  patterns:
    - TDD RED-GREEN-REFACTOR cycle
    - Decimal for monetary precision
    - Dataclasses for data models
    - Pure functions for calculations

key_files:
  created:
    - maple_return/exit_model.py (148 lines)
    - tests/test_exit_model.py (229 lines)
  modified:
    - None

decisions:
  - Use single commission rate (not buyer/seller split) for simplicity
  - Pass-through closing costs as flat amount (not itemized)
  - No mortgage discharge penalty per user decision
  - Appreciation rate is informational only (not used for total return yet)
  - USD conversions for sale_price and net_proceeds only (not all intermediate values)

metrics:
  duration: 133 seconds (2m 13s)
  completed_date: 2026-02-15
  tasks_completed: 1
  tests_added: 9
  test_coverage: 100% (exit_model.py fully covered)
  commits: 2 (RED + GREEN, no refactor needed)
---

# Phase 5 Plan 1: Exit Model Summary

**One-liner:** Exit model calculates net proceeds waterfall (sale → commission → closing → mortgage → net) with annualized appreciation rate using CAGR formula.

## What Was Built

Built the exit model engine that calculates net proceeds from a property sale with complete waterfall breakdown. The model shows exactly where sale money flows: commission to realtor, closing costs to lawyers/title company, mortgage payoff to lender, and what's left as net proceeds to the owner.

**Core Components:**

1. **ExitInput dataclass** — Captures all sale parameters:
   - sale_price, sale_year, commission_rate, closing_costs
   - remaining_mortgage_balance (from amortization schedule)
   - purchase_price, down_payment (for context/calculations)
   - cad_per_usd (for USD conversions)

2. **ExitResult dataclass** — Provides waterfall breakdown:
   - sale_price → commission → closing_costs → mortgage_payoff → net_proceeds
   - USD conversions for sale_price and net_proceeds
   - implied_appreciation_rate (annualized CAGR)

3. **calculate_exit** — Pure function that:
   - Computes commission (sale_price * commission_rate)
   - Calculates net proceeds (sale - commission - closing - mortgage)
   - Handles negative net proceeds (underwater scenario)
   - Converts key amounts to USD via existing convert_to_usd
   - Computes appreciation rate

4. **calculate_appreciation_rate** — Pure function that:
   - Computes annualized CAGR: (sale/purchase)^(1/years) - 1
   - Handles edge cases: zero years → 0.0000, zero purchase → 0.0000
   - Quantizes to 4 decimal places for percentage display
   - Works for both appreciation (positive) and depreciation (negative)

## Execution Notes

**TDD Approach:**

- **RED phase:** Created comprehensive test suite (9 tests) covering waterfall arithmetic, edge cases, USD conversion, appreciation rate formulas
- **GREEN phase:** Implemented exit_model.py with ExitInput/ExitResult dataclasses and calculation functions
- **REFACTOR phase:** Not needed — code was clean on first pass

**Test Coverage:**

1. Basic waterfall: $600k sale → $30k commission → $5k closing → $350k mortgage → $215k net
2. Negative net proceeds: Underwater scenario ($300k sale, $350k mortgage remaining)
3. Zero commission: Private sale edge case
4. USD conversion: Verified convert_to_usd integration
5. Appreciation rate basic: 5-year hold, 3.71% annualized growth
6. Appreciation rate zero years: Returns 0.0000
7. Appreciation rate zero purchase: Returns 0.0000 (avoid division by zero)
8. Depreciation: Negative rate when sale < purchase (-7.17% annualized)
9. Full field validation: All ExitResult fields populated with correct types

**Manual Verification:**

- Waterfall arithmetic confirmed: 600k - 30k - 5k - 350k = 215k ✓
- Negative proceeds handled correctly: -$70k ✓
- Appreciation rate ~0.0371 (3.71%) for 20% growth over 5 years ✓
- Edge cases: zero years, zero purchase price → 0.0000 ✓

## Deviations from Plan

None — plan executed exactly as written. All test cases from plan implemented and passing.

## Verification Results

✅ `just test` — All 125 tests pass (116 existing + 9 new exit model tests)
✅ `just lint` — No errors (clean code, no unused imports)
✅ Waterfall arithmetic verified manually
✅ Appreciation rate formula verified against known values
✅ USD conversion uses existing convert_to_usd (not reimplemented)

## Output Artifacts

**Created Files:**
- `/Users/sergenasr/Workspace/maple-return/maple_return/exit_model.py` (148 lines)
  - ExitInput, ExitResult dataclasses
  - calculate_exit, calculate_appreciation_rate functions
- `/Users/sergenasr/Workspace/maple-return/tests/test_exit_model.py` (229 lines)
  - 9 comprehensive tests covering all scenarios

**Commits:**
- `fa3ead9` — test(05-01): add failing tests for exit model and net proceeds (RED)
- `b0d0a2d` — feat(05-01): implement exit model with waterfall and appreciation rate (GREEN)

## Integration Points

**Dependencies:**
- `maple_return.cashflow.convert_to_usd` — Reused for USD conversions
- Follows Decimal patterns from metrics.py (quantization to 4 decimal places)
- Follows dataclass patterns from models.py

**Provides to downstream:**
- ExitInput/ExitResult available for 05-02 (total return calculation)
- calculate_exit ready for integration with frontend/API
- Waterfall breakdown ready for visualization

## Next Steps

Plan 05-02 will build total return calculation that combines:
- Exit model net proceeds (this plan)
- Cumulative cash flows from operating + mortgage schedules
- Initial down payment
- To compute: total equity gain, total ROI, annualized ROI, IRR with exit

## Self-Check: PASSED

**Files verified:**
```
✓ maple_return/exit_model.py exists (148 lines)
✓ tests/test_exit_model.py exists (229 lines)
```

**Commits verified:**
```
✓ fa3ead9 exists (RED phase commit)
✓ b0d0a2d exists (GREEN phase commit)
```

**Tests verified:**
```
✓ All 125 tests passing
✓ 9 new exit model tests included
✓ No test failures or skips
```

**Lint verified:**
```
✓ No lint errors
✓ No unused imports
✓ Code follows project style
```
