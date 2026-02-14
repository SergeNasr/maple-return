"""Tests for investment metric calculations."""

from datetime import date
from decimal import Decimal

import pytest

from maple_return.cashflow import AnnualOperatingSummary, MonthlyCashFlow
from maple_return.metrics import (
    AnnualMetrics,
    calculate_annual_metrics,
    calculate_cap_rate,
    calculate_cash_on_cash,
    calculate_equity_position,
    calculate_irr,
)


class TestIRR:
    """Test Internal Rate of Return calculations."""

    def test_positive_irr_with_monthly_positive_cashflows(self):
        """IRR calculation with positive monthly cash flows and terminal value."""
        down_payment = Decimal("100000")
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, i, 1),
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
                net_cashflow=Decimal("500"),
                net_cashflow_usd=Decimal("370"),
                noi_usd=Decimal("925"),
            )
            for i in range(1, 61)
        ]
        current_property_value = Decimal("500000")

        irr = calculate_irr(down_payment, monthly_cashflows, current_property_value)

        # With $100k down, 60 months of $500/month, and $500k terminal value
        # IRR should be in the 30-40% range (very high return scenario)
        assert irr is not None
        assert Decimal("0.25") <= irr <= Decimal("0.45")

    def test_negative_irr_with_losses(self):
        """IRR calculation with negative cash flows."""
        down_payment = Decimal("100000")
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, i, 1),
                gross_rent=Decimal("1500"),
                vacancy_deduction=Decimal("75"),
                effective_rent=Decimal("1425"),
                property_tax=Decimal("300"),
                insurance=Decimal("100"),
                maintenance=Decimal("150"),
                management_fee=Decimal("75"),
                total_operating_expenses=Decimal("625"),
                noi=Decimal("800"),
                mortgage_payment=Decimal("1000"),
                mortgage_principal=Decimal("300"),
                mortgage_interest=Decimal("700"),
                net_cashflow=Decimal("-200"),
                net_cashflow_usd=Decimal("-148"),
                noi_usd=Decimal("592"),
            )
            for i in range(1, 13)
        ]
        current_property_value = Decimal("100000")

        irr = calculate_irr(down_payment, monthly_cashflows, current_property_value)

        # With $100k down, 12 months of -$200/month, and $100k terminal value
        # IRR should be slightly negative (small loss)
        assert irr is not None
        assert irr < Decimal("0")
        assert irr > Decimal("-0.05")  # Not catastrophic

    def test_irr_all_negative_flows_returns_none(self):
        """IRR cannot be calculated when all flows are negative."""
        down_payment = Decimal("100000")
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, i, 1),
                gross_rent=Decimal("0"),
                vacancy_deduction=Decimal("0"),
                effective_rent=Decimal("0"),
                property_tax=Decimal("300"),
                insurance=Decimal("100"),
                maintenance=Decimal("150"),
                management_fee=Decimal("0"),
                total_operating_expenses=Decimal("550"),
                noi=Decimal("-550"),
                mortgage_payment=Decimal("1000"),
                mortgage_principal=Decimal("200"),
                mortgage_interest=Decimal("800"),
                net_cashflow=Decimal("-1550"),
                net_cashflow_usd=Decimal("-1148"),
                noi_usd=Decimal("-407"),
            )
            for i in range(1, 13)
        ]
        current_property_value = Decimal("0")

        irr = calculate_irr(down_payment, monthly_cashflows, current_property_value)

        # No sign change in cash flows -> no IRR
        assert irr is None

    def test_irr_zero_down_payment(self):
        """IRR with zero down payment edge case."""
        down_payment = Decimal("0")
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, i, 1),
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
                net_cashflow=Decimal("500"),
                net_cashflow_usd=Decimal("370"),
                noi_usd=Decimal("925"),
            )
            for i in range(1, 13)
        ]
        current_property_value = Decimal("100000")

        # With zero down payment, IRR should be extremely high
        irr = calculate_irr(down_payment, monthly_cashflows, current_property_value)

        # Should handle gracefully (possibly very high IRR or None)
        # This is an edge case - any result is acceptable as long as no exception
        assert irr is None or irr > Decimal("0")


class TestCapRate:
    """Test Cap Rate calculations."""

    def test_cap_rate_normal_case(self):
        """Cap rate with standard NOI and property value."""
        annual_noi = Decimal("30000")
        property_value = Decimal("500000")

        cap_rate = calculate_cap_rate(annual_noi, property_value)

        assert cap_rate == Decimal("0.0600")

    def test_cap_rate_zero_noi(self):
        """Cap rate with zero NOI."""
        annual_noi = Decimal("0")
        property_value = Decimal("500000")

        cap_rate = calculate_cap_rate(annual_noi, property_value)

        assert cap_rate == Decimal("0.0000")

    def test_cap_rate_zero_property_value(self):
        """Cap rate with zero property value returns zero."""
        annual_noi = Decimal("30000")
        property_value = Decimal("0")

        cap_rate = calculate_cap_rate(annual_noi, property_value)

        assert cap_rate == Decimal("0.0000")

    def test_cap_rate_precision(self):
        """Cap rate is quantized to 4 decimal places."""
        annual_noi = Decimal("32500")
        property_value = Decimal("500000")

        cap_rate = calculate_cap_rate(annual_noi, property_value)

        # 32500 / 500000 = 0.065
        assert cap_rate == Decimal("0.0650")
        # Check precision (4 decimal places)
        assert cap_rate.as_tuple().exponent == -4


class TestCashOnCash:
    """Test Cash-on-Cash Return calculations."""

    def test_cash_on_cash_positive_return(self):
        """Cash-on-cash with positive annual cash flow."""
        annual_net_cashflow = Decimal("8000")
        down_payment = Decimal("100000")

        coc = calculate_cash_on_cash(annual_net_cashflow, down_payment)

        assert coc == Decimal("0.0800")

    def test_cash_on_cash_negative_return(self):
        """Cash-on-cash with negative annual cash flow."""
        annual_net_cashflow = Decimal("-2000")
        down_payment = Decimal("100000")

        coc = calculate_cash_on_cash(annual_net_cashflow, down_payment)

        assert coc == Decimal("-0.0200")

    def test_cash_on_cash_zero_down_payment(self):
        """Cash-on-cash with zero down payment returns zero."""
        annual_net_cashflow = Decimal("8000")
        down_payment = Decimal("0")

        coc = calculate_cash_on_cash(annual_net_cashflow, down_payment)

        assert coc == Decimal("0.0000")

    def test_cash_on_cash_precision(self):
        """Cash-on-cash is quantized to 4 decimal places."""
        annual_net_cashflow = Decimal("8333")
        down_payment = Decimal("100000")

        coc = calculate_cash_on_cash(annual_net_cashflow, down_payment)

        # 8333 / 100000 = 0.08333
        assert coc == Decimal("0.0833")
        assert coc.as_tuple().exponent == -4


class TestEquityPosition:
    """Test Equity Position calculations."""

    def test_equity_position_normal_case(self):
        """Equity position with standard property value and mortgage balance."""
        current_property_value = Decimal("550000")
        remaining_balance = Decimal("350000")

        equity = calculate_equity_position(current_property_value, remaining_balance)

        assert equity == Decimal("200000")

    def test_equity_position_paid_off_property(self):
        """Equity position with no remaining mortgage balance."""
        current_property_value = Decimal("500000")
        remaining_balance = Decimal("0")

        equity = calculate_equity_position(current_property_value, remaining_balance)

        assert equity == Decimal("500000")

    def test_equity_position_underwater(self):
        """Equity position when property value is less than mortgage balance."""
        current_property_value = Decimal("400000")
        remaining_balance = Decimal("450000")

        equity = calculate_equity_position(current_property_value, remaining_balance)

        # Negative equity (underwater)
        assert equity == Decimal("-50000")


class TestAnnualMetrics:
    """Test annual metrics summary calculation."""

    def test_annual_metrics_full_year(self):
        """Calculate annual metrics for a full 12-month year."""
        annual_summary = AnnualOperatingSummary(
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
            total_net_cashflow_usd=Decimal("4444"),
            total_noi_usd=Decimal("11111"),
        )
        property_value = Decimal("500000")
        remaining_balance = Decimal("350000")
        down_payment = Decimal("100000")
        is_partial_year = False
        months_in_year = 12

        metrics = calculate_annual_metrics(
            annual_summary,
            property_value,
            remaining_balance,
            down_payment,
            is_partial_year,
            months_in_year,
        )

        # Cap rate: 15000 / 500000 = 0.03
        assert metrics.cap_rate == Decimal("0.0300")
        # Cash on cash: 6000 / 100000 = 0.06
        assert metrics.cash_on_cash == Decimal("0.0600")
        # Equity: 500000 - 350000 = 150000
        assert metrics.equity_position == Decimal("150000")
        assert metrics.year == 2024
        assert metrics.is_partial_year is False

    def test_annual_metrics_partial_year_annualized(self):
        """Calculate annual metrics for a partial year with annualization."""
        annual_summary = AnnualOperatingSummary(
            year=2024,
            total_gross_rent=Decimal("12000"),
            total_vacancy_deduction=Decimal("600"),
            total_effective_rent=Decimal("11400"),
            total_operating_expenses=Decimal("3900"),
            total_noi=Decimal("7500"),  # 6 months
            total_mortgage_payments=Decimal("4500"),
            total_mortgage_principal=Decimal("1200"),
            total_mortgage_interest=Decimal("3300"),
            total_net_cashflow=Decimal("3000"),  # 6 months
            total_net_cashflow_usd=Decimal("2222"),
            total_noi_usd=Decimal("5555"),
        )
        property_value = Decimal("500000")
        remaining_balance = Decimal("350000")
        down_payment = Decimal("100000")
        is_partial_year = True
        months_in_year = 6

        metrics = calculate_annual_metrics(
            annual_summary,
            property_value,
            remaining_balance,
            down_payment,
            is_partial_year,
            months_in_year,
        )

        # Annualized NOI: (7500 / 6) * 12 = 15000
        # Cap rate: 15000 / 500000 = 0.03
        assert metrics.cap_rate == Decimal("0.0300")
        # Annualized cash flow: (3000 / 6) * 12 = 6000
        # Cash on cash: 6000 / 100000 = 0.06
        assert metrics.cash_on_cash == Decimal("0.0600")
        # Equity: 500000 - 350000 = 150000
        assert metrics.equity_position == Decimal("150000")
        assert metrics.year == 2024
        assert metrics.is_partial_year is True

    def test_annual_metrics_partial_year_3_months(self):
        """Calculate annual metrics for a 3-month partial year."""
        annual_summary = AnnualOperatingSummary(
            year=2024,
            total_gross_rent=Decimal("6000"),
            total_vacancy_deduction=Decimal("300"),
            total_effective_rent=Decimal("5700"),
            total_operating_expenses=Decimal("1950"),
            total_noi=Decimal("3750"),  # 3 months
            total_mortgage_payments=Decimal("2250"),
            total_mortgage_principal=Decimal("600"),
            total_mortgage_interest=Decimal("1650"),
            total_net_cashflow=Decimal("1500"),  # 3 months
            total_net_cashflow_usd=Decimal("1111"),
            total_noi_usd=Decimal("2777"),
        )
        property_value = Decimal("500000")
        remaining_balance = Decimal("350000")
        down_payment = Decimal("100000")
        is_partial_year = True
        months_in_year = 3

        metrics = calculate_annual_metrics(
            annual_summary,
            property_value,
            remaining_balance,
            down_payment,
            is_partial_year,
            months_in_year,
        )

        # Annualized NOI: (3750 / 3) * 12 = 15000
        # Cap rate: 15000 / 500000 = 0.03
        assert metrics.cap_rate == Decimal("0.0300")
        # Annualized cash flow: (1500 / 3) * 12 = 6000
        # Cash on cash: 6000 / 100000 = 0.06
        assert metrics.cash_on_cash == Decimal("0.0600")
        assert metrics.year == 2024
        assert metrics.is_partial_year is True
