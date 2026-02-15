# Phase 6: User Interface - Context

**Gathered:** 2026-02-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Web-based interface that allows the user to input property data (purchase details, mortgage, operating expenses, income, exit strategy) and view simulation results (amortization table, P&L table, metrics dashboard, exit analysis). Uses the existing FastAPI backend and calculation engines built in Phases 1-5.

</domain>

<decisions>
## Implementation Decisions

### Form layout & input flow
- Multi-step wizard with 5 steps: Property → Mortgage → Operating → Scenarios → Exit
- Scenarios get their own dedicated step (not inline in mortgage)
- Fields start blank with placeholder hints (not pre-filled with example data)
- Inline real-time validation — red borders and messages as user types
- Block advancement on invalid/missing required fields

### Results presentation
- Dashboard + drill-down layout: summary dashboard on top, click into detail tables
- Dashboard shows key metric cards plus a mini chart (cash flow or equity trend over time)
- Scenario comparison displayed as side-by-side columns in tables
- Detail tables (amortization, P&L) show CAD as primary currency
- USD only in dashboard metrics and summaries (not in detail tables)

### Page structure & navigation
- Single page vs multi-page: Claude's discretion based on wizard + dashboard flow
- Desktop-first design; responsive is nice-to-have, not required
- Auto-save: wizard state persists automatically to SQLite as user fills in
- No explicit save/load UI — last state always available on return
- Saved property configs persist in the existing SQLite database

### Interaction & feedback
- Calculation runs on wizard complete (first time), then live recalculation on any edit from results page
- Server-rendered with HTMX: Jinja2 templates + HTMX for interactivity
- Clean and minimal visual style: white background, subtle grays, focus on data

### Claude's Discretion
- Single-page vs two-page routing decision
- Exact wizard step transitions and progress indicator design
- Dashboard metric card layout and mini chart type
- Drill-down table navigation (accordion, tabs, or separate views)
- HTMX swap strategy and partial update patterns
- CSS framework choice (Tailwind, Pico, vanilla, etc.)
- Loading states and error presentation

</decisions>

<specifics>
## Specific Ideas

- Wizard flow: Property (price, date, down payment) → Mortgage (rate, amort, payment) → Operating (rent, expenses, FX) → Scenarios (renewal rates 1-3) → Exit (sale price, fees)
- "Spreadsheet-meets-modern-web" — clean data presentation, not flashy
- Auto-save means user can close browser and come back to where they left off
- First calculation on wizard submit, then live updates when editing from results

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 06-user-interface*
*Context gathered: 2026-02-15*
