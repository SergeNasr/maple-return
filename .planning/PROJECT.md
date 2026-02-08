# Maple Return

## What This Is

A web-based simulation tool for a Canadian citizen living in the US who owns Canadian rental real estate. It lets the owner model their investment performance over time — including mortgage scenarios, operating costs, taxes, FX impact, and exit strategies — and compare returns against stock market benchmarks. One property, detailed tables, form-based input.

## Core Value

The owner can clearly see how their Canadian rental property investment is performing and project where it's headed under different scenarios, so they can make informed hold/sell/refinance decisions.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Dashboard showing current investment snapshot (equity position, cash flow, returns to date) based on purchase date and original purchase price
- [ ] Forward projection engine with monthly granularity and annual summaries
- [ ] Canadian mortgage modeling: original purchase date, purchase price, down payment, 30-year amortization, variable rate, fixed payments, 5-year term renewal cycles
- [ ] Mortgage scenario simulation — rate changes, switch variable↔fixed at renewal, project across multiple terms
- [ ] Operating expense inputs: property tax, insurance, maintenance, vacancy rate
- [ ] Rental income input with vacancy month modeling
- [ ] FX rate input (single fixed CAD/USD assumption applied across simulation)
- [ ] Tax estimation using user-supplied effective rates (Canadian income tax, US income tax, property tax, capital gains)
- [ ] Exit strategy modeling: selling price, FX rate at sale, agent commissions/fees, capital gains tax
- [ ] Key investment metrics: IRR, ROI, cap rate, cash-on-cash return, equity growth
- [ ] Stock market comparison benchmark (e.g., "if I had invested the same capital in index funds at X% return")
- [ ] Detailed amortization and year-by-year P&L tables
- [ ] Form-based data entry for all property inputs (purchase date, purchase price, down payment, mortgage details, expenses, income, etc.)

### Out of Scope

- Multiple property comparison — single property only
- Actual tax bracket calculations — uses flat effective rates supplied by user
- Data import/export from spreadsheets or external sources
- Mobile app — web only
- Real-time FX or market data feeds — manual input
- Canadian non-resident tax treaty nuances — user handles tax complexity offline

## Context

- Owner is a Canadian citizen residing in the US, so cross-border tax implications matter at a high level
- Canadian mortgages work differently from US mortgages: typically 5-year terms with rate renewal, 30-year amortization, variable or fixed rate within each term
- The mortgage currently has a variable rate with fixed payments — when rates change, the interest/principal split changes but payment stays the same (until renewal)
- The owner wants to see both "where am I now" and "where am I headed" with ability to tweak variables they control (rate assumptions, renovation spend, selling timeline, etc.)
- FX rate matters because income is in CAD but the owner's "home" currency for comparison purposes is USD
- "Simple and understandable" means detailed tables with clear labeling — not hidden complexity, not oversimplified summaries
- The purchase date and original price are key inputs — the tool needs to model from acquisition forward, showing historical performance to date and projections into the future

## Constraints

- **Tech stack**: Python backend (uv for package management, ruff for linting, justfile for task running), web frontend
- **Data persistence**: Local storage sufficient — single user tool
- **Tax accuracy**: Rough estimates only — not tax advice, not CRA/IRS compliant
- **FX model**: Single fixed rate assumption (not time-varying)
- **Amortization**: 30-year amortization with 5-year term renewals

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python backend with uv/ruff/justfile | Owner's preferred toolchain | — Pending |
| Flat effective tax rates | User knows their marginal rates; bracket modeling adds complexity without proportional value | — Pending |
| Single FX rate assumption | Simplifies model; user can re-run with different rates to test sensitivity | — Pending |
| Monthly granularity with annual rollups | Matches mortgage payment cycles; annual view for big-picture trends | — Pending |

---
*Last updated: 2026-02-08 after initialization*
