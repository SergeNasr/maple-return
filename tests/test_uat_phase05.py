"""UAT integration tests for Phase 05: Exit Strategy.

These tests verify user-observable behavior from the owner's perspective:
- Can I see the net proceeds waterfall from selling my property?
- Does the model handle underwater sales correctly?
- Can I see my appreciation rate over the hold period?
- Are exit amounts shown in both CAD and USD?
- Does total return truncate cash flows at the sale year?
- Can I see total profit and simple ROI?
- Does hold-period IRR include exit proceeds?
"""

from datetime import date
from decimal import Decimal

from dateutil.relativedelta import relativedelta

from maple_return.cashflow import MonthlyCashFlow
from maple_return.exit_model import (
    ExitInput,
    ExitResult,
    TotalReturnSummary,
    calculate_appreciation_rate,
    calculate_exit,
    calculate_total_return,
)


def _make_exit_input(**overrides) -> ExitInput:
    """Helper to create an ExitInput with sensible defaults."""
    defaults = dict(
        sale_price=Decimal("600000"),
        sale_year=5,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000"),
        remaining_mortgage_balance=Decimal("350000"),
        purchase_price=Decimal("500000"),
        down_payment=Decimal("100000"),
        cad_per_usd=Decimal("1.35"),
    )
    defaults.update(overrides)
    return ExitInput(**defaults)


def _make_cashflow(month: date, net_cashflow: Decimal = Decimal("200")) -> MonthlyCashFlow:
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
        mortgage_payment=Decimal("1050"),
        mortgage_principal=Decimal("500"),
        mortgage_interest=Decimal("550"),
        net_cashflow=net_cashflow,
        net_cashflow_usd=Decimal("148.15"),
        noi_usd=Decimal("925.93"),
    )


class TestUATExitWaterfall:
    """UAT: Owner can see where sale proceeds go."""

    def test_waterfall_commission_and_net_proceeds(self):
        """$600k sale, 5% commission, $5k closing, $350k mortgage → $215k net."""
        result = calculate_exit(_make_exit_input())

        assert result.commission == Decimal("30000.00")
        assert result.net_proceeds == Decimal("215000.00")
        # Verify waterfall arithmetic: sale - commission - closing - mortgage = net
        expected = (
            result.sale_price - result.commission - result.closing_costs - result.mortgage_payoff
        )
        assert result.net_proceeds == expected

    def test_underwater_sale_gives_negative_proceeds(self):
        """Sale below mortgage + costs produces negative net proceeds."""
        result = calculate_exit(
            _make_exit_input(
                sale_price=Decimal("300000"),
                remaining_mortgage_balance=Decimal("350000"),
            )
        )

        assert result.net_proceeds < Decimal("0")
        # 300k - 15k commission - 5k closing - 350k mortgage = -70k
        assert result.net_proceeds == Decimal("-70000.00")

    def test_zero_commission_private_sale(self):
        """Private sale with 0% commission keeps full sale price minus other costs."""
        result = calculate_exit(_make_exit_input(commission_rate=Decimal("0")))

        assert result.commission == Decimal("0.00")
        # 600k - 0 - 5k - 350k = 245k
        assert result.net_proceeds == Decimal("245000.00")


class TestUATAppreciationRate:
    """UAT: Owner can see annualized property value growth."""

    def test_appreciation_rate_5_year_hold(self):
        """$500k → $600k over 5 years gives ~3.71% annualized."""
        rate = calculate_appreciation_rate(Decimal("500000"), Decimal("600000"), 5)

        assert rate == Decimal("0.0371")

    def test_depreciation_shows_negative_rate(self):
        """Sale below purchase price gives negative appreciation rate."""
        rate = calculate_appreciation_rate(Decimal("500000"), Decimal("400000"), 5)

        assert rate < Decimal("0")

    def test_zero_years_returns_zero(self):
        """Immediate sale returns 0% appreciation (no time for growth)."""
        rate = calculate_appreciation_rate(Decimal("500000"), Decimal("600000"), 0)

        assert rate == Decimal("0.0000")


class TestUATExitUSDConversion:
    """UAT: Owner can see exit amounts in USD."""

    def test_sale_price_and_net_proceeds_in_usd(self):
        """Both sale price and net proceeds converted to USD at CAD/USD rate."""
        result = calculate_exit(_make_exit_input(cad_per_usd=Decimal("1.35")))

        # Sale price USD: 600k / 1.35 ≈ 444,444.44
        assert result.sale_price_usd is not None
        assert result.sale_price_usd < result.sale_price  # USD < CAD when rate > 1

        # Net proceeds USD: 215k / 1.35 ≈ 159,259.26
        assert result.net_proceeds_usd is not None
        assert result.net_proceeds_usd < result.net_proceeds


class TestUATCashFlowTruncation:
    """UAT: Total return only uses cash flows up to sale year."""

    def test_30_years_truncated_to_5_year_sale(self):
        """360 months of cash flows truncated to 60 when selling in year 5."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(360)]

        result = calculate_total_return(_make_exit_input(), cashflows, start)

        assert result.total_months == 60
        assert result.hold_period_years == 5


class TestUATTotalProfitAndROI:
    """UAT: Owner can see total profit and simple ROI."""

    def test_total_profit_formula(self):
        """Total profit = cumulative cash flow + net proceeds - down payment."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        result = calculate_total_return(_make_exit_input(), cashflows, start)

        # Cumulative: 60 months * $200/month = $12,000
        assert result.cumulative_net_cashflow == Decimal("12000")
        # Total profit: 12,000 + 215,000 - 100,000 = 127,000
        assert result.total_profit == Decimal("127000.00")

    def test_simple_roi(self):
        """Simple ROI = total profit / down payment."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        result = calculate_total_return(_make_exit_input(), cashflows, start)

        # ROI: 127,000 / 100,000 = 1.2700
        assert result.simple_roi == Decimal("1.2700")

    def test_zero_down_payment_roi_is_zero(self):
        """Zero down payment returns ROI = 0.0000, no exception."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        result = calculate_total_return(
            _make_exit_input(down_payment=Decimal("0")), cashflows, start
        )

        assert result.simple_roi == Decimal("0.0000")

    def test_total_profit_usd_present(self):
        """Total profit has USD conversion."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        result = calculate_total_return(_make_exit_input(), cashflows, start)

        assert result.total_profit_usd is not None
        assert result.total_profit_usd < result.total_profit


class TestUATHoldPeriodIRR:
    """UAT: Owner can see hold-period IRR with exit."""

    def test_irr_is_positive_for_profitable_exit(self):
        """Profitable 5-year hold produces a positive IRR."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        result = calculate_total_return(_make_exit_input(), cashflows, start)

        assert result.hold_period_irr is not None
        assert result.hold_period_irr > Decimal("0")

    def test_irr_is_none_for_year_zero_sale(self):
        """Immediate sale (year 0) has no cash flows, IRR = None."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        result = calculate_total_return(
            _make_exit_input(sale_year=0), cashflows, start
        )

        assert result.total_months == 0
        assert result.hold_period_irr is None

    def test_exit_result_nested_in_summary(self):
        """TotalReturnSummary contains full exit waterfall breakdown."""
        start = date(2020, 6, 15)
        cashflows = [_make_cashflow(start + relativedelta(months=i)) for i in range(60)]

        result = calculate_total_return(_make_exit_input(), cashflows, start)

        assert isinstance(result.exit_result, ExitResult)
        assert result.exit_result.commission == Decimal("30000.00")
        assert result.exit_result.net_proceeds == Decimal("215000.00")
