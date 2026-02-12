"""Tests for cash flow integration and FX conversion."""

from datetime import date
from decimal import Decimal

import pytest

from maple_return.cashflow import (
    AnnualOperatingSummary,
    MonthlyCashFlow,
    convert_to_usd,
    generate_annual_operating_summaries,
    generate_monthly_cashflows,
)
from maple_return.mortgage import MortgageInput, TermDefinition, calculate_multi_term
from maple_return.operating import OperatingInput


def test_convert_to_usd_basic():
    """$1,350 CAD at 1.35 rate = $1,000 USD."""
    cad_amount = Decimal("1350.00")
    cad_per_usd = Decimal("1.35")
    result = convert_to_usd(cad_amount, cad_per_usd)
    assert result == Decimal("1000.00")


def test_convert_to_usd_rounding():
    """Verify 2 decimal place rounding."""
    cad_amount = Decimal("100.00")
    cad_per_usd = Decimal("1.33")  # 100 / 1.33 = 75.1879699248... -> 75.19
    result = convert_to_usd(cad_amount, cad_per_usd)
    assert result == Decimal("75.19")


def test_convert_to_usd_zero_rate():
    """Rate of 0 returns $0.00 (not division error)."""
    cad_amount = Decimal("1000.00")
    cad_per_usd = Decimal("0")
    result = convert_to_usd(cad_amount, cad_per_usd)
    assert result == Decimal("0.00")


def test_monthly_cashflow_structure():
    """All fields populated correctly for one month."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.02"),
        expense_escalation_rate=Decimal("0.02"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule

    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)

    # Check first month has all expected fields
    first = cashflows[0]
    assert first.month == date(2025, 1, 1)
    assert first.gross_rent == Decimal("2500.00")
    assert first.vacancy_deduction == Decimal("125.00")  # 5% of 2500
    assert first.effective_rent == Decimal("2375.00")
    assert first.property_tax > Decimal("0")
    assert first.insurance > Decimal("0")
    assert first.maintenance > Decimal("0")
    assert first.management_fee == Decimal("250.00")  # 10% of gross rent
    assert first.total_operating_expenses > Decimal("0")
    assert first.noi > Decimal("0")
    assert first.mortgage_payment == mortgage_schedule[0].payment
    assert first.mortgage_principal == mortgage_schedule[0].principal
    assert first.mortgage_interest == mortgage_schedule[0].interest
    assert first.net_cashflow != Decimal("0")
    assert first.net_cashflow_usd != Decimal("0")
    assert first.noi_usd != Decimal("0")


def test_cashflow_pipeline_gross_to_net():
    """Verify: gross rent -> vacancy -> effective -> expenses -> NOI -> mortgage -> net."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)
    first = cashflows[0]

    # Verify pipeline: gross_rent -> vacancy_deduction -> effective_rent
    assert first.effective_rent == first.gross_rent - first.vacancy_deduction

    # effective_rent -> expenses -> NOI
    assert first.noi == first.effective_rent - first.total_operating_expenses

    # NOI -> mortgage -> net_cashflow
    assert first.net_cashflow == first.noi - first.mortgage_payment


def test_net_cashflow_is_noi_minus_mortgage():
    """net_cashflow = noi - mortgage_payment."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)

    # Verify formula for all months
    for cf in cashflows[:12]:  # Check first year
        assert cf.net_cashflow == cf.noi - cf.mortgage_payment


def test_usd_amounts_present():
    """Monthly entries include net_cashflow_usd and noi_usd."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)

    first = cashflows[0]
    # USD amounts should be present and non-zero
    assert first.noi_usd > Decimal("0")
    assert first.net_cashflow_usd != Decimal("0")

    # Verify conversion: CAD / rate = USD
    expected_noi_usd = (first.noi / cad_per_usd).quantize(Decimal("0.01"))
    assert abs(first.noi_usd - expected_noi_usd) < Decimal("0.01")


def test_cashflow_length_matches_mortgage():
    """Output length equals mortgage schedule length."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)

    assert len(cashflows) == len(mortgage_schedule)


def test_annual_summary_groups_by_calendar_year():
    """12 months across 2 calendar years produce 2 summaries."""
    # Create test data spanning two years
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2024, 7, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2024, 7, 1),  # July 2024
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule[:12]  # Take first 12 months
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)

    annual_summaries = generate_annual_operating_summaries(cashflows)

    # 6 months in 2024 (Jul-Dec), 6 months in 2025 (Jan-Jun) = 2 summaries
    assert len(annual_summaries) == 2
    assert annual_summaries[0].year == 2024
    assert annual_summaries[1].year == 2025


def test_annual_summary_totals_match_monthly():
    """Sum of monthly entries equals annual totals."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule[:12]  # First 12 months
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)
    annual_summaries = generate_annual_operating_summaries(cashflows)

    # Should be one year summary
    assert len(annual_summaries) == 1
    summary = annual_summaries[0]

    # Verify totals match sum of monthly
    monthly_gross_rent = sum(cf.gross_rent for cf in cashflows)
    monthly_noi = sum(cf.noi for cf in cashflows)
    monthly_net_cashflow = sum(cf.net_cashflow for cf in cashflows)
    monthly_mortgage_payments = sum(cf.mortgage_payment for cf in cashflows)

    assert summary.total_gross_rent == monthly_gross_rent
    assert summary.total_noi == monthly_noi
    assert summary.total_net_cashflow == monthly_net_cashflow
    assert summary.total_mortgage_payments == monthly_mortgage_payments


def test_annual_summary_includes_usd():
    """Annual summaries include USD totals."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("2500.00"),
        vacancy_rate=Decimal("0.05"),
        property_tax_annual=Decimal("4000.00"),
        insurance_annual=Decimal("2400.00"),
        maintenance_annual=Decimal("1200.00"),
        management_fee_rate=Decimal("0.10"),
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule[:12]
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)
    annual_summaries = generate_annual_operating_summaries(cashflows)

    summary = annual_summaries[0]

    # Verify USD totals exist and match sum of monthly USD values
    assert summary.total_noi_usd > Decimal("0")
    assert summary.total_net_cashflow_usd != Decimal("0")

    monthly_noi_usd = sum(cf.noi_usd for cf in cashflows)
    monthly_net_cashflow_usd = sum(cf.net_cashflow_usd for cf in cashflows)

    assert summary.total_noi_usd == monthly_noi_usd
    assert summary.total_net_cashflow_usd == monthly_net_cashflow_usd


def test_positive_cashflow_scenario():
    """High rent, low expenses = positive net cash flow."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("3500.00"),  # High rent
        vacancy_rate=Decimal("0.02"),  # Low vacancy
        property_tax_annual=Decimal("2000.00"),  # Low expenses
        insurance_annual=Decimal("1200.00"),
        maintenance_annual=Decimal("600.00"),
        management_fee_rate=Decimal("0.05"),  # Low fee
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("400000.00"),  # Lower mortgage
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("1610.47"),  # Lower payment
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule[:12]
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)

    # All months should have positive cash flow
    for cf in cashflows:
        assert cf.net_cashflow > Decimal("0"), f"Expected positive cash flow, got {cf.net_cashflow}"


def test_negative_cashflow_scenario():
    """Low rent, high expenses = negative net cash flow."""
    operating_input = OperatingInput(
        monthly_rent=Decimal("1500.00"),  # Low rent
        vacancy_rate=Decimal("0.10"),  # High vacancy
        property_tax_annual=Decimal("6000.00"),  # High expenses
        insurance_annual=Decimal("3600.00"),
        maintenance_annual=Decimal("2400.00"),
        management_fee_rate=Decimal("0.15"),  # High fee
        rent_escalation_rate=Decimal("0.00"),
        expense_escalation_rate=Decimal("0.00"),
        lease_start_date=date(2025, 1, 1),
    )

    mortgage_input = MortgageInput(
        purchase_price=Decimal("500000.00"),  # High mortgage
        down_payment=Decimal("100000.00"),
        annual_rate=Decimal("0.05"),
        monthly_payment=Decimal("2147.29"),  # High payment
        amortization_years=30,
        start_date=date(2025, 1, 1),
        rate_type="fixed",
        renewal_scenarios=[],
    )

    scenarios = calculate_multi_term(mortgage_input)
    mortgage_schedule = scenarios[0].schedule[:12]
    cad_per_usd = Decimal("1.35")

    cashflows = generate_monthly_cashflows(operating_input, mortgage_schedule, cad_per_usd)

    # All months should have negative cash flow
    for cf in cashflows:
        assert cf.net_cashflow < Decimal("0"), f"Expected negative cash flow, got {cf.net_cashflow}"
