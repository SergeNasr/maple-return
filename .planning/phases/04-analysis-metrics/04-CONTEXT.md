# Phase 4: Analysis & Metrics - Context

**Gathered:** 2026-02-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce detailed financial analysis and key investment metrics from the mortgage engine and operating model outputs. This phase delivers calculation logic and structured output — amortization tables, year-by-year P&L, dashboard snapshot, and investment metrics (IRR, ROI, cap rate, cash-on-cash return, equity growth). Stock market benchmark comparison is explicitly out of scope (separate phase).

</domain>

<decisions>
## Implementation Decisions

### Metric definitions
- All-in IRR: down payment as outflow, monthly net cash flows (rent - expenses - mortgage), current estimated value as terminal cash inflow
- IRR terminal value uses current estimated property value as stand-in until Phase 5 (Exit Strategy) adds proper sale modeling
- Cap rate calculated per year across the full projection (evolves as rent and expenses escalate)
- Cash-on-cash return based on initial down payment only (traditional calculation: annual cash flow / down payment)
- Stock market benchmark comparison deferred to a separate phase

### Table presentation
- Amortization table: monthly rows with full detail (date, payment, principal, interest, balance)
- P&L table: annual rows with full breakdown — gross rent, vacancy loss, net rent, operating expenses, NOI, mortgage payment, net cash flow, principal portion, interest portion, equity gained, cumulative cash flow, cumulative equity
- Tables in CAD (native property currency); USD equivalents in dashboard/summary metrics only

### Dashboard snapshot
- "As of today" — always reflects current position based on purchase date to now, no date picker
- Annualized return (IRR) is the hero metric — most prominent number
- Equity position uses user-input current estimated property value (not just purchase price)
- No health indicators or color-coded signals — present data cleanly, let the owner interpret
- Show all key metrics: equity position, cumulative cash flow, annualized return, cap rate, cash-on-cash

### Calculation edge cases
- Partial current year: annualize metrics (e.g., 6 months of data × 2)
- Year 1 (purchase year): flag as partial with annotation — not directly comparable to full years
- Negative cash flow periods: visually highlight in output so they stand out
- Current estimated property value: new user input, serves as terminal value for IRR and equity position on dashboard

### Claude's Discretion
- Exact table formatting and column widths
- How to visually highlight negative cash flow (styling approach)
- Annotation format for partial-year flagging
- Internal calculation order and data pipeline architecture

</decisions>

<specifics>
## Specific Ideas

- Two property value concepts: current estimated value (user input for dashboard/IRR) and projected sale price (Phase 5 adds this later)
- P&L should show the mortgage split (principal vs interest) alongside operating metrics — owner wants to see equity being built through payments
- Cap rate evolving year-over-year shows how the investment improves as rent escalates

</specifics>

<deferred>
## Deferred Ideas

- Stock market benchmark comparison ("what if I invested the down payment in index funds at X%") — separate phase
- Projected sale price and full exit modeling — Phase 5
- Time-selectable dashboard snapshot (pick any historical date) — future enhancement

</deferred>

---

*Phase: 04-analysis-metrics*
*Context gathered: 2026-02-13*
