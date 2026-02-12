"""Operating income and expense calculation engine.

Calculates rental income (with vacancy and escalation) and operating expenses
(with escalation and property management fee) for a single-unit Canadian rental property.
"""

from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from maple_return.mortgage import _add_months


@dataclass
class OperatingInput:
    """Input parameters for operating income and expense calculations.

    All monetary amounts are in CAD.
    """

    monthly_rent: Decimal  # Base monthly rent in CAD
    vacancy_rate: Decimal  # 0.0 to 1.0, e.g., 0.05 for 5%
    property_tax_annual: Decimal  # Annual amount in CAD
    insurance_annual: Decimal  # Annual amount in CAD
    maintenance_annual: Decimal  # Annual amount in CAD
    management_fee_rate: Decimal  # % of gross rent, e.g., 0.10 for 10%
    rent_escalation_rate: Decimal  # Annual %, e.g., 0.02 for 2%
    expense_escalation_rate: Decimal  # Annual %
    lease_start_date: date  # For lease anniversary escalation timing


@dataclass
class MonthlyOperating:
    """Monthly operating income and expense statement.

    All monetary amounts are in CAD, quantized to 2 decimal places.
    """

    month: date
    gross_rent: Decimal  # Rent before vacancy
    vacancy_deduction: Decimal  # gross_rent * vacancy_rate
    effective_rent: Decimal  # gross_rent - vacancy_deduction
    property_tax: Decimal  # Monthly portion
    insurance: Decimal  # Monthly portion
    maintenance: Decimal  # Monthly portion
    management_fee: Decimal  # management_fee_rate * gross_rent
    total_expenses: Decimal  # Sum of all expense line items
    noi: Decimal  # Net Operating Income: effective_rent - total_expenses


def calculate_monthly_operating(input_data: OperatingInput, month: date) -> MonthlyOperating:
    """Calculate operating income and expenses for a single month.

    Rent escalates on lease anniversary date using compounding.
    Expenses escalate on lease anniversary date using compounding.
    Vacancy is applied evenly across all months.
    Management fee is % of gross rent (not vacancy-adjusted).

    Args:
        input_data: Operating parameters
        month: The month to calculate for

    Returns:
        MonthlyOperating with all income and expense line items
    """
    # Calculate years elapsed since lease start (for escalation)
    # Full years = floor(months_elapsed / 12)
    months_elapsed = (
        (month.year - input_data.lease_start_date.year) * 12
        + month.month
        - input_data.lease_start_date.month
    )
    years_elapsed = months_elapsed // 12

    # Calculate gross rent with escalation
    # Rent increases on anniversary: base * (1 + rate)^years
    if input_data.rent_escalation_rate == Decimal("0"):
        gross_rent = input_data.monthly_rent
    else:
        escalation_factor = (Decimal("1") + input_data.rent_escalation_rate) ** years_elapsed
        gross_rent = input_data.monthly_rent * escalation_factor

    gross_rent = gross_rent.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Calculate vacancy deduction
    vacancy_deduction = (gross_rent * input_data.vacancy_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Calculate effective rent
    effective_rent = gross_rent - vacancy_deduction

    # Calculate monthly expenses with escalation
    # Base monthly = annual / 12, then apply escalation
    if input_data.expense_escalation_rate == Decimal("0"):
        expense_factor = Decimal("1")
    else:
        expense_factor = (Decimal("1") + input_data.expense_escalation_rate) ** years_elapsed

    property_tax = ((input_data.property_tax_annual / 12) * expense_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    insurance = ((input_data.insurance_annual / 12) * expense_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    maintenance = ((input_data.maintenance_annual / 12) * expense_factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Management fee is % of gross rent (scales with income, not vacancy-adjusted)
    management_fee = (gross_rent * input_data.management_fee_rate).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    # Calculate total expenses
    total_expenses = property_tax + insurance + maintenance + management_fee

    # Calculate NOI
    noi = (effective_rent - total_expenses).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return MonthlyOperating(
        month=month,
        gross_rent=gross_rent,
        vacancy_deduction=vacancy_deduction,
        effective_rent=effective_rent,
        property_tax=property_tax,
        insurance=insurance,
        maintenance=maintenance,
        management_fee=management_fee,
        total_expenses=total_expenses,
        noi=noi,
    )


def generate_operating_schedule(
    input_data: OperatingInput, start_date: date, num_months: int
) -> list[MonthlyOperating]:
    """Generate full operating schedule for consecutive months.

    Args:
        input_data: Operating parameters
        start_date: First month of schedule
        num_months: Number of months to generate

    Returns:
        List of MonthlyOperating entries for consecutive months
    """
    schedule = []
    current_date = start_date
    original_day = start_date.day

    for month_num in range(num_months):
        monthly_operating = calculate_monthly_operating(input_data, current_date)
        schedule.append(monthly_operating)

        # Move to next month
        if month_num < num_months - 1:  # Don't advance after the last month
            current_date = _add_months(start_date, month_num + 1, original_day)

    return schedule
