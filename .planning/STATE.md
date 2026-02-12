# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-08)

**Core value:** The owner can clearly see how their Canadian rental property investment is performing and project where it's headed under different scenarios, so they can make informed hold/sell/refinance decisions.
**Current focus:** Phase 2 - Mortgage Engine

## Current Position

Phase: 2 of 6 (Mortgage Engine)
Plan: 3 of 3 in current phase
Status: Complete
Last activity: 2026-02-12 — Completed plan 02-03 (Annual Summaries and Scenario Comparison)

Progress: [██████████] 100% (3/3 plans in phase 02)

## Performance Metrics

**Velocity:**
- Total plans completed: 6
- Average duration: 6.7 min
- Total execution time: 0.67 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-foundation | 3 | 29.2 min | 9.7 min |
| 02-mortgage-engine | 3 | 12.0 min | 4.0 min |

**Recent Trend:**
- Last 5 plans: 01-03 (23.7min), 02-01 (5.0min), 02-02 (4.0min), 02-03 (3.0min)
- Trend: TDD approach consistently fast, mortgage engine plans very efficient

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

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-12
Stopped at: Completed 02-03-PLAN.md (Annual Summaries and Scenario Comparison)
Resume file: .planning/phases/02-mortgage-engine/02-03-SUMMARY.md
