# Phase 3: Operating Model - Context

**Gathered:** 2026-02-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Model rental income, operating expenses, and currency conversion for a Canadian rental property. Combine with mortgage payments from Phase 2 to produce monthly and annual cash flow projections. Tax calculations, exit strategy, and UI are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Income modeling
- Single unit property — one rental income stream
- Vacancy modeled as annual vacancy rate % applied evenly across all months
- Rent increases at a fixed annual escalation % (single rate, applied every year)
- Rent increase timing: on lease anniversary date (not calendar year)

### Expense categories
- Standard set: property tax, insurance, maintenance/repairs, property management fee
- All expenses input as annual amounts (tool divides by 12 for monthly)
- Single escalation rate applied to all expense categories equally
- Property management fee is % of gross rent (scales with income), not a flat amount

### FX conversion
- Owner is USD-based investor; property and all inputs are in CAD
- Single fixed exchange rate expressed as CAD per USD (e.g., 1.35 means 1 USD = 1.35 CAD)
- USD amounts shown in summary/rollup views only (monthly and annual totals, key metrics)
- Detailed line items stay CAD-only for readability

### Cash flow structure
- Both NOI (Net Operating Income) and net cash flow after mortgage are important outputs
- Operating model integrates with Phase 2 mortgage engine — cash flow includes mortgage payment deduction
- Output: gross rent → vacancy-adjusted rent → expenses → NOI → mortgage payment → net cash flow

### Claude's Discretion
- Monthly cash flow detail level (full expense breakdown vs summary lines)
- Expense escalation timing (calendar year vs lease anniversary)
- Internal data structures for operating model

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-operating-model*
*Context gathered: 2026-02-12*
