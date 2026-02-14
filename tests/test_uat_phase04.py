"""UAT integration tests for Phase 04: Analysis & Metrics.

These tests verify user-observable behavior from the owner's perspective:
- Can I calculate IRR for my property?
- Can I see cap rate, cash-on-cash, equity position?
- Does the P&L table have all the columns I need?
- Does the dashboard snapshot show my current position?
"""

from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from maple_return.analysis import (
    DashboardSnapshot,
    PnLRow,
    build_amortization_table,
    build_dashboard_snapshot,
    build_pnl_table,
)
from maple_return.cashflow import AnnualOperatingSummary, MonthlyCashFlow
from maple_return.metrics import (
    calculate_cap_rate,
    calculate_cash_on_cash,
    calculate_equity_position,
    calculate_irr,
)
from maple_return.mortgage import AmortizationEntry
from maple_return.mortgage_summary import AnnualSummary


def _make_cashflow(month: date, net_cashflow: Decimal = Decimal("500")) -> MonthlyCashFlow:
    """Helper to create a MonthlyCashFlow with realistic fields."""
    return MonthlyCashFlow(
        month=month,
        gross_rent=Decimal("2000"),
        vacancy_deduction=Decimal("100"),
        effective_rent=Decimal("1900"),
        property_tax=Decimal("300"),
        insurance=Decimal("100"),
        maintenance=Decimal("150"),
        management_fee=Decimal("100"),
        total_operating_expenses=Decimal("650"),
        noi=Decimal("1250"),
        mortgage_payment=Decimal("750"),
        mortgage_principal=Decimal("200"),
        mortgage_interest=Decimal("550"),
        net_cashflow=net_cashflow,
        net_cashflow_usd=Decimal("370"),
        noi_usd=Decimal("925"),
    )


class TestUATMetricCalculations:
    """UAT: Owner can calculate key investment metrics."""

    def test_irr_returns_reasonable_value_for_typical_scenario(self):
        """IRR for $100k down, 60 months $500/mo positive, $500k terminal = 30-45%."""
        start = date(2024, 1, 1)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        irr = calculate_irr(Decimal("100000"), cashflows, Decimal("500000"))

        assert irr is not None
        assert Decimal("0.25") <= irr <= Decimal("0.45"), f"IRR {irr} outside expected range"

    def test_cap_rate_30k_noi_500k_value(self):
        """Cap rate: $30k NOI / $500k property = 6.00%."""
        result = calculate_cap_rate(Decimal("30000"), Decimal("500000"))
        assert result == Decimal("0.0600")

    def test_cash_on_cash_8k_flow_100k_down(self):
        """Cash-on-cash: $8k annual flow / $100k down payment = 8.00%."""
        result = calculate_cash_on_cash(Decimal("8000"), Decimal("100000"))
        assert result == Decimal("0.0800")

    def test_equity_position_550k_value_350k_balance(self):
        """Equity: $550k value - $350k balance = $200k."""
        result = calculate_equity_position(Decimal("550000"), Decimal("350000"))
        assert result == Decimal("200000")

    def test_negative_cashflow_does_not_break_metrics(self):
        """Metrics handle negative cash flow gracefully."""
        result = calculate_cash_on_cash(Decimal("-2000"), Decimal("100000"))
        assert result == Decimal("-0.0200")

    def test_zero_down_payment_returns_zero(self):
        """Edge case: zero down payment returns 0, not exception."""
        result = calculate_cash_on_cash(Decimal("8000"), Decimal("0"))
        assert result == Decimal("0.0000")


class TestUATPnLTable:
    """UAT: Owner can see year-by-year P&L with all required columns."""

    def test_pnl_has_all_16_fields(self):
        """P&L row contains all columns the owner needs."""
        expected_fields = {
            "year", "gross_rent", "vacancy_loss", "net_rent",
            "operating_expenses", "noi", "mortgage_payment", "net_cashflow",
            "principal_paid", "interest_paid", "equity_gained",
            "cumulative_cashflow", "cumulative_equity",
            "cap_rate", "cash_on_cash", "is_partial_year",
        }
        actual_fields = set(PnLRow.__dataclass_fields__.keys())
        assert expected_fields == actual_fields, (
            f"Missing: {expected_fields - actual_fields}, "
            f"Extra: {actual_fields - expected_fields}"
        )

    def test_first_year_flagged_as_partial(self):
        """Purchase year (year 1) is always flagged as partial."""
        annual_summaries = [
            AnnualOperatingSummary(
                year=2024,
                total_gross_rent=Decimal("24000"),
                total_vacancy_deduction=Decimal("1200"),
                total_effective_rent=Decimal("22800"),
                total_operating_expenses=Decimal("7800"),
                total_noi=Decimal("15000"),
                total_mortgage_payments=Decimal("9000"),
                total_mortgage_principal=Decimal("2400"),
                total_mortgage_interest=Decimal("6600"),
                total_net_cashflow=Decimal("6000"),
                total_net_cashflow_usd=Decimal("4440"),
                total_noi_usd=Decimal("11100"),
            ),
        ]
        mortgage_summaries = [
            AnnualSummary(
                year=2024,
                total_principal_paid=Decimal("2400"),
                total_interest_paid=Decimal("6600"),
                total_payments=Decimal("9000"),
                year_end_balance=Decimal("397600"),
                equity=Decimal("122400"),
            ),
        ]
        rows = build_pnl_table(
            annual_summaries,
            mortgage_summaries,
            purchase_price=Decimal("500000"),
            current_property_value=Decimal("520000"),
            down_payment=Decimal("100000"),
        )
        assert len(rows) == 1
        assert rows[0].is_partial_year is True

    def test_cumulative_cashflow_is_running_sum(self):
        """Cumulative cash flow grows across years."""
        annual_summaries = [
            AnnualOperatingSummary(
                year=2024 + i,
                total_gross_rent=Decimal("24000"),
                total_vacancy_deduction=Decimal("1200"),
                total_effective_rent=Decimal("22800"),
                total_operating_expenses=Decimal("7800"),
                total_noi=Decimal("15000"),
                total_mortgage_payments=Decimal("9000"),
                total_mortgage_principal=Decimal("2400"),
                total_mortgage_interest=Decimal("6600"),
                total_net_cashflow=Decimal("6000"),
                total_net_cashflow_usd=Decimal("4440"),
                total_noi_usd=Decimal("11100"),
            )
            for i in range(3)
        ]
        mortgage_summaries = [
            AnnualSummary(
                year=2024 + i,
                total_principal_paid=Decimal("2400"),
                total_interest_paid=Decimal("6600"),
                total_payments=Decimal("9000"),
                year_end_balance=Decimal("397600") - Decimal("2400") * i,
                equity=Decimal("122400") + Decimal("2400") * i,
            )
            for i in range(3)
        ]
        rows = build_pnl_table(
            annual_summaries,
            mortgage_summaries,
            purchase_price=Decimal("500000"),
            current_property_value=Decimal("520000"),
            down_payment=Decimal("100000"),
        )
        assert len(rows) == 3
        assert rows[0].cumulative_cashflow == Decimal("6000")
        assert rows[1].cumulative_cashflow == Decimal("12000")
        assert rows[2].cumulative_cashflow == Decimal("18000")


class TestUATDashboard:
    """UAT: Owner can see current position snapshot."""

    def test_dashboard_has_all_required_fields(self):
        """Dashboard snapshot contains all metrics the owner needs."""
        expected_fields = {
            "as_of_date", "equity_position", "equity_position_usd",
            "cumulative_cashflow", "cumulative_cashflow_usd",
            "annualized_return_irr", "current_cap_rate", "cash_on_cash_return",
            "months_held", "current_property_value", "remaining_balance",
        }
        actual_fields = set(DashboardSnapshot.__dataclass_fields__.keys())
        assert expected_fields == actual_fields, (
            f"Missing: {expected_fields - actual_fields}, "
            f"Extra: {actual_fields - expected_fields}"
        )

    def test_dashboard_uses_estimated_value_not_purchase_price(self):
        """Dashboard equity = current estimated value - balance, NOT purchase price - balance."""
        start = date(2023, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(12)]

        snapshot = build_dashboard_snapshot(
            monthly_cashflows=cashflows,
            purchase_date=start,
            down_payment=Decimal("100000"),
            current_property_value=Decimal("550000"),  # Appreciated from 500k purchase
            remaining_balance=Decimal("380000"),
            cad_per_usd=Decimal("1.35"),
        )

        # Equity should be 550k - 380k = 170k, NOT 500k - 380k = 120k
        assert snapshot.equity_position == Decimal("170000")

    def test_dashboard_includes_usd_conversions(self):
        """Dashboard shows USD equivalents for equity and cumulative cash flow."""
        start = date(2023, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(12)]

        snapshot = build_dashboard_snapshot(
            monthly_cashflows=cashflows,
            purchase_date=start,
            down_payment=Decimal("100000"),
            current_property_value=Decimal("550000"),
            remaining_balance=Decimal("380000"),
            cad_per_usd=Decimal("1.35"),
        )

        # USD values should be CAD / 1.35
        assert snapshot.equity_position_usd is not None
        assert snapshot.cumulative_cashflow_usd is not None
        # Rough check: USD < CAD (since CAD/USD > 1)
        assert snapshot.equity_position_usd < snapshot.equity_position


class TestUATAmortizationTable:
    """UAT: Owner can see monthly mortgage breakdown."""

    def test_amortization_table_has_monthly_rows(self):
        """Amortization table wraps schedule into output rows."""
        schedule = [
            AmortizationEntry(
                month_number=i + 1,
                date=date(2024, 1, 1) + relativedelta(months=i),
                payment=Decimal("1500"),
                principal=Decimal("400"),
                interest=Decimal("1100"),
                balance=Decimal("400000") - Decimal("400") * (i + 1),
            )
            for i in range(12)
        ]

        rows = build_amortization_table(schedule)

        assert len(rows) == 12
        assert rows[0].payment == Decimal("1500")
        assert rows[0].principal == Decimal("400")
        assert rows[0].interest == Decimal("1100")
        assert rows[-1].balance == Decimal("400000") - Decimal("400") * 12
