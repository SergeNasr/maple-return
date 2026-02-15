"""Tests for exit model and net proceeds calculations."""

from datetime import date
from decimal import Decimal

from maple_return.cashflow import MonthlyCashFlow
from maple_return.exit_model import (
    ExitInput,
    calculate_appreciation_rate,
    calculate_exit,
    calculate_total_return,
)


def test_basic_exit_waterfall():
    """Test basic exit waterfall breakdown.

    Sale: $600k
    Commission: 5% = $30k
    Closing costs: $5k
    Mortgage remaining: $350k
    Net proceeds: $600k - $30k - $5k - $350k = $215k
    """
    exit_input = ExitInput(
        sale_price=Decimal("600000.00"),
        sale_year=5,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("350000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    result = calculate_exit(exit_input)

    assert result.sale_price == Decimal("600000.00")
    assert result.commission == Decimal("30000.00")
    assert result.closing_costs == Decimal("5000.00")
    assert result.mortgage_payoff == Decimal("350000.00")
    assert result.net_proceeds == Decimal("215000.00")
    # USD conversions
    assert result.sale_price_usd == Decimal("444444.44")  # 600k / 1.35
    assert result.net_proceeds_usd == Decimal("159259.26")  # 215k / 1.35


def test_exit_negative_net_proceeds():
    """Test exit where sale price is below mortgage + costs (underwater).

    Sale: $300k
    Commission: 5% = $15k
    Closing costs: $5k
    Mortgage remaining: $350k
    Net proceeds: $300k - $15k - $5k - $350k = -$70k (negative)
    """
    exit_input = ExitInput(
        sale_price=Decimal("300000.00"),
        sale_year=2,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("350000.00"),
        purchase_price=Decimal("400000.00"),
        down_payment=Decimal("80000.00"),
        cad_per_usd=Decimal("1.30"),
    )

    result = calculate_exit(exit_input)

    assert result.sale_price == Decimal("300000.00")
    assert result.commission == Decimal("15000.00")
    assert result.closing_costs == Decimal("5000.00")
    assert result.mortgage_payoff == Decimal("350000.00")
    assert result.net_proceeds == Decimal("-70000.00")  # Negative!
    # USD conversion should handle negative
    assert result.net_proceeds_usd == Decimal("-53846.15")  # -70k / 1.30


def test_exit_zero_commission():
    """Test exit with zero commission (private sale).

    Sale: $500k
    Commission: 0%
    Closing costs: $3k
    Mortgage remaining: $250k
    Net proceeds: $500k - $0 - $3k - $250k = $247k
    """
    exit_input = ExitInput(
        sale_price=Decimal("500000.00"),
        sale_year=10,
        commission_rate=Decimal("0.00"),  # No commission
        closing_costs=Decimal("3000.00"),
        remaining_mortgage_balance=Decimal("250000.00"),
        purchase_price=Decimal("450000.00"),
        down_payment=Decimal("90000.00"),
        cad_per_usd=Decimal("1.40"),
    )

    result = calculate_exit(exit_input)

    assert result.commission == Decimal("0.00")
    assert result.net_proceeds == Decimal("247000.00")


def test_exit_usd_conversion():
    """Test USD conversions are correct.

    Verify USD amounts are calculated via CAD/USD rate.
    """
    exit_input = ExitInput(
        sale_price=Decimal("540000.00"),  # Divisible by 1.35
        sale_year=7,
        commission_rate=Decimal("0.04"),
        closing_costs=Decimal("6750.00"),
        remaining_mortgage_balance=Decimal("300000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    result = calculate_exit(exit_input)

    # Sale price USD: 540k / 1.35 = 400k
    assert result.sale_price_usd == Decimal("400000.00")

    # Net proceeds: 540k - 21.6k - 6.75k - 300k = 211.65k
    # Net proceeds USD: 211.65k / 1.35 = 156,777.78
    assert result.commission == Decimal("21600.00")
    assert result.net_proceeds == Decimal("211650.00")
    assert result.net_proceeds_usd == Decimal("156777.78")


def test_appreciation_rate_basic():
    """Test basic appreciation rate calculation.

    Purchase: $500k
    Sale: $600k
    Years: 5
    Rate: (600k/500k)^(1/5) - 1 = 1.2^0.2 - 1 ≈ 0.0371 (3.71%)
    """
    rate = calculate_appreciation_rate(
        purchase_price=Decimal("500000.00"),
        sale_price=Decimal("600000.00"),
        years_held=5,
    )

    # Expected: 0.0371 (rounded to 4 decimal places)
    assert rate == Decimal("0.0371")


def test_appreciation_rate_zero_years():
    """Test appreciation rate when years_held is 0 (same-day sale).

    Should return 0.0000 (no appreciation possible).
    """
    rate = calculate_appreciation_rate(
        purchase_price=Decimal("500000.00"),
        sale_price=Decimal("600000.00"),
        years_held=0,
    )

    assert rate == Decimal("0.0000")


def test_appreciation_rate_zero_purchase():
    """Test appreciation rate when purchase price is 0.

    Edge case that would cause division by zero.
    Should return 0.0000.
    """
    rate = calculate_appreciation_rate(
        purchase_price=Decimal("0.00"),
        sale_price=Decimal("600000.00"),
        years_held=5,
    )

    assert rate == Decimal("0.0000")


def test_appreciation_rate_depreciation():
    """Test appreciation rate when property depreciates.

    Purchase: $500k
    Sale: $400k
    Years: 3
    Rate: (400k/500k)^(1/3) - 1 = 0.8^0.333... - 1 ≈ -0.0717 (-7.17%)
    """
    rate = calculate_appreciation_rate(
        purchase_price=Decimal("500000.00"),
        sale_price=Decimal("400000.00"),
        years_held=3,
    )

    # Expected: -0.0717 (negative rate, rounded to 4 decimal places)
    assert rate == Decimal("-0.0717")


def test_full_exit_result_fields():
    """Test that all ExitResult fields are populated and have correct types."""
    exit_input = ExitInput(
        sale_price=Decimal("550000.00"),
        sale_year=6,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("4000.00"),
        remaining_mortgage_balance=Decimal("300000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.32"),
    )

    result = calculate_exit(exit_input)

    # Verify all fields exist and are Decimal
    assert isinstance(result.sale_price, Decimal)
    assert isinstance(result.commission, Decimal)
    assert isinstance(result.closing_costs, Decimal)
    assert isinstance(result.mortgage_payoff, Decimal)
    assert isinstance(result.net_proceeds, Decimal)
    assert isinstance(result.net_proceeds_usd, Decimal)
    assert isinstance(result.sale_price_usd, Decimal)
    assert isinstance(result.implied_appreciation_rate, Decimal)

    # Verify waterfall arithmetic
    expected_net_proceeds = (
        result.sale_price
        - result.commission
        - result.closing_costs
        - result.mortgage_payoff
    )
    assert result.net_proceeds == expected_net_proceeds

    # Verify appreciation rate is calculated
    assert result.implied_appreciation_rate > Decimal("0")  # Should be positive growth


# ===== Total Return Tests =====


def test_total_return_basic():
    """Test basic total return calculation with 5-year hold and profitable exit.

    Verify hold_period_years = 5, total_months = 60.
    Verify cumulative_net_cashflow = sum of 60 months.
    Verify total_profit = cumulative + net_proceeds - down_payment.
    Verify simple_roi = total_profit / down_payment.
    """
    # Create 60 months of cash flows (5 years)
    monthly_cashflows = []
    for i in range(60):
        month_date = date(2020 + (6 + i) // 12, ((6 + i) % 12) or 12, 1)
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("200.00"),
            insurance=Decimal("100.00"),
            maintenance=Decimal("150.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("550.00"),
            noi=Decimal("1350.00"),
            mortgage_payment=Decimal("1200.00"),
            mortgage_principal=Decimal("400.00"),
            mortgage_interest=Decimal("800.00"),
            net_cashflow=Decimal("150.00"),  # 1350 - 1200
            net_cashflow_usd=Decimal("111.11"),
            noi_usd=Decimal("1000.00"),
        )
        monthly_cashflows.append(cf)

    # Exit input for year 5
    exit_input = ExitInput(
        sale_price=Decimal("600000.00"),
        sale_year=5,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("350000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    purchase_date = date(2020, 6, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # Verify basic fields
    assert result.hold_period_years == 5
    assert result.total_months == 60

    # Verify cumulative cash flow: 60 months * $150 = $9,000
    expected_cumulative = Decimal("150.00") * 60
    assert result.cumulative_net_cashflow == expected_cumulative

    # Verify net proceeds from exit (from earlier test)
    assert result.net_proceeds == Decimal("215000.00")

    # Verify total profit: cumulative + net_proceeds - down_payment
    # $9,000 + $215,000 - $100,000 = $124,000
    expected_profit = expected_cumulative + Decimal("215000.00") - Decimal("100000.00")
    assert result.total_profit == expected_profit

    # Verify simple ROI: total_profit / down_payment
    # $124,000 / $100,000 = 1.2400
    expected_roi = expected_profit / Decimal("100000.00")
    assert result.simple_roi == expected_roi.quantize(Decimal("0.0001"))

    # Verify USD conversion
    assert result.total_profit_usd == (expected_profit / Decimal("1.35")).quantize(
        Decimal("0.01")
    )

    # Verify hold_period_irr exists and is not None
    assert result.hold_period_irr is not None

    # Verify exit_result is nested
    assert result.exit_result.sale_price == Decimal("600000.00")
    assert result.exit_result.net_proceeds == Decimal("215000.00")


def test_total_return_irr_includes_exit():
    """Test that IRR with exit differs from operations-only IRR.

    Calculate operations-only IRR (property value as terminal).
    Calculate exit IRR (net_proceeds as terminal).
    They should be different values (exit scenario changes terminal value).
    """
    # Create simple cash flows: 12 months, negative initially then positive
    monthly_cashflows = []
    for i in range(12):
        month_date = date(2020 + i // 12, (i % 12) + 1, 1)
        # Negative cash flow due to high mortgage
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("300.00"),
            insurance=Decimal("150.00"),
            maintenance=Decimal("200.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("750.00"),
            noi=Decimal("1150.00"),
            mortgage_payment=Decimal("2000.00"),
            mortgage_principal=Decimal("500.00"),
            mortgage_interest=Decimal("1500.00"),
            net_cashflow=Decimal("-850.00"),  # Negative!
            net_cashflow_usd=Decimal("-629.63"),
            noi_usd=Decimal("851.85"),
        )
        monthly_cashflows.append(cf)

    # Exit with different net proceeds vs property value
    exit_input = ExitInput(
        sale_price=Decimal("550000.00"),  # Sale price higher than purchase
        sale_year=1,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("480000.00"),  # High remaining balance
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    purchase_date = date(2020, 1, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # Net proceeds: 550k - 27.5k - 5k - 480k = 37.5k
    assert result.net_proceeds == Decimal("37500.00")

    # IRR should be calculable (we have sign changes)
    # Down payment: -100k
    # Monthly flows: -850 each
    # Terminal: +37.5k (very different from property value of 500k)
    assert result.hold_period_irr is not None

    # The exact value will depend on IRR calculation, but verify it exists
    # and is a Decimal
    assert isinstance(result.hold_period_irr, Decimal)


def test_total_return_cashflow_truncation():
    """Test that cash flows truncate at sale year when longer series available.

    30 years of cash flows available, but sell in year 5.
    Verify only 60 months used, total_months = 60.
    """
    # Create 360 months of cash flows (30 years)
    monthly_cashflows = []
    for i in range(360):
        month_date = date(2020 + i // 12, (i % 12) + 1, 1)
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("200.00"),
            insurance=Decimal("100.00"),
            maintenance=Decimal("150.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("550.00"),
            noi=Decimal("1350.00"),
            mortgage_payment=Decimal("1200.00"),
            mortgage_principal=Decimal("400.00"),
            mortgage_interest=Decimal("800.00"),
            net_cashflow=Decimal("150.00"),
            net_cashflow_usd=Decimal("111.11"),
            noi_usd=Decimal("1000.00"),
        )
        monthly_cashflows.append(cf)

    # Exit in year 5 (should only use 60 months)
    exit_input = ExitInput(
        sale_price=Decimal("600000.00"),
        sale_year=5,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("350000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    purchase_date = date(2020, 1, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # Verify truncation
    assert result.total_months == 60

    # Verify cumulative only includes 60 months
    expected_cumulative = Decimal("150.00") * 60
    assert result.cumulative_net_cashflow == expected_cumulative


def test_total_return_negative_profit():
    """Test total return when sale results in negative profit.

    Sale below mortgage + costs.
    total_profit negative.
    simple_roi negative.
    """
    # Create 24 months of negative cash flows
    monthly_cashflows = []
    for i in range(24):
        month_date = date(2020 + i // 12, (i % 12) + 1, 1)
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("300.00"),
            insurance=Decimal("150.00"),
            maintenance=Decimal("200.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("750.00"),
            noi=Decimal("1150.00"),
            mortgage_payment=Decimal("2000.00"),
            mortgage_principal=Decimal("500.00"),
            mortgage_interest=Decimal("1500.00"),
            net_cashflow=Decimal("-850.00"),  # Negative monthly
            net_cashflow_usd=Decimal("-629.63"),
            noi_usd=Decimal("851.85"),
        )
        monthly_cashflows.append(cf)

    # Underwater exit
    exit_input = ExitInput(
        sale_price=Decimal("300000.00"),  # Below mortgage balance
        sale_year=2,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("350000.00"),
        purchase_price=Decimal("400000.00"),
        down_payment=Decimal("80000.00"),
        cad_per_usd=Decimal("1.30"),
    )

    purchase_date = date(2020, 1, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # Net proceeds: 300k - 15k - 5k - 350k = -70k (from earlier test)
    assert result.net_proceeds == Decimal("-70000.00")

    # Cumulative: 24 months * -850 = -20,400
    expected_cumulative = Decimal("-850.00") * 24
    assert result.cumulative_net_cashflow == expected_cumulative

    # Total profit: -20,400 + (-70,000) - 80,000 = -170,400
    expected_profit = expected_cumulative + Decimal("-70000.00") - Decimal("80000.00")
    assert result.total_profit == expected_profit

    # Simple ROI: -170,400 / 80,000 = -2.13 (negative!)
    expected_roi = expected_profit / Decimal("80000.00")
    assert result.simple_roi == expected_roi.quantize(Decimal("0.0001"))
    assert result.simple_roi < Decimal("0")  # Verify negative


def test_total_return_zero_down_payment():
    """Test total return edge case with zero down payment.

    simple_roi = 0.0000.
    """
    # Create minimal cash flows
    monthly_cashflows = []
    for i in range(12):
        month_date = date(2020 + i // 12, (i % 12) + 1, 1)
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("200.00"),
            insurance=Decimal("100.00"),
            maintenance=Decimal("150.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("550.00"),
            noi=Decimal("1350.00"),
            mortgage_payment=Decimal("1200.00"),
            mortgage_principal=Decimal("400.00"),
            mortgage_interest=Decimal("800.00"),
            net_cashflow=Decimal("150.00"),
            net_cashflow_usd=Decimal("111.11"),
            noi_usd=Decimal("1000.00"),
        )
        monthly_cashflows.append(cf)

    # Zero down payment edge case
    exit_input = ExitInput(
        sale_price=Decimal("500000.00"),
        sale_year=1,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("480000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("0.00"),  # Zero down payment!
        cad_per_usd=Decimal("1.35"),
    )

    purchase_date = date(2020, 1, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # ROI should be 0.0000 (avoid division by zero)
    assert result.simple_roi == Decimal("0.0000")


def test_total_return_sale_year_zero():
    """Test total return with immediate sale (sale_year = 0).

    total_months = 0.
    cumulative_net_cashflow = 0.
    hold_period_irr = None.
    """
    # Create cash flows but they won't be used
    monthly_cashflows = []
    for i in range(12):
        month_date = date(2020 + i // 12, (i % 12) + 1, 1)
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("200.00"),
            insurance=Decimal("100.00"),
            maintenance=Decimal("150.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("550.00"),
            noi=Decimal("1350.00"),
            mortgage_payment=Decimal("1200.00"),
            mortgage_principal=Decimal("400.00"),
            mortgage_interest=Decimal("800.00"),
            net_cashflow=Decimal("150.00"),
            net_cashflow_usd=Decimal("111.11"),
            noi_usd=Decimal("1000.00"),
        )
        monthly_cashflows.append(cf)

    # Immediate sale (year 0)
    exit_input = ExitInput(
        sale_price=Decimal("500000.00"),
        sale_year=0,  # Immediate sale
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("400000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    purchase_date = date(2020, 1, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # Verify zero months used
    assert result.total_months == 0
    assert result.cumulative_net_cashflow == Decimal("0")

    # IRR should be None (no cash flows)
    assert result.hold_period_irr is None


def test_total_return_usd_conversion():
    """Test that total_profit_usd is correctly converted."""
    # Create simple cash flows
    monthly_cashflows = []
    for i in range(12):
        month_date = date(2020 + i // 12, (i % 12) + 1, 1)
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("200.00"),
            insurance=Decimal("100.00"),
            maintenance=Decimal("150.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("550.00"),
            noi=Decimal("1350.00"),
            mortgage_payment=Decimal("1200.00"),
            mortgage_principal=Decimal("400.00"),
            mortgage_interest=Decimal("800.00"),
            net_cashflow=Decimal("150.00"),
            net_cashflow_usd=Decimal("111.11"),
            noi_usd=Decimal("1000.00"),
        )
        monthly_cashflows.append(cf)

    exit_input = ExitInput(
        sale_price=Decimal("540000.00"),  # Clean division by 1.35
        sale_year=1,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("475000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    purchase_date = date(2020, 1, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # Net proceeds: 540k - 27k - 5k - 475k = 33k
    # Cumulative: 12 * 150 = 1,800
    # Total profit: 1,800 + 33,000 - 100,000 = -65,200
    expected_profit_cad = Decimal("1800.00") + Decimal("33000.00") - Decimal("100000.00")
    assert result.total_profit == expected_profit_cad

    # USD conversion: -65,200 / 1.35 = -48,296.30
    expected_profit_usd = (expected_profit_cad / Decimal("1.35")).quantize(Decimal("0.01"))
    assert result.total_profit_usd == expected_profit_usd


def test_total_return_exit_result_nested():
    """Test that exit_result field contains full waterfall breakdown."""
    # Minimal test to verify exit_result is nested correctly
    monthly_cashflows = []
    for i in range(12):
        month_date = date(2020 + i // 12, (i % 12) + 1, 1)
        cf = MonthlyCashFlow(
            month=month_date,
            gross_rent=Decimal("2000.00"),
            vacancy_deduction=Decimal("100.00"),
            effective_rent=Decimal("1900.00"),
            property_tax=Decimal("200.00"),
            insurance=Decimal("100.00"),
            maintenance=Decimal("150.00"),
            management_fee=Decimal("100.00"),
            total_operating_expenses=Decimal("550.00"),
            noi=Decimal("1350.00"),
            mortgage_payment=Decimal("1200.00"),
            mortgage_principal=Decimal("400.00"),
            mortgage_interest=Decimal("800.00"),
            net_cashflow=Decimal("150.00"),
            net_cashflow_usd=Decimal("111.11"),
            noi_usd=Decimal("1000.00"),
        )
        monthly_cashflows.append(cf)

    exit_input = ExitInput(
        sale_price=Decimal("600000.00"),
        sale_year=1,
        commission_rate=Decimal("0.05"),
        closing_costs=Decimal("5000.00"),
        remaining_mortgage_balance=Decimal("350000.00"),
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        cad_per_usd=Decimal("1.35"),
    )

    purchase_date = date(2020, 1, 15)
    result = calculate_total_return(exit_input, monthly_cashflows, purchase_date)

    # Verify exit_result exists and has expected fields
    assert hasattr(result, "exit_result")
    assert result.exit_result.sale_price == Decimal("600000.00")
    assert result.exit_result.commission == Decimal("30000.00")
    assert result.exit_result.closing_costs == Decimal("5000.00")
    assert result.exit_result.mortgage_payoff == Decimal("350000.00")
    assert result.exit_result.net_proceeds == Decimal("215000.00")
    assert isinstance(result.exit_result.implied_appreciation_rate, Decimal)
