"""Canadian mortgage amortization engine.

Implements Canadian semi-annual compounding convention and generates
full monthly amortization schedules for mortgage loans.

Supports multi-term mortgages with rate renewals every 5 years (standard Canadian
mortgage structure) and scenario comparison across different renewal rate assumptions.
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


@dataclass
class TermDefinition:
    """Interest rate definition for a single mortgage term.

    Defines the rate parameters for one 5-year term in a multi-term mortgage.
    Used in renewal scenarios to specify different rate assumptions.
    """

    rate: Decimal  # Nominal annual rate for this term
    rate_type: str  # "variable" or "fixed" (metadata, doesn't affect calculation)


@dataclass
class MortgageInput:
    """Complete input specification for multi-term mortgage calculation.

    Captures initial mortgage parameters and renewal rate scenarios for
    comparing different rate assumptions over the full amortization period.
    """

    purchase_price: Decimal
    down_payment: Decimal
    annual_rate: Decimal  # Initial term rate
    monthly_payment: Decimal  # Initial term payment (user-specified)
    amortization_years: int  # Total amortization (e.g., 30)
    start_date: date  # First payment date
    rate_type: str  # Initial term: "variable" or "fixed"
    renewal_scenarios: list[list[TermDefinition]]  # 1-3 lists of renewal terms


@dataclass
class TermSummary:
    """Summary statistics for a single 5-year mortgage term.

    Aggregates payment details and balance changes for one term within
    a multi-term mortgage structure.
    """

    term_number: int
    rate: Decimal
    rate_type: str
    monthly_payment: Decimal
    start_balance: Decimal
    end_balance: Decimal
    total_principal: Decimal
    total_interest: Decimal
    months: int


@dataclass
class ScenarioResult:
    """Complete results for one renewal rate scenario.

    Contains the full amortization schedule, per-term summaries, and
    aggregate totals for a specific set of renewal rate assumptions.
    """

    scenario_index: int  # 0-based
    schedule: list[AmortizationEntry]  # Full monthly schedule
    terms: list[TermSummary]  # Per-term summary
    total_interest: Decimal  # Grand total interest paid
    total_payments: Decimal  # Grand total of all payments
    final_balance: Decimal  # Balance at end (should be 0)
    months_to_payoff: int  # Total months


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


def calculate_multi_term(input_data: MortgageInput) -> list[ScenarioResult]:
    """Calculate multi-term mortgage with renewal rate scenarios.

    Chains single-term calculations across 5-year renewal boundaries, recalculating
    payments at each renewal based on remaining balance, new rate, and remaining
    amortization. Supports 1-3 different renewal rate scenarios for comparison.

    Each term is exactly 5 years (60 months). At each renewal:
    1. Take remaining balance from end of previous term
    2. Calculate remaining amortization months
    3. Apply new renewal rate
    4. Recalculate payment using calculate_standard_payment()
    5. Generate next term's schedule using calculate_amortization()

    If renewal_scenarios list is shorter than needed, the last rate repeats for
    all subsequent terms.

    Args:
        input_data: Complete mortgage input including initial parameters and
                   renewal rate scenarios

    Returns:
        List of ScenarioResult objects, one per renewal scenario (1-3 scenarios)
    """
    total_amortization_months = input_data.amortization_years * 12
    initial_principal = input_data.purchase_price - input_data.down_payment

    # If no renewal scenarios provided, still need to process at least one scenario
    # but we'll only run the initial term (no renewals)
    scenarios_to_process = input_data.renewal_scenarios
    has_renewals = bool(scenarios_to_process)
    if not scenarios_to_process:
        scenarios_to_process = [[]]  # Single empty scenario (no renewals, just initial term)

    results = []

    for scenario_idx, renewal_rates in enumerate(scenarios_to_process):
        full_schedule: list[AmortizationEntry] = []
        term_summaries: list[TermSummary] = []

        current_balance = initial_principal
        current_date = input_data.start_date
        original_day = input_data.start_date.day
        months_elapsed = 0
        term_number = 1

        # Initial term uses user-specified payment and rate
        current_rate = input_data.annual_rate
        current_rate_type = input_data.rate_type
        current_payment = input_data.monthly_payment

        while months_elapsed < total_amortization_months and current_balance > Decimal("0.00"):
            # Determine how many months remaining in full amortization
            remaining_amortization = total_amortization_months - months_elapsed

            # Generate schedule for full remaining amortization
            # We'll truncate to 60 months (5-year term) unless it pays off sooner
            term_schedule = calculate_amortization(
                purchase_price=current_balance,
                down_payment=Decimal("0"),  # Already accounted for
                annual_rate=current_rate,
                monthly_payment=current_payment,
                amortization_months=remaining_amortization,
                start_date=current_date,
            )

            # Truncate to 60 months max (5-year term) unless it paid off earlier
            term_months = min(60, len(term_schedule))
            term_schedule = term_schedule[:term_months]

            # Adjust month numbers to be continuous
            month_offset = months_elapsed
            for entry in term_schedule:
                entry.month_number += month_offset

            # Calculate term summary
            start_balance = current_balance
            end_balance = term_schedule[-1].balance
            total_principal = sum(entry.principal for entry in term_schedule)
            total_interest = sum(entry.interest for entry in term_schedule)
            actual_months = len(term_schedule)

            term_summary = TermSummary(
                term_number=term_number,
                rate=current_rate,
                rate_type=current_rate_type,
                monthly_payment=current_payment,
                start_balance=start_balance,
                end_balance=end_balance,
                total_principal=total_principal,
                total_interest=total_interest,
                months=actual_months,
            )
            term_summaries.append(term_summary)

            # Append term schedule to full schedule
            full_schedule.extend(term_schedule)

            # Update state for next term
            months_elapsed += actual_months
            current_balance = end_balance

            # Check if we're done (balance paid off)
            if current_balance == Decimal("0.00"):
                break

            # If no renewals were specified, stop after first term
            if not has_renewals:
                break

            # Prepare for next term (renewal)
            term_number += 1

            # Get next rate from scenario (or repeat last rate if list is shorter)
            renewal_index = term_number - 2  # -1 for 0-based, -1 because term 1 used initial rate
            if renewal_index < len(renewal_rates):
                next_term = renewal_rates[renewal_index]
                current_rate = next_term.rate
                current_rate_type = next_term.rate_type
            elif renewal_rates:
                # Repeat last rate
                last_term = renewal_rates[-1]
                current_rate = last_term.rate
                current_rate_type = last_term.rate_type
            else:
                # No renewal rates specified, keep using initial rate
                current_rate = input_data.annual_rate
                current_rate_type = input_data.rate_type

            # Recalculate payment for next term
            remaining_months = total_amortization_months - months_elapsed
            monthly_rate = calculate_monthly_rate(current_rate)
            current_payment = calculate_standard_payment(
                current_balance, monthly_rate, remaining_months
            )

            # Update current_date for next term
            current_date = full_schedule[-1].date
            current_date = _add_months(current_date, 1, original_day)

        # Calculate scenario totals
        total_interest = sum(entry.interest for entry in full_schedule)
        total_payments = sum(entry.payment for entry in full_schedule)
        final_balance = full_schedule[-1].balance if full_schedule else current_balance
        months_to_payoff = len(full_schedule)

        scenario_result = ScenarioResult(
            scenario_index=scenario_idx,
            schedule=full_schedule,
            terms=term_summaries,
            total_interest=total_interest,
            total_payments=total_payments,
            final_balance=final_balance,
            months_to_payoff=months_to_payoff,
        )
        results.append(scenario_result)

    return results
