# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-08)

**Core value:** The owner can clearly see how their Canadian rental property investment is performing and project where it's headed under different scenarios, so they can make informed hold/sell/refinance decisions.
**Current focus:** Phase 4 - Analysis & Metrics

## Current Position

Phase: 4 of 6 (Analysis & Metrics)
Plan: 2 of 2 in current phase
Status: Completed
Last activity: 2026-02-14 — Completed plan 04-02 (P&L Table, Amortization Table, Dashboard Snapshot)

Progress: [██████████] 100% (2/2 plans in phase 04)

## Performance Metrics

**Velocity:**
- Total plans completed: 10
- Average duration: 5.5 min
- Total execution time: 0.95 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 3 | 29.2 min | 9.7 min |
| 02-mortgage-engine | 3 | 12.0 min | 4.0 min |
| 03-operating-model | 2 | 5.7 min | 2.85 min |
| 04-analysis-metrics | 2 | 6.7 min | 3.35 min |

**Recent Trend:**
- Last 5 plans: 03-01 (2.8min), 03-02 (2.9min), 04-01 (3.3min), 04-02 (3.4min)
- Trend: Consistent sub-4-minute execution with TDD approach

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Python backend with uv/ruff/justfile (owner's preferred toolchain)
- Flat effective tax rates (deferred to v2 - TAX requirements)
- Single FX rate assumption (simplifies model)
- Monthly granularity with annual rollups (matches mortgage payment cycles)

**From plan 01-01:**
- Python 3.12 as baseline version
- uv for package management (modern, fast alternative)
- ruff for linting (fast, comprehensive)
- justfile for task automation
- Line length 100 characters
- Dev dependencies in optional-dependencies section

**From plan 01-02:**
- Use Python dataclasses for data models (simple, type-safe, standard library)
- Use Decimal for all monetary amounts (precision, no floating-point errors)
- Use date for temporal fields (matches mortgage payment cycles)

**From plan 01-03:**
- Use SQLAlchemy async with aiosqlite driver for database access
- Use lifespan event handlers instead of deprecated on_event decorator
- Use port 8001 for dev server (user has 8000 reserved)
- Store database file in project root (maple_return.db)
- Async-first architecture for web routes and database sessions

**From plan 02-01:**
- Use repr() for float-to-Decimal conversion to preserve full precision in rate calculations
- Preserve original day-of-month across payment dates (handle month-end edge cases)
- Force final payoff at amortization_months if payment > interest (handles rounding accumulation)

**From plan 02-02:**
- Empty renewal_scenarios means single-term only (no automatic continuation with initial rate)
- Payment recalculation at renewals spreads remaining balance over remaining amortization
- Last renewal rate repeats for all subsequent terms when scenario list is shorter than needed
- Terms truncate at 60 months unless mortgage pays off earlier within the term

**From plan 02-03:**
- Annual summaries group by calendar year (not mortgage year)
- Partial first/last years include all months that fall in that calendar year
- Equity calculated as purchase_price minus remaining balance at each summary level
- Renewal rates list excludes initial term (term 1) since it's the same across all scenarios

**From plan 03-01:**
- Use lease anniversary for both rent and expense escalation timing (not calendar year)
- Management fee calculated as % of gross rent (not effective rent after vacancy)
- Compounding escalation formula: base * (1 + rate)^years (not simple interest)

**From plan 03-02:**
- FX conversion divides CAD by CAD-per-USD rate (locked decision from 03-CONTEXT.md)
- Use itertools.groupby for annual summaries (efficient, handles partial years naturally)
- USD amounts only in summaries (not all line items) - focused on high-level metrics

**From plan 04-01:**
- IRR solver uses Newton-Raphson with 1e-6 tolerance for practical convergence
- Partial year annualization uses linear scaling (value/months)*12 for comparability
- All metrics quantized to 4 decimal places for percentage display precision
- Error handling returns zero/None (not exceptions) for invalid cases

**From plan 04-02:**
- First year always flagged as partial (purchase year per user decision)
- Equity gained computed as year-over-year change (year 1 relative to down payment)
- Dashboard filters cashflows to today for current position snapshot
- Dashboard annualizes metrics from most recent 12 months (or available months)
- Months held calculation includes current month if day >= purchase day

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-14
Stopped at: Completed 04-02-PLAN.md (P&L Table, Amortization Table, Dashboard Snapshot)
Resume file: .planning/phases/04-analysis-metrics/04-02-SUMMARY.md
