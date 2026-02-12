"""Tests for multi-term mortgage renewal and scenario comparison.

Tests the calculate_multi_term function that chains single-term calculations
across 5-year renewal boundaries with rate changes and payment recalculation.
"""

from datetime import date
from decimal import Decimal

import pytest

from maple_return.mortgage import (
    MortgageInput,
    ScenarioResult,
    TermDefinition,
    TermSummary,
    calculate_multi_term,
    calculate_standard_payment,
)


class TestMultiTermRenewal:
    """Test basic multi-term mortgage renewal mechanics."""

    def test_single_term_no_renewals(self):
        """Single 5-year term within 30-year amortization should generate 60 months."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000"),
            amortization_years=30,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[],  # No renewals
        )

        results = calculate_multi_term(input_data)

        # Should have one scenario (base scenario using initial rate)
        assert len(results) == 1

        scenario = results[0]
        assert scenario.scenario_index == 0
        assert len(scenario.schedule) == 60  # 5 years
        assert len(scenario.terms) == 1

        # Verify term summary
        term = scenario.terms[0]
        assert term.term_number == 1
        assert term.rate == Decimal("0.05")
        assert term.rate_type == "fixed"
        assert term.monthly_payment == Decimal("2000")
        assert term.months == 60
        assert term.end_balance > Decimal("0")  # Still owes money after 5 years

    def test_two_terms_same_rate(self):
        """Two terms with same rate should produce same result as continuous term."""
        monthly_payment = Decimal("2000")

        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=monthly_payment,
            amortization_years=10,  # 120 months = 2 terms
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.05"), rate_type="fixed")]
            ],
        )

        results = calculate_multi_term(input_data)
        assert len(results) == 1

        scenario = results[0]
        assert len(scenario.terms) == 2

        # Both terms should have same rate
        assert scenario.terms[0].rate == Decimal("0.05")
        assert scenario.terms[1].rate == Decimal("0.05")

        # First term payment is user-specified
        assert scenario.terms[0].monthly_payment == monthly_payment

        # Schedule should have 120 months
        assert len(scenario.schedule) == 120

    def test_two_terms_different_rate(self):
        """Payment should recalculate at renewal with different rate."""
        initial_payment = Decimal("2000")

        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),  # 5% initial
            monthly_payment=initial_payment,
            amortization_years=10,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.07"), rate_type="fixed")]  # 7% renewal
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        assert len(scenario.terms) == 2

        # First term: user-specified payment
        assert scenario.terms[0].monthly_payment == initial_payment

        # Second term: recalculated payment should be higher (higher rate)
        assert scenario.terms[1].monthly_payment > initial_payment

        # Verify payment recalculation logic
        # Payment should be based on: remaining_balance, new_rate, remaining_months
        term1 = scenario.terms[0]
        term2 = scenario.terms[1]

        # Verify term 2 payment was recalculated correctly
        from maple_return.mortgage import calculate_monthly_rate

        expected_monthly_rate = calculate_monthly_rate(Decimal("0.07"))
        remaining_months = (10 * 12) - 60  # 60 months remaining
        expected_payment = calculate_standard_payment(
            term1.end_balance, expected_monthly_rate, remaining_months
        )

        assert term2.monthly_payment == expected_payment

    def test_term_boundaries(self):
        """Verify term boundaries align correctly at 60-month intervals."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000"),
            amortization_years=10,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.05"), rate_type="fixed")]
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        # Term 1 should be months 1-60
        assert scenario.schedule[0].month_number == 1
        assert scenario.schedule[59].month_number == 60

        # Term 2 should be months 61-120
        assert scenario.schedule[60].month_number == 61
        assert scenario.schedule[119].month_number == 120


class TestScenarioComparison:
    """Test multiple renewal scenarios with different rate assumptions."""

    def test_three_scenarios_different_rates(self):
        """Three scenarios with different renewal rates should produce different total interest."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000"),
            amortization_years=10,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.03"), rate_type="fixed")],  # Low
                [TermDefinition(rate=Decimal("0.05"), rate_type="fixed")],  # Medium
                [TermDefinition(rate=Decimal("0.07"), rate_type="fixed")],  # High
            ],
        )

        results = calculate_multi_term(input_data)

        # Should have 3 scenarios
        assert len(results) == 3

        # Verify scenario indices
        assert results[0].scenario_index == 0
        assert results[1].scenario_index == 1
        assert results[2].scenario_index == 2

        # Total interest should increase with rate
        interest_low = results[0].total_interest
        interest_med = results[1].total_interest
        interest_high = results[2].total_interest

        assert interest_low < interest_med < interest_high

        # All scenarios should have 2 terms
        for result in results:
            assert len(result.terms) == 2

    def test_scenario_with_early_payoff(self):
        """High payment should pay off mortgage before term ends."""
        # Calculate a payment that will pay off faster
        from maple_return.mortgage import calculate_monthly_rate

        principal = Decimal("320000")  # 400k - 80k
        monthly_rate = calculate_monthly_rate(Decimal("0.05"))
        high_payment = calculate_standard_payment(
            principal, monthly_rate, 180
        )  # 15-year payoff

        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=high_payment,
            amortization_years=30,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.05"), rate_type="fixed")]
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        # Should pay off early (before 30 years)
        assert scenario.months_to_payoff < 360
        assert scenario.final_balance == Decimal("0.00")

        # Last entry should have zero balance
        assert scenario.schedule[-1].balance == Decimal("0.00")


class TestRenewalRateRepetition:
    """Test behavior when renewal_scenarios list is shorter than needed."""

    def test_last_rate_repeats(self):
        """Last renewal rate should repeat for subsequent terms."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000"),
            amortization_years=15,  # 180 months = 3 terms
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [
                    TermDefinition(rate=Decimal("0.06"), rate_type="fixed")
                ]  # Only 1 renewal rate
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        # Should have 3 terms
        assert len(scenario.terms) == 3

        # Term 1: 5%, Term 2: 6%, Term 3: 6% (repeated)
        assert scenario.terms[0].rate == Decimal("0.05")
        assert scenario.terms[1].rate == Decimal("0.06")
        assert scenario.terms[2].rate == Decimal("0.06")  # Repeated from term 2

    def test_full_amortization_multiple_terms(self):
        """30-year mortgage should produce up to 6 terms."""
        # Use a payment that will fully amortize
        from maple_return.mortgage import calculate_monthly_rate

        principal = Decimal("320000")
        monthly_rate = calculate_monthly_rate(Decimal("0.05"))
        payment = calculate_standard_payment(principal, monthly_rate, 360)

        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=payment,
            amortization_years=30,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [
                    TermDefinition(rate=Decimal("0.05"), rate_type="fixed"),
                    TermDefinition(rate=Decimal("0.05"), rate_type="fixed"),
                ]  # Only 2 explicit renewals
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        # Should have 6 terms (30 years / 5 years per term)
        assert len(scenario.terms) == 6

        # Terms 4-6 should all use the repeated rate from term 3
        assert scenario.terms[3].rate == Decimal("0.05")
        assert scenario.terms[4].rate == Decimal("0.05")
        assert scenario.terms[5].rate == Decimal("0.05")

        # Should have 360 months (or slightly less if early payoff due to rounding)
        assert scenario.months_to_payoff <= 360
        assert scenario.final_balance == Decimal("0.00")


class TestScenarioResultStructure:
    """Test ScenarioResult and TermSummary data structure correctness."""

    def test_term_summary_calculations(self):
        """Verify TermSummary totals match schedule entries."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000"),
            amortization_years=10,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.06"), rate_type="fixed")]
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        # Verify term 1 summary matches schedule
        term1 = scenario.terms[0]
        term1_schedule = scenario.schedule[0:60]  # First 60 months

        calculated_principal = sum(entry.principal for entry in term1_schedule)
        calculated_interest = sum(entry.interest for entry in term1_schedule)

        assert term1.total_principal == calculated_principal
        assert term1.total_interest == calculated_interest
        assert term1.start_balance == term1_schedule[0].balance + term1_schedule[0].principal
        assert term1.end_balance == term1_schedule[-1].balance

    def test_scenario_result_totals(self):
        """Verify ScenarioResult totals aggregate all terms correctly."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000"),
            down_payment=Decimal("80000"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000"),
            amortization_years=10,
            start_date=date(2024, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.06"), rate_type="fixed")]
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        # Total interest should equal sum of all term interests
        term_interest_sum = sum(term.total_interest for term in scenario.terms)
        assert scenario.total_interest == term_interest_sum

        # Total payments should equal sum of all schedule payments
        schedule_payment_sum = sum(entry.payment for entry in scenario.schedule)
        assert scenario.total_payments == schedule_payment_sum

        # Months to payoff should match schedule length
        assert scenario.months_to_payoff == len(scenario.schedule)

        # Final balance should match last schedule entry
        assert scenario.final_balance == scenario.schedule[-1].balance
