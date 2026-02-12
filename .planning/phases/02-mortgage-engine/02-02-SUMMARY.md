---
phase: 02-mortgage-engine
plan: 02
subsystem: mortgage-calculations
tags: [multi-term, renewals, scenario-comparison, tdd]
dependency-graph:
  requires: [02-01-amortization-engine]
  provides: [multi-term-calculation, scenario-comparison, renewal-logic]
  affects: []
tech-stack:
  added: []
  patterns:
    - TDD (red-green-refactor)
    - Multi-term mortgage modeling
    - Rate scenario comparison
    - Payment recalculation at renewals
key-files:
  created:
    - tests/test_mortgage_scenarios.py
  modified:
    - maple_return/mortgage.py
    - tests/test_mortgage.py
decisions:
  - Empty renewal_scenarios means single-term only (no automatic continuation)
  - Payment recalculation at renewals spreads remaining balance over remaining amortization
  - Last renewal rate repeats for all subsequent terms when scenario list is shorter
  - Terms truncate at 60 months unless mortgage pays off earlier within the term
metrics:
  duration: 4
  tasks: 2
  files-created: 1
  files-modified: 2
  tests-added: 10
  completed-at: 2026-02-12T05:01:23Z
---

# Phase 02 Plan 02: Multi-Term Renewal and Scenario Comparison

**One-liner:** TDD-driven multi-term mortgage engine with 5-year renewal boundaries, payment recalculation at renewals, and 1-3 scenario comparison for different rate assumptions.

## Summary

Built the multi-term mortgage calculation engine that chains single-term calculations across 5-year renewal boundaries, recalculates payments at each renewal based on remaining balance and new rates, and supports comparing up to 3 different renewal rate scenarios. All 10 new tests passing with full coverage of term boundaries, payment recalculation, early payoff, and rate repetition logic.

**TDD Process:**
1. **RED:** Created 10 failing tests covering multi-term renewals, scenario comparison, and edge cases
2. **GREEN:** Implemented calculate_multi_term() with all 4 new dataclasses and full renewal logic
3. **REFACTOR:** No refactoring needed - code emerged clean from TDD process

## What Was Built

### New Data Structures

**`TermDefinition` dataclass**
- rate: Decimal (nominal annual rate for the term)
- rate_type: str ("variable" or "fixed", metadata only)
- Defines rate parameters for one 5-year term in renewal scenarios

**`MortgageInput` dataclass**
- purchase_price, down_payment, annual_rate, monthly_payment, amortization_years
- start_date, rate_type
- renewal_scenarios: list[list[TermDefinition]] (1-3 scenarios)
- Complete input specification for multi-term calculations

**`TermSummary` dataclass**
- term_number, rate, rate_type, monthly_payment
- start_balance, end_balance, total_principal, total_interest, months
- Aggregated statistics for a single 5-year term

**`ScenarioResult` dataclass**
- scenario_index (0-based)
- schedule: list[AmortizationEntry] (full monthly schedule)
- terms: list[TermSummary] (per-term summaries)
- total_interest, total_payments, final_balance, months_to_payoff
- Complete results for one renewal rate scenario

### Core Function

**`calculate_multi_term(input_data: MortgageInput) -> list[ScenarioResult]`**

Multi-term mortgage calculation with renewal rate scenarios:

1. **For each renewal scenario:**
   - Term 1: Use user-specified payment and initial rate, generate up to 60 months
   - Terms 2+: For each renewal boundary at 60-month intervals:
     - Take remaining balance from previous term
     - Calculate remaining amortization months
     - Apply new renewal rate (or repeat last if list is shorter)
     - Recalculate payment using calculate_standard_payment()
     - Generate term schedule, truncate to 60 months
   - Continue until balance = 0 or amortization period exhausted

2. **Handles edge cases:**
   - Empty renewal_scenarios: runs single term only, no automatic continuation
   - Early payoff within term: stops when balance reaches zero
   - Short scenario lists: repeats last renewal rate for subsequent terms
   - Full 30-year (6-term) mortgages: correctly chains all terms

3. **Returns:** List of ScenarioResult objects (1 per scenario)

### Term Renewal Mechanics

**Payment Recalculation:**
- Initial term (Term 1): uses user-specified payment
- Renewal terms (Term 2+): payment = calculate_standard_payment(remaining_balance, new_monthly_rate, remaining_months)
- This spreads the remaining balance over the remaining amortization period at the new rate

**Term Boundaries:**
- All terms are exactly 60 months (5 years), except:
  - Last term may be shorter if fewer than 60 months remain
  - Term ends early if mortgage pays off within the term
- Month numbers are continuous across terms (1-360 for full 30-year)
- Term 1 = months 1-60, Term 2 = 61-120, etc.

**Rate Repetition:**
- If renewal_scenarios[i] has only 2 TermDefinitions but mortgage needs 5 renewals (6 terms total)
- The last TermDefinition rate repeats for terms 4, 5, and 6
- Example: [Term2_rate, Term3_rate] → Term4+ all use Term3_rate

## Tests Added

**10 comprehensive tests organized in 4 suites:**

1. **TestMultiTermRenewal (4 tests)**
   - Single term with no renewals (stops after 60 months)
   - Two terms with same rate (payment stays constant across renewal)
   - Two terms with different rate (payment recalculates higher with higher rate)
   - Term boundaries align at 60-month intervals

2. **TestScenarioComparison (2 tests)**
   - Three scenarios with different renewal rates produce different total interest
   - Early payoff when payment is high enough to clear balance within term

3. **TestRenewalRateRepetition (2 tests)**
   - Last rate repeats for subsequent terms when list is shorter
   - Full 30-year (6-term) mortgage with rate repetition

4. **TestScenarioResultStructure (2 tests)**
   - TermSummary totals match schedule entries for the term
   - ScenarioResult totals aggregate all terms correctly

All tests use realistic mortgage parameters and verify correct Canadian mortgage behavior across multiple terms.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test payment calculation for early payoff scenario**
- **Found during:** Test execution (GREEN phase)
- **Issue:** Test used $6000/month which paid off most of balance in term 1, but payment recalculation at term 2 dropped it to $12/month, dragging out to 360 months (correct behavior per spec, but test expectation was wrong)
- **Fix:** Updated test to calculate 60-month standard payment and add $200 extra to ensure full payoff within first term (< 60 months)
- **Files modified:** tests/test_mortgage_scenarios.py
- **Commit:** c0ea5ba (included in GREEN commit)
- **Rationale:** Specification says payments recalculate at renewals, so initial high payment doesn't carry forward

**2. [Rule 1 - Bug] Fixed lint issues from existing test file**
- **Found during:** Lint run
- **Issue:** Long comment line (105 > 100 chars) in test_mortgage.py
- **Fix:** Split comment to two lines
- **Files modified:** tests/test_mortgage.py
- **Commit:** c0ea5ba (included in GREEN commit)

No architectural changes needed. All deviations were correctness fixes during TDD process.

## Implementation Decisions

**1. Empty renewal_scenarios behavior**
- Empty list means "single term only, no renewals"
- Does NOT automatically continue with initial rate for all terms
- After term 1, stops (respects user intent of "I'm only planning for 5 years")

**2. Payment recalculation strategy**
- At each renewal: payment = standard_payment(remaining_balance, new_rate, remaining_months)
- Ensures mortgage pays off exactly at amortization period (or earlier if rates drop)
- Initial high payment doesn't carry forward - recalculation may lower it significantly

**3. Term truncation logic**
- Generate schedule for full remaining amortization
- Truncate to 60 months max per term
- Prevents `calculate_amortization` from forcing early payoff at month 60 when there are more terms remaining

**4. Month number continuity**
- Month numbers are global across all terms (1-360)
- After generating each term's schedule, adjust month_number by adding months_elapsed offset
- Simplifies analysis: user can see "month 143" directly in schedule

**5. Rate repetition logic**
- Check if renewal_index < len(renewal_rates) for explicit rate
- If not, use renewal_rates[-1] to repeat last rate
- If renewal_rates is empty, use initial rate for all subsequent terms

## Verification

**All verification criteria met:**

- ✅ `just test` passes with all 10 new tests green (38 total: 28 existing + 10 new)
- ✅ `just lint` passes with no errors
- ✅ 30-year mortgage with 6 terms produces exactly 360 months (or fewer for early payoff)
- ✅ Two scenarios with different renewal rates produce different total interest amounts
- ✅ Payment recalculation at renewal matches calculate_standard_payment output
- ✅ Term boundaries align correctly (term 1 = 1-60, term 2 = 61-120, etc.)

**Manual verification:**
- $400k at 5% with $2000/month over 30 years: 6 terms, payments recalculate at each renewal
- Three scenarios (3%, 5%, 7% renewal): total interest increases with rate as expected
- Single-term (no renewals): stops at 60 months with remaining balance

## Commits

| Commit  | Type | Description                                    |
| ------- | ---- | ---------------------------------------------- |
| 5b2d22f | test | Add failing tests (RED phase)                  |
| c0ea5ba | feat | Implement multi-term engine (GREEN phase)      |

**Total commits:** 2 (TDD: RED → GREEN, no REFACTOR needed)

## Next Steps

**Immediate (Plan 02-03):**
- Implement annual summaries and totals
- Aggregate monthly data into yearly rollups
- Calculate cumulative totals and remaining balances per year

**Dependencies resolved:**
- Plan 02-01 provided: Core amortization engine, rate conversion, single-term calculation
- This plan provides: Multi-term chaining, renewal payment recalculation, scenario comparison

**Known limitations (deferred to future plans):**
- No annual summaries yet (just monthly detail)
- No lump sum payments or prepayments
- No accelerated payment options (bi-weekly, weekly)
- No integration with property/cash flow models

## Self-Check

Verifying claimed work exists on disk and in git...

```bash
# Check created files
[ -f "/Users/sergenasr/Workspace/maple-return/tests/test_mortgage_scenarios.py" ] && echo "✓ test_mortgage_scenarios.py"

# Check modified files
[ -f "/Users/sergenasr/Workspace/maple-return/maple_return/mortgage.py" ] && echo "✓ mortgage.py (modified)"

# Check commits
git log --oneline | grep -q "5b2d22f" && echo "✓ RED commit (5b2d22f)"
git log --oneline | grep -q "c0ea5ba" && echo "✓ GREEN commit (c0ea5ba)"

# Check key structures exist
grep -q "class TermDefinition" maple_return/mortgage.py && echo "✓ TermDefinition dataclass"
grep -q "class MortgageInput" maple_return/mortgage.py && echo "✓ MortgageInput dataclass"
grep -q "class TermSummary" maple_return/mortgage.py && echo "✓ TermSummary dataclass"
grep -q "class ScenarioResult" maple_return/mortgage.py && echo "✓ ScenarioResult dataclass"
grep -q "def calculate_multi_term" maple_return/mortgage.py && echo "✓ calculate_multi_term()"

# Check tests run
pytest tests/test_mortgage_scenarios.py -v --tb=no -q 2>&1 | grep -q "10 passed" && echo "✓ All 10 tests passing"
```

## Self-Check: PASSED

All files, commits, and functionality verified present and working.
