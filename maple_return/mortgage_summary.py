"""Annual summary and scenario comparison for mortgage calculations.

Provides functions to roll up monthly mortgage schedules into annual summaries
and compare multiple renewal rate scenarios side-by-side.
"""

from dataclasses import dataclass
from decimal import Decimal
from itertools import groupby

from maple_return.mortgage import AmortizationEntry, ScenarioResult


@dataclass
class AnnualSummary:
    """Annual summary of mortgage payments and balances.

    Aggregates monthly payment details into yearly totals showing
    principal paid, interest paid, and equity position.
    """

    year: int
    total_principal_paid: Decimal
    total_interest_paid: Decimal
    total_payments: Decimal
    year_end_balance: Decimal
    equity: Decimal


@dataclass
class ScenarioComparison:
    """Side-by-side comparison of renewal rate scenarios.

    Shows key metrics for one scenario to enable comparing different
    renewal rate assumptions.
    """

    scenario_index: int
    renewal_rates: list[Decimal]
    total_interest: Decimal
    total_payments: Decimal
    final_balance: Decimal
    months_to_payoff: int
    total_equity: Decimal


def generate_annual_summaries(
    schedule: list[AmortizationEntry],
    purchase_price: Decimal,
) -> list[AnnualSummary]:
    """Generate annual summaries from monthly amortization schedule.

    Groups monthly entries by calendar year and produces yearly totals.
    For partial first/last years, includes whatever months fall in that
    calendar year.

    Args:
        schedule: List of monthly amortization entries
        purchase_price: Original property purchase price (for equity calculation)

    Returns:
        List of AnnualSummary objects, one per calendar year
    """
    if not schedule:
        return []

    # Group entries by calendar year
    schedule_sorted = sorted(schedule, key=lambda e: e.date.year)
    grouped = groupby(schedule_sorted, key=lambda e: e.date.year)

    summaries = []

    for year, entries_iter in grouped:
        entries = list(entries_iter)

        # Sum totals for this year
        total_principal = sum(entry.principal for entry in entries)
        total_interest = sum(entry.interest for entry in entries)
        total_payments = sum(entry.payment for entry in entries)

        # Year-end balance is the balance from last month of this year
        year_end_balance = entries[-1].balance

        # Equity = purchase price - remaining balance
        equity = purchase_price - year_end_balance

        summary = AnnualSummary(
            year=year,
            total_principal_paid=total_principal,
            total_interest_paid=total_interest,
            total_payments=total_payments,
            year_end_balance=year_end_balance,
            equity=equity,
        )
        summaries.append(summary)

    return summaries


def compare_scenarios(
    scenarios: list[ScenarioResult],
    purchase_price: Decimal,
) -> list[ScenarioComparison]:
    """Compare multiple renewal rate scenarios side-by-side.

    Extracts key metrics from each scenario result for comparison.
    Renewal rates list excludes the initial term (term 1) since that's
    the same across all scenarios.

    Args:
        scenarios: List of ScenarioResult objects to compare
        purchase_price: Original property purchase price (for equity calculation)

    Returns:
        List of ScenarioComparison objects, one per scenario
    """
    comparisons = []

    for scenario in scenarios:
        # Extract renewal rates from terms (skip term 1 which is the initial rate)
        renewal_rates = []
        if len(scenario.terms) > 1:
            # Terms 2+ are renewals
            renewal_rates = [term.rate for term in scenario.terms[1:]]

        # Calculate total equity
        total_equity = purchase_price - scenario.final_balance

        comparison = ScenarioComparison(
            scenario_index=scenario.scenario_index,
            renewal_rates=renewal_rates,
            total_interest=scenario.total_interest,
            total_payments=scenario.total_payments,
            final_balance=scenario.final_balance,
            months_to_payoff=scenario.months_to_payoff,
            total_equity=total_equity,
        )
        comparisons.append(comparison)

    return comparisons
