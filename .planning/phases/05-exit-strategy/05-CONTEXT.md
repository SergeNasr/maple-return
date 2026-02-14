# Phase 5: Exit Strategy - Context

**Gathered:** 2026-02-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Model property sale and calculate total investment return over the full hold period. User inputs a selling price and sale year, model calculates net proceeds and total return metrics. Tax calculations (capital gains) are deferred to a future version.

</domain>

<decisions>
## Implementation Decisions

### Sale cost modeling
- Single commission percentage applied to sale price (not buyer/seller split)
- Closing costs modeled as a flat dollar amount (not itemized categories)
- No mortgage discharge penalty — user accounts for this externally if needed
- Net proceeds displayed as waterfall breakdown: sale price → minus commission → minus closing costs → minus mortgage payoff → net proceeds

### Appreciation assumptions
- User enters sale price directly (no appreciation rate input)
- Single sale price per simulation (no multi-scenario comparison)
- Sale price in CAD with USD conversion, consistent with existing model
- Show implied annualized appreciation rate as informational metric (sale price vs purchase price)

### Return calculation scope
- Total return includes all cash flows plus sale proceeds — equity buildup is realized through sale (sale price minus remaining mortgage balance)
- Full hold-period IRR recalculated including exit (replaces operations-only IRR when exit is modeled)
- Simple ROI included: total profit / down payment
- Down payment is the invested base for ROI (not including negative cash flow months)
- Capital gains / tax calculations deferred to future version (consistent with flat tax rate deferral)

### Sale timing
- User specifies sale year as year number of ownership (e.g., year 5, year 10)
- Sale occurs at end of specified year (includes that year's full rental income and expenses)
- Cash flows truncate at sale year — clean hold period, not full 30-year projection
- Single exit year per simulation (user reruns to compare different years)

### Claude's Discretion
- How to structure the exit calculation engine internally
- Whether to reuse existing metrics functions or create exit-specific ones
- Error handling for edge cases (sale year beyond amortization, sale price below mortgage balance)

</decisions>

<specifics>
## Specific Ideas

- Waterfall breakdown for net proceeds gives step-by-step visibility into where sale money goes
- Implied appreciation rate helps the user gut-check whether their sale price assumption is reasonable
- IRR with exit is the definitive "was this investment worth it" number

</specifics>

<deferred>
## Deferred Ideas

- Capital gains tax estimation — future tax phase
- Multiple sale price scenarios — could add later if needed
- Mortgage discharge penalty modeling — keep simple for v1
- Multi-year exit comparison (sell in year 5 vs 10 vs 15) — user reruns for now

</deferred>

---

*Phase: 05-exit-strategy*
*Context gathered: 2026-02-14*
