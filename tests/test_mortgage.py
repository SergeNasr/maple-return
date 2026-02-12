"""Tests for Canadian mortgage amortization engine."""

from datetime import date
from decimal import Decimal

import pytest

from maple_return.mortgage import (
    AmortizationEntry,
    calculate_amortization,
    calculate_monthly_rate,
    calculate_standard_payment,
)


class TestMonthlyRateCalculation:
    """Test Canadian semi-annual compounding conversion."""

    def test_calculate_monthly_rate_canadian_convention(self):
        """Canadian semi-annual compounding: (1 + annual/2)^(1/6) - 1."""
        annual_rate = Decimal("0.05")  # 5% nominal annual
        monthly_rate = calculate_monthly_rate(annual_rate)

        # Expected: (1 + 0.05/2)^(1/6) - 1 = (1.025)^(1/6) - 1
        # = 0.00412037... ≈ 0.41204% monthly
        assert abs(monthly_rate - Decimal("0.004120368673896")) < Decimal("0.000000000001")

    def test_calculate_monthly_rate_zero_rate(self):
        """Zero interest rate should produce zero monthly rate."""
        monthly_rate = calculate_monthly_rate(Decimal("0"))
        assert monthly_rate == Decimal("0")

    def test_calculate_monthly_rate_3_percent(self):
        """Test 3% annual rate conversion."""
        annual_rate = Decimal("0.03")
        monthly_rate = calculate_monthly_rate(annual_rate)

        # Expected: (1.015)^(1/6) - 1 ≈ 0.00247585
        assert abs(monthly_rate - Decimal("0.002475854")) < Decimal("0.000001")


class TestStandardPaymentCalculation:
    """Test standard amortization payment formula."""

    def test_standard_payment_400k_mortgage(self):
        """Standard payment for $400k at 5% over 30 years."""
        principal = Decimal("400000.00")
        monthly_rate = calculate_monthly_rate(Decimal("0.05"))
        num_months = 360

        payment = calculate_standard_payment(principal, monthly_rate, num_months)

        # Expected formula: P * r * (1+r)^n / ((1+r)^n - 1)
        # With r = 0.004120368673896, this is approximately $2,147.29
        assert abs(payment - Decimal("2147.29")) < Decimal("1.00")

    def test_standard_payment_zero_rate(self):
        """Zero rate means equal principal payments over term."""
        principal = Decimal("100000.00")
        monthly_rate = Decimal("0")
        num_months = 100

        payment = calculate_standard_payment(principal, monthly_rate, num_months)

        # With zero rate, payment = principal / num_months
        assert payment == Decimal("1000.00")

    def test_standard_payment_short_term(self):
        """Small mortgage over 5 years at 4%."""
        principal = Decimal("50000.00")
        monthly_rate = calculate_monthly_rate(Decimal("0.04"))
        num_months = 60

        payment = calculate_standard_payment(principal, monthly_rate, num_months)

        # Expected approximately $920.41
        assert abs(payment - Decimal("920.41")) < Decimal("1.00")


class TestAmortizationSchedule:
    """Test full amortization schedule generation."""

    def test_first_month_interest_calculation(self):
        """First month interest should be full balance * monthly_rate."""
        purchase_price = Decimal("500000.00")
        down_payment = Decimal("100000.00")
        principal = purchase_price - down_payment  # $400k
        annual_rate = Decimal("0.05")
        monthly_rate = calculate_monthly_rate(annual_rate)
        monthly_payment = Decimal("2150.00")
        amortization_months = 360
        start_date = date(2024, 1, 1)

        schedule = calculate_amortization(
            purchase_price=purchase_price,
            down_payment=down_payment,
            annual_rate=annual_rate,
            monthly_payment=monthly_payment,
            amortization_months=amortization_months,
            start_date=start_date,
        )

        # First month
        first_month = schedule[0]
        expected_interest = (principal * monthly_rate).quantize(Decimal("0.01"))

        assert first_month.month_number == 1
        assert first_month.date == date(2024, 1, 1)
        assert first_month.payment == monthly_payment
        assert first_month.interest == expected_interest
        assert first_month.principal == monthly_payment - expected_interest
        assert first_month.balance == principal - first_month.principal

    def test_amortization_schedule_length_standard_payment(self):
        """Standard payment should reach zero balance at exactly amortization_months."""
        purchase_price = Decimal("400000.00")
        down_payment = Decimal("0.00")
        annual_rate = Decimal("0.05")
        monthly_payment = calculate_standard_payment(
            purchase_price,
            calculate_monthly_rate(annual_rate),
            360,
        )

        schedule = calculate_amortization(
            purchase_price=purchase_price,
            down_payment=down_payment,
            annual_rate=annual_rate,
            monthly_payment=monthly_payment,
            amortization_months=360,
            start_date=date(2024, 1, 1),
        )

        # Should have exactly 360 entries
        assert len(schedule) == 360

        # Final balance should be zero
        assert schedule[-1].balance == Decimal("0.00")

    def test_amortization_final_month_adjustment(self):
        """Final month should adjust payment to exactly zero out balance."""
        purchase_price = Decimal("100000.00")
        down_payment = Decimal("20000.00")
        annual_rate = Decimal("0.04")
        monthly_payment = Decimal("400.00")
        amortization_months = 300

        schedule = calculate_amortization(
            purchase_price=purchase_price,
            down_payment=down_payment,
            annual_rate=annual_rate,
            monthly_payment=monthly_payment,
            amortization_months=amortization_months,
            start_date=date(2024, 1, 1),
        )

        # Final entry should have balance of 0
        final = schedule[-1]
        assert final.balance == Decimal("0.00")

        # Final payment should be smaller than regular payment (remaining balance + interest)
        assert final.payment < monthly_payment

    def test_higher_payment_pays_off_early(self):
        """Payment higher than standard should pay off before amortization_months."""
        purchase_price = Decimal("100000.00")
        down_payment = Decimal("0.00")
        annual_rate = Decimal("0.05")

        # Standard payment for 10-year amortization
        standard = calculate_standard_payment(
            purchase_price,
            calculate_monthly_rate(annual_rate),
            120,
        )

        # Pay 20% more
        higher_payment = (standard * Decimal("1.2")).quantize(Decimal("0.01"))

        schedule = calculate_amortization(
            purchase_price=purchase_price,
            down_payment=down_payment,
            annual_rate=annual_rate,
            monthly_payment=higher_payment,
            amortization_months=120,
            start_date=date(2024, 1, 1),
        )

        # Should pay off in fewer than 120 months
        assert len(schedule) < 120
        assert schedule[-1].balance == Decimal("0.00")

    def test_payment_lower_than_interest_stops_at_amortization_months(self):
        """Payment below interest-only should stop at amortization_months with remaining balance."""
        purchase_price = Decimal("100000.00")
        down_payment = Decimal("0.00")
        annual_rate = Decimal("0.05")
        monthly_rate = calculate_monthly_rate(annual_rate)

        # Interest-only would be principal * monthly_rate
        interest_only = (purchase_price * monthly_rate).quantize(Decimal("0.01"))

        # Pay less than interest-only
        low_payment = interest_only - Decimal("50.00")

        schedule = calculate_amortization(
            purchase_price=purchase_price,
            down_payment=down_payment,
            annual_rate=annual_rate,
            monthly_payment=low_payment,
            amortization_months=120,
            start_date=date(2024, 1, 1),
        )

        # Should have exactly 120 entries (stopped at limit)
        assert len(schedule) == 120

        # Final balance should be greater than principal (negative amortization)
        assert schedule[-1].balance > purchase_price

    def test_amortization_entry_structure(self):
        """AmortizationEntry should have all required fields."""
        schedule = calculate_amortization(
            purchase_price=Decimal("100000.00"),
            down_payment=Decimal("20000.00"),
            annual_rate=Decimal("0.03"),
            monthly_payment=Decimal("400.00"),
            amortization_months=300,
            start_date=date(2024, 6, 15),
        )

        entry = schedule[0]

        # Check all fields exist and have correct types
        assert isinstance(entry.month_number, int)
        assert isinstance(entry.date, date)
        assert isinstance(entry.payment, Decimal)
        assert isinstance(entry.principal, Decimal)
        assert isinstance(entry.interest, Decimal)
        assert isinstance(entry.balance, Decimal)

        # Verify first entry specifics
        assert entry.month_number == 1
        assert entry.date == date(2024, 6, 15)

    def test_date_progression_monthly(self):
        """Dates should progress by one month each entry."""
        schedule = calculate_amortization(
            purchase_price=Decimal("100000.00"),
            down_payment=Decimal("0.00"),
            annual_rate=Decimal("0.04"),
            monthly_payment=Decimal("500.00"),
            amortization_months=300,
            start_date=date(2024, 1, 31),
        )

        # Check first few months
        assert schedule[0].date == date(2024, 1, 31)
        assert schedule[1].date == date(2024, 2, 29)  # Leap year
        assert schedule[2].date == date(2024, 3, 31)
        assert schedule[11].date == date(2024, 12, 31)
        assert schedule[12].date == date(2025, 1, 31)

    def test_balance_decreases_monotonically_normal_payment(self):
        """With normal payment, balance should decrease each month."""
        schedule = calculate_amortization(
            purchase_price=Decimal("200000.00"),
            down_payment=Decimal("40000.00"),
            annual_rate=Decimal("0.045"),
            monthly_payment=Decimal("1000.00"),
            amortization_months=240,
            start_date=date(2024, 1, 1),
        )

        # Balance should decrease each month
        for i in range(1, min(len(schedule), 50)):
            assert schedule[i].balance < schedule[i - 1].balance

    def test_principal_plus_interest_equals_payment_except_final(self):
        """Each month (except final): principal + interest = payment."""
        schedule = calculate_amortization(
            purchase_price=Decimal("150000.00"),
            down_payment=Decimal("30000.00"),
            annual_rate=Decimal("0.04"),
            monthly_payment=Decimal("600.00"),
            amortization_months=300,
            start_date=date(2024, 1, 1),
        )

        # Check all non-final months
        for entry in schedule[:-1]:
            assert entry.principal + entry.interest == entry.payment

        # Final month is special (adjusted payment)
        final = schedule[-1]
        assert final.principal + final.interest == final.payment
        assert final.balance == Decimal("0.00")
