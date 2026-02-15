"""Tests for exit model and net proceeds calculations."""

from decimal import Decimal

import pytest

from maple_return.exit_model import (
    ExitInput,
    ExitResult,
    calculate_appreciation_rate,
    calculate_exit,
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
    Rate: (400k/500k)^(1/3) - 1 = 0.8^0.333... - 1 ≈ -0.0718 (-7.18%)
    """
    rate = calculate_appreciation_rate(
        purchase_price=Decimal("500000.00"),
        sale_price=Decimal("400000.00"),
        years_held=3,
    )

    # Expected: -0.0718 (negative rate)
    assert rate == Decimal("-0.0718")


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
