"""Investment metric calculations for real estate analysis.

Provides core financial metrics: IRR, cap rate, cash-on-cash return, and equity growth.
All functions operate on Decimal types for monetary precision.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from maple_return.cashflow import AnnualOperatingSummary, MonthlyCashFlow


@dataclass
class AnnualMetrics:
    """Annual investment performance metrics.

    Combines profitability metrics (cap rate, cash-on-cash) with equity position
    for comprehensive investment performance tracking.
    """

    year: int
    cap_rate: Decimal
    cash_on_cash: Decimal
    equity_position: Decimal
    is_partial_year: bool


def calculate_irr(
    down_payment: Decimal,
    monthly_cashflows: list[MonthlyCashFlow],
    current_property_value: Decimal,
) -> Decimal | None:
    """Calculate Internal Rate of Return (IRR) for the investment.

    IRR is the annualized rate of return that makes the NPV of all cash flows equal to zero.
    Uses Newton-Raphson method to solve for the monthly rate, then annualizes it.

    Cash flow structure:
    - Period 0: -down_payment (initial outflow)
    - Periods 1..N: monthly net_cashflow values
    - Period N: monthly net_cashflow + current_property_value (terminal inflow)

    Args:
        down_payment: Initial investment (will be made negative for calculation)
        monthly_cashflows: List of monthly cash flow entries
        current_property_value: Terminal property value (added to last period)

    Returns:
        Annualized IRR as a decimal (e.g., 0.08 for 8%), or None if IRR cannot be computed
    """
    if not monthly_cashflows:
        return None

    # Build cash flow array: initial outflow + monthly flows + terminal value
    cashflows = [-float(down_payment)]  # Period 0: initial outflow

    for i, cf in enumerate(monthly_cashflows):
        flow = float(cf.net_cashflow)
        # Add terminal value to last period
        if i == len(monthly_cashflows) - 1:
            flow += float(current_property_value)
        cashflows.append(flow)

    # Check for sign change (required for IRR to exist)
    signs = [1 if cf > 0 else -1 if cf < 0 else 0 for cf in cashflows]
    if len(set(signs)) <= 1:  # All same sign or all zero
        return None

    # Newton-Raphson method to solve for monthly rate
    def npv(rate: float) -> float:
        """Calculate Net Present Value at given rate."""
        return sum(cf / (1 + rate) ** i for i, cf in enumerate(cashflows))

    def npv_derivative(rate: float) -> float:
        """Calculate derivative of NPV with respect to rate."""
        return sum(-i * cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cashflows))

    # Initial guess: 1% monthly rate
    monthly_rate = 0.01
    tolerance = 1e-6  # Relaxed tolerance for practical convergence
    max_iterations = 1000

    for iteration in range(max_iterations):
        npv_value = npv(monthly_rate)

        # Check convergence
        if abs(npv_value) < tolerance:
            # Annualize: (1 + monthly_rate)^12 - 1
            annual_rate = (1 + monthly_rate) ** 12 - 1
            return Decimal(str(annual_rate)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        # Newton-Raphson step
        derivative = npv_derivative(monthly_rate)
        if abs(derivative) < 1e-10:
            # Derivative too small, cannot continue
            break

        new_rate = monthly_rate - npv_value / derivative

        # Check if rate change is very small (convergence)
        if abs(new_rate - monthly_rate) < 1e-10:
            annual_rate = (1 + new_rate) ** 12 - 1
            return Decimal(str(annual_rate)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        monthly_rate = new_rate

        # Prevent extreme values
        if monthly_rate < -0.99 or monthly_rate > 10:
            break

    # If we didn't converge, return None
    return None


def calculate_cap_rate(annual_noi: Decimal, property_value: Decimal) -> Decimal:
    """Calculate capitalization rate (cap rate).

    Cap rate is the ratio of annual Net Operating Income to property value.
    It's a key metric for comparing real estate investments.

    Formula: annual_noi / property_value

    Args:
        annual_noi: Annual Net Operating Income
        property_value: Current property value

    Returns:
        Cap rate as a decimal (e.g., 0.0650 for 6.5%), quantized to 4 decimal places
    """
    if property_value == Decimal("0"):
        return Decimal("0.0000")

    cap_rate = annual_noi / property_value
    return cap_rate.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def calculate_cash_on_cash(annual_net_cashflow: Decimal, down_payment: Decimal) -> Decimal:
    """Calculate cash-on-cash return.

    Cash-on-cash return measures the annual pre-tax cash flow relative to the
    initial cash investment (down payment).

    Formula: annual_net_cashflow / down_payment

    Args:
        annual_net_cashflow: Annual net cash flow (after all expenses and mortgage)
        down_payment: Initial down payment (cash invested)

    Returns:
        Cash-on-cash return as a decimal (e.g., 0.0800 for 8%), quantized to 4 decimal places
    """
    if down_payment == Decimal("0"):
        return Decimal("0.0000")

    coc = annual_net_cashflow / down_payment
    return coc.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def calculate_equity_position(
    current_property_value: Decimal, remaining_balance: Decimal
) -> Decimal:
    """Calculate current equity position.

    Equity position is the difference between current property value and
    remaining mortgage balance. Can be negative if underwater.

    Formula: current_property_value - remaining_balance

    Args:
        current_property_value: Current estimated property value
        remaining_balance: Remaining mortgage principal balance

    Returns:
        Equity position (can be negative if underwater)
    """
    return current_property_value - remaining_balance


def calculate_annual_metrics(
    annual_summary: AnnualOperatingSummary,
    property_value: Decimal,
    remaining_balance: Decimal,
    down_payment: Decimal,
    is_partial_year: bool,
    months_in_year: int,
) -> AnnualMetrics:
    """Calculate annual investment metrics summary.

    Combines operating performance with property valuation to produce
    comprehensive annual metrics. Annualizes partial years for comparability.

    For partial years, scales NOI and net cash flow:
    - annualized_noi = (noi_so_far / months_in_year) * 12
    - annualized_cashflow = (cashflow_so_far / months_in_year) * 12

    Args:
        annual_summary: Annual operating summary (revenue, expenses, cash flow)
        property_value: Current property value for cap rate and equity
        remaining_balance: Remaining mortgage balance for equity
        down_payment: Initial down payment for cash-on-cash
        is_partial_year: Whether this is a partial year (needs annualization)
        months_in_year: Number of months in this year (for annualization)

    Returns:
        AnnualMetrics with cap rate, cash-on-cash, equity, and partial year flag
    """
    # Annualize if partial year
    if is_partial_year and months_in_year > 0:
        annualized_noi = (annual_summary.total_noi / Decimal(months_in_year)) * Decimal("12")
        annualized_cashflow = (
            annual_summary.total_net_cashflow / Decimal(months_in_year)
        ) * Decimal("12")
    else:
        annualized_noi = annual_summary.total_noi
        annualized_cashflow = annual_summary.total_net_cashflow

    # Calculate metrics using annualized values
    cap_rate = calculate_cap_rate(annualized_noi, property_value)
    cash_on_cash = calculate_cash_on_cash(annualized_cashflow, down_payment)
    equity_position = calculate_equity_position(property_value, remaining_balance)

    return AnnualMetrics(
        year=annual_summary.year,
        cap_rate=cap_rate,
        cash_on_cash=cash_on_cash,
        equity_position=equity_position,
        is_partial_year=is_partial_year,
    )
