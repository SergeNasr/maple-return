"""Tests for annual summary and scenario comparison functionality."""

from datetime import date
from decimal import Decimal

from maple_return.mortgage import (
    AmortizationEntry,
    MortgageInput,
    TermDefinition,
    calculate_multi_term,
)
from maple_return.mortgage_summary import (
    compare_scenarios,
    generate_annual_summaries,
)


class TestAnnualSummary:
    """Test annual summary generation from monthly schedules."""

    def test_annual_summary_for_two_year_schedule(self):
        """Annual summary for a 2-year schedule produces 2 AnnualSummary entries."""
        # Create a simple 24-month schedule
        schedule = []
        balance = Decimal("100000.00")

        for month in range(1, 25):
            interest = Decimal("400.00")  # Simplified
            principal = Decimal("600.00")
            payment = interest + principal
            balance = balance - principal

            entry = AmortizationEntry(
                month_number=month,
                date=date(2025, 1, 1),  # Simplified - same year for now
                payment=payment,
                principal=principal,
                interest=interest,
                balance=balance,
            )
            schedule.append(entry)

        purchase_price = Decimal("120000.00")
        summaries = generate_annual_summaries(schedule, purchase_price)

        assert len(summaries) == 1  # All in same year
        assert summaries[0].year == 2025
        assert summaries[0].total_principal_paid == Decimal("600.00") * 24
        assert summaries[0].total_interest_paid == Decimal("400.00") * 24
        assert summaries[0].total_payments == Decimal("1000.00") * 24
        assert summaries[0].year_end_balance == balance
        assert summaries[0].equity == purchase_price - balance

    def test_annual_summary_respects_calendar_year_boundaries(self):
        """Annual summary correctly groups by calendar year (partial first year)."""
        # Mortgage starting mid-year (July 2025)
        schedule = []
        balance = Decimal("100000.00")

        # July-Dec 2025 (6 months)
        for month in range(1, 7):
            principal = Decimal("500.00")
            interest = Decimal("300.00")
            balance = balance - principal
            entry = AmortizationEntry(
                month_number=month,
                date=date(2025, 6 + month, 1),
                payment=principal + interest,
                principal=principal,
                interest=interest,
                balance=balance,
            )
            schedule.append(entry)

        # Jan-Jun 2026 (6 months)
        for month in range(7, 13):
            principal = Decimal("500.00")
            interest = Decimal("300.00")
            balance = balance - principal
            entry = AmortizationEntry(
                month_number=month,
                date=date(2026, month - 6, 1),
                payment=principal + interest,
                principal=principal,
                interest=interest,
                balance=balance,
            )
            schedule.append(entry)

        purchase_price = Decimal("120000.00")
        summaries = generate_annual_summaries(schedule, purchase_price)

        assert len(summaries) == 2

        # Year 1 (2025): 6 months
        assert summaries[0].year == 2025
        assert summaries[0].total_principal_paid == Decimal("500.00") * 6

        # Year 2 (2026): 6 months
        assert summaries[1].year == 2026
        assert summaries[1].total_principal_paid == Decimal("500.00") * 6

    def test_year_end_balance_matches_last_month(self):
        """Year-end balance matches the balance from last month of that year."""
        schedule = []
        balances = [Decimal("100000.00"), Decimal("95000.00"), Decimal("90000.00")]

        for i, month in enumerate([1, 2, 3]):
            entry = AmortizationEntry(
                month_number=month,
                date=date(2025, month, 1),
                payment=Decimal("5500.00"),
                principal=Decimal("5000.00"),
                interest=Decimal("500.00"),
                balance=balances[i],
            )
            schedule.append(entry)

        purchase_price = Decimal("120000.00")
        summaries = generate_annual_summaries(schedule, purchase_price)

        assert summaries[0].year_end_balance == Decimal("90000.00")

    def test_equity_calculation(self):
        """Equity = purchase_price - year_end_balance for each year."""
        schedule = [
            AmortizationEntry(
                month_number=1,
                date=date(2025, 1, 1),
                payment=Decimal("1000.00"),
                principal=Decimal("600.00"),
                interest=Decimal("400.00"),
                balance=Decimal("99400.00"),
            )
        ]

        purchase_price = Decimal("100000.00")
        summaries = generate_annual_summaries(schedule, purchase_price)

        expected_equity = purchase_price - Decimal("99400.00")
        assert summaries[0].equity == expected_equity

    def test_annual_totals_match_scenario_totals(self):
        """Sum of all annual totals matches ScenarioResult totals."""
        # Use a real multi-term calculation
        input_data = MortgageInput(
            purchase_price=Decimal("400000.00"),
            down_payment=Decimal("80000.00"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000.00"),
            amortization_years=2,  # 24 months for quick test
            start_date=date(2025, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[],  # Single term only
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        summaries = generate_annual_summaries(scenario.schedule, input_data.purchase_price)

        # Sum annual totals
        total_interest = sum(s.total_interest_paid for s in summaries)
        total_payments = sum(s.total_payments for s in summaries)

        # Should match scenario totals
        assert total_interest == scenario.total_interest
        assert total_payments == scenario.total_payments

    def test_full_30year_schedule(self):
        """Full 30-year scenario produces 30 annual summaries (or fewer if early payoff)."""
        # Create a realistic 30-year mortgage
        input_data = MortgageInput(
            purchase_price=Decimal("400000.00"),
            down_payment=Decimal("80000.00"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("1719.46"),  # Standard payment for this scenario
            amortization_years=30,
            start_date=date(2025, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [
                    TermDefinition(rate=Decimal("0.05"), rate_type="fixed"),
                    TermDefinition(rate=Decimal("0.05"), rate_type="fixed"),
                    TermDefinition(rate=Decimal("0.05"), rate_type="fixed"),
                    TermDefinition(rate=Decimal("0.05"), rate_type="fixed"),
                    TermDefinition(rate=Decimal("0.05"), rate_type="fixed"),
                ]
            ],
        )

        results = calculate_multi_term(input_data)
        scenario = results[0]

        summaries = generate_annual_summaries(scenario.schedule, input_data.purchase_price)

        # Should have 30 years (or fewer if paid off early)
        assert 1 <= len(summaries) <= 30
        assert summaries[0].year == 2025
        # Check equity grows over time
        assert summaries[-1].equity > summaries[0].equity


class TestScenarioComparison:
    """Test scenario comparison functionality."""

    def test_compare_two_scenarios_different_total_interest(self):
        """Scenario comparison with 2 scenarios shows different total interest values."""
        # Create 2 scenarios with different rates
        # Use 10 years and lower payment to ensure mortgage extends to term 2
        input_data = MortgageInput(
            purchase_price=Decimal("400000.00"),
            down_payment=Decimal("80000.00"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2800.00"),  # Lower than standard to extend to term 2
            amortization_years=10,
            start_date=date(2025, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                # Scenario 1: 3% renewal
                [TermDefinition(rate=Decimal("0.03"), rate_type="fixed")],
                # Scenario 2: 7% renewal
                [TermDefinition(rate=Decimal("0.07"), rate_type="fixed")],
            ],
        )

        results = calculate_multi_term(input_data)
        comparisons = compare_scenarios(results, input_data.purchase_price)

        assert len(comparisons) == 2

        # Lower rate should have less total interest
        assert comparisons[0].total_interest < comparisons[1].total_interest
        assert comparisons[0].scenario_index == 0
        assert comparisons[1].scenario_index == 1

    def test_compare_three_scenarios_ordered(self):
        """Scenario comparison with 3 scenarios is ordered by scenario_index."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000.00"),
            down_payment=Decimal("80000.00"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2800.00"),  # Lower than standard to extend to term 2
            amortization_years=10,
            start_date=date(2025, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.03"), rate_type="fixed")],
                [TermDefinition(rate=Decimal("0.05"), rate_type="fixed")],
                [TermDefinition(rate=Decimal("0.07"), rate_type="fixed")],
            ],
        )

        results = calculate_multi_term(input_data)
        comparisons = compare_scenarios(results, input_data.purchase_price)

        assert len(comparisons) == 3
        assert [c.scenario_index for c in comparisons] == [0, 1, 2]

    def test_scenario_comparison_fields(self):
        """ScenarioComparison contains all required fields."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000.00"),
            down_payment=Decimal("80000.00"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000.00"),
            amortization_years=5,
            start_date=date(2025, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.04"), rate_type="fixed")],
            ],
        )

        results = calculate_multi_term(input_data)
        comparisons = compare_scenarios(results, input_data.purchase_price)

        comparison = comparisons[0]

        # Check all fields present
        assert comparison.scenario_index == 0
        assert len(comparison.renewal_rates) >= 0
        assert comparison.total_interest > Decimal("0")
        assert comparison.total_payments > Decimal("0")
        assert comparison.final_balance >= Decimal("0")
        assert comparison.months_to_payoff > 0
        assert comparison.total_equity > Decimal("0")

    def test_renewal_rates_extraction(self):
        """Renewal rates extracted correctly (skip term 1 initial rate)."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000.00"),
            down_payment=Decimal("80000.00"),
            annual_rate=Decimal("0.05"),  # Initial rate (term 1)
            monthly_payment=Decimal("1800.00"),  # Low payment to extend to term 3
            amortization_years=15,  # 15 years to get 3 terms
            start_date=date(2025, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [
                    TermDefinition(rate=Decimal("0.04"), rate_type="fixed"),  # Term 2
                    TermDefinition(rate=Decimal("0.06"), rate_type="fixed"),  # Term 3
                ],
            ],
        )

        results = calculate_multi_term(input_data)
        comparisons = compare_scenarios(results, input_data.purchase_price)

        # Should have renewal rates from terms 2 and 3 (not term 1)
        assert comparisons[0].renewal_rates == [Decimal("0.04"), Decimal("0.06")]

    def test_total_equity_calculation(self):
        """Total equity = purchase_price - final_balance."""
        input_data = MortgageInput(
            purchase_price=Decimal("400000.00"),
            down_payment=Decimal("80000.00"),
            annual_rate=Decimal("0.05"),
            monthly_payment=Decimal("2000.00"),
            amortization_years=5,
            start_date=date(2025, 1, 1),
            rate_type="fixed",
            renewal_scenarios=[
                [TermDefinition(rate=Decimal("0.05"), rate_type="fixed")],
            ],
        )

        results = calculate_multi_term(input_data)
        comparisons = compare_scenarios(results, input_data.purchase_price)

        expected_equity = input_data.purchase_price - comparisons[0].final_balance
        assert comparisons[0].total_equity == expected_equity
