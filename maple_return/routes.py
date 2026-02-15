"""API routes for property configuration and simulation orchestration."""

import json
from dataclasses import asdict, is_dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .analysis import build_amortization_table, build_dashboard_snapshot, build_pnl_table
from .cashflow import generate_annual_operating_summaries, generate_monthly_cashflows
from .database import get_db
from .db_models import PropertyConfig
from .exit_model import ExitInput, calculate_exit, calculate_total_return
from .mortgage import MortgageInput, TermDefinition, calculate_multi_term
from .mortgage_summary import compare_scenarios, generate_annual_summaries
from .operating import OperatingInput

router = APIRouter(prefix="/api")


def _serialize(obj: Any) -> Any:
    """Recursively serialize dataclass instances, Decimals, and dates to JSON-compatible types.

    Converts:
    - Dataclasses to dicts
    - Decimal to str
    - date to ISO string
    - Lists recursively
    - Dicts recursively

    Args:
        obj: Object to serialize

    Returns:
        JSON-serializable version of the object
    """
    if is_dataclass(obj):
        return _serialize(asdict(obj))
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    else:
        return obj


@router.post("/save")
async def save_config(data: dict, db: AsyncSession = Depends(get_db)) -> dict:
    """Auto-save property configuration (partial updates supported).

    Upserts row id=1 with provided fields. If row exists, updates only provided fields.
    If not, creates new row. This supports incremental auto-save as user fills wizard.

    Args:
        data: JSON body with any subset of PropertyConfig fields
        db: Database session

    Returns:
        {"status": "ok"}
    """
    # Check if config row exists
    result = await db.execute(select(PropertyConfig).where(PropertyConfig.id == 1))
    config = result.scalar_one_or_none()

    if config:
        # Update existing row with provided fields
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
    else:
        # Create new row with provided fields
        config = PropertyConfig(id=1, **data)
        db.add(config)

    await db.commit()
    return {"status": "ok"}


@router.get("/load")
async def load_config(db: AsyncSession = Depends(get_db)) -> dict:
    """Load saved property configuration.

    Returns:
        Full PropertyConfig as JSON dict, or empty dict {} if no config exists
    """
    result = await db.execute(select(PropertyConfig).where(PropertyConfig.id == 1))
    config = result.scalar_one_or_none()

    if not config:
        return {}

    # Convert to dict, excluding SQLAlchemy metadata
    return {
        "id": config.id,
        "updated_at": config.updated_at.isoformat() if config.updated_at else None,
        "purchase_date": config.purchase_date,
        "purchase_price": config.purchase_price,
        "down_payment": config.down_payment,
        "annual_rate": config.annual_rate,
        "monthly_payment": config.monthly_payment,
        "amortization_years": config.amortization_years,
        "rate_type": config.rate_type,
        "monthly_rent": config.monthly_rent,
        "vacancy_rate": config.vacancy_rate,
        "property_tax_annual": config.property_tax_annual,
        "insurance_annual": config.insurance_annual,
        "maintenance_annual": config.maintenance_annual,
        "management_fee_rate": config.management_fee_rate,
        "rent_escalation_rate": config.rent_escalation_rate,
        "expense_escalation_rate": config.expense_escalation_rate,
        "cad_per_usd": config.cad_per_usd,
        "renewal_scenario_1": config.renewal_scenario_1,
        "renewal_scenario_2": config.renewal_scenario_2,
        "renewal_scenario_3": config.renewal_scenario_3,
        "sale_price": config.sale_price,
        "sale_year": config.sale_year,
        "commission_rate": config.commission_rate,
        "closing_costs": config.closing_costs,
    }


@router.post("/simulate")
async def simulate(db: AsyncSession = Depends(get_db)) -> dict:
    """Run full property simulation orchestrating all calculation engines.

    Reads PropertyConfig from DB, validates required fields, then orchestrates:
    - Multi-term mortgage calculation
    - Monthly cashflow generation
    - Annual summaries (operating and mortgage)
    - PnL and amortization tables
    - Dashboard snapshot
    - Exit calculation (if exit fields present)
    - Scenario comparison

    Returns:
        JSON with all calculation results, or 422 with missing fields error

    Raises:
        HTTPException: 422 if required fields missing
    """
    # Load config
    result = await db.execute(select(PropertyConfig).where(PropertyConfig.id == 1))
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(status_code=422, detail={"error": "No configuration saved"})

    # Validate required fields for core calculation
    required_fields = [
        "purchase_date",
        "purchase_price",
        "down_payment",
        "annual_rate",
        "monthly_payment",
        "amortization_years",
        "rate_type",
        "monthly_rent",
        "vacancy_rate",
        "property_tax_annual",
        "insurance_annual",
        "maintenance_annual",
        "management_fee_rate",
        "rent_escalation_rate",
        "expense_escalation_rate",
        "cad_per_usd",
    ]
    missing = [f for f in required_fields if getattr(config, f) is None]
    if missing:
        raise HTTPException(
            status_code=422, detail={"error": f"Missing fields: {', '.join(missing)}"}
        )

    # Parse renewal scenarios from JSON strings
    renewal_scenarios = []
    for scenario_json in [
        config.renewal_scenario_1,
        config.renewal_scenario_2,
        config.renewal_scenario_3,
    ]:
        if scenario_json:
            try:
                terms = json.loads(scenario_json)
                renewal_scenarios.append(
                    [TermDefinition(rate=Decimal(t["rate"]), rate_type=t["type"]) for t in terms]
                )
            except (json.JSONDecodeError, KeyError):
                # Skip invalid scenarios
                pass

    # Build MortgageInput
    purchase_date = date.fromisoformat(config.purchase_date)
    # Start date is purchase date + 1 month (first payment)
    start_year = purchase_date.year
    start_month = purchase_date.month + 1
    if start_month > 12:
        start_month = 1
        start_year += 1
    start_date = date(start_year, start_month, purchase_date.day)

    mortgage_input = MortgageInput(
        purchase_price=Decimal(config.purchase_price),
        down_payment=Decimal(config.down_payment),
        annual_rate=Decimal(config.annual_rate),
        monthly_payment=Decimal(config.monthly_payment),
        amortization_years=config.amortization_years,
        start_date=start_date,
        rate_type=config.rate_type,
        renewal_scenarios=renewal_scenarios if renewal_scenarios else [],
    )

    # Calculate multi-term mortgage scenarios
    scenarios = calculate_multi_term(mortgage_input)

    # Base case is scenario[0]
    base_scenario = scenarios[0]

    # Build OperatingInput
    operating_input = OperatingInput(
        monthly_rent=Decimal(config.monthly_rent),
        vacancy_rate=Decimal(config.vacancy_rate),
        property_tax_annual=Decimal(config.property_tax_annual),
        insurance_annual=Decimal(config.insurance_annual),
        maintenance_annual=Decimal(config.maintenance_annual),
        management_fee_rate=Decimal(config.management_fee_rate),
        rent_escalation_rate=Decimal(config.rent_escalation_rate),
        expense_escalation_rate=Decimal(config.expense_escalation_rate),
        lease_start_date=purchase_date,
    )

    # Generate monthly cashflows
    cashflows = generate_monthly_cashflows(
        operating_input=operating_input,
        mortgage_schedule=base_scenario.schedule,
        cad_per_usd=Decimal(config.cad_per_usd),
    )

    # Generate annual summaries
    annual_operating = generate_annual_operating_summaries(
        monthly_cashflows=cashflows,
    )

    annual_mortgage = generate_annual_summaries(
        schedule=base_scenario.schedule,
        purchase_price=Decimal(config.purchase_price),
    )

    # Build analysis tables
    # Use purchase_price as current value (no appreciation assumed for ongoing property)
    current_property_value = Decimal(config.purchase_price)

    pnl_table = build_pnl_table(
        annual_summaries=annual_operating,
        mortgage_annual_summaries=annual_mortgage,
        purchase_price=Decimal(config.purchase_price),
        current_property_value=current_property_value,
        down_payment=Decimal(config.down_payment),
    )

    amortization_table = build_amortization_table(
        schedule=base_scenario.schedule,
    )

    # Build dashboard snapshot
    # Get most recent remaining balance from mortgage schedule
    remaining_balance = (
        base_scenario.schedule[-1].balance if base_scenario.schedule else Decimal("0")
    )

    dashboard = build_dashboard_snapshot(
        monthly_cashflows=cashflows,
        purchase_date=purchase_date,
        down_payment=Decimal(config.down_payment),
        current_property_value=current_property_value,
        remaining_balance=remaining_balance,
        cad_per_usd=Decimal(config.cad_per_usd),
    )

    # Calculate exit if fields present
    exit_results = None
    total_return = None
    if all(
        [
            config.sale_price,
            config.sale_year,
            config.commission_rate,
            config.closing_costs,
        ]
    ):
        # Get mortgage balance at sale year (month = sale_year * 12)
        sale_month_index = config.sale_year * 12 - 1  # 0-indexed
        if sale_month_index < len(base_scenario.schedule):
            sale_month_balance = base_scenario.schedule[sale_month_index].balance
        else:
            # If sale year is beyond mortgage schedule, use last balance
            sale_month_balance = (
                base_scenario.schedule[-1].balance
                if base_scenario.schedule
                else Decimal("0")
            )

        exit_input = ExitInput(
            sale_price=Decimal(config.sale_price),
            sale_year=config.sale_year,
            commission_rate=Decimal(config.commission_rate),
            closing_costs=Decimal(config.closing_costs),
            remaining_mortgage_balance=sale_month_balance,
            purchase_price=Decimal(config.purchase_price),
            down_payment=Decimal(config.down_payment),
            cad_per_usd=Decimal(config.cad_per_usd),
        )

        exit_results = calculate_exit(exit_input=exit_input)

        total_return = calculate_total_return(
            exit_input=exit_input,
            monthly_cashflows=cashflows,
            purchase_date=purchase_date,
        )

    # Compare scenarios
    scenario_comparison = None
    if len(scenarios) > 1:
        scenario_comparison = compare_scenarios(
            scenarios=scenarios,
            purchase_price=Decimal(config.purchase_price),
        )

    # Serialize and return all results
    return _serialize(
        {
            "dashboard": dashboard,
            "pnl_table": pnl_table,
            "amortization_table": amortization_table,
            "annual_operating": annual_operating,
            "annual_mortgage": annual_mortgage,
            "cashflows": cashflows,
            "exit": exit_results,
            "total_return": total_return,
            "scenario_comparison": scenario_comparison,
            "scenarios": scenarios,
        }
    )
