"""Tests for FastAPI web application routes and endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from maple_return.main import app


@pytest.mark.asyncio
async def test_home_route_redirects_when_no_data(mock_db):
    """Test that the home route redirects to wizard when simulation fails."""
    with patch("maple_return.main.simulate", side_effect=Exception("no config")):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get("/")
            assert response.status_code == 307
            assert response.headers["location"] == "/wizard"


@pytest.mark.asyncio
async def test_home_route_shows_results_with_data(mock_db):
    """Test that the home route renders results when simulation succeeds."""
    from starlette.responses import HTMLResponse

    fake_data = {"dashboard": {}, "pnl_rows": [], "amort_rows": []}
    with (
        patch("maple_return.main.simulate", new_callable=AsyncMock, return_value=fake_data),
        patch("maple_return.main.templates") as mock_templates,
    ):
        mock_templates.TemplateResponse.return_value = HTMLResponse("<html>results</html>")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
            assert response.status_code == 200
            mock_templates.TemplateResponse.assert_called_once()


@pytest.mark.asyncio
async def test_wizard_route_returns_200():
    """Test that the wizard route returns a successful response."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/wizard")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_wizard_route_contains_title():
    """Test that the wizard route contains the expected title text."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/wizard")
        assert "Property Wizard" in response.text
        assert "Maple Return" in response.text


@pytest.mark.asyncio
async def test_wizard_route_renders_html():
    """Test that the wizard route returns HTML content."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/wizard")
        assert response.headers["content-type"].startswith("text/html")
        assert "<!DOCTYPE html>" in response.text


@pytest.mark.asyncio
async def test_wizard_has_progress_indicator():
    """Test that the wizard has a 5-step progress indicator."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/wizard")
        html = response.text
        assert "wizard-progress" in html
        assert "Property" in html
        assert "Mortgage" in html
        assert "Operating" in html
        assert "Scenarios" in html
        assert "Exit" in html


@pytest.mark.asyncio
async def test_wizard_has_all_step_partials():
    """Test that the wizard includes all 5 step partials."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/wizard")
        html = response.text
        # Check for key fields from each step
        assert 'name="purchase_price"' in html
        assert 'name="annual_rate"' in html
        assert 'name="monthly_rent"' in html
        assert 'name="renewal_scenario_1"' in html
        assert 'name="sale_price"' in html
