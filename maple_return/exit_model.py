"""Exit model for property sale calculations.

Calculates net proceeds from a property sale, showing waterfall breakdown of:
sale price → commission → closing costs → mortgage payoff → net proceeds.

Also computes implied appreciation rate to show property value growth over hold period.

Provides total return calculation that combines exit proceeds with cumulative cash flows
to compute hold-period IRR, simple ROI, and total profit metrics.
"""

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from maple_return.cashflow import MonthlyCashFlow, convert_to_usd
from maple_return.metrics import calculate_irr


@dataclass
class ExitInput:
    """Input parameters for exit scenario modeling.

    All monetary amounts in CAD unless explicitly marked otherwise.
    """

    sale_price: Decimal  # Target selling price in CAD
    sale_year: int  # Year of ownership when sold (e.g., 5 = end of year 5)
    commission_rate: Decimal  # Single commission % (e.g., 0.05 for 5%)
    closing_costs: Decimal  # Flat closing costs in CAD
    remaining_mortgage_balance: Decimal  # Mortgage balance at time of sale
    purchase_price: Decimal  # Original purchase price for appreciation calc
    down_payment: Decimal  # Initial investment for ROI context
    cad_per_usd: Decimal  # FX rate for USD conversion


@dataclass
class ExitResult:
    """Exit scenario results with waterfall breakdown.

    Shows complete waterfall from sale price to net proceeds,
    plus implied appreciation rate and USD conversions.

    All monetary amounts in CAD unless explicitly marked _usd.
    """

    sale_price: Decimal  # CAD
    commission: Decimal  # CAD (sale_price * commission_rate)
    closing_costs: Decimal  # CAD (pass-through from input)
    mortgage_payoff: Decimal  # CAD (remaining balance)
    net_proceeds: Decimal  # CAD (sale - commission - closing - mortgage)
    net_proceeds_usd: Decimal  # USD conversion of net proceeds
    sale_price_usd: Decimal  # USD conversion of sale price
    implied_appreciation_rate: Decimal  # Annualized appreciation rate


@dataclass
class TotalReturnSummary:
    """Total return summary for investment with exit.

    Combines cumulative cash flows with exit proceeds to calculate total return
    metrics including hold-period IRR, simple ROI, and total profit.

    All monetary amounts in CAD unless explicitly marked _usd.
    """

    hold_period_years: int  # Same as sale_year from ExitInput
    total_months: int  # Number of months in truncated cash flow series
    cumulative_net_cashflow: Decimal  # Sum of all monthly net cash flows through sale year (CAD)
    net_proceeds: Decimal  # From ExitResult (CAD)
    total_profit: Decimal  # cumulative_net_cashflow + net_proceeds - down_payment (CAD)
    total_profit_usd: Decimal  # USD conversion
    simple_roi: Decimal  # total_profit / down_payment (quantized 4 decimal places)
    hold_period_irr: Decimal | None  # Annualized IRR using truncated flows + net proceeds
    exit_result: ExitResult  # Full waterfall breakdown (nested)


def calculate_appreciation_rate(
    purchase_price: Decimal, sale_price: Decimal, years_held: int
) -> Decimal:
    """Calculate annualized compound appreciation rate.

    Formula: (sale_price / purchase_price) ^ (1 / years_held) - 1

    This is the compound annual growth rate (CAGR) of the property value.

    Edge cases:
    - years_held = 0: Returns 0.0000 (no time for appreciation)
    - purchase_price = 0: Returns 0.0000 (avoid division by zero)

    Args:
        purchase_price: Original purchase price
        sale_price: Target sale price
        years_held: Number of years held (can be 0)

    Returns:
        Annualized appreciation rate as decimal (e.g., 0.0371 for 3.71%),
        quantized to 4 decimal places
    """
    # Edge case: zero years held
    if years_held == 0:
        return Decimal("0.0000")

    # Edge case: zero purchase price
    if purchase_price == Decimal("0"):
        return Decimal("0.0000")

    # Calculate appreciation ratio
    ratio = sale_price / purchase_price

    # Convert to float for exponentiation, calculate CAGR
    ratio_float = float(ratio)
    exponent = 1.0 / years_held
    growth_factor = ratio_float**exponent

    # Annualized rate: growth_factor - 1
    annual_rate = growth_factor - 1.0

    # Convert back to Decimal and quantize to 4 decimal places
    return Decimal(str(annual_rate)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def calculate_exit(exit_input: ExitInput) -> ExitResult:
    """Calculate exit scenario with waterfall breakdown.

    Waterfall:
    1. Sale price (input)
    2. - Commission (sale_price * commission_rate)
    3. - Closing costs (input)
    4. - Mortgage payoff (input)
    5. = Net proceeds (can be negative if underwater)

    Also calculates:
    - USD conversions for sale price and net proceeds
    - Implied appreciation rate from purchase to sale

    Args:
        exit_input: Exit scenario parameters

    Returns:
        ExitResult with complete waterfall breakdown and metrics
    """
    # Calculate commission
    commission = (exit_input.sale_price * exit_input.commission_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Calculate net proceeds (can be negative)
    net_proceeds = (
        exit_input.sale_price
        - commission
        - exit_input.closing_costs
        - exit_input.remaining_mortgage_balance
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Convert to USD
    sale_price_usd = convert_to_usd(exit_input.sale_price, exit_input.cad_per_usd)
    net_proceeds_usd = convert_to_usd(net_proceeds, exit_input.cad_per_usd)

    # Calculate implied appreciation rate
    appreciation_rate = calculate_appreciation_rate(
        exit_input.purchase_price, exit_input.sale_price, exit_input.sale_year
    )

    return ExitResult(
        sale_price=exit_input.sale_price,
        commission=commission,
        closing_costs=exit_input.closing_costs,
        mortgage_payoff=exit_input.remaining_mortgage_balance,
        net_proceeds=net_proceeds,
        net_proceeds_usd=net_proceeds_usd,
        sale_price_usd=sale_price_usd,
        implied_appreciation_rate=appreciation_rate,
    )


def calculate_total_return(
    exit_input: ExitInput,
    monthly_cashflows: list[MonthlyCashFlow],
    purchase_date: date,
) -> TotalReturnSummary:
    """Calculate total return including exit proceeds and hold-period IRR.

    Combines cumulative cash flows with exit proceeds to compute total investment
    return metrics. Cash flows are truncated at the sale year boundary.

    The total return calculation:
    1. Truncate cash flows to sale_year * 12 months
    2. Sum net cash flows for cumulative_net_cashflow
    3. Calculate exit result (net proceeds from sale)
    4. Compute total_profit = cumulative + net_proceeds - down_payment
    5. Compute simple_roi = total_profit / down_payment
    6. Compute hold_period_irr using truncated flows + net_proceeds as terminal value

    Args:
        exit_input: Exit scenario parameters (sale price, year, costs)
        monthly_cashflows: List of monthly cash flow entries (all available)
        purchase_date: Property purchase date for calculating sale month

    Returns:
        TotalReturnSummary with all return metrics and nested exit breakdown
    """
    # 1. Determine sale date and truncate cash flows
    sale_year = exit_input.sale_year
    max_months = sale_year * 12

    # Truncate cash flows: keep first sale_year * 12 months (or all if fewer)
    truncated_cashflows = monthly_cashflows[:max_months]
    total_months = len(truncated_cashflows)

    # 2. Calculate exit result
    exit_result = calculate_exit(exit_input)

    # 3. Compute cumulative net cash flow
    cumulative_net_cashflow = sum(cf.net_cashflow for cf in truncated_cashflows)

    # 4. Compute total profit: cumulative + net_proceeds - down_payment
    total_profit = (
        cumulative_net_cashflow + exit_result.net_proceeds - exit_input.down_payment
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # 5. Convert total_profit to USD
    total_profit_usd = convert_to_usd(total_profit, exit_input.cad_per_usd)

    # 6. Compute simple ROI: total_profit / down_payment
    if exit_input.down_payment == Decimal("0"):
        simple_roi = Decimal("0.0000")
    else:
        simple_roi = (total_profit / exit_input.down_payment).quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )

    # 7. Compute hold-period IRR
    # Use calculate_irr with net_proceeds as terminal value instead of property value
    if total_months == 0:
        # No cash flows, IRR cannot be calculated
        hold_period_irr = None
    else:
        hold_period_irr = calculate_irr(
            down_payment=exit_input.down_payment,
            monthly_cashflows=truncated_cashflows,
            current_property_value=exit_result.net_proceeds,  # Terminal value is net proceeds
        )

    # 8. Return TotalReturnSummary
    return TotalReturnSummary(
        hold_period_years=sale_year,
        total_months=total_months,
        cumulative_net_cashflow=cumulative_net_cashflow,
        net_proceeds=exit_result.net_proceeds,
        total_profit=total_profit,
        total_profit_usd=total_profit_usd,
        simple_roi=simple_roi,
        hold_period_irr=hold_period_irr,
        exit_result=exit_result,
    )
