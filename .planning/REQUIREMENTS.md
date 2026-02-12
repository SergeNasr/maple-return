# Requirements: Maple Return

**Defined:** 2026-02-08
**Core Value:** The owner can clearly see how their Canadian rental property investment is performing and project where it's headed under different scenarios, so they can make informed hold/sell/refinance decisions.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Property & Mortgage

- [x] **MORT-01**: User can input purchase date, purchase price, and down payment
- [x] **MORT-02**: User can input mortgage rate (variable), payment amount (fixed), and 30-year amortization period
- [x] **MORT-03**: Tool generates full amortization schedule with monthly principal/interest split
- [ ] **MORT-04**: ~~User can model rate changes within a term~~ — Deferred: user decided single rate per term during Phase 2 context gathering. Rate changes happen at 5-year renewal boundaries (MORT-05).
- [x] **MORT-05**: User can define 5-year term renewal scenarios (switch variable↔fixed, set new rate)
- [x] **MORT-06**: Tool projects mortgage across multiple term renewals through full amortization

### Income & Expenses

- [x] **OPEX-01**: User can input monthly rental income amount
- [x] **OPEX-02**: User can input vacancy rate or specific vacant months
- [x] **OPEX-03**: User can input annual operating costs: property tax, insurance, maintenance
- [x] **OPEX-04**: User can set annual escalation percentages for rent and expenses

### FX & Cross-Border

- [x] **FX-01**: User can input a single fixed CAD/USD exchange rate
- [x] **FX-02**: All monetary outputs are shown in both CAD and USD

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
| MORT-01 | Phase 2 | ✓ Complete |
| MORT-02 | Phase 2 | ✓ Complete |
| MORT-03 | Phase 2 | ✓ Complete |
| MORT-04 | Deferred | Deferred (single rate per term decided) |
| MORT-05 | Phase 2 | ✓ Complete |
| MORT-06 | Phase 2 | ✓ Complete |
| OPEX-01 | Phase 3 | ✓ Complete |
| OPEX-02 | Phase 3 | ✓ Complete |
| OPEX-03 | Phase 3 | ✓ Complete |
| OPEX-04 | Phase 3 | ✓ Complete |
| FX-01 | Phase 3 | ✓ Complete |
| FX-02 | Phase 3 | ✓ Complete |
| EXIT-01 | Phase 5 | Pending |
| EXIT-02 | Phase 5 | Pending |
| EXIT-03 | Phase 5 | Pending |
| EXIT-04 | Phase 5 | Pending |
| OUT-01 | Phase 4 | Pending |
| OUT-02 | Phase 4 | Pending |
| OUT-03 | Phase 4 | Pending |
| OUT-04 | Phase 4 | Pending |
| UI-01 | Phase 6 | Pending |
| UI-02 | Phase 6 | Pending |
| UI-03 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 22
- Deferred: 1 (MORT-04)
- Unmapped: 0

**Note:** Phase 1 (Foundation) has no explicit requirements but provides infrastructure needed for all subsequent phases.

---
*Requirements defined: 2026-02-08*
*Last updated: 2026-02-12 after Phase 3 completion*
