"""Tests for operating income and expense calculations."""

from datetime import date
from decimal import Decimal

import pytest

from maple_return.operating import (
    OperatingInput,
    calculate_monthly_operating,
    generate_operating_schedule,
)


@pytest.fixture
def base_input():
    """Standard operating input for Canadian rental property."""
    return OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.02"),
        expense_escalation_rate=Decimal("0.02"),
        lease_start_date=date(2024, 1, 1),
    )


def test_base_rent_no_escalation(base_input):
    """Month 1: gross rent equals base rent, no escalation applied."""
    result = calculate_monthly_operating(base_input, date(2024, 1, 1))

    assert result.gross_rent == Decimal("2500.00")
    assert result.month == date(2024, 1, 1)


def test_vacancy_deduction(base_input):
    """Vacancy rate of 5% deducts 5% from gross rent."""
    result = calculate_monthly_operating(base_input, date(2024, 1, 1))

    expected_vacancy = Decimal("2500.00") * Decimal("0.05")
    assert result.vacancy_deduction == expected_vacancy
    assert result.effective_rent == Decimal("2500.00") - expected_vacancy


def test_rent_escalation_on_anniversary(base_input):
    """Rent stays same for 12 months, then increases by escalation_rate on month 13."""
    # Month 12 - still using base rent
    result_month_12 = calculate_monthly_operating(base_input, date(2024, 12, 1))
    assert result_month_12.gross_rent == Decimal("2500.00")

    # Month 13 - one year anniversary, rent escalates
    result_month_13 = calculate_monthly_operating(base_input, date(2025, 1, 1))
    expected_rent = Decimal("2500.00") * (Decimal("1") + Decimal("0.02"))
    assert result_month_13.gross_rent == expected_rent.quantize(Decimal("0.01"))


def test_rent_escalation_compounding(base_input):
    """After 2 full years, rent = base * (1 + rate)^2."""
    # Month 25 - two years have passed
    result = calculate_monthly_operating(base_input, date(2026, 1, 1))

    expected_rent = Decimal("2500.00") * (Decimal("1.02") ** 2)
    assert result.gross_rent == expected_rent.quantize(Decimal("0.01"))


def test_monthly_expenses_from_annual(base_input):
    """Annual amounts divided by 12 for monthly."""
    result = calculate_monthly_operating(base_input, date(2024, 1, 1))

    assert result.property_tax == (Decimal("4000.00") / 12).quantize(Decimal("0.01"))
    assert result.insurance == (Decimal("2400.00") / 12).quantize(Decimal("0.01"))
    assert result.maintenance == (Decimal("1200.00") / 12).quantize(Decimal("0.01"))


def test_expense_escalation(base_input):
    """Expenses increase after anniversary."""
    # Month 13 - one year anniversary, expenses escalate
    result_month_13 = calculate_monthly_operating(base_input, date(2025, 1, 1))
    expected_property_tax = (Decimal("4000.00") / 12) * (Decimal("1.02") ** 1)
    assert result_month_13.property_tax == expected_property_tax.quantize(Decimal("0.01"))


def test_management_fee_scales_with_gross_rent(base_input):
    """Fee is % of gross rent (not effective rent)."""
    result = calculate_monthly_operating(base_input, date(2024, 1, 1))

    expected_fee = Decimal("2500.00") * Decimal("0.10")
    assert result.management_fee == expected_fee.quantize(Decimal("0.01"))

    # Verify it's based on gross rent, not effective rent
    assert result.management_fee != result.effective_rent * Decimal("0.10")


def test_management_fee_increases_with_rent_escalation(base_input):
    """As rent escalates, management fee escalates too."""
    # Month 13 - one year later, rent escalated, so fee escalates too
    result_month_13 = calculate_monthly_operating(base_input, date(2025, 1, 1))
    escalated_rent = Decimal("2500.00") * Decimal("1.02")
    expected_fee = escalated_rent * Decimal("0.10")
    assert result_month_13.management_fee == expected_fee.quantize(Decimal("0.01"))


def test_noi_calculation(base_input):
    """NOI = effective_rent - total_expenses."""
    result = calculate_monthly_operating(base_input, date(2024, 1, 1))

    expected_noi = result.effective_rent - result.total_expenses
    assert result.noi == expected_noi.quantize(Decimal("0.01"))


def test_generate_schedule_length(base_input):
    """Schedule returns correct number of months."""
    schedule = generate_operating_schedule(base_input, date(2024, 1, 1), 24)

    assert len(schedule) == 24
    assert schedule[0].month == date(2024, 1, 1)
    assert schedule[23].month == date(2025, 12, 1)


def test_zero_vacancy_rate(base_input):
    """0% vacancy means effective_rent = gross_rent."""
    base_input.vacancy_rate = Decimal("0.00")
    result = calculate_monthly_operating(base_input, date(2024, 1, 1))

    assert result.vacancy_deduction == Decimal("0.00")
    assert result.effective_rent == result.gross_rent


def test_zero_escalation_rates(base_input):
    """No escalation means flat rent and expenses throughout."""
    base_input.rent_escalation_rate = Decimal("0.00")
    base_input.expense_escalation_rate = Decimal("0.00")

    # Month 1
    result_month_1 = calculate_monthly_operating(base_input, date(2024, 1, 1))

    # Month 25 (two years later)
    result_month_25 = calculate_monthly_operating(base_input, date(2026, 1, 1))

    # Rent should be flat
    assert result_month_1.gross_rent == result_month_25.gross_rent

    # Expenses should be flat
    assert result_month_1.property_tax == result_month_25.property_tax
    assert result_month_1.insurance == result_month_25.insurance
    assert result_month_1.maintenance == result_month_25.maintenance
