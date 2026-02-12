"""Cash flow integration and FX conversion.

Combines operating model (income and expenses) with mortgage schedule to produce
complete monthly and annual cash flow projections with CAD and USD amounts.
"""

import itertools
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from maple_return.mortgage import AmortizationEntry
from maple_return.operating import OperatingInput, calculate_monthly_operating


@dataclass
class MonthlyCashFlow:
    """Complete monthly cash flow statement with operating and financing components.

    Integrates operating income/expenses with mortgage payments and provides
    FX-converted USD amounts for key metrics.

    All monetary amounts in CAD unless explicitly marked _usd.
    """

    month: date
    gross_rent: Decimal  # CAD
    vacancy_deduction: Decimal  # CAD
    effective_rent: Decimal  # CAD
    property_tax: Decimal  # CAD, monthly
    insurance: Decimal  # CAD, monthly
    maintenance: Decimal  # CAD, monthly
    management_fee: Decimal  # CAD, monthly
    total_operating_expenses: Decimal  # CAD
    noi: Decimal  # CAD, Net Operating Income
    mortgage_payment: Decimal  # CAD
    mortgage_principal: Decimal  # CAD
    mortgage_interest: Decimal  # CAD
    net_cashflow: Decimal  # CAD, noi - mortgage_payment
    net_cashflow_usd: Decimal  # USD
    noi_usd: Decimal  # USD


@dataclass
class AnnualOperatingSummary:
    """Annual operating summary grouped by calendar year.

    Aggregates monthly cash flows within each calendar year, handling partial
    first/last years naturally.

    All monetary amounts in CAD unless explicitly marked _usd.
    """

    year: int  # Calendar year
    total_gross_rent: Decimal  # CAD
    total_vacancy_deduction: Decimal  # CAD
    total_effective_rent: Decimal  # CAD
    total_operating_expenses: Decimal  # CAD
    total_noi: Decimal  # CAD
    total_mortgage_payments: Decimal  # CAD
    total_mortgage_principal: Decimal  # CAD
    total_mortgage_interest: Decimal  # CAD
    total_net_cashflow: Decimal  # CAD
    total_net_cashflow_usd: Decimal  # USD
    total_noi_usd: Decimal  # USD


def convert_to_usd(cad_amount: Decimal, cad_per_usd: Decimal) -> Decimal:
    """Convert CAD to USD using CAD per USD rate.

    Formula: USD = CAD / (CAD per USD)
    Example: $1,350 CAD / 1.35 = $1,000 USD

    Args:
        cad_amount: Amount in Canadian dollars
        cad_per_usd: Exchange rate (CAD per 1 USD), e.g., 1.35

    Returns:
        Amount in US dollars, quantized to 2 decimal places
    """
    if cad_per_usd == Decimal("0"):
        return Decimal("0.00")

    usd_amount = cad_amount / cad_per_usd
    return usd_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def generate_monthly_cashflows(
    operating_input: OperatingInput,
    mortgage_schedule: list[AmortizationEntry],
    cad_per_usd: Decimal,
) -> list[MonthlyCashFlow]:
    """Generate complete monthly cash flow projections.

    Combines operating model with mortgage schedule to produce full cash flow
    statements for each month. Includes FX conversion to USD for key metrics.

    The cash flow pipeline:
    1. Gross rent -> vacancy deduction -> effective rent
    2. Effective rent -> operating expenses -> NOI
    3. NOI -> mortgage payment -> net cash flow
    4. Convert NOI and net cash flow to USD

    Args:
        operating_input: Operating income and expense parameters
        mortgage_schedule: Monthly mortgage amortization schedule
        cad_per_usd: FX rate (CAD per 1 USD)

    Returns:
        List of MonthlyCashFlow entries, one per month in mortgage schedule
    """
    cashflows = []

    for amort_entry in mortgage_schedule:
        # Calculate operating income/expenses for this month
        monthly_operating = calculate_monthly_operating(operating_input, amort_entry.date)

        # Calculate net cash flow: NOI - mortgage payment
        net_cashflow = (monthly_operating.noi - amort_entry.payment).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Convert to USD
        noi_usd = convert_to_usd(monthly_operating.noi, cad_per_usd)
        net_cashflow_usd = convert_to_usd(net_cashflow, cad_per_usd)

        # Build cash flow entry
        cashflow = MonthlyCashFlow(
            month=amort_entry.date,
            gross_rent=monthly_operating.gross_rent,
            vacancy_deduction=monthly_operating.vacancy_deduction,
            effective_rent=monthly_operating.effective_rent,
            property_tax=monthly_operating.property_tax,
            insurance=monthly_operating.insurance,
            maintenance=monthly_operating.maintenance,
            management_fee=monthly_operating.management_fee,
            total_operating_expenses=monthly_operating.total_expenses,
            noi=monthly_operating.noi,
            mortgage_payment=amort_entry.payment,
            mortgage_principal=amort_entry.principal,
            mortgage_interest=amort_entry.interest,
            net_cashflow=net_cashflow,
            net_cashflow_usd=net_cashflow_usd,
            noi_usd=noi_usd,
        )
        cashflows.append(cashflow)

    return cashflows


def generate_annual_operating_summaries(
    monthly_cashflows: list[MonthlyCashFlow],
) -> list[AnnualOperatingSummary]:
    """Generate annual operating summaries grouped by calendar year.

    Groups monthly cash flows by calendar year and sums all monetary fields.
    Handles partial first/last years naturally (includes all months that fall
    within each calendar year).

    Args:
        monthly_cashflows: List of monthly cash flow entries

    Returns:
        List of AnnualOperatingSummary, one per calendar year
    """
    if not monthly_cashflows:
        return []

    # Group by calendar year
    # Sort by date first to ensure proper grouping
    sorted_cashflows = sorted(monthly_cashflows, key=lambda cf: cf.month)

    # Group by year using itertools.groupby
    def year_key(cf: MonthlyCashFlow) -> int:
        return cf.month.year

    summaries = []

    for year, group in itertools.groupby(sorted_cashflows, key=year_key):
        # Convert iterator to list for aggregation
        year_cashflows = list(group)

        # Sum all monetary fields
        total_gross_rent = sum(cf.gross_rent for cf in year_cashflows)
        total_vacancy_deduction = sum(cf.vacancy_deduction for cf in year_cashflows)
        total_effective_rent = sum(cf.effective_rent for cf in year_cashflows)
        total_operating_expenses = sum(cf.total_operating_expenses for cf in year_cashflows)
        total_noi = sum(cf.noi for cf in year_cashflows)
        total_mortgage_payments = sum(cf.mortgage_payment for cf in year_cashflows)
        total_mortgage_principal = sum(cf.mortgage_principal for cf in year_cashflows)
        total_mortgage_interest = sum(cf.mortgage_interest for cf in year_cashflows)
        total_net_cashflow = sum(cf.net_cashflow for cf in year_cashflows)
        total_net_cashflow_usd = sum(cf.net_cashflow_usd for cf in year_cashflows)
        total_noi_usd = sum(cf.noi_usd for cf in year_cashflows)

        summary = AnnualOperatingSummary(
            year=year,
            total_gross_rent=total_gross_rent,
            total_vacancy_deduction=total_vacancy_deduction,
            total_effective_rent=total_effective_rent,
            total_operating_expenses=total_operating_expenses,
            total_noi=total_noi,
            total_mortgage_payments=total_mortgage_payments,
            total_mortgage_principal=total_mortgage_principal,
            total_mortgage_interest=total_mortgage_interest,
            total_net_cashflow=total_net_cashflow,
            total_net_cashflow_usd=total_net_cashflow_usd,
            total_noi_usd=total_noi_usd,
        )
        summaries.append(summary)

    return summaries
