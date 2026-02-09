# Phase 1: Foundation - Context

**Gathered:** 2026-02-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Project infrastructure setup: Python project with uv/ruff/justfile, FastAPI web server, SQLite database, core data models, and basic page rendering. No business logic — just the skeleton that all subsequent phases build on.

</domain>

<decisions>
## Implementation Decisions

### Web Framework
- FastAPI as the web framework
- Lightweight HTML rendering with htmx or similar (not a JS SPA) — must be battle-tested with good Python support
- SQLite for data persistence — store only inputs, compute everything on the fly
- Local dev server only (`just run`, localhost) — no Docker, no deployment

### Data Model Shape
- Persist only property inputs (purchase info, mortgage details, expenses, income config)
- No saved scenarios — all simulation results computed on demand from current inputs
- Mortgage term renewals: "current + next" model — user sets current term, then adjusts next term when it comes (not a full timeline of all terms upfront)
- Vacancy modeled as a percentage rate applied across all months (not specific months)

### Project Structure
- Package name: `maple_return`
- Domain modules for calculation logic: mortgage.py, cashflow.py, metrics.py, exit.py (separate concerns)
- pytest from day one — especially important for financial calculations
- Justfile with standard commands: lint (ruff), test (pytest), run (dev server)
- uv for package management, ruff for linting

### Frontend Approach
- Currency display: toggle button to switch everything between CAD and USD (not dual columns)
- Tables, forms, and layout details are Claude's discretion — keep it clean and functional

### Claude's Discretion
- Specific htmx-like library choice (must be battle-tested, good Python integration)
- CSS framework choice (lightweight, makes plain HTML look good)
- Table pagination/scrolling strategy for large datasets (360 months)
- Form/results layout (side-by-side vs sequential vs tabbed)
- Frontend templates location (inside package vs top-level)

</decisions>

<specifics>
## Specific Ideas

- "Simple and understandable" — detailed tables with clear labeling, not hidden complexity
- Lightweight feel throughout — htmx-style interactivity, not a heavy JS framework
- Single-user personal tool — no auth, no multi-tenancy, no deployment concerns

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-02-08*
