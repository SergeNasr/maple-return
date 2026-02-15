# Roadmap: Maple Return

## Overview

This roadmap builds a rental property investment simulation tool from the ground up. Starting with project foundation and core calculation engines (mortgage amortization, operating expenses, FX), then layering on analytical outputs (metrics, tables, dashboard), exit strategy modeling, and finally the web interface that ties it all together. Each phase delivers verifiable capabilities that build toward complete investment analysis.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - Project setup, tooling, data models ✓
- [x] **Phase 2: Mortgage Engine** - Canadian mortgage amortization with term renewals ✓
- [x] **Phase 3: Operating Model** - Income, expenses, FX conversion ✓
- [x] **Phase 4: Analysis & Metrics** - Financial calculations and detailed outputs ✓
- [x] **Phase 5: Exit Strategy** - Sale modeling and total return calculation ✓
- [ ] **Phase 6: User Interface** - Web forms and table display

## Phase Details

### Phase 1: Foundation
**Goal**: Project infrastructure is ready for development with data models defined
**Depends on**: Nothing (first phase)
**Requirements**: UI-01 (partial - project structure)
**Success Criteria** (what must be TRUE):
  1. Python project exists with uv package management configured
  2. Justfile with standard commands (lint, test, run) works
  3. Core data models for Property, Mortgage, CashFlow are defined
  4. Basic web server runs and serves a test page
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Project infrastructure with uv, ruff, and pytest
- [x] 01-02-PLAN.md — Core data models (Property, Mortgage, CashFlow)
- [x] 01-03-PLAN.md — FastAPI web server with SQLite and test page

### Phase 2: Mortgage Engine
**Goal**: Tool accurately calculates Canadian mortgage amortization across multiple terms
**Depends on**: Phase 1
**Requirements**: MORT-01, MORT-02, MORT-03, MORT-05, MORT-06
**Success Criteria** (what must be TRUE):
  1. User can input purchase date, price, down payment, rate, payment amount, and amortization period
  2. Tool generates full amortization schedule with monthly principal/interest breakdown
  3. 5-year term renewals with rate/type changes (variable/fixed) work across full 30-year amortization
  4. Remaining balance at end of each term is correct
  5. User can compare 1-3 renewal rate scenarios side by side
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Core Canadian mortgage amortization engine (TDD)
- [x] 02-02-PLAN.md — Multi-term renewal and scenario comparison (TDD)
- [x] 02-03-PLAN.md — Annual summaries and scenario comparison output (TDD)

### Phase 3: Operating Model
**Goal**: Tool models rental income, operating expenses, and currency conversion
**Depends on**: Phase 2
**Requirements**: OPEX-01, OPEX-02, OPEX-03, OPEX-04, FX-01, FX-02
**Success Criteria** (what must be TRUE):
  1. User can input monthly rental income and vacancy rate or specific vacant months
  2. User can input annual operating costs (property tax, insurance, maintenance)
  3. User can set annual escalation percentages for rent and expenses
  4. User can input a single fixed CAD/USD exchange rate
  5. All monetary values display in both CAD and USD
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md — Operating income and expense engine (TDD)
- [x] 03-02-PLAN.md — Cash flow integration with FX conversion (TDD)

### Phase 4: Analysis & Metrics
**Goal**: Tool produces detailed financial analysis and key investment metrics
**Depends on**: Phase 3
**Requirements**: OUT-01, OUT-02, OUT-03, OUT-04
**Success Criteria** (what must be TRUE):
  1. Tool displays detailed monthly amortization table
  2. Tool displays year-by-year P&L showing income, expenses, net cash flow
  3. Dashboard shows current snapshot: equity position, cash flow to date, returns to date
  4. Key metrics are calculated and displayed: IRR, ROI, cap rate, cash-on-cash return, equity growth
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md — Investment metrics engine: IRR, cap rate, cash-on-cash, equity growth (TDD)
- [x] 04-02-PLAN.md — P&L table, amortization table, and dashboard snapshot (TDD)

### Phase 5: Exit Strategy
**Goal**: Tool models property sale and calculates total investment return
**Depends on**: Phase 4
**Requirements**: EXIT-01, EXIT-02, EXIT-03, EXIT-04
**Success Criteria** (what must be TRUE):
  1. User can input target selling price and year of sale
  2. User can input agent commissions and closing fees
  3. Tool calculates net proceeds from sale after all fees
  4. Tool calculates total return for the full hold period including exit proceeds
**Plans**: 2 plans

Plans:
- [x] 05-01-PLAN.md — Exit model: sale costs, net proceeds waterfall, appreciation rate (TDD)
- [x] 05-02-PLAN.md — Total return with exit: hold-period IRR, ROI, cash flow truncation (TDD)

### Phase 6: User Interface
**Goal**: Web-based interface allows user to input data and view results
**Depends on**: Phase 5
**Requirements**: UI-01, UI-02, UI-03
**Success Criteria** (what must be TRUE):
  1. Web form accepts all property inputs (purchase details, mortgage, expenses, income)
  2. Scenario controls allow user to adjust mortgage rates and term renewal parameters
  3. Results display as detailed tables (amortization, P&L, metrics)
  4. User can run complete simulation from input to results in web browser
**Plans**: 3 plans

Plans:
- [ ] 06-01-PLAN.md — Backend foundation: DB model, API routes (save/load/simulate), HTMX + CSS
- [ ] 06-02-PLAN.md — Wizard form: 5-step input flow with validation and auto-save
- [ ] 06-03-PLAN.md — Results dashboard, detail tables, and end-to-end verification

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | ✓ Complete | 2026-02-08 |
| 2. Mortgage Engine | 3/3 | ✓ Complete | 2026-02-12 |
| 3. Operating Model | 2/2 | ✓ Complete | 2026-02-12 |
| 4. Analysis & Metrics | 2/2 | ✓ Complete | 2026-02-13 |
| 5. Exit Strategy | 2/2 | ✓ Complete | 2026-02-14 |
| 6. User Interface | 0/? | Not started | - |

---
*Roadmap created: 2026-02-08*
*Last updated: 2026-02-14 after Phase 5 execution*
