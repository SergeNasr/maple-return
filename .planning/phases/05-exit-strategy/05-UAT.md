---
status: complete
phase: 05-exit-strategy
source: [05-01-SUMMARY.md, 05-02-SUMMARY.md]
started: 2026-02-14T23:30:00Z
updated: 2026-02-14T23:45:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Waterfall Commission and Net Proceeds
expected: $600k sale, 5% commission, $5k closing, $350k mortgage → commission $30k, net proceeds $215k
result: pass

### 2. Underwater Sale (Negative Proceeds)
expected: Sale at $300k with $350k mortgage → negative net proceeds (-$70k)
result: pass

### 3. Zero Commission Private Sale
expected: 0% commission → net proceeds $245k (no commission deducted)
result: pass

### 4. Appreciation Rate (5-Year Hold)
expected: $500k → $600k over 5 years → 3.71% annualized
result: pass

### 5. Depreciation Shows Negative Rate
expected: Sale below purchase price → negative appreciation rate
result: pass

### 6. Zero Years Returns Zero Appreciation
expected: Immediate sale → 0.0000% appreciation
result: pass

### 7. USD Conversion on Exit Amounts
expected: Sale price and net proceeds converted to USD, both less than CAD values
result: pass

### 8. Cash Flow Truncation at Sale Year
expected: 360 months available, sell year 5 → only 60 months used
result: pass

### 9. Total Profit Formula
expected: 60 months * $200 = $12k cumulative + $215k net proceeds - $100k down = $127k profit
result: pass

### 10. Simple ROI
expected: $127k profit / $100k down = 1.2700
result: pass

### 11. Zero Down Payment ROI
expected: Zero down payment → ROI = 0.0000, no exception
result: pass

### 12. Total Profit USD Present
expected: total_profit_usd present and less than CAD value
result: pass

### 13. Hold-Period IRR Positive for Profitable Exit
expected: 5-year profitable hold → IRR positive and not None
result: pass

### 14. Year Zero Sale IRR is None
expected: Immediate sale → 0 months, IRR = None
result: pass

### 15. Exit Result Nested in Summary
expected: TotalReturnSummary.exit_result contains full waterfall with correct values
result: pass

## Summary

total: 15
passed: 15
issues: 0
pending: 0
skipped: 0

## Gaps

[none]
