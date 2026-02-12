"""Canadian mortgage amortization engine.

Implements Canadian semi-annual compounding convention and generates
full monthly amortization schedules for mortgage loans.
"""

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal


def _add_months(start_date: date, months: int, original_day: int) -> date:
    """Add months to a date, preserving the original day-of-month when possible.

    Preserves the day from the very first payment date throughout the schedule.
    If the target month has fewer days, use the last day of that month.

    Args:
        start_date: Starting date
        months: Number of months to add
        original_day: The original day-of-month to preserve

    Returns:
        New date after adding months
    """
    # Calculate target year and month
    target_month = start_date.month + months
    target_year = start_date.year + (target_month - 1) // 12
    target_month = ((target_month - 1) % 12) + 1

    # Get the last day of the target month
    last_day = calendar.monthrange(target_year, target_month)[1]

    # Use the original day or the last day of the month, whichever is smaller
    target_day = min(original_day, last_day)

    return date(target_year, target_month, target_day)


@dataclass
class AmortizationEntry:
    """Single month's amortization details.

    Represents one row in a mortgage amortization schedule showing
    the payment breakdown and remaining balance.
    """

    month_number: int  # 1-indexed month counter
    date: date  # Payment date for this month
    payment: Decimal  # Total payment amount
    principal: Decimal  # Principal portion (reduces balance)
    interest: Decimal  # Interest portion
    balance: Decimal  # Remaining balance after payment


def calculate_monthly_rate(annual_rate: Decimal) -> Decimal:
    """Convert nominal annual rate to effective monthly rate using Canadian convention.

    Canadian mortgages compound semi-annually but pay monthly.
    Formula: (1 + annual_rate/2)^(1/6) - 1

    Args:
        annual_rate: Nominal annual interest rate (e.g., 0.05 for 5%)

    Returns:
        Effective monthly interest rate
    """
    if annual_rate == Decimal("0"):
        return Decimal("0")

    # Canadian semi-annual compounding: (1 + r/2)^(1/6) - 1
    # Convert to float for power calculation with high precision
    semi_annual_rate = float(annual_rate) / 2.0
    effective_monthly = ((1 + semi_annual_rate) ** (1.0 / 6.0)) - 1

    # Return with high precision to avoid rounding errors in subsequent calculations
    return Decimal(repr(effective_monthly))


def calculate_standard_payment(
    principal: Decimal, monthly_rate: Decimal, num_months: int
) -> Decimal:
    """Calculate standard amortization payment amount.

    Uses the standard mortgage payment formula:
    P * r * (1+r)^n / ((1+r)^n - 1)

    Args:
        principal: Loan principal amount
        monthly_rate: Effective monthly interest rate
        num_months: Number of monthly payments (amortization period)

    Returns:
        Monthly payment amount rounded to 2 decimal places
    """
    if monthly_rate == Decimal("0"):
        # Zero interest: equal principal payments
        return (principal / Decimal(num_months)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    # Standard formula: P * r * (1+r)^n / ((1+r)^n - 1)
    # Use float for power calculation
    one_plus_r = float(1 + monthly_rate)
    power_n = one_plus_r**num_months

    numerator = float(principal) * float(monthly_rate) * power_n
    denominator = power_n - 1

    payment = Decimal(str(numerator / denominator))

    return payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_amortization(
    purchase_price: Decimal,
    down_payment: Decimal,
    annual_rate: Decimal,
    monthly_payment: Decimal,
    amortization_months: int,
    start_date: date,
) -> list[AmortizationEntry]:
    """Generate full monthly amortization schedule.

    Calculates month-by-month payment breakdown showing principal, interest,
    and remaining balance. Handles edge cases like early payoff and
    negative amortization.

    Args:
        purchase_price: Total property purchase price
        down_payment: Down payment amount (not percentage)
        annual_rate: Nominal annual interest rate (e.g., 0.05 for 5%)
        monthly_payment: Fixed monthly payment amount
        amortization_months: Maximum number of months (amortization period)
        start_date: Date of first payment

    Returns:
        List of AmortizationEntry objects, one per month until balance is zero
        or amortization_months is reached
    """
    # Calculate initial principal
    principal = purchase_price - down_payment
    balance = principal

    # Convert to effective monthly rate
    monthly_rate = calculate_monthly_rate(annual_rate)

    schedule = []
    current_date = start_date
    original_day = start_date.day

    for month_num in range(1, amortization_months + 1):
        # Calculate interest for this month (rounded to 2 decimal places)
        interest = (balance * monthly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Determine payment and principal for this month
        if balance + interest <= monthly_payment:
            # Final month: payment is exactly balance + interest (balance is low enough to pay off)
            payment = balance + interest
            principal_portion = balance
            new_balance = Decimal("0.00")
        elif month_num == amortization_months and monthly_payment > interest:
            # Last month of amortization period: if payment > interest, force final payoff
            # (This handles rounding accumulation in standard payment scenarios)
            payment = balance + interest
            principal_portion = balance
            new_balance = Decimal("0.00")
        else:
            # Normal month: fixed payment
            payment = monthly_payment
            principal_portion = payment - interest
            new_balance = balance - principal_portion

        # Create entry
        entry = AmortizationEntry(
            month_number=month_num,
            date=current_date,
            payment=payment,
            principal=principal_portion,
            interest=interest,
            balance=new_balance,
        )
        schedule.append(entry)

        # Check if we're done
        if new_balance == Decimal("0.00"):
            break

        # Update for next iteration
        balance = new_balance
        current_date = _add_months(start_date, month_num, original_day)

    return schedule
