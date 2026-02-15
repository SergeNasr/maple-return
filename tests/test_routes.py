"""Tests for API routes - save, load, and simulate endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from maple_return.main import app


@pytest.mark.asyncio
async def test_save_creates_config():
    """Test that POST /api/save creates a config with partial data."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/save", json={"purchase_price": "500000"}
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_save_partial_update():
    """Test that partial updates don't clobber existing fields."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save first field
        await client.post("/api/save", json={"purchase_price": "500000"})

        # Save second field
        await client.post("/api/save", json={"down_payment": "100000"})

        # Load and verify both fields are present
        load_response = await client.get("/api/load")
        data = load_response.json()
        assert data["purchase_price"] == "500000"
        assert data["down_payment"] == "100000"


@pytest.mark.asyncio
async def test_load_returns_saved_data():
    """Test that GET /api/load returns saved configuration."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save multiple fields
        save_data = {
            "purchase_price": "500000",
            "down_payment": "100000",
            "annual_rate": "0.045",
        }
        await client.post("/api/save", json=save_data)

        # Load and verify
        load_response = await client.get("/api/load")
        assert load_response.status_code == 200
        data = load_response.json()
        assert data["purchase_price"] == "500000"
        assert data["down_payment"] == "100000"
        assert data["annual_rate"] == "0.045"


@pytest.mark.asyncio
async def test_simulate_missing_fields_returns_422():
    """Test that POST /api/simulate returns 422 when required fields are missing."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Clear any existing config by saving minimal incomplete data
        # This overrides all fields from previous tests with None
        minimal_config = {
            "purchase_price": "500000",
            "purchase_date": None,
            "down_payment": None,
            "annual_rate": None,
            "monthly_payment": None,
            "amortization_years": None,
            "rate_type": None,
            "monthly_rent": None,
            "vacancy_rate": None,
            "property_tax_annual": None,
            "insurance_annual": None,
            "maintenance_annual": None,
            "management_fee_rate": None,
            "rent_escalation_rate": None,
            "expense_escalation_rate": None,
            "cad_per_usd": None,
        }
        await client.post("/api/save", json=minimal_config)

        # Attempt to simulate
        response = await client.post("/api/simulate")
        assert response.status_code == 422
        assert "error" in response.json()["detail"]
        assert "Missing fields" in response.json()["detail"]["error"]


@pytest.mark.asyncio
async def test_simulate_complete_config_returns_200():
    """Test that POST /api/simulate returns 200 with complete configuration."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Save complete config
        complete_config = {
            "purchase_date": "2020-01-15",
            "purchase_price": "500000",
            "down_payment": "100000",
            "annual_rate": "0.045",
            "monthly_payment": "2100",
            "amortization_years": 30,
            "rate_type": "variable",
            "monthly_rent": "2500",
            "vacancy_rate": "0.05",
            "property_tax_annual": "4000",
            "insurance_annual": "1800",
            "maintenance_annual": "2400",
            "management_fee_rate": "0.10",
            "rent_escalation_rate": "0.02",
            "expense_escalation_rate": "0.02",
            "cad_per_usd": "1.35",
            "renewal_scenario_1": '[{"rate": "0.05", "type": "fixed"}]',
            "sale_price": "600000",
            "sale_year": 5,
            "commission_rate": "0.05",
            "closing_costs": "5000",
        }
        await client.post("/api/save", json=complete_config)

        # Simulate
        response = await client.post("/api/simulate")
        assert response.status_code == 200

        # Verify response structure has expected top-level keys
        data = response.json()
        assert "dashboard" in data
        assert "pnl_table" in data
        assert "amortization_table" in data
        assert "annual_operating" in data
        assert "annual_mortgage" in data
        assert "cashflows" in data
        assert "exit" in data
        assert "total_return" in data
        assert "scenarios" in data
