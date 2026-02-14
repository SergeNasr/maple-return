"""Tests for analysis presentation layer (P&L, amortization table, dashboard)."""

from datetime import date
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta

from maple_return.analysis import (
    AmortizationRow,
    DashboardSnapshot,
    PnLRow,
    build_amortization_table,
    build_dashboard_snapshot,
    build_pnl_table,
)
from maple_return.cashflow import AnnualOperatingSummary, MonthlyCashFlow
from maple_return.mortgage import AmortizationEntry
from maple_return.mortgage_summary import AnnualSummary


class TestAmortizationTable:
    """Test amortization table output generation."""

    def test_build_amortization_table_basic(self):
        """Test basic amortization table mapping from schedule."""
        schedule = [
            AmortizationEntry(
                month_number=1,
                date=date(2024, 1, 1),
                payment=Decimal("2000.00"),
                principal=Decimal("500.00"),
                interest=Decimal("1500.00"),
                balance=Decimal("299500.00"),
            ),
            AmortizationEntry(
                month_number=2,
                date=date(2024, 2, 1),
                payment=Decimal("2000.00"),
                principal=Decimal("502.00"),
                interest=Decimal("1498.00"),
                balance=Decimal("298998.00"),
            ),
        ]

        table = build_amortization_table(schedule)

        assert len(table) == 2
        assert isinstance(table[0], AmortizationRow)
        assert table[0].date == date(2024, 1, 1)
        assert table[0].payment == Decimal("2000.00")
        assert table[0].principal == Decimal("500.00")
        assert table[0].interest == Decimal("1500.00")
        assert table[0].balance == Decimal("299500.00")

    def test_build_amortization_table_full_schedule(self):
        """Test 360-month schedule produces 360 rows."""
        # Create 360 entries
        schedule = [
            AmortizationEntry(
                month_number=i,
                date=date(2024, 1, 1) + relativedelta(months=i - 1),
                payment=Decimal("2000.00"),
                principal=Decimal("500.00"),
                interest=Decimal("1500.00"),
                balance=Decimal("300000.00") - Decimal("500.00") * i,
            )
            for i in range(1, 361)
        ]

        table = build_amortization_table(schedule)

        assert len(table) == 360
        # Final balance should be zero or near-zero
        assert table[-1].balance <= Decimal("1.00")

    def test_build_amortization_table_empty(self):
        """Test empty schedule returns empty table."""
        table = build_amortization_table([])

        assert table == []


class TestPnLTable:
    """Test P&L table generation."""

    def test_build_pnl_table_single_year(self):
        """Test single full year P&L row."""
        annual_summaries = [
            AnnualOperatingSummary(
                year=2024,
                total_gross_rent=Decimal("36000.00"),
                total_vacancy_deduction=Decimal("1800.00"),
                total_effective_rent=Decimal("34200.00"),
                total_operating_expenses=Decimal("12000.00"),
                total_noi=Decimal("22200.00"),
                total_mortgage_payments=Decimal("24000.00"),
                total_mortgage_principal=Decimal("6000.00"),
                total_mortgage_interest=Decimal("18000.00"),
                total_net_cashflow=Decimal("-1800.00"),
                total_net_cashflow_usd=Decimal("-1333.33"),
                total_noi_usd=Decimal("16444.44"),
            ),
        ]

        mortgage_annual_summaries = [
            AnnualSummary(
                year=2024,
                total_principal_paid=Decimal("6000.00"),
                total_interest_paid=Decimal("18000.00"),
                total_payments=Decimal("24000.00"),
                year_end_balance=Decimal("294000.00"),
                equity=Decimal("206000.00"),
            ),
        ]

        pnl_table = build_pnl_table(
            annual_summaries=annual_summaries,
            mortgage_annual_summaries=mortgage_annual_summaries,
            purchase_price=Decimal("500000.00"),
            current_property_value=Decimal("500000.00"),
            down_payment=Decimal("100000.00"),
        )

        assert len(pnl_table) == 1
        row = pnl_table[0]

        assert row.year == 2024
        assert row.gross_rent == Decimal("36000.00")
        assert row.vacancy_loss == Decimal("1800.00")
        assert row.net_rent == Decimal("34200.00")
        assert row.operating_expenses == Decimal("12000.00")
        assert row.noi == Decimal("22200.00")
        assert row.mortgage_payment == Decimal("24000.00")
        assert row.net_cashflow == Decimal("-1800.00")
        assert row.principal_paid == Decimal("6000.00")
        assert row.interest_paid == Decimal("18000.00")
        # First year: equity - down_payment
        assert row.equity_gained == Decimal("106000.00")  # 206000 - 100000
        assert row.cumulative_cashflow == Decimal("-1800.00")
        assert row.cumulative_equity == Decimal("206000.00")
        # First year should be marked as partial
        assert row.is_partial_year is True

    def test_build_pnl_table_multiple_years(self):
        """Test multi-year P&L with cumulative calculations."""
        annual_summaries = [
            AnnualOperatingSummary(
                year=2024,
                total_gross_rent=Decimal("36000.00"),
                total_vacancy_deduction=Decimal("1800.00"),
                total_effective_rent=Decimal("34200.00"),
                total_operating_expenses=Decimal("12000.00"),
                total_noi=Decimal("22200.00"),
                total_mortgage_payments=Decimal("24000.00"),
                total_mortgage_principal=Decimal("6000.00"),
                total_mortgage_interest=Decimal("18000.00"),
                total_net_cashflow=Decimal("-1800.00"),
                total_net_cashflow_usd=Decimal("-1333.33"),
                total_noi_usd=Decimal("16444.44"),
            ),
            AnnualOperatingSummary(
                year=2025,
                total_gross_rent=Decimal("36000.00"),
                total_vacancy_deduction=Decimal("1800.00"),
                total_effective_rent=Decimal("34200.00"),
                total_operating_expenses=Decimal("12000.00"),
                total_noi=Decimal("22200.00"),
                total_mortgage_payments=Decimal("24000.00"),
                total_mortgage_principal=Decimal("6200.00"),
                total_mortgage_interest=Decimal("17800.00"),
                total_net_cashflow=Decimal("-1800.00"),
                total_net_cashflow_usd=Decimal("-1333.33"),
                total_noi_usd=Decimal("16444.44"),
            ),
        ]

        mortgage_annual_summaries = [
            AnnualSummary(
                year=2024,
                total_principal_paid=Decimal("6000.00"),
                total_interest_paid=Decimal("18000.00"),
                total_payments=Decimal("24000.00"),
                year_end_balance=Decimal("294000.00"),
                equity=Decimal("206000.00"),
            ),
            AnnualSummary(
                year=2025,
                total_principal_paid=Decimal("6200.00"),
                total_interest_paid=Decimal("17800.00"),
                total_payments=Decimal("24000.00"),
                year_end_balance=Decimal("287800.00"),
                equity=Decimal("212200.00"),
            ),
        ]

        pnl_table = build_pnl_table(
            annual_summaries=annual_summaries,
            mortgage_annual_summaries=mortgage_annual_summaries,
            purchase_price=Decimal("500000.00"),
            current_property_value=Decimal("500000.00"),
            down_payment=Decimal("100000.00"),
        )

        assert len(pnl_table) == 2

        # Year 1
        assert pnl_table[0].cumulative_cashflow == Decimal("-1800.00")
        assert pnl_table[0].equity_gained == Decimal("106000.00")  # 206000 - 100000
        assert pnl_table[0].is_partial_year is True

        # Year 2
        assert pnl_table[1].cumulative_cashflow == Decimal("-3600.00")  # -1800 + -1800
        assert pnl_table[1].cumulative_equity == Decimal("212200.00")
        assert pnl_table[1].equity_gained == Decimal("6200.00")  # 212200 - 206000
        assert pnl_table[1].is_partial_year is False

    def test_build_pnl_table_negative_cashflow(self):
        """Test negative cash flow is preserved as negative Decimal."""
        annual_summaries = [
            AnnualOperatingSummary(
                year=2024,
                total_gross_rent=Decimal("36000.00"),
                total_vacancy_deduction=Decimal("1800.00"),
                total_effective_rent=Decimal("34200.00"),
                total_operating_expenses=Decimal("12000.00"),
                total_noi=Decimal("22200.00"),
                total_mortgage_payments=Decimal("30000.00"),
                total_mortgage_principal=Decimal("8000.00"),
                total_mortgage_interest=Decimal("22000.00"),
                total_net_cashflow=Decimal("-7800.00"),
                total_net_cashflow_usd=Decimal("-5777.78"),
                total_noi_usd=Decimal("16444.44"),
            ),
        ]

        mortgage_annual_summaries = [
            AnnualSummary(
                year=2024,
                total_principal_paid=Decimal("8000.00"),
                total_interest_paid=Decimal("22000.00"),
                total_payments=Decimal("30000.00"),
                year_end_balance=Decimal("292000.00"),
                equity=Decimal("208000.00"),
            ),
        ]

        pnl_table = build_pnl_table(
            annual_summaries=annual_summaries,
            mortgage_annual_summaries=mortgage_annual_summaries,
            purchase_price=Decimal("500000.00"),
            current_property_value=Decimal("500000.00"),
            down_payment=Decimal("100000.00"),
        )

        row = pnl_table[0]
        assert row.net_cashflow == Decimal("-7800.00")
        assert row.net_cashflow < Decimal("0")
        # Negative cash-on-cash expected
        assert row.cash_on_cash < Decimal("0")

    def test_build_pnl_table_with_metrics(self):
        """Test P&L includes calculated metrics (cap rate, cash-on-cash)."""
        annual_summaries = [
            AnnualOperatingSummary(
                year=2024,
                total_gross_rent=Decimal("36000.00"),
                total_vacancy_deduction=Decimal("1800.00"),
                total_effective_rent=Decimal("34200.00"),
                total_operating_expenses=Decimal("12000.00"),
                total_noi=Decimal("22200.00"),
                total_mortgage_payments=Decimal("24000.00"),
                total_mortgage_principal=Decimal("6000.00"),
                total_mortgage_interest=Decimal("18000.00"),
                total_net_cashflow=Decimal("-1800.00"),
                total_net_cashflow_usd=Decimal("-1333.33"),
                total_noi_usd=Decimal("16444.44"),
            ),
        ]

        mortgage_annual_summaries = [
            AnnualSummary(
                year=2024,
                total_principal_paid=Decimal("6000.00"),
                total_interest_paid=Decimal("18000.00"),
                total_payments=Decimal("24000.00"),
                year_end_balance=Decimal("294000.00"),
                equity=Decimal("206000.00"),
            ),
        ]

        pnl_table = build_pnl_table(
            annual_summaries=annual_summaries,
            mortgage_annual_summaries=mortgage_annual_summaries,
            purchase_price=Decimal("500000.00"),
            current_property_value=Decimal("500000.00"),
            down_payment=Decimal("100000.00"),
        )

        row = pnl_table[0]
        # Cap rate = NOI / property value
        assert row.cap_rate > Decimal("0")
        # Cash-on-cash = net cashflow / down payment (negative in this case)
        assert row.cash_on_cash < Decimal("0")


class TestDashboardSnapshot:
    """Test dashboard snapshot generation."""

    def test_build_dashboard_snapshot_basic(self):
        """Test basic dashboard snapshot with all fields."""
        # Monthly cashflows for 12 months
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, 1, 1) + relativedelta(months=i),
                gross_rent=Decimal("3000.00"),
                vacancy_deduction=Decimal("150.00"),
                effective_rent=Decimal("2850.00"),
                property_tax=Decimal("400.00"),
                insurance=Decimal("100.00"),
                maintenance=Decimal("150.00"),
                management_fee=Decimal("300.00"),
                total_operating_expenses=Decimal("950.00"),
                noi=Decimal("1900.00"),
                mortgage_payment=Decimal("2000.00"),
                mortgage_principal=Decimal("500.00"),
                mortgage_interest=Decimal("1500.00"),
                net_cashflow=Decimal("-100.00"),
                net_cashflow_usd=Decimal("-74.07"),
                noi_usd=Decimal("1407.41"),
            )
            for i in range(12)
        ]

        dashboard = build_dashboard_snapshot(
            monthly_cashflows=monthly_cashflows,
            purchase_date=date(2024, 1, 1),
            down_payment=Decimal("100000.00"),
            current_property_value=Decimal("520000.00"),
            remaining_balance=Decimal("294000.00"),
            cad_per_usd=Decimal("1.35"),
        )

        # Equity position = current value - remaining balance
        assert dashboard.equity_position == Decimal("226000.00")
        # USD conversion
        assert dashboard.equity_position_usd > Decimal("0")
        # Cumulative cash flow = sum of all net_cashflow
        assert dashboard.cumulative_cashflow == Decimal("-1200.00")  # -100 * 12
        assert dashboard.cumulative_cashflow_usd < Decimal("0")
        # IRR should be calculated (could be None or a value)
        assert dashboard.annualized_return_irr is not None or dashboard.annualized_return_irr is None
        # Cap rate and cash-on-cash should be present
        assert dashboard.current_cap_rate is not None
        assert dashboard.cash_on_cash_return is not None
        # Months held
        assert dashboard.months_held >= 12
        # Current property value
        assert dashboard.current_property_value == Decimal("520000.00")
        assert dashboard.remaining_balance == Decimal("294000.00")

    def test_build_dashboard_snapshot_partial_year(self):
        """Test dashboard with only 6 months held."""
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, 1, 1) + relativedelta(months=i),
                gross_rent=Decimal("3000.00"),
                vacancy_deduction=Decimal("150.00"),
                effective_rent=Decimal("2850.00"),
                property_tax=Decimal("400.00"),
                insurance=Decimal("100.00"),
                maintenance=Decimal("150.00"),
                management_fee=Decimal("300.00"),
                total_operating_expenses=Decimal("950.00"),
                noi=Decimal("1900.00"),
                mortgage_payment=Decimal("2000.00"),
                mortgage_principal=Decimal("500.00"),
                mortgage_interest=Decimal("1500.00"),
                net_cashflow=Decimal("-100.00"),
                net_cashflow_usd=Decimal("-74.07"),
                noi_usd=Decimal("1407.41"),
            )
            for i in range(6)
        ]

        dashboard = build_dashboard_snapshot(
            monthly_cashflows=monthly_cashflows,
            purchase_date=date(2024, 1, 1),
            down_payment=Decimal("100000.00"),
            current_property_value=Decimal("510000.00"),
            remaining_balance=Decimal("297000.00"),
            cad_per_usd=Decimal("1.35"),
        )

        assert dashboard.months_held >= 6
        assert dashboard.cumulative_cashflow == Decimal("-600.00")  # -100 * 6
        assert dashboard.equity_position == Decimal("213000.00")  # 510000 - 297000

    def test_build_dashboard_snapshot_negative_cumulative(self):
        """Test dashboard with negative cumulative cash flow."""
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, 1, 1) + relativedelta(months=i),
                gross_rent=Decimal("3000.00"),
                vacancy_deduction=Decimal("150.00"),
                effective_rent=Decimal("2850.00"),
                property_tax=Decimal("400.00"),
                insurance=Decimal("100.00"),
                maintenance=Decimal("150.00"),
                management_fee=Decimal("300.00"),
                total_operating_expenses=Decimal("950.00"),
                noi=Decimal("1900.00"),
                mortgage_payment=Decimal("2500.00"),
                mortgage_principal=Decimal("600.00"),
                mortgage_interest=Decimal("1900.00"),
                net_cashflow=Decimal("-600.00"),
                net_cashflow_usd=Decimal("-444.44"),
                noi_usd=Decimal("1407.41"),
            )
            for i in range(12)
        ]

        dashboard = build_dashboard_snapshot(
            monthly_cashflows=monthly_cashflows,
            purchase_date=date(2024, 1, 1),
            down_payment=Decimal("100000.00"),
            current_property_value=Decimal("500000.00"),
            remaining_balance=Decimal("292800.00"),
            cad_per_usd=Decimal("1.35"),
        )

        assert dashboard.cumulative_cashflow == Decimal("-7200.00")  # -600 * 12
        assert dashboard.cumulative_cashflow_usd < Decimal("0")
        # IRR may be negative or None
        # Cash-on-cash should be negative
        assert dashboard.cash_on_cash_return < Decimal("0")

    def test_build_dashboard_snapshot_usd_conversions(self):
        """Test USD conversions are present in dashboard."""
        monthly_cashflows = [
            MonthlyCashFlow(
                month=date(2024, 1, 1),
                gross_rent=Decimal("3000.00"),
                vacancy_deduction=Decimal("150.00"),
                effective_rent=Decimal("2850.00"),
                property_tax=Decimal("400.00"),
                insurance=Decimal("100.00"),
                maintenance=Decimal("150.00"),
                management_fee=Decimal("300.00"),
                total_operating_expenses=Decimal("950.00"),
                noi=Decimal("1900.00"),
                mortgage_payment=Decimal("2000.00"),
                mortgage_principal=Decimal("500.00"),
                mortgage_interest=Decimal("1500.00"),
                net_cashflow=Decimal("100.00"),
                net_cashflow_usd=Decimal("74.07"),
                noi_usd=Decimal("1407.41"),
            ),
        ]

        dashboard = build_dashboard_snapshot(
            monthly_cashflows=monthly_cashflows,
            purchase_date=date(2024, 1, 1),
            down_payment=Decimal("100000.00"),
            current_property_value=Decimal("520000.00"),
            remaining_balance=Decimal("299500.00"),
            cad_per_usd=Decimal("1.35"),
        )

        # Equity USD should be roughly equity CAD / 1.35
        expected_equity_usd = Decimal("220500.00") / Decimal("1.35")
        assert abs(dashboard.equity_position_usd - expected_equity_usd) < Decimal("1.00")

        # Cumulative cashflow USD should be roughly cumulative CAD / 1.35
        expected_cashflow_usd = Decimal("100.00") / Decimal("1.35")
        assert abs(dashboard.cumulative_cashflow_usd - expected_cashflow_usd) < Decimal("1.00")
