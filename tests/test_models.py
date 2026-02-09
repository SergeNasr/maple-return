"""Tests for core data models."""

from datetime import date
from decimal import Decimal

from maple_return.models import CashFlow, Mortgage, Property


class TestProperty:
    """Tests for Property model."""

    def test_property_creation(self):
        """Test creating a Property with valid data."""
        purchase_date = date(2020, 1, 15)
        purchase_price = Decimal("500000.00")
        down_payment = Decimal("100000.00")
        monthly_rent = Decimal("2500.00")
        vacancy_rate = Decimal("0.05")
        property_tax_annual = Decimal("3000.00")
        insurance_annual = Decimal("1200.00")
        maintenance_annual = Decimal("2400.00")
        rent_escalation_rate = Decimal("0.02")
        expense_escalation_rate = Decimal("0.02")

        prop = Property(
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            down_payment=down_payment,
            monthly_rent=monthly_rent,
            vacancy_rate=vacancy_rate,
            property_tax_annual=property_tax_annual,
            insurance_annual=insurance_annual,
            maintenance_annual=maintenance_annual,
            rent_escalation_rate=rent_escalation_rate,
            expense_escalation_rate=expense_escalation_rate,
        )

        assert prop.purchase_date == purchase_date
        assert prop.purchase_price == purchase_price
        assert prop.down_payment == down_payment
        assert prop.monthly_rent == monthly_rent
        assert prop.vacancy_rate == vacancy_rate
        assert prop.property_tax_annual == property_tax_annual
        assert prop.insurance_annual == insurance_annual
        assert prop.maintenance_annual == maintenance_annual
        assert prop.rent_escalation_rate == rent_escalation_rate
        assert prop.expense_escalation_rate == expense_escalation_rate

    def test_property_types(self):
        """Test that Property monetary fields are Decimal."""
        prop = Property(
            purchase_date=date(2020, 1, 15),
            purchase_price=Decimal("500000.00"),
            down_payment=Decimal("100000.00"),
            monthly_rent=Decimal("2500.00"),
            vacancy_rate=Decimal("0.05"),
            property_tax_annual=Decimal("3000.00"),
            insurance_annual=Decimal("1200.00"),
            maintenance_annual=Decimal("2400.00"),
            rent_escalation_rate=Decimal("0.02"),
            expense_escalation_rate=Decimal("0.02"),
        )

        assert isinstance(prop.purchase_price, Decimal)
        assert isinstance(prop.down_payment, Decimal)

    def test_property_date(self):
        """Test that Property purchase_date is a date object."""
        prop = Property(
            purchase_date=date(2020, 1, 15),
            purchase_price=Decimal("500000.00"),
            down_payment=Decimal("100000.00"),
            monthly_rent=Decimal("2500.00"),
            vacancy_rate=Decimal("0.05"),
            property_tax_annual=Decimal("3000.00"),
            insurance_annual=Decimal("1200.00"),
            maintenance_annual=Decimal("2400.00"),
            rent_escalation_rate=Decimal("0.02"),
            expense_escalation_rate=Decimal("0.02"),
        )

        assert isinstance(prop.purchase_date, date)


class TestMortgage:
    """Tests for Mortgage model."""

    def test_mortgage_creation(self):
        """Test creating a Mortgage with valid data."""
        principal = Decimal("400000.00")
        rate = Decimal("0.045")
        payment_amount = Decimal("2027.00")

        mortgage = Mortgage(
            principal=principal,
            rate=rate,
            payment_amount=payment_amount,
            amortization_years=30,
            term_years=5,
            is_variable=True,
        )

        assert mortgage.principal == principal
        assert mortgage.rate == rate
        assert mortgage.payment_amount == payment_amount
        assert mortgage.amortization_years == 30
        assert mortgage.term_years == 5
        assert mortgage.is_variable is True

    def test_mortgage_defaults(self):
        """Test that Mortgage has correct default values."""
        mortgage = Mortgage(
            principal=Decimal("400000.00"),
            rate=Decimal("0.045"),
            payment_amount=Decimal("2027.00"),
        )

        assert mortgage.amortization_years == 30
        assert mortgage.term_years == 5
        assert mortgage.is_variable is False

    def test_mortgage_types(self):
        """Test that Mortgage monetary fields are Decimal."""
        mortgage = Mortgage(
            principal=Decimal("400000.00"),
            rate=Decimal("0.045"),
            payment_amount=Decimal("2027.00"),
        )

        assert isinstance(mortgage.principal, Decimal)
        assert isinstance(mortgage.rate, Decimal)
        assert isinstance(mortgage.payment_amount, Decimal)


class TestCashFlow:
    """Tests for CashFlow model."""

    def test_cashflow_creation(self):
        """Test creating a CashFlow with valid data."""
        month = date(2020, 2, 1)
        rent_income = Decimal("2500.00")
        property_tax = Decimal("250.00")
        insurance = Decimal("100.00")
        maintenance = Decimal("200.00")
        mortgage_payment = Decimal("2027.00")
        mortgage_principal = Decimal("527.00")
        mortgage_interest = Decimal("1500.00")
        net_cashflow = Decimal("-577.00")

        cf = CashFlow(
            month=month,
            rent_income=rent_income,
            property_tax=property_tax,
            insurance=insurance,
            maintenance=maintenance,
            mortgage_payment=mortgage_payment,
            mortgage_principal=mortgage_principal,
            mortgage_interest=mortgage_interest,
            net_cashflow=net_cashflow,
        )

        assert cf.month == month
        assert cf.rent_income == rent_income
        assert cf.property_tax == property_tax
        assert cf.insurance == insurance
        assert cf.maintenance == maintenance
        assert cf.mortgage_payment == mortgage_payment
        assert cf.mortgage_principal == mortgage_principal
        assert cf.mortgage_interest == mortgage_interest
        assert cf.net_cashflow == net_cashflow

    def test_cashflow_calculations(self):
        """Test that CashFlow net_cashflow matches expected value."""
        # Income: 2500
        # Expenses: 250 + 100 + 200 + 2027 = 2577
        # Net: 2500 - 2577 = -77
        cf = CashFlow(
            month=date(2020, 2, 1),
            rent_income=Decimal("2500.00"),
            property_tax=Decimal("250.00"),
            insurance=Decimal("100.00"),
            maintenance=Decimal("200.00"),
            mortgage_payment=Decimal("2027.00"),
            mortgage_principal=Decimal("527.00"),
            mortgage_interest=Decimal("1500.00"),
            net_cashflow=Decimal("-77.00"),
        )

        # Verify the net cashflow is correct
        expected_net = (
            cf.rent_income
            - cf.property_tax
            - cf.insurance
            - cf.maintenance
            - cf.mortgage_payment
        )
        assert cf.net_cashflow == expected_net
