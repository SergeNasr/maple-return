# Phase 2: Mortgage Engine - Context

**Gathered:** 2026-02-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Canadian mortgage amortization engine that calculates full payment schedules across multiple 5-year terms with rate renewals. Supports 1-3 renewal rate scenarios for comparison. Operating expenses, income, and FX are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Input parameters
- User enters: purchase date, purchase price, down payment (dollar amount), interest rate, monthly payment amount, amortization period
- Single rate per term (no mid-term rate changes)
- Rate type is variable or fixed per term, but variable terms use a single effective average rate (no prime-tracking)
- Canadian semi-annual compounding convention: convert nominal rate to effective monthly rate per Canadian mortgage rules
- Monthly payment frequency only (matches Phase 1 monthly granularity decision)
- Fixed monthly payment per term — no lump sums or extra payments
- No CMHC insurance calculation — user handles that separately
- Down payment as dollar amount, not percentage

### Term renewal behavior
- All terms are fixed 5-year length — standard Canadian renewal cycle
- Initial term: user specifies the payment amount
- Renewal terms: payment is recalculated from new rate + remaining balance + remaining amortization
- User enters 1 to 3 renewal rate assumptions to generate multiple scenarios for comparison
- Each scenario produces its own amortization schedule from the renewal point forward

### Output & schedule format
- Monthly detail: month, payment, principal portion, interest portion, remaining balance (core four fields)
- Annual summaries: total principal paid, total interest paid, total payments, year-end remaining balance, plus equity position (purchase price minus remaining balance)
- Scenario comparison: side-by-side summary table showing key metrics per renewal rate scenario (total interest, final balance, equity), with full detail available per scenario

### Claude's Discretion
- How to structure term definitions internally (list of terms upfront vs current + defaults for projections)
- Rounding rules for monthly calculations
- How to handle the final month when remaining balance doesn't divide evenly
- Internal data structures and algorithm design

</decisions>

<specifics>
## Specific Ideas

- Canadian mortgages compound semi-annually but pay monthly — this is a real convention that must be implemented correctly
- The scenario comparison is key: user wants to see "what if renewal is at 3%, 4%, or 5%?" side by side
- Payment recalculation at renewal makes sense for projections — user doesn't know future payments, just rates

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-mortgage-engine*
*Context gathered: 2026-02-10*
