"""Core data models for Maple Return property investment simulation."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Property:
    """Property investment details and operating parameters.

    Captures purchase information and ongoing operating expenses for a rental property.
    All monetary amounts are in CAD.
    """

    purchase_date: date
    purchase_price: Decimal
    down_payment: Decimal
    monthly_rent: Decimal
    vacancy_rate: Decimal  # 0.0 to 1.0, e.g., 0.05 for 5%
    property_tax_annual: Decimal
    insurance_annual: Decimal
    maintenance_annual: Decimal
    rent_escalation_rate: Decimal  # Annual %, e.g., 0.02 for 2%
    expense_escalation_rate: Decimal  # Annual %


@dataclass
class Mortgage:
    """Mortgage loan details and term structure.

    Models Canadian mortgage characteristics: 5-year terms with rate renewal,
    30-year amortization, variable or fixed rate within each term.
    All monetary amounts are in CAD.
    """

    principal: Decimal
    rate: Decimal  # Current interest rate, e.g., 0.045 for 4.5%
    payment_amount: Decimal
    amortization_years: int = 30
    term_years: int = 5  # Canadian mortgage standard
    is_variable: bool = False


@dataclass
class CashFlow:
    """Monthly cash flow statement for a rental property.

    Captures all income and expense components for a single month,
    including the breakdown of mortgage payment into principal and interest.
    All monetary amounts are in CAD.
    """

    month: date
    rent_income: Decimal
    property_tax: Decimal  # Monthly portion
    insurance: Decimal  # Monthly portion
    maintenance: Decimal  # Monthly portion
    mortgage_payment: Decimal
    mortgage_principal: Decimal  # Principal portion of payment
    mortgage_interest: Decimal  # Interest portion of payment
    net_cashflow: Decimal  # Total income - total expenses
