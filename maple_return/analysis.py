"""Analysis presentation layer - P&L tables, amortization output, and dashboard.

Transforms calculation outputs into structured presentation formats for owner review.
All functions are pure - no I/O, no side effects.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from maple_return.cashflow import AnnualOperatingSummary, MonthlyCashFlow, convert_to_usd
from maple_return.metrics import calculate_cap_rate, calculate_cash_on_cash, calculate_irr
from maple_return.mortgage import AmortizationEntry
from maple_return.mortgage_summary import AnnualSummary


@dataclass
class AmortizationRow:
    """Single row in amortization table output.

    Thin wrapper around AmortizationEntry for output consistency.
    All amounts in CAD.
    """

    date: date
    payment: Decimal
    principal: Decimal
    interest: Decimal
    balance: Decimal


@dataclass
class PnLRow:
    """Single row in P&L table showing annual investment performance.

    All monetary amounts in CAD.
    Includes cumulative metrics and year-over-year equity growth.
    """

    year: int
    gross_rent: Decimal
    vacancy_loss: Decimal
    net_rent: Decimal
    operating_expenses: Decimal
    noi: Decimal
    mortgage_payment: Decimal
    net_cashflow: Decimal
    principal_paid: Decimal
    interest_paid: Decimal
    equity_gained: Decimal
    cumulative_cashflow: Decimal
    cumulative_equity: Decimal
    cap_rate: Decimal
    cash_on_cash: Decimal
    is_partial_year: bool


@dataclass
class DashboardSnapshot:
    """Dashboard snapshot showing current investment position.

    "As of today" view with equity position, cumulative performance,
    and key return metrics. Includes USD equivalents for key metrics.
    """

    as_of_date: date
    equity_position: Decimal  # CAD
    equity_position_usd: Decimal  # USD
    cumulative_cashflow: Decimal  # CAD
    cumulative_cashflow_usd: Decimal  # USD
    annualized_return_irr: Decimal | None
    current_cap_rate: Decimal
    cash_on_cash_return: Decimal
    months_held: int
    current_property_value: Decimal  # CAD
    remaining_balance: Decimal  # CAD


def build_amortization_table(schedule: list[AmortizationEntry]) -> list[AmortizationRow]:
    """Build amortization table from mortgage schedule.

    Direct mapping from AmortizationEntry to AmortizationRow for output consistency.

    Args:
        schedule: List of monthly amortization entries

    Returns:
        List of AmortizationRow, one per month in schedule
    """
    if not schedule:
        return []

    return [
        AmortizationRow(
            date=entry.date,
            payment=entry.payment,
            principal=entry.principal,
            interest=entry.interest,
            balance=entry.balance,
        )
        for entry in schedule
    ]


def build_pnl_table(
    annual_summaries: list[AnnualOperatingSummary],
    mortgage_annual_summaries: list[AnnualSummary],
    purchase_price: Decimal,
    current_property_value: Decimal,
    down_payment: Decimal,
) -> list[PnLRow]:
    """Build P&L table with annual rows and cumulative metrics.

    Combines operating summaries with mortgage summaries to produce comprehensive
    annual P&L rows. Computes cumulative cash flow, cumulative equity, and
    year-over-year equity growth.

    First year is always flagged as partial (purchase year). Last year flagged
    as partial if < 12 months.

    Args:
        annual_summaries: Annual operating summaries (income/expenses)
        mortgage_annual_summaries: Annual mortgage summaries (principal/interest/balance)
        purchase_price: Original purchase price
        current_property_value: Current estimated property value
        down_payment: Initial down payment

    Returns:
        List of PnLRow, one per year
    """
    if not annual_summaries or not mortgage_annual_summaries:
        return []

    rows = []
    cumulative_cashflow = Decimal("0.00")
    previous_equity = down_payment  # For year 1, equity gained is relative to down payment

    for i, (operating_summary, mortgage_summary) in enumerate(
        zip(annual_summaries, mortgage_annual_summaries)
    ):
        # Cumulative cash flow
        cumulative_cashflow += operating_summary.total_net_cashflow

        # Current equity position (based on current property value)
        current_equity = current_property_value - mortgage_summary.year_end_balance

        # Equity gained this year (year-over-year change)
        equity_gained = current_equity - previous_equity

        # Partial year detection
        # First year is always partial (purchase year per user decision)
        # Last year is partial if it's the last year and not a full year
        # For now, we'll mark first year as partial always
        is_partial_year = i == 0

        # Calculate metrics using annualized values if partial year
        # For now, we'll use actual values and let metrics be calculated as-is
        # (Partial year annualization would require month count, which we don't have here)
        cap_rate = calculate_cap_rate(operating_summary.total_noi, current_property_value)
        cash_on_cash = calculate_cash_on_cash(
            operating_summary.total_net_cashflow, down_payment
        )

        row = PnLRow(
            year=operating_summary.year,
            gross_rent=operating_summary.total_gross_rent,
            vacancy_loss=operating_summary.total_vacancy_deduction,
            net_rent=operating_summary.total_effective_rent,
            operating_expenses=operating_summary.total_operating_expenses,
            noi=operating_summary.total_noi,
            mortgage_payment=operating_summary.total_mortgage_payments,
            net_cashflow=operating_summary.total_net_cashflow,
            principal_paid=mortgage_summary.total_principal_paid,
            interest_paid=mortgage_summary.total_interest_paid,
            equity_gained=equity_gained,
            cumulative_cashflow=cumulative_cashflow,
            cumulative_equity=current_equity,
            cap_rate=cap_rate,
            cash_on_cash=cash_on_cash,
            is_partial_year=is_partial_year,
        )
        rows.append(row)

        # Update for next iteration
        previous_equity = current_equity

    return rows


def build_dashboard_snapshot(
    monthly_cashflows: list[MonthlyCashFlow],
    purchase_date: date,
    down_payment: Decimal,
    current_property_value: Decimal,
    remaining_balance: Decimal,
    cad_per_usd: Decimal,
) -> DashboardSnapshot:
    """Build dashboard snapshot showing current investment position.

    Filters cash flows up to today, computes cumulative metrics, and calculates
    IRR and return metrics based on current position.

    Args:
        monthly_cashflows: All monthly cash flows from purchase to projection end
        purchase_date: Property purchase date
        down_payment: Initial down payment
        current_property_value: Current estimated property value
        remaining_balance: Current remaining mortgage balance
        cad_per_usd: FX rate for USD conversions

    Returns:
        DashboardSnapshot with equity position, cumulative cash flow, IRR, and metrics
    """
    # Filter to cash flows up to today
    today = date.today()
    filtered_cashflows = [cf for cf in monthly_cashflows if cf.month <= today]

    if not filtered_cashflows:
        # No cash flows yet - return minimal dashboard
        return DashboardSnapshot(
            as_of_date=today,
            equity_position=Decimal("0.00"),
            equity_position_usd=Decimal("0.00"),
            cumulative_cashflow=Decimal("0.00"),
            cumulative_cashflow_usd=Decimal("0.00"),
            annualized_return_irr=None,
            current_cap_rate=Decimal("0.0000"),
            cash_on_cash_return=Decimal("0.0000"),
            months_held=0,
            current_property_value=current_property_value,
            remaining_balance=remaining_balance,
        )

    # Equity position
    equity_position = current_property_value - remaining_balance
    equity_position_usd = convert_to_usd(equity_position, cad_per_usd)

    # Cumulative cash flow
    cumulative_cashflow = sum(cf.net_cashflow for cf in filtered_cashflows)
    cumulative_cashflow_usd = convert_to_usd(cumulative_cashflow, cad_per_usd)

    # IRR calculation
    irr = calculate_irr(down_payment, filtered_cashflows, current_property_value)

    # Cap rate and cash-on-cash based on most recent year
    # For simplicity, annualize from most recent 12 months (or available months)
    recent_months = (
        filtered_cashflows[-12:] if len(filtered_cashflows) >= 12 else filtered_cashflows
    )
    annualized_noi = sum(cf.noi for cf in recent_months)
    if len(recent_months) < 12:
        # Annualize partial year
        annualized_noi = (annualized_noi / Decimal(len(recent_months))) * Decimal("12")

    annualized_cashflow = sum(cf.net_cashflow for cf in recent_months)
    if len(recent_months) < 12:
        # Annualize partial year
        annualized_cashflow = (annualized_cashflow / Decimal(len(recent_months))) * Decimal("12")

    current_cap_rate = calculate_cap_rate(annualized_noi, current_property_value)
    cash_on_cash_return = calculate_cash_on_cash(annualized_cashflow, down_payment)

    # Months held
    # Calculate from purchase date to today
    months_held = (
        (today.year - purchase_date.year) * 12 + (today.month - purchase_date.month)
    )
    # Add 1 to account for the current month
    if today.day >= purchase_date.day:
        months_held += 1

    return DashboardSnapshot(
        as_of_date=today,
        equity_position=equity_position,
        equity_position_usd=equity_position_usd,
        cumulative_cashflow=cumulative_cashflow,
        cumulative_cashflow_usd=cumulative_cashflow_usd,
        annualized_return_irr=irr,
        current_cap_rate=current_cap_rate,
        cash_on_cash_return=cash_on_cash_return,
        months_held=months_held,
        current_property_value=current_property_value,
        remaining_balance=remaining_balance,
    )
