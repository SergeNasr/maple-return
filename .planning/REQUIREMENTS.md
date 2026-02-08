# Requirements: Maple Return

**Defined:** 2026-02-08
**Core Value:** The owner can clearly see how their Canadian rental property investment is performing and project where it's headed under different scenarios, so they can make informed hold/sell/refinance decisions.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Property & Mortgage

- [ ] **MORT-01**: User can input purchase date, purchase price, and down payment
- [ ] **MORT-02**: User can input mortgage rate (variable), payment amount (fixed), and 30-year amortization period
- [ ] **MORT-03**: Tool generates full amortization schedule with monthly principal/interest split
- [ ] **MORT-04**: User can model rate changes within a term (interest/principal split adjusts, payment stays fixed)
- [ ] **MORT-05**: User can define 5-year term renewal scenarios (switch variable↔fixed, set new rate)
- [ ] **MORT-06**: Tool projects mortgage across multiple term renewals through full amortization

### Income & Expenses

- [ ] **OPEX-01**: User can input monthly rental income amount
- [ ] **OPEX-02**: User can input vacancy rate or specific vacant months
- [ ] **OPEX-03**: User can input annual operating costs: property tax, insurance, maintenance
- [ ] **OPEX-04**: User can set annual escalation percentages for rent and expenses

### FX & Cross-Border

- [ ] **FX-01**: User can input a single fixed CAD/USD exchange rate
- [ ] **FX-02**: All monetary outputs are shown in both CAD and USD

### Exit Strategy

- [ ] **EXIT-01**: User can input a target selling price and year of sale
- [ ] **EXIT-02**: User can input agent commissions and closing fees
- [ ] **EXIT-03**: Tool calculates net proceeds from sale after fees
- [ ] **EXIT-04**: Tool calculates total return for the full hold period including exit

### Analysis & Output

- [ ] **OUT-01**: Tool displays detailed monthly amortization table
- [ ] **OUT-02**: Tool displays year-by-year P&L (income, expenses, net cash flow)
- [ ] **OUT-03**: Tool calculates and displays key metrics: IRR, ROI, cap rate, cash-on-cash return, equity growth
- [ ] **OUT-04**: Dashboard shows current snapshot: equity position, cash flow to date, returns to date

### Interface

- [ ] **UI-01**: Web-based form for all property inputs
- [ ] **UI-02**: Scenario controls to adjust mortgage rates and terms
- [ ] **UI-03**: Results displayed as detailed tables

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Tax Estimation

- **TAX-01**: User can input effective tax rates (Canadian income, US income, property tax, capital gains)
- **TAX-02**: Tool shows net-of-tax cash flow in projections
- **TAX-03**: Tool calculates capital gains tax impact on exit

### Comparison

- **COMP-01**: Stock market benchmark comparison (index fund alternative at user-specified return rate)
- **COMP-02**: Side-by-side total return comparison (property vs index fund)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multiple property comparison | Single property tool only |
| Actual tax bracket calculations | Uses flat effective rates supplied by user |
| Data import/export from spreadsheets | Manual form entry sufficient for one property |
| Mobile app | Web only |
| Real-time FX or market data feeds | Manual input |
| Canadian non-resident tax treaty modeling | User handles tax complexity offline |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| MORT-01 | TBD | Pending |
| MORT-02 | TBD | Pending |
| MORT-03 | TBD | Pending |
| MORT-04 | TBD | Pending |
| MORT-05 | TBD | Pending |
| MORT-06 | TBD | Pending |
| OPEX-01 | TBD | Pending |
| OPEX-02 | TBD | Pending |
| OPEX-03 | TBD | Pending |
| OPEX-04 | TBD | Pending |
| FX-01 | TBD | Pending |
| FX-02 | TBD | Pending |
| EXIT-01 | TBD | Pending |
| EXIT-02 | TBD | Pending |
| EXIT-03 | TBD | Pending |
| EXIT-04 | TBD | Pending |
| OUT-01 | TBD | Pending |
| OUT-02 | TBD | Pending |
| OUT-03 | TBD | Pending |
| OUT-04 | TBD | Pending |
| UI-01 | TBD | Pending |
| UI-02 | TBD | Pending |
| UI-03 | TBD | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 0
- Unmapped: 23 ⚠️

---
*Requirements defined: 2026-02-08*
*Last updated: 2026-02-08 after initial definition*
