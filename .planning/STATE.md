# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-08)

**Core value:** The owner can clearly see how their Canadian rental property investment is performing and project where it's headed under different scenarios, so they can make informed hold/sell/refinance decisions.
**Current focus:** Phase 3 - Operating Model

## Current Position

Phase: 3 of 6 (Operating Model)
Plan: 2 of 2 in current phase
Status: Completed
Last activity: 2026-02-12 — Completed plan 03-02 (Cash Flow Integration and FX Conversion)

Progress: [██████████] 100% (2/2 plans in phase 03)

## Performance Metrics

**Velocity:**
- Total plans completed: 8
- Average duration: 5.9 min
- Total execution time: 0.78 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 3 | 29.2 min | 9.7 min |
| 02-mortgage-engine | 3 | 12.0 min | 4.0 min |
| 03-operating-model | 2 | 5.7 min | 2.85 min |

**Recent Trend:**
- Last 5 plans: 02-02 (4.0min), 02-03 (3.0min), 03-01 (2.8min), 03-02 (2.9min)
- Trend: Excellent efficiency with TDD approach, phase 03 complete in record time

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

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-12
Stopped at: Completed 03-02-PLAN.md (Cash Flow Integration and FX Conversion)
Resume file: .planning/phases/03-operating-model/03-02-SUMMARY.md
