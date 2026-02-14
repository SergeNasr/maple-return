---
status: complete
phase: 04-analysis-metrics
source: [04-01-SUMMARY.md, 04-02-SUMMARY.md]
started: 2026-02-14T00:00:00Z
updated: 2026-02-14T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. IRR Calculation
expected: IRR for $100k down, 60 months $500/mo, $500k terminal returns 30-45% range
result: pass

### 2. Cap Rate Calculation
expected: $30k NOI / $500k value returns 0.0600
result: pass

### 3. Cash-on-Cash Return
expected: $8k annual flow / $100k down returns 0.0800
result: pass

### 4. Equity Position
expected: $550k value - $350k balance returns $200k
result: pass

### 5. Negative Cash Flow Handling
expected: Negative cash flow returns negative percentage, no exceptions
result: pass

### 6. Zero Down Payment Edge Case
expected: Zero down payment returns 0.0000, no exceptions
result: pass

### 7. P&L Table Has All 16 Fields
expected: PnLRow has year, gross_rent, vacancy_loss, net_rent, operating_expenses, noi, mortgage_payment, net_cashflow, principal_paid, interest_paid, equity_gained, cumulative_cashflow, cumulative_equity, cap_rate, cash_on_cash, is_partial_year
result: pass

### 8. First Year Flagged as Partial
expected: Purchase year (year 1) always has is_partial_year=True
result: pass

### 9. Cumulative Cash Flow is Running Sum
expected: 3-year projection shows cumulative_cashflow growing: 6000, 12000, 18000
result: pass

### 10. Dashboard Has All Required Fields
expected: DashboardSnapshot has as_of_date, equity_position, equity_position_usd, cumulative_cashflow, cumulative_cashflow_usd, annualized_return_irr, current_cap_rate, cash_on_cash_return, months_held, current_property_value, remaining_balance
result: pass

### 11. Dashboard Uses Estimated Value Not Purchase Price
expected: Equity = $550k estimated - $380k balance = $170k (not purchase price)
result: pass

### 12. Dashboard Includes USD Conversions
expected: equity_position_usd and cumulative_cashflow_usd present and < CAD values
result: pass

### 13. Amortization Table Has Monthly Rows
expected: 12-month schedule produces 12 rows with correct payment, principal, interest, balance
result: pass

## Summary

total: 13
passed: 13
issues: 0
pending: 0
skipped: 0

## Gaps

[none]
