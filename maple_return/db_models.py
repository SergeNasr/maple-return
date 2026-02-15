"""SQLAlchemy ORM models for property configuration persistence."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class PropertyConfig(Base):
    """Property configuration model for wizard auto-save.

    Stores all property input parameters as a single row (id=1).
    All fields except id are nullable to support partial auto-save as user fills wizard.
    Monetary values stored as strings to preserve Decimal precision.
    """

    __tablename__ = "property_config"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Property step
    purchase_date: Mapped[str | None] = mapped_column(String, nullable=True)
    purchase_price: Mapped[str | None] = mapped_column(String, nullable=True)
    down_payment: Mapped[str | None] = mapped_column(String, nullable=True)

    # Mortgage step
    annual_rate: Mapped[str | None] = mapped_column(String, nullable=True)
    monthly_payment: Mapped[str | None] = mapped_column(String, nullable=True)
    amortization_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rate_type: Mapped[str | None] = mapped_column(String, nullable=True)

    # Operating step
    monthly_rent: Mapped[str | None] = mapped_column(String, nullable=True)
    vacancy_rate: Mapped[str | None] = mapped_column(String, nullable=True)
    property_tax_annual: Mapped[str | None] = mapped_column(String, nullable=True)
    insurance_annual: Mapped[str | None] = mapped_column(String, nullable=True)
    maintenance_annual: Mapped[str | None] = mapped_column(String, nullable=True)
    management_fee_rate: Mapped[str | None] = mapped_column(String, nullable=True)
    rent_escalation_rate: Mapped[str | None] = mapped_column(String, nullable=True)
    expense_escalation_rate: Mapped[str | None] = mapped_column(String, nullable=True)
    cad_per_usd: Mapped[str | None] = mapped_column(String, nullable=True)

    # Scenarios step
    renewal_scenario_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    renewal_scenario_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    renewal_scenario_3: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Exit step
    sale_price: Mapped[str | None] = mapped_column(String, nullable=True)
    sale_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    commission_rate: Mapped[str | None] = mapped_column(String, nullable=True)
    closing_costs: Mapped[str | None] = mapped_column(String, nullable=True)
