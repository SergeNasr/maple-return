"""Tests for FastAPI web application routes and endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from maple_return.main import app


@pytest.mark.asyncio
async def test_home_route_returns_200():
    """Test that the home route returns a successful response."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_home_route_contains_title():
    """Test that the home route contains the expected title text."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert "Maple Return" in response.text


@pytest.mark.asyncio
async def test_home_route_contains_test_message():
    """Test that the home route contains the foundation phase test message."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert "Foundation phase: Web server is running successfully" in response.text


@pytest.mark.asyncio
async def test_home_route_renders_html():
    """Test that the home route returns HTML content."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
        assert response.headers["content-type"].startswith("text/html")
        assert "<!DOCTYPE html>" in response.text
